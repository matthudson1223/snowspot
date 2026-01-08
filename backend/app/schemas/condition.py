"""
Pydantic schemas for Condition endpoints.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ConditionBase(BaseModel):
    """Base schema for condition data."""

    # Snow measurements (inches)
    base_depth_in: Optional[Decimal] = Field(
        None, ge=0, le=9999, description="Base depth in inches"
    )
    summit_depth_in: Optional[Decimal] = Field(
        None, ge=0, le=9999, description="Summit depth in inches"
    )
    new_snow_24h_in: Optional[Decimal] = Field(
        None, ge=0, le=999, description="New snow in last 24 hours (inches)"
    )
    new_snow_48h_in: Optional[Decimal] = Field(
        None, ge=0, le=999, description="New snow in last 48 hours (inches)"
    )
    new_snow_7d_in: Optional[Decimal] = Field(
        None, ge=0, le=999, description="New snow in last 7 days (inches)"
    )

    # Weather conditions
    temperature_f: Optional[Decimal] = Field(
        None, ge=-100, le=150, description="Temperature in Fahrenheit"
    )
    wind_speed_mph: Optional[Decimal] = Field(
        None, ge=0, le=500, description="Wind speed in mph"
    )
    wind_direction: Optional[int] = Field(
        None, ge=0, le=360, description="Wind direction in degrees"
    )
    precipitation_in: Optional[Decimal] = Field(
        None, ge=0, le=100, description="Precipitation in inches"
    )
    humidity_percent: Optional[int] = Field(
        None, ge=0, le=100, description="Relative humidity percentage"
    )
    visibility_miles: Optional[Decimal] = Field(
        None, ge=0, le=100, description="Visibility in miles"
    )

    # Resort operations
    lifts_open: Optional[int] = Field(
        None, ge=0, description="Number of lifts open"
    )
    lifts_total: Optional[int] = Field(
        None, ge=0, description="Total number of lifts"
    )
    runs_open: Optional[int] = Field(
        None, ge=0, description="Number of runs open"
    )
    runs_total: Optional[int] = Field(
        None, ge=0, description="Total number of runs"
    )
    terrain_parks_open: Optional[int] = Field(
        None, ge=0, description="Number of terrain parks open"
    )


class ConditionCreate(ConditionBase):
    """Schema for creating new conditions."""

    resort_id: int = Field(..., description="Resort ID")
    time: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of conditions (defaults to now)",
    )

    # Derived metrics (can be provided or calculated)
    snow_quality_score: Optional[Decimal] = Field(
        None, ge=0, le=100, description="Snow quality score (0-100)"
    )
    skiability_index: Optional[Decimal] = Field(
        None, ge=0, le=100, description="Skiability index (0-100)"
    )
    crowd_level: Optional[int] = Field(
        None, ge=1, le=5, description="Crowd level (1-5)"
    )

    # Data provenance
    data_sources: Optional[dict[str, Any]] = Field(
        None, description="Sources that contributed to this record"
    )
    confidence_score: Optional[Decimal] = Field(
        None, ge=0, le=1, description="Data confidence score (0-1)"
    )


class ConditionResponse(ConditionBase):
    """Schema for condition response data."""

    model_config = ConfigDict(from_attributes=True)

    time: datetime = Field(..., description="Timestamp of conditions")
    resort_id: int = Field(..., description="Resort ID")

    # Derived metrics
    snow_quality_score: Optional[Decimal] = Field(
        None, description="Snow quality score (0-100)"
    )
    skiability_index: Optional[Decimal] = Field(
        None, description="Skiability index (0-100)"
    )
    crowd_level: Optional[int] = Field(
        None, description="Crowd level (1-5)"
    )

    # Data provenance
    data_sources: Optional[dict[str, Any]] = Field(
        None, description="Sources that contributed to this record"
    )
    confidence_score: Optional[Decimal] = Field(
        None, description="Data confidence score (0-1)"
    )


class ConditionWithQuality(ConditionResponse):
    """Condition response with quality description."""

    quality_description: Optional[str] = Field(
        None, description="Human-readable quality description"
    )


class ConditionSummary(BaseModel):
    """Lightweight condition summary."""

    model_config = ConfigDict(from_attributes=True)

    time: datetime
    resort_id: int
    new_snow_24h_in: Optional[Decimal]
    temperature_f: Optional[Decimal]
    snow_quality_score: Optional[Decimal]
    lifts_open: Optional[int]
    lifts_total: Optional[int]


class ConditionHistory(BaseModel):
    """Container for condition history."""

    resort_id: int
    resort_name: str
    resort_slug: str
    start_time: datetime
    end_time: datetime
    conditions: List[ConditionResponse]
    count: int


class LatestConditions(BaseModel):
    """Latest conditions for a resort with summary stats."""

    model_config = ConfigDict(from_attributes=True)

    resort_id: int
    resort_name: str
    resort_slug: str
    condition: Optional[ConditionResponse] = Field(
        None, description="Most recent condition record"
    )
    quality_description: Optional[str] = Field(
        None, description="Human-readable quality description"
    )
    last_updated: Optional[datetime] = Field(
        None, description="When conditions were last updated"
    )


# Combined resort + conditions schemas
class ResortWithLatestCondition(BaseModel):
    """Resort data with its latest condition."""

    model_config = ConfigDict(from_attributes=True)

    # Resort fields
    id: int
    name: str
    slug: str
    latitude: Decimal
    longitude: Decimal
    state: Optional[str]
    region: Optional[str]
    base_elevation_ft: Optional[int]
    summit_elevation_ft: Optional[int]
    vertical_drop_ft: Optional[int]
    total_lifts: Optional[int]
    total_runs: Optional[int]
    is_active: bool

    # Latest condition
    latest_condition: Optional[ConditionResponse] = Field(
        None, description="Most recent condition data"
    )
    quality_description: Optional[str] = Field(
        None, description="Human-readable quality description"
    )
