"""
Data fusion module for combining multiple data sources.

Provides pure functions for fusing measurements from multiple sources
using weighted averaging with time decay and confidence scoring.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


# Default source weights (higher = more trusted)
SOURCE_WEIGHTS: dict[str, float] = {
    "resort_official": 0.5,  # Most trusted - direct from resort
    "snotel": 0.4,  # NOAA weather stations - very reliable
    "weather_api": 0.1,  # Third-party APIs - least trusted
}

# Decay rate per hour (5% decay)
DECAY_RATE: float = 0.95

# Default maximum age for data (hours)
DEFAULT_MAX_AGE_HOURS: int = 24


@dataclass
class DataSource:
    """Single data source with value and metadata."""

    source_name: str
    value: float
    timestamp: datetime
    confidence: float  # 0-1 source-reported confidence
    weight: Optional[float] = None  # Base weight for this source type

    def __post_init__(self):
        """Set default weight based on source name if not provided."""
        if self.weight is None:
            self.weight = SOURCE_WEIGHTS.get(self.source_name, 0.1)


@dataclass
class FusionResult:
    """Result of data fusion operation."""

    best_estimate: float
    confidence: float
    sources_used: int
    total_sources: int


def calculate_age_hours(
    timestamp: datetime, current_time: Optional[datetime] = None
) -> float:
    """
    Calculate age of a timestamp in hours.

    Args:
        timestamp: The timestamp to calculate age for
        current_time: Reference time (defaults to now UTC)

    Returns:
        Age in hours as a float
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)

    # Handle timezone-naive timestamps by assuming UTC
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)

    delta = current_time - timestamp
    return delta.total_seconds() / 3600.0


def calculate_age_factor(age_hours: float, decay_rate: float = DECAY_RATE) -> float:
    """
    Calculate age decay factor using exponential decay.

    Args:
        age_hours: Age of data in hours
        decay_rate: Decay rate per hour (default 0.95 = 5% decay/hour)

    Returns:
        Decay factor from 0-1 (1 = fresh, lower = older)
    """
    if age_hours < 0:
        return 1.0  # Future timestamp, treat as fresh
    return decay_rate**age_hours


def calculate_effective_weight(
    base_weight: float, confidence: float, age_factor: float
) -> float:
    """
    Calculate effective weight for a data source.

    Args:
        base_weight: Base weight for the source type
        confidence: Source-reported confidence (0-1)
        age_factor: Time decay factor (0-1)

    Returns:
        Effective weight combining all factors
    """
    return base_weight * confidence * age_factor


def fuse_measurements(
    sources: list[DataSource],
    max_age_hours: int = DEFAULT_MAX_AGE_HOURS,
    current_time: Optional[datetime] = None,
    decay_rate: float = DECAY_RATE,
) -> Optional[FusionResult]:
    """
    Fuse multiple measurements into a single best estimate.

    Uses weighted averaging with:
    - Base weight per source type
    - Source-reported confidence
    - Exponential time decay

    Args:
        sources: List of DataSource objects to fuse
        max_age_hours: Maximum age to consider (older data ignored)
        current_time: Reference time for age calculation (defaults to now UTC)
        decay_rate: Exponential decay rate per hour (default 0.95)

    Returns:
        FusionResult with best estimate and confidence, or None if no valid data
    """
    if not sources:
        return None

    if current_time is None:
        current_time = datetime.now(timezone.utc)

    weighted_sum = 0.0
    total_weight = 0.0
    sources_used = 0
    total_base_weight = 0.0

    for source in sources:
        # Track total base weight for confidence calculation
        weight = source.weight if source.weight is not None else SOURCE_WEIGHTS.get(
            source.source_name, 0.1
        )
        total_base_weight += weight

        # Calculate age and check if too old
        age_hours = calculate_age_hours(source.timestamp, current_time)
        if age_hours > max_age_hours:
            continue  # Too old, skip

        # Calculate factors
        age_factor = calculate_age_factor(age_hours, decay_rate)
        effective_weight = calculate_effective_weight(
            weight, source.confidence, age_factor
        )

        # Accumulate weighted values
        weighted_sum += source.value * effective_weight
        total_weight += effective_weight
        sources_used += 1

    if total_weight == 0 or sources_used == 0:
        return None

    # Calculate best estimate
    best_estimate = weighted_sum / total_weight

    # Calculate confidence (0-1)
    # Higher when more sources contribute with higher weights
    confidence = min(1.0, total_weight / total_base_weight) if total_base_weight > 0 else 0.0

    return FusionResult(
        best_estimate=best_estimate,
        confidence=confidence,
        sources_used=sources_used,
        total_sources=len(sources),
    )


def fuse_measurements_simple(
    sources: list[DataSource],
    max_age_hours: int = DEFAULT_MAX_AGE_HOURS,
    current_time: Optional[datetime] = None,
) -> Optional[tuple[float, float]]:
    """
    Simplified fusion returning just (estimate, confidence) tuple.

    Args:
        sources: List of DataSource objects to fuse
        max_age_hours: Maximum age to consider (older data ignored)
        current_time: Reference time for age calculation

    Returns:
        Tuple of (best_estimate, confidence_score) or None if no valid data
    """
    result = fuse_measurements(sources, max_age_hours, current_time)
    if result is None:
        return None
    return (result.best_estimate, result.confidence)


def get_source_weight(source_name: str) -> float:
    """
    Get the default weight for a source type.

    Args:
        source_name: Name of the data source

    Returns:
        Default weight for that source (0.1 if unknown)
    """
    return SOURCE_WEIGHTS.get(source_name, 0.1)


def create_data_source(
    source_name: str,
    value: float,
    timestamp: datetime,
    confidence: float,
    weight: Optional[float] = None,
) -> DataSource:
    """
    Factory function to create a DataSource with proper defaults.

    Args:
        source_name: Name identifying the source type
        value: Measured value
        timestamp: When the measurement was taken
        confidence: Source-reported confidence (0-1)
        weight: Override weight (defaults to source type weight)

    Returns:
        DataSource instance
    """
    return DataSource(
        source_name=source_name,
        value=value,
        timestamp=timestamp,
        confidence=confidence,
        weight=weight if weight is not None else get_source_weight(source_name),
    )
