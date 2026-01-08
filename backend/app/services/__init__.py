# Business logic services

from app.services.quality_scorer import (
    SnowConditions,
    calculate_quality_score,
    calculate_new_snow_score,
    calculate_temperature_score,
    calculate_wind_score,
    calculate_snow_age_score,
    calculate_humidity_score,
    get_quality_description,
    calculate_with_description,
)

from app.services.data_fusion import (
    DataSource,
    FusionResult,
    SOURCE_WEIGHTS,
    fuse_measurements,
    fuse_measurements_simple,
    calculate_age_hours,
    calculate_age_factor,
    calculate_effective_weight,
    get_source_weight,
    create_data_source,
)

__all__ = [
    # Quality scorer
    "SnowConditions",
    "calculate_quality_score",
    "calculate_new_snow_score",
    "calculate_temperature_score",
    "calculate_wind_score",
    "calculate_snow_age_score",
    "calculate_humidity_score",
    "get_quality_description",
    "calculate_with_description",
    # Data fusion
    "DataSource",
    "FusionResult",
    "SOURCE_WEIGHTS",
    "fuse_measurements",
    "fuse_measurements_simple",
    "calculate_age_hours",
    "calculate_age_factor",
    "calculate_effective_weight",
    "get_source_weight",
    "create_data_source",
]
