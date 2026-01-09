"""
Weather Forecast Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ForecastBase(BaseModel):
    """Base schema for weather forecast data."""

    generated_at: datetime = Field(..., description="When the forecast was generated")
    forecast_for: datetime = Field(..., description="Date and time this forecast is for")
    temperature_high_f: Optional[float] = Field(None, description="Predicted high temperature in Fahrenheit")
    temperature_low_f: Optional[float] = Field(None, description="Predicted low temperature in Fahrenheit")
    predicted_snowfall_in: Optional[float] = Field(None, description="Predicted snowfall in inches")
    wind_speed_mph: Optional[float] = Field(None, description="Predicted wind speed in mph")
    precipitation_prob_percent: Optional[int] = Field(None, ge=0, le=100, description="Precipitation probability percentage")
    source: Optional[str] = Field(None, description="Forecast data source (e.g., 'noaa', 'openweather')")
    model: Optional[str] = Field(None, description="Weather model used (e.g., 'GFS', 'NAM')")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Forecast confidence score (0-1)")


class ForecastResponse(ForecastBase):
    """Response schema for weather forecast."""

    id: int
    resort_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ForecastCreate(BaseModel):
    """Schema for creating a new forecast."""

    resort_id: int
    generated_at: datetime
    forecast_for: datetime
    temperature_high_f: Optional[float] = None
    temperature_low_f: Optional[float] = None
    predicted_snowfall_in: Optional[float] = None
    wind_speed_mph: Optional[float] = None
    precipitation_prob_percent: Optional[int] = Field(None, ge=0, le=100)
    source: Optional[str] = None
    model: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)
