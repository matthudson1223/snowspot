"""
Tests for the snow quality scoring module.

Covers edge cases including null values, extreme conditions,
boundary conditions, and full scoring scenarios.
"""

import pytest
from app.services.quality_scorer import (
    SnowConditions,
    calculate_new_snow_score,
    calculate_temperature_score,
    calculate_wind_score,
    calculate_snow_age_score,
    calculate_humidity_score,
    calculate_quality_score,
    get_quality_description,
    calculate_with_description,
)


class TestCalculateNewSnowScore:
    """Tests for new snow scoring (0-30 points)."""

    def test_none_value_returns_zero(self):
        """Null new snow value should return 0."""
        assert calculate_new_snow_score(None) == 0.0

    def test_zero_snow_returns_zero(self):
        """No new snow should return 0."""
        assert calculate_new_snow_score(0) == 0.0

    def test_negative_snow_returns_zero(self):
        """Negative snow (invalid) should return 0."""
        assert calculate_new_snow_score(-5) == 0.0

    def test_trace_snow_returns_10(self):
        """Trace amounts of snow (< 1 inch) should return 10."""
        assert calculate_new_snow_score(0.5) == 10.0
        assert calculate_new_snow_score(0.1) == 10.0
        assert calculate_new_snow_score(0.99) == 10.0

    def test_light_snow_returns_15(self):
        """1-3 inches should return 15."""
        assert calculate_new_snow_score(1) == 15.0
        assert calculate_new_snow_score(2) == 15.0
        assert calculate_new_snow_score(2.99) == 15.0

    def test_moderate_snow_returns_20(self):
        """3-6 inches should return 20."""
        assert calculate_new_snow_score(3) == 20.0
        assert calculate_new_snow_score(4.5) == 20.0
        assert calculate_new_snow_score(5.99) == 20.0

    def test_heavy_snow_returns_25(self):
        """6-12 inches should return 25."""
        assert calculate_new_snow_score(6) == 25.0
        assert calculate_new_snow_score(9) == 25.0
        assert calculate_new_snow_score(11.99) == 25.0

    def test_epic_snow_returns_30(self):
        """12+ inches should return 30 (epic powder)."""
        assert calculate_new_snow_score(12) == 30.0
        assert calculate_new_snow_score(24) == 30.0
        assert calculate_new_snow_score(48) == 30.0

    def test_boundary_at_1_inch(self):
        """Test boundary at 1 inch."""
        assert calculate_new_snow_score(0.99) == 10.0
        assert calculate_new_snow_score(1.0) == 15.0

    def test_boundary_at_3_inches(self):
        """Test boundary at 3 inches."""
        assert calculate_new_snow_score(2.99) == 15.0
        assert calculate_new_snow_score(3.0) == 20.0

    def test_boundary_at_6_inches(self):
        """Test boundary at 6 inches."""
        assert calculate_new_snow_score(5.99) == 20.0
        assert calculate_new_snow_score(6.0) == 25.0

    def test_boundary_at_12_inches(self):
        """Test boundary at 12 inches."""
        assert calculate_new_snow_score(11.99) == 25.0
        assert calculate_new_snow_score(12.0) == 30.0


class TestCalculateTemperatureScore:
    """Tests for temperature scoring (0-25 points)."""

    def test_none_value_returns_zero(self):
        """Null temperature should return 0."""
        assert calculate_temperature_score(None) == 0.0

    def test_perfect_powder_temp_returns_25(self):
        """15-28°F should return 25 (ideal for powder)."""
        assert calculate_temperature_score(15) == 25.0
        assert calculate_temperature_score(22) == 25.0
        assert calculate_temperature_score(28) == 25.0

    def test_good_temp_returns_20(self):
        """10-32°F (outside 15-28) should return 20."""
        assert calculate_temperature_score(10) == 20.0
        assert calculate_temperature_score(12) == 20.0
        assert calculate_temperature_score(30) == 20.0
        assert calculate_temperature_score(32) == 20.0

    def test_acceptable_temp_returns_15(self):
        """5-35°F (outside 10-32) should return 15."""
        assert calculate_temperature_score(5) == 15.0
        assert calculate_temperature_score(7) == 15.0
        assert calculate_temperature_score(34) == 15.0
        assert calculate_temperature_score(35) == 15.0

    def test_too_cold_returns_10(self):
        """Below 5°F should return 10 (brittle snow)."""
        assert calculate_temperature_score(4) == 10.0
        assert calculate_temperature_score(0) == 10.0
        assert calculate_temperature_score(-10) == 10.0
        assert calculate_temperature_score(-40) == 10.0

    def test_too_warm_returns_5(self):
        """Above 35°F should return 5 (wet/heavy snow)."""
        assert calculate_temperature_score(36) == 5.0
        assert calculate_temperature_score(40) == 5.0
        assert calculate_temperature_score(50) == 5.0

    def test_extreme_cold(self):
        """Extremely cold temperatures."""
        assert calculate_temperature_score(-50) == 10.0

    def test_extreme_warm(self):
        """Extremely warm temperatures."""
        assert calculate_temperature_score(60) == 5.0


class TestCalculateWindScore:
    """Tests for wind speed scoring (0-15 points)."""

    def test_none_value_returns_zero(self):
        """Null wind should return 0."""
        assert calculate_wind_score(None) == 0.0

    def test_negative_wind_returns_zero(self):
        """Negative wind (invalid) should return 0."""
        assert calculate_wind_score(-5) == 0.0

    def test_calm_wind_returns_15(self):
        """< 10 mph should return 15."""
        assert calculate_wind_score(0) == 15.0
        assert calculate_wind_score(5) == 15.0
        assert calculate_wind_score(9.99) == 15.0

    def test_breezy_wind_returns_10(self):
        """10-20 mph should return 10."""
        assert calculate_wind_score(10) == 10.0
        assert calculate_wind_score(15) == 10.0
        assert calculate_wind_score(19.99) == 10.0

    def test_windy_returns_5(self):
        """20-30 mph should return 5."""
        assert calculate_wind_score(20) == 5.0
        assert calculate_wind_score(25) == 5.0
        assert calculate_wind_score(29.99) == 5.0

    def test_extreme_wind_returns_zero(self):
        """30+ mph should return 0 (dangerous)."""
        assert calculate_wind_score(30) == 0.0
        assert calculate_wind_score(50) == 0.0
        assert calculate_wind_score(100) == 0.0

    def test_hurricane_force_wind(self):
        """Hurricane force winds should return 0."""
        assert calculate_wind_score(75) == 0.0
        assert calculate_wind_score(150) == 0.0

    def test_boundary_at_10_mph(self):
        """Test boundary at 10 mph."""
        assert calculate_wind_score(9.99) == 15.0
        assert calculate_wind_score(10.0) == 10.0

    def test_boundary_at_20_mph(self):
        """Test boundary at 20 mph."""
        assert calculate_wind_score(19.99) == 10.0
        assert calculate_wind_score(20.0) == 5.0

    def test_boundary_at_30_mph(self):
        """Test boundary at 30 mph."""
        assert calculate_wind_score(29.99) == 5.0
        assert calculate_wind_score(30.0) == 0.0


class TestCalculateSnowAgeScore:
    """Tests for snow age scoring (0-20 points)."""

    def test_none_value_returns_zero(self):
        """Null snow age should return 0."""
        assert calculate_snow_age_score(None) == 0.0

    def test_negative_days_returns_zero(self):
        """Negative days (invalid) should return 0."""
        assert calculate_snow_age_score(-1) == 0.0

    def test_fresh_today_returns_20(self):
        """0 days old should return 20."""
        assert calculate_snow_age_score(0) == 20.0

    def test_yesterday_returns_15(self):
        """1 day old should return 15."""
        assert calculate_snow_age_score(1) == 15.0

    def test_recent_returns_10(self):
        """2-3 days old should return 10."""
        assert calculate_snow_age_score(2) == 10.0
        assert calculate_snow_age_score(3) == 10.0

    def test_week_old_returns_5(self):
        """4-7 days old should return 5."""
        assert calculate_snow_age_score(4) == 5.0
        assert calculate_snow_age_score(5) == 5.0
        assert calculate_snow_age_score(7) == 5.0

    def test_old_snow_returns_zero(self):
        """8+ days old should return 0."""
        assert calculate_snow_age_score(8) == 0.0
        assert calculate_snow_age_score(14) == 0.0
        assert calculate_snow_age_score(30) == 0.0


class TestCalculateHumidityScore:
    """Tests for humidity scoring (0-10 points)."""

    def test_none_value_returns_zero(self):
        """Null humidity should return 0."""
        assert calculate_humidity_score(None) == 0.0

    def test_negative_humidity_returns_zero(self):
        """Negative humidity (invalid) should return 0."""
        assert calculate_humidity_score(-10) == 0.0

    def test_bone_dry_returns_10(self):
        """< 30% humidity should return 10."""
        assert calculate_humidity_score(0) == 10.0
        assert calculate_humidity_score(15) == 10.0
        assert calculate_humidity_score(29) == 10.0

    def test_dry_returns_8(self):
        """30-50% humidity should return 8."""
        assert calculate_humidity_score(30) == 8.0
        assert calculate_humidity_score(40) == 8.0
        assert calculate_humidity_score(49) == 8.0

    def test_average_returns_5(self):
        """50-70% humidity should return 5."""
        assert calculate_humidity_score(50) == 5.0
        assert calculate_humidity_score(60) == 5.0
        assert calculate_humidity_score(69) == 5.0

    def test_humid_returns_2(self):
        """70%+ humidity should return 2."""
        assert calculate_humidity_score(70) == 2.0
        assert calculate_humidity_score(80) == 2.0
        assert calculate_humidity_score(100) == 2.0

    def test_over_100_humidity(self):
        """Over 100% humidity should return 2."""
        assert calculate_humidity_score(120) == 2.0


class TestCalculateQualityScore:
    """Tests for overall quality score calculation."""

    def test_all_none_values_returns_zero(self):
        """All null conditions should return 0."""
        conditions = SnowConditions()
        assert calculate_quality_score(conditions) == 0.0

    def test_epic_powder_day(self):
        """Perfect conditions should yield max score (100)."""
        conditions = SnowConditions(
            new_snow_24h_in=14.0,  # 30 points
            temperature_f=22.0,  # 25 points
            wind_speed_mph=5.0,  # 15 points
            days_since_snow=0,  # 20 points
            humidity_percent=20,  # 10 points
        )
        assert calculate_quality_score(conditions) == 100.0

    def test_poor_conditions(self):
        """Bad conditions should yield low score."""
        conditions = SnowConditions(
            new_snow_24h_in=0,  # 0 points
            temperature_f=40,  # 5 points (too warm)
            wind_speed_mph=35,  # 0 points (too windy)
            days_since_snow=10,  # 0 points (old snow)
            humidity_percent=90,  # 2 points (humid)
        )
        assert calculate_quality_score(conditions) == 7.0

    def test_partial_conditions(self):
        """Some null values should calculate with available data."""
        conditions = SnowConditions(
            new_snow_24h_in=6.0,  # 25 points
            temperature_f=25.0,  # 25 points
            # wind_speed_mph is None -> 0 points
            # days_since_snow is None -> 0 points
            humidity_percent=40,  # 8 points
        )
        assert calculate_quality_score(conditions) == 58.0

    def test_score_capped_at_100(self):
        """Score should never exceed 100."""
        conditions = SnowConditions(
            new_snow_24h_in=100,  # 30 points
            temperature_f=22.0,  # 25 points
            wind_speed_mph=0,  # 15 points
            days_since_snow=0,  # 20 points
            humidity_percent=10,  # 10 points
        )
        # Total would be 100, which is also the cap
        assert calculate_quality_score(conditions) == 100.0

    def test_decent_conditions(self):
        """Average conditions."""
        conditions = SnowConditions(
            new_snow_24h_in=2.0,  # 15 points
            temperature_f=30,  # 20 points
            wind_speed_mph=15,  # 10 points
            days_since_snow=2,  # 10 points
            humidity_percent=45,  # 8 points
        )
        assert calculate_quality_score(conditions) == 63.0


class TestGetQualityDescription:
    """Tests for quality description generation."""

    def test_epic_description(self):
        """Score 90+ should be epic."""
        assert get_quality_description(90) == "Epic Powder Day!"
        assert get_quality_description(100) == "Epic Powder Day!"

    def test_excellent_description(self):
        """Score 80-89 should be excellent."""
        assert get_quality_description(80) == "Excellent Conditions"
        assert get_quality_description(89) == "Excellent Conditions"

    def test_great_description(self):
        """Score 70-79 should be great."""
        assert get_quality_description(70) == "Great Day to Ski"
        assert get_quality_description(79) == "Great Day to Ski"

    def test_good_description(self):
        """Score 60-69 should be good."""
        assert get_quality_description(60) == "Good Conditions"
        assert get_quality_description(69) == "Good Conditions"

    def test_decent_description(self):
        """Score 50-59 should be decent."""
        assert get_quality_description(50) == "Decent Skiing"
        assert get_quality_description(59) == "Decent Skiing"

    def test_fair_description(self):
        """Score 40-49 should be fair."""
        assert get_quality_description(40) == "Fair Conditions"
        assert get_quality_description(49) == "Fair Conditions"

    def test_poor_description(self):
        """Score < 40 should be poor."""
        assert get_quality_description(0) == "Poor Conditions"
        assert get_quality_description(39) == "Poor Conditions"


class TestCalculateWithDescription:
    """Tests for combined score and description."""

    def test_returns_tuple(self):
        """Should return tuple of (score, description)."""
        conditions = SnowConditions(
            new_snow_24h_in=14.0,
            temperature_f=22.0,
            wind_speed_mph=5.0,
            days_since_snow=0,
            humidity_percent=20,
        )
        result = calculate_with_description(conditions)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == 100.0
        assert result[1] == "Epic Powder Day!"

    def test_poor_conditions_tuple(self):
        """Poor conditions should return matching tuple."""
        conditions = SnowConditions()
        score, description = calculate_with_description(conditions)
        assert score == 0.0
        assert description == "Poor Conditions"


class TestSnowConditionsDataclass:
    """Tests for SnowConditions dataclass."""

    def test_default_values_are_none(self):
        """All defaults should be None."""
        conditions = SnowConditions()
        assert conditions.new_snow_24h_in is None
        assert conditions.temperature_f is None
        assert conditions.wind_speed_mph is None
        assert conditions.days_since_snow is None
        assert conditions.humidity_percent is None

    def test_partial_initialization(self):
        """Should allow partial initialization."""
        conditions = SnowConditions(new_snow_24h_in=10.0)
        assert conditions.new_snow_24h_in == 10.0
        assert conditions.temperature_f is None

    def test_full_initialization(self):
        """Should allow full initialization."""
        conditions = SnowConditions(
            new_snow_24h_in=10.0,
            temperature_f=25.0,
            wind_speed_mph=5.0,
            days_since_snow=1,
            humidity_percent=30,
        )
        assert conditions.new_snow_24h_in == 10.0
        assert conditions.temperature_f == 25.0
        assert conditions.wind_speed_mph == 5.0
        assert conditions.days_since_snow == 1
        assert conditions.humidity_percent == 30
