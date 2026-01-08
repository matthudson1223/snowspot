"""
Resort API endpoints.

All responses are wrapped in the standard API response envelope.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models.resort import Resort
from app.models.condition import Condition
from app.schemas.resort import (
    ResortCreate,
    ResortUpdate,
    ResortResponse,
    ResortSummary,
)
from app.schemas.condition import (
    ConditionResponse,
    ConditionHistory,
    ResortWithLatestCondition,
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
)

router = APIRouter()


def _get_quality_description_for_condition(condition: Optional[Condition]) -> Optional[str]:
    """Get quality description for a condition record."""
    if condition is None or condition.snow_quality_score is None:
        return None
    return get_quality_description(float(condition.snow_quality_score))


@router.get(
    "/",
    response_model=APIResponse[List[ResortResponse]],
    summary="List all resorts",
    description="Get a paginated list of resorts with optional filtering by state, region, and active status.",
)
async def list_resorts(
    state: Optional[str] = Query(None, description="Filter by state"),
    region: Optional[str] = Query(None, description="Filter by region"),
    active_only: bool = Query(True, description="Only return active resorts"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """List all resorts with optional filtering and pagination."""
    query = db.query(Resort)

    if active_only:
        query = query.filter(Resort.is_active == True)
    if state:
        query = query.filter(Resort.state.ilike(f"%{state}%"))
    if region:
        query = query.filter(Resort.region.ilike(f"%{region}%"))

    # Get total count for pagination
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    resorts = query.order_by(Resort.name).offset(offset).limit(page_size).all()

    # Create pagination metadata
    pagination = create_pagination_meta(total=total, page=page, page_size=page_size)

    return create_success_response(
        data=[ResortResponse.model_validate(r) for r in resorts],
        pagination=pagination,
    )


@router.get(
    "/with-conditions",
    response_model=APIResponse[List[ResortWithLatestCondition]],
    summary="List resorts with latest conditions",
    description="Get resorts with their most recent condition data and quality scores.",
)
async def list_resorts_with_conditions(
    state: Optional[str] = Query(None, description="Filter by state"),
    region: Optional[str] = Query(None, description="Filter by region"),
    active_only: bool = Query(True, description="Only return active resorts"),
    min_quality_score: Optional[float] = Query(
        None, ge=0, le=100, description="Minimum snow quality score"
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """List resorts with their latest condition data."""
    # Subquery to get latest condition time for each resort
    latest_condition_subquery = (
        db.query(
            Condition.resort_id,
            func.max(Condition.time).label("max_time"),
        )
        .group_by(Condition.resort_id)
        .subquery()
    )

    # Build main query
    query = db.query(Resort)

    if active_only:
        query = query.filter(Resort.is_active == True)
    if state:
        query = query.filter(Resort.state.ilike(f"%{state}%"))
    if region:
        query = query.filter(Resort.region.ilike(f"%{region}%"))

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    resorts = query.order_by(Resort.name).offset(offset).limit(page_size).all()

    # Fetch latest conditions for each resort
    results = []
    for resort in resorts:
        # Get latest condition for this resort
        latest_condition = (
            db.query(Condition)
            .filter(Condition.resort_id == resort.id)
            .order_by(desc(Condition.time))
            .first()
        )

        # Skip if filtering by quality score and condition doesn't meet threshold
        if min_quality_score is not None:
            if (
                latest_condition is None
                or latest_condition.snow_quality_score is None
                or float(latest_condition.snow_quality_score) < min_quality_score
            ):
                continue

        # Get quality description
        quality_desc = _get_quality_description_for_condition(latest_condition)

        results.append(
            ResortWithLatestCondition(
                id=resort.id,
                name=resort.name,
                slug=resort.slug,
                latitude=resort.latitude,
                longitude=resort.longitude,
                state=resort.state,
                region=resort.region,
                base_elevation_ft=resort.base_elevation_ft,
                summit_elevation_ft=resort.summit_elevation_ft,
                vertical_drop_ft=resort.vertical_drop_ft,
                total_lifts=resort.total_lifts,
                total_runs=resort.total_runs,
                is_active=resort.is_active,
                latest_condition=(
                    ConditionResponse.model_validate(latest_condition)
                    if latest_condition
                    else None
                ),
                quality_description=quality_desc,
            )
        )

    # Adjust total if filtering by quality score
    adjusted_total = len(results) if min_quality_score is not None else total
    pagination = create_pagination_meta(
        total=adjusted_total, page=page, page_size=page_size
    )

    return create_success_response(data=results, pagination=pagination)


@router.get(
    "/{resort_slug}",
    response_model=APIResponse[ResortWithLatestCondition],
    summary="Get resort by slug",
    description="Get detailed resort information by its URL slug, including latest conditions.",
    responses={
        404: {"model": APIErrorResponse, "description": "Resort not found"},
    },
)
async def get_resort(
    resort_slug: str,
    include_conditions: bool = Query(
        True, description="Include latest conditions in response"
    ),
    db: Session = Depends(get_db),
):
    """Get a single resort by slug with optional latest conditions."""
    resort = db.query(Resort).filter(Resort.slug == resort_slug).first()

    if not resort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"Resort with slug '{resort_slug}' not found",
            ),
        )

    # Get latest condition if requested
    latest_condition = None
    quality_desc = None
    if include_conditions:
        latest_condition = (
            db.query(Condition)
            .filter(Condition.resort_id == resort.id)
            .order_by(desc(Condition.time))
            .first()
        )
        quality_desc = _get_quality_description_for_condition(latest_condition)

    result = ResortWithLatestCondition(
        id=resort.id,
        name=resort.name,
        slug=resort.slug,
        latitude=resort.latitude,
        longitude=resort.longitude,
        state=resort.state,
        region=resort.region,
        base_elevation_ft=resort.base_elevation_ft,
        summit_elevation_ft=resort.summit_elevation_ft,
        vertical_drop_ft=resort.vertical_drop_ft,
        total_lifts=resort.total_lifts,
        total_runs=resort.total_runs,
        is_active=resort.is_active,
        latest_condition=(
            ConditionResponse.model_validate(latest_condition)
            if latest_condition
            else None
        ),
        quality_description=quality_desc,
    )

    return create_success_response(data=result)


@router.get(
    "/{resort_slug}/history",
    response_model=APIResponse[ConditionHistory],
    summary="Get resort condition history",
    description="Get historical condition data for a resort over a specified time period.",
    responses={
        404: {"model": APIErrorResponse, "description": "Resort not found"},
    },
)
async def get_resort_history(
    resort_slug: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of history (max 7 days)"),
    db: Session = Depends(get_db),
):
    """Get condition history for a resort."""
    resort = db.query(Resort).filter(Resort.slug == resort_slug).first()

    if not resort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"Resort with slug '{resort_slug}' not found",
            ),
        )

    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)

    # Query conditions within time range
    conditions = (
        db.query(Condition)
        .filter(
            Condition.resort_id == resort.id,
            Condition.time >= start_time,
            Condition.time <= end_time,
        )
        .order_by(desc(Condition.time))
        .all()
    )

    history = ConditionHistory(
        resort_id=resort.id,
        resort_name=resort.name,
        resort_slug=resort.slug,
        start_time=start_time,
        end_time=end_time,
        conditions=[ConditionResponse.model_validate(c) for c in conditions],
        count=len(conditions),
    )

    return create_success_response(data=history)


@router.post(
    "/",
    response_model=APIResponse[ResortResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new resort",
    description="Create a new resort entry.",
    responses={
        400: {"model": APIErrorResponse, "description": "Validation error"},
    },
)
async def create_resort(
    resort_data: ResortCreate,
    db: Session = Depends(get_db),
):
    """Create a new resort."""
    # Check if slug already exists
    existing = db.query(Resort).filter(Resort.slug == resort_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_error_response(
                code=ErrorCodes.BAD_REQUEST,
                message=f"Resort with slug '{resort_data.slug}' already exists",
                field="slug",
            ),
        )

    # Create resort
    resort = Resort(**resort_data.model_dump())
    db.add(resort)
    db.commit()
    db.refresh(resort)

    return create_success_response(
        data=ResortResponse.model_validate(resort),
        message="Resort created successfully",
    )


@router.patch(
    "/{resort_slug}",
    response_model=APIResponse[ResortResponse],
    summary="Update a resort",
    description="Update an existing resort's information.",
    responses={
        404: {"model": APIErrorResponse, "description": "Resort not found"},
    },
)
async def update_resort(
    resort_slug: str,
    resort_data: ResortUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing resort."""
    resort = db.query(Resort).filter(Resort.slug == resort_slug).first()

    if not resort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"Resort with slug '{resort_slug}' not found",
            ),
        )

    # Update only provided fields
    update_data = resort_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resort, field, value)

    db.commit()
    db.refresh(resort)

    return create_success_response(
        data=ResortResponse.model_validate(resort),
        message="Resort updated successfully",
    )


@router.delete(
    "/{resort_slug}",
    response_model=APIResponse[dict],
    summary="Delete a resort",
    description="Soft delete a resort by setting is_active to false.",
    responses={
        404: {"model": APIErrorResponse, "description": "Resort not found"},
    },
)
async def delete_resort(
    resort_slug: str,
    db: Session = Depends(get_db),
):
    """Soft delete a resort (sets is_active to False)."""
    resort = db.query(Resort).filter(Resort.slug == resort_slug).first()

    if not resort:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=create_error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"Resort with slug '{resort_slug}' not found",
            ),
        )

    resort.is_active = False
    db.commit()

    return create_success_response(
        data={"slug": resort_slug, "is_active": False},
        message=f"Resort '{resort.name}' has been deactivated",
    )
