"""
Snow quality scoring module.

Provides pure functions for calculating snow quality scores based on
multiple environmental factors. Scores range from 0-100.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SnowConditions:
    """Current snow conditions for scoring."""

    new_snow_24h_in: Optional[float] = None
    temperature_f: Optional[float] = None
    wind_speed_mph: Optional[float] = None
    days_since_snow: Optional[int] = None
    humidity_percent: Optional[float] = None


def calculate_new_snow_score(new_snow_inches: Optional[float]) -> float:
    """
    Calculate score based on new snow amount (0-30 points).

    Args:
        new_snow_inches: Amount of new snow in last 24 hours (inches)

    Returns:
        Score from 0-30 based on snow amount
    """
    if new_snow_inches is None:
        return 0.0

    if new_snow_inches >= 12:
        return 30.0  # Epic powder day
    elif new_snow_inches >= 6:
        return 25.0  # Great day
    elif new_snow_inches >= 3:
        return 20.0  # Good day
    elif new_snow_inches >= 1:
        return 15.0  # Decent
    elif new_snow_inches > 0:
        return 10.0  # Some fresh snow
    else:
        return 0.0  # No new snow


def calculate_temperature_score(temperature_f: Optional[float]) -> float:
    """
    Calculate score based on temperature (0-25 points).

    Ideal temperature for light, dry powder is 15-28°F.

    Args:
        temperature_f: Current temperature in Fahrenheit

    Returns:
        Score from 0-25 based on temperature
    """
    if temperature_f is None:
        return 0.0

    if 15 <= temperature_f <= 28:
        return 25.0  # Perfect temp for powder
    elif 10 <= temperature_f <= 32:
        return 20.0  # Good temp
    elif 5 <= temperature_f <= 35:
        return 15.0  # Acceptable
    elif temperature_f < 5:
        return 10.0  # Too cold (brittle snow)
    else:
        return 5.0  # Too warm (heavy/wet snow)


def calculate_wind_score(wind_speed_mph: Optional[float]) -> float:
    """
    Calculate score based on wind speed (0-15 points).

    Lower wind is better for skiing conditions.

    Args:
        wind_speed_mph: Current wind speed in mph

    Returns:
        Score from 0-15 based on wind conditions
    """
    if wind_speed_mph is None:
        return 0.0

    if wind_speed_mph < 0:
        return 0.0  # Invalid wind speed

    if wind_speed_mph < 10:
        return 15.0  # Calm, perfect
    elif wind_speed_mph < 20:
        return 10.0  # Breezy but manageable
    elif wind_speed_mph < 30:
        return 5.0  # Windy
    else:
        return 0.0  # Too windy, dangerous


def calculate_snow_age_score(days_since_snow: Optional[int]) -> float:
    """
    Calculate score based on snow age (0-20 points).

    Fresh snow is best; older snow loses quality.

    Args:
        days_since_snow: Number of days since last snowfall

    Returns:
        Score from 0-20 based on snow freshness
    """
    if days_since_snow is None:
        return 0.0

    if days_since_snow < 0:
        return 0.0  # Invalid value

    if days_since_snow == 0:
        return 20.0  # Fresh today!
    elif days_since_snow == 1:
        return 15.0  # Yesterday's snow
    elif days_since_snow <= 3:
        return 10.0  # Recent snow
    elif days_since_snow <= 7:
        return 5.0  # Week-old snow
    else:
        return 0.0  # Old snow


def calculate_humidity_score(humidity_percent: Optional[float]) -> float:
    """
    Calculate score based on humidity (0-10 points).

    Lower humidity means lighter, fluffier powder snow.

    Args:
        humidity_percent: Current relative humidity (0-100)

    Returns:
        Score from 0-10 based on humidity
    """
    if humidity_percent is None:
        return 0.0

    if humidity_percent < 0:
        return 0.0  # Invalid value

    if humidity_percent < 30:
        return 10.0  # Bone dry powder
    elif humidity_percent < 50:
        return 8.0  # Dry
    elif humidity_percent < 70:
        return 5.0  # Average
    else:
        return 2.0  # Humid (heavier snow)


def calculate_quality_score(conditions: SnowConditions) -> float:
    """
    Calculate overall snow quality score (0-100).

    Combines multiple factors:
    - New snow amount (max 30 points)
    - Temperature (max 25 points)
    - Wind (max 15 points)
    - Age of snow (max 20 points)
    - Humidity (max 10 points)

    Args:
        conditions: SnowConditions dataclass with current conditions

    Returns:
        Total quality score from 0-100
    """
    score = 0.0

    score += calculate_new_snow_score(conditions.new_snow_24h_in)
    score += calculate_temperature_score(conditions.temperature_f)
    score += calculate_wind_score(conditions.wind_speed_mph)
    score += calculate_snow_age_score(conditions.days_since_snow)
    score += calculate_humidity_score(conditions.humidity_percent)

    return min(100.0, score)


def get_quality_description(score: float) -> str:
    """
    Get human-readable description for a quality score.

    Args:
        score: Quality score from 0-100

    Returns:
        Human-friendly description of conditions
    """
    if score >= 90:
        return "Epic Powder Day!"
    elif score >= 80:
        return "Excellent Conditions"
    elif score >= 70:
        return "Great Day to Ski"
    elif score >= 60:
        return "Good Conditions"
    elif score >= 50:
        return "Decent Skiing"
    elif score >= 40:
        return "Fair Conditions"
    else:
        return "Poor Conditions"


def calculate_with_description(conditions: SnowConditions) -> tuple[float, str]:
    """
    Calculate quality score and return with description.

    Args:
        conditions: SnowConditions dataclass with current conditions

    Returns:
        Tuple of (score, description)
    """
    score = calculate_quality_score(conditions)
    description = get_quality_description(score)
    return score, description
