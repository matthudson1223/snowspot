"""
Conditions API endpoints.

All responses are wrapped in the standard API response envelope.
Uses the quality_scorer service to calculate snow quality before saving.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models.resort import Resort
from app.models.condition import Condition
from app.schemas.condition import (
    ConditionCreate,
    ConditionResponse,
    ConditionWithQuality,
    ConditionSummary,
    LatestConditions,
)
from app.schemas.api_response import (
    APIResponse,
    APIErrorResponse,
    ErrorCodes,
    create_success_response,
    create_error_response,
    create_pagination_meta,
)
from app.services.quality_scorer import (
    SnowConditions,
    calculate_quality_score,
    get_quality_description,
    calculate_with_description,
)

router = APIRouter()


def _calculate_days_since_snow(
    db: Session, resort_id: int, current_time: datetime
) -> Optional[int]:
    """
    Calculate days since last significant snowfall for a resort.

    Args:
        db: Database session
        resort_id: Resort ID to check
        current_time: Reference time

    Returns:
        Days since last snowfall (>=1 inch in 24h), or None if unknown
    """
    # Look for the most recent condition with significant new snow
    last_snow = (
        db.query(Condition)
        .filter(
            Condition.resort_id == resort_id,
            Condition.new_snow_24h_in >= 1.0,
            Condition.time <= current_time,
        )
        .order_by(desc(Condition.time))
        .first()
    )

    if last_snow is None:
        return None

    delta = current_time - last_snow.time.replace(tzinfo=None)
    return delta.days


def _calculate_snow_quality(
    condition_data: dict,
    db: Session,
    resort_id: int,
    current_time: datetime,
) -> tuple[float, str]:
    """
    Calculate snow quality score using the quality_scorer service.

    Args:
        condition_data: Condition data dict
        db: Database session
        resort_id: Resort ID
        current_time: Reference time

    Returns:
        Tuple of (quality_score, quality_description)
    """
    # Build SnowConditions from data
    snow_conditions = SnowConditions(
        new_snow_24h_in=(
            float(condition_data.get("new_snow_24h_in"))
            if condition_data.get("new_snow_24h_in") is not None
            else None
        ),
        temperature_f=(
            float(condition_data.get("temperature_f"))
            if condition_data.get("temperature_f") is not None
            else None
        ),
        wind_speed_mph=(
            float(condition_data.get("wind_speed_mph"))
            if condition_data.get("wind_speed_mph") is not None
            else None
        ),
        humidity_percent=(
            float(condition_data.get("humidity_percent"))
            if condition_data.get("humidity_percent") is not None
            else None
        ),
        days_since_snow=_calculate_days_since_snow(db, resort_id, current_time),
    )

    # Calculate score and description
    return calculate_with_description(snow_conditions)


@router.get(
    "/latest",
    response_model=APIResponse[List[LatestConditions]],
    summary="Get latest conditions for all resorts",
    description="Get the most recent condition data for all active resorts.",
)
async def get_latest_conditions(
    state: Optional[str] = Query(None, description="Filter by state"),
    region: Optional[str] = Query(None, description="Filter by region"),
    min_quality_score: Optional[float] = Query(
        None, ge=0, le=100, description="Minimum snow quality score"
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Get latest conditions for all active resorts."""
    # Build query for active resorts
    query = db.query(Resort).filter(Resort.is_active == True)

    if state:
        query = query.filter(Resort.state.ilike(f"%{state}%"))
    if region:
        query = query.filter(Resort.region.ilike(f"%{region}%"))

    resorts = query.order_by(Resort.name).all()

    results = []
    for resort in resorts:
        # Get latest condition
        latest = (
            db.query(Condition)
            .filter(Condition.resort_id == resort.id)
            .order_by(desc(Condition.time))
            .first()
        )

        # Apply quality score filter
        if min_quality_score is not None:
            if (
                latest is None
                or latest.snow_quality_score is None
                or float(latest.snow_quality_score) < min_quality_score
            ):
                continue

        # Get quality description
        quality_desc = None
        if latest and latest.snow_quality_score is not None:
            quality_desc = get_quality_description(float(latest.snow_quality_score))

        results.append(
            LatestConditions(
                resort_id=resort.id,
                resort_name=resort.name,
                resort_slug=resort.slug,
                condition=(
                    ConditionResponse.model_validate(latest) if latest else None
                ),
                quality_description=quality_desc,
                last_updated=latest.time if latest else None,
            )
        )

    # Apply pagination
    total = len(results)
    offset = (page - 1) * page_size
    paginated_results = results[offset : offset + page_size]

    pagination = create_pagination_meta(total=total, page=page, page_size=page_size)

    return create_success_response(data=paginated_results, pagination=pagination)


@router.get(
    "/resort/{resort_id}",
    response_model=APIResponse[List[ConditionWithQuality]],
    summary="Get conditions for a resort",
    description="Get condition history for a specific resort.",
    responses={
        404: {"model": APIErrorResponse, "description": "Resort not found"},
    },
)
async def get_conditions_by_resort(
    resort_id: int,
    hours: int = Query(24, ge=1, le=168, description="Hours of history (max 7 days)"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Get condition history for a resort."""
    # Verify resort exists
    resort = db.query(Resort).filter(Resort.id == resort_id).first()
    if not resort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"Resort with ID {resort_id} not found",
            ),
        )

    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)

    # Query conditions
    query = db.query(Condition).filter(
        Condition.resort_id == resort_id,
        Condition.time >= start_time,
        Condition.time <= end_time,
    )

    total = query.count()

    offset = (page - 1) * page_size
    conditions = (
        query.order_by(desc(Condition.time)).offset(offset).limit(page_size).all()
    )

    # Add quality descriptions
    results = []
    for condition in conditions:
        quality_desc = None
        if condition.snow_quality_score is not None:
            quality_desc = get_quality_description(float(condition.snow_quality_score))

        result = ConditionWithQuality(
            **ConditionResponse.model_validate(condition).model_dump(),
            quality_description=quality_desc,
        )
        results.append(result)

    pagination = create_pagination_meta(total=total, page=page, page_size=page_size)

    return create_success_response(data=results, pagination=pagination)


@router.get(
    "/{resort_id}/latest",
    response_model=APIResponse[ConditionWithQuality],
    summary="Get latest condition for a resort",
    description="Get the most recent condition data for a specific resort.",
    responses={
        404: {"model": APIErrorResponse, "description": "Resort or condition not found"},
    },
)
async def get_latest_condition_for_resort(
    resort_id: int,
    db: Session = Depends(get_db),
):
    """Get the latest condition for a specific resort."""
    # Verify resort exists
    resort = db.query(Resort).filter(Resort.id == resort_id).first()
    if not resort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"Resort with ID {resort_id} not found",
            ),
        )

    # Get latest condition
    condition = (
        db.query(Condition)
        .filter(Condition.resort_id == resort_id)
        .order_by(desc(Condition.time))
        .first()
    )

    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"No condition data available for resort ID {resort_id}",
            ),
        )

    # Get quality description
    quality_desc = None
    if condition.snow_quality_score is not None:
        quality_desc = get_quality_description(float(condition.snow_quality_score))

    result = ConditionWithQuality(
        **ConditionResponse.model_validate(condition).model_dump(),
        quality_description=quality_desc,
    )

    return create_success_response(data=result)


@router.post(
    "/",
    response_model=APIResponse[ConditionWithQuality],
    status_code=status.HTTP_201_CREATED,
    summary="Create new conditions",
    description="Create new condition data for a resort. Snow quality score is automatically calculated using the quality_scorer service.",
    responses={
        404: {"model": APIErrorResponse, "description": "Resort not found"},
        400: {"model": APIErrorResponse, "description": "Validation error"},
    },
)
async def create_condition(
    condition_data: ConditionCreate,
    db: Session = Depends(get_db),
):
    """
    Create new condition data for a resort.

    The snow quality score is automatically calculated using the quality_scorer
    service based on the provided condition data.
    """
    # Verify resort exists
    resort = db.query(Resort).filter(Resort.id == condition_data.resort_id).first()
    if not resort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"Resort with ID {condition_data.resort_id} not found",
            ),
        )

    # Prepare condition data
    data = condition_data.model_dump()
    current_time = data.get("time") or datetime.utcnow()
    data["time"] = current_time

    # Calculate snow quality score using quality_scorer service
    quality_score, quality_description = _calculate_snow_quality(
        data, db, condition_data.resort_id, current_time
    )

    # Set the calculated quality score (override if provided)
    data["snow_quality_score"] = Decimal(str(round(quality_score, 2)))

    # Create condition record
    condition = Condition(**data)
    db.add(condition)
    db.commit()
    db.refresh(condition)

    result = ConditionWithQuality(
        **ConditionResponse.model_validate(condition).model_dump(),
        quality_description=quality_description,
    )

    return create_success_response(
        data=result,
        message="Condition data created successfully with calculated quality score",
    )


@router.post(
    "/bulk",
    response_model=APIResponse[List[ConditionWithQuality]],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple conditions",
    description="Bulk create condition data for multiple resorts. Snow quality scores are automatically calculated.",
    responses={
        400: {"model": APIErrorResponse, "description": "Validation error"},
    },
)
async def create_conditions_bulk(
    conditions: List[ConditionCreate],
    db: Session = Depends(get_db),
):
    """
    Bulk create condition data.

    Snow quality scores are automatically calculated for each condition
    using the quality_scorer service.
    """
    if not conditions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                code=ErrorCodes.BAD_REQUEST,
                message="At least one condition must be provided",
            ),
        )

    if len(conditions) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                code=ErrorCodes.BAD_REQUEST,
                message="Maximum 100 conditions per bulk request",
            ),
        )

    # Get all resort IDs to verify they exist
    resort_ids = {c.resort_id for c in conditions}
    existing_resorts = (
        db.query(Resort.id).filter(Resort.id.in_(resort_ids)).all()
    )
    existing_ids = {r.id for r in existing_resorts}

    missing_ids = resort_ids - existing_ids
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                code=ErrorCodes.BAD_REQUEST,
                message=f"Resort IDs not found: {sorted(missing_ids)}",
            ),
        )

    results = []
    for condition_data in conditions:
        data = condition_data.model_dump()
        current_time = data.get("time") or datetime.utcnow()
        data["time"] = current_time

        # Calculate snow quality score
        quality_score, quality_description = _calculate_snow_quality(
            data, db, condition_data.resort_id, current_time
        )
        data["snow_quality_score"] = Decimal(str(round(quality_score, 2)))

        # Create condition record
        condition = Condition(**data)
        db.add(condition)
        db.flush()  # Get ID without committing

        results.append(
            ConditionWithQuality(
                **ConditionResponse.model_validate(condition).model_dump(),
                quality_description=quality_description,
            )
        )

    db.commit()

    return create_success_response(
        data=results,
        message=f"Successfully created {len(results)} condition records",
    )


@router.get(
    "/compare",
    response_model=APIResponse[List[LatestConditions]],
    summary="Compare conditions across resorts",
    description="Get latest conditions for multiple resorts for comparison.",
)
async def compare_conditions(
    resort_ids: List[int] = Query(..., description="List of resort IDs to compare"),
    db: Session = Depends(get_db),
):
    """Compare latest conditions across multiple resorts."""
    if len(resort_ids) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                code=ErrorCodes.BAD_REQUEST,
                message="Maximum 10 resorts can be compared at once",
            ),
        )

    # Get resorts
    resorts = db.query(Resort).filter(Resort.id.in_(resort_ids)).all()

    if not resorts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                code=ErrorCodes.NOT_FOUND,
                message="No resorts found with the provided IDs",
            ),
        )

    results = []
    for resort in resorts:
        # Get latest condition
        latest = (
            db.query(Condition)
            .filter(Condition.resort_id == resort.id)
            .order_by(desc(Condition.time))
            .first()
        )

        quality_desc = None
        if latest and latest.snow_quality_score is not None:
            quality_desc = get_quality_description(float(latest.snow_quality_score))

        results.append(
            LatestConditions(
                resort_id=resort.id,
                resort_name=resort.name,
                resort_slug=resort.slug,
                condition=(
                    ConditionResponse.model_validate(latest) if latest else None
                ),
                quality_description=quality_desc,
                last_updated=latest.time if latest else None,
            )
        )

    # Sort by quality score (descending), putting None values last
    results.sort(
        key=lambda x: (
            x.condition.snow_quality_score if x.condition and x.condition.snow_quality_score else Decimal(0)
        ),
        reverse=True,
    )

    return create_success_response(data=results)


@router.get(
    "/powder-alert",
    response_model=APIResponse[List[LatestConditions]],
    summary="Get powder day resorts",
    description="Get resorts with excellent snow conditions (quality score >= 70 and new snow >= 6 inches).",
)
async def get_powder_alert_resorts(
    state: Optional[str] = Query(None, description="Filter by state"),
    min_new_snow: float = Query(
        6.0, ge=0, description="Minimum new snow in 24h (inches)"
    ),
    min_quality: float = Query(70.0, ge=0, le=100, description="Minimum quality score"),
    db: Session = Depends(get_db),
):
    """Get resorts currently experiencing powder conditions."""
    # Get all active resorts
    query = db.query(Resort).filter(Resort.is_active == True)
    if state:
        query = query.filter(Resort.state.ilike(f"%{state}%"))

    resorts = query.all()

    results = []
    for resort in resorts:
        # Get latest condition
        latest = (
            db.query(Condition)
            .filter(Condition.resort_id == resort.id)
            .order_by(desc(Condition.time))
            .first()
        )

        if not latest:
            continue

        # Check powder criteria
        has_new_snow = (
            latest.new_snow_24h_in is not None
            and float(latest.new_snow_24h_in) >= min_new_snow
        )
        has_quality = (
            latest.snow_quality_score is not None
            and float(latest.snow_quality_score) >= min_quality
        )

        if not (has_new_snow and has_quality):
            continue

        quality_desc = get_quality_description(float(latest.snow_quality_score))

        results.append(
            LatestConditions(
                resort_id=resort.id,
                resort_name=resort.name,
                resort_slug=resort.slug,
                condition=ConditionResponse.model_validate(latest),
                quality_description=quality_desc,
                last_updated=latest.time,
            )
        )

    # Sort by quality score descending
    results.sort(
        key=lambda x: float(x.condition.snow_quality_score) if x.condition else 0,
        reverse=True,
    )

    return create_success_response(
        data=results,
        message=(
            f"Found {len(results)} resort(s) with powder conditions"
            if results
            else "No resorts currently meeting powder criteria"
        ),
    )
