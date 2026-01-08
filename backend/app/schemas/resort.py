"""
Pydantic schemas for Resort endpoints.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class ResortBase(BaseModel):
    """Base schema for resort data."""

    name: str = Field(..., min_length=1, max_length=255, description="Resort name")
    slug: str = Field(
        ..., min_length=1, max_length=255, description="URL-friendly identifier"
    )
    latitude: Decimal = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: Decimal = Field(..., ge=-180, le=180, description="Longitude coordinate")
    timezone: str = Field(
        default="America/Denver", max_length=50, description="Resort timezone"
    )
    region: Optional[str] = Field(None, max_length=100, description="Geographic region")
    state: Optional[str] = Field(None, max_length=50, description="State/Province")
    country: str = Field(default="USA", max_length=50, description="Country")


class ResortCreate(ResortBase):
    """Schema for creating a new resort."""

    base_elevation_ft: Optional[int] = Field(
        None, ge=0, description="Base elevation in feet"
    )
    summit_elevation_ft: Optional[int] = Field(
        None, ge=0, description="Summit elevation in feet"
    )
    vertical_drop_ft: Optional[int] = Field(
        None, ge=0, description="Vertical drop in feet"
    )
    total_lifts: Optional[int] = Field(None, ge=0, description="Total number of lifts")
    total_runs: Optional[int] = Field(None, ge=0, description="Total number of runs")
    total_acres: Optional[int] = Field(
        None, ge=0, description="Total skiable acres"
    )
    official_url: Optional[str] = Field(
        None, max_length=500, description="Official resort website"
    )
    data_source_config: Optional[dict[str, Any]] = Field(
        None, description="Scraping configuration"
    )
    snotel_station_ids: Optional[List[str]] = Field(
        None, description="Nearby SNOTEL station IDs"
    )
    weather_station_id: Optional[str] = Field(
        None, max_length=50, description="Weather station ID"
    )


class ResortUpdate(BaseModel):
    """Schema for updating a resort (all fields optional)."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Resort name"
    )
    latitude: Optional[Decimal] = Field(
        None, ge=-90, le=90, description="Latitude coordinate"
    )
    longitude: Optional[Decimal] = Field(
        None, ge=-180, le=180, description="Longitude coordinate"
    )
    timezone: Optional[str] = Field(None, max_length=50, description="Resort timezone")
    region: Optional[str] = Field(None, max_length=100, description="Geographic region")
    state: Optional[str] = Field(None, max_length=50, description="State/Province")
    country: Optional[str] = Field(None, max_length=50, description="Country")
    base_elevation_ft: Optional[int] = Field(
        None, ge=0, description="Base elevation in feet"
    )
    summit_elevation_ft: Optional[int] = Field(
        None, ge=0, description="Summit elevation in feet"
    )
    vertical_drop_ft: Optional[int] = Field(
        None, ge=0, description="Vertical drop in feet"
    )
    total_lifts: Optional[int] = Field(None, ge=0, description="Total number of lifts")
    total_runs: Optional[int] = Field(None, ge=0, description="Total number of runs")
    total_acres: Optional[int] = Field(None, ge=0, description="Total skiable acres")
    official_url: Optional[str] = Field(
        None, max_length=500, description="Official resort website"
    )
    is_active: Optional[bool] = Field(None, description="Whether resort is active")
    data_source_config: Optional[dict[str, Any]] = Field(
        None, description="Scraping configuration"
    )
    snotel_station_ids: Optional[List[str]] = Field(
        None, description="Nearby SNOTEL station IDs"
    )
    weather_station_id: Optional[str] = Field(
        None, max_length=50, description="Weather station ID"
    )


class ResortResponse(ResortBase):
    """Schema for resort response data."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique resort ID")
    base_elevation_ft: Optional[int] = Field(
        None, description="Base elevation in feet"
    )
    summit_elevation_ft: Optional[int] = Field(
        None, description="Summit elevation in feet"
    )
    vertical_drop_ft: Optional[int] = Field(
        None, description="Vertical drop in feet"
    )
    total_lifts: Optional[int] = Field(None, description="Total number of lifts")
    total_runs: Optional[int] = Field(None, description="Total number of runs")
    total_acres: Optional[int] = Field(None, description="Total skiable acres")
    official_url: Optional[str] = Field(None, description="Official resort website")
    is_active: bool = Field(True, description="Whether resort is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ResortSummary(BaseModel):
    """Lightweight resort summary for lists."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    state: Optional[str]
    region: Optional[str]
    is_active: bool
