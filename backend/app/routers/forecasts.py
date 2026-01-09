"""
Weather Forecasts API Router.

Provides endpoints for retrieving weather forecast data for ski resorts.
"""

from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resort import Resort
from app.models.forecast import WeatherForecast
from app.schemas.api_response import create_success_response, create_error_response, ErrorCodes
from app.schemas.forecast import ForecastResponse

router = APIRouter()


@router.get("/{resort_id}")
async def get_resort_forecasts(
    resort_id: int,
    days: int = Query(default=7, ge=1, le=14, description="Number of forecast days"),
    db: Session = Depends(get_db),
):
    """
    Get weather forecasts for a specific resort.

    Args:
        resort_id: The ID of the resort
        days: Number of days to forecast (1-14, default 7)

    Returns:
        List of forecast data for the resort
    """
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

    # Query forecasts
    forecasts = (
        db.query(WeatherForecast)
        .filter(WeatherForecast.resort_id == resort_id)
        .filter(WeatherForecast.forecast_for >= datetime.now(timezone.utc).date())
        .order_by(WeatherForecast.forecast_for)
        .limit(days)
        .all()
    )

    # Return empty list if no forecasts found (don't error)
    forecast_data = [ForecastResponse.model_validate(f) for f in forecasts]

    return create_success_response(
        data=forecast_data,
        message=f"Retrieved {len(forecast_data)} forecast days for {resort.name}",
    )
