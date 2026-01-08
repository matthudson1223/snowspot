"""
Tests for the data fusion module.

Covers edge cases including null values, extreme ages, single sources,
multiple sources with various weights, and time decay scenarios.
"""

import pytest
from datetime import datetime, timezone, timedelta
from app.services.data_fusion import (
    DataSource,
    FusionResult,
    SOURCE_WEIGHTS,
    DECAY_RATE,
    calculate_age_hours,
    calculate_age_factor,
    calculate_effective_weight,
    fuse_measurements,
    fuse_measurements_simple,
    get_source_weight,
    create_data_source,
)


class TestSourceWeights:
    """Tests for source weight constants."""

    def test_resort_official_weight(self):
        """Resort official should be most trusted."""
        assert SOURCE_WEIGHTS["resort_official"] == 0.5

    def test_snotel_weight(self):
        """SNOTEL should be second most trusted."""
        assert SOURCE_WEIGHTS["snotel"] == 0.4

    def test_weather_api_weight(self):
        """Weather API should be least trusted."""
        assert SOURCE_WEIGHTS["weather_api"] == 0.1

    def test_weights_sum(self):
        """Weights should sum to 1.0."""
        assert sum(SOURCE_WEIGHTS.values()) == 1.0


class TestCalculateAgeHours:
    """Tests for age calculation in hours."""

    def test_zero_age(self, current_time):
        """Same timestamp should be 0 hours."""
        assert calculate_age_hours(current_time, current_time) == 0.0

    def test_one_hour_ago(self, current_time, one_hour_ago):
        """One hour difference."""
        result = calculate_age_hours(one_hour_ago, current_time)
        assert result == pytest.approx(1.0)

    def test_two_hours_ago(self, current_time, two_hours_ago):
        """Two hour difference."""
        result = calculate_age_hours(two_hours_ago, current_time)
        assert result == pytest.approx(2.0)

    def test_one_day_ago(self, current_time, one_day_ago):
        """24 hour difference."""
        result = calculate_age_hours(one_day_ago, current_time)
        assert result == pytest.approx(24.0)

    def test_future_timestamp(self, current_time):
        """Future timestamp should return negative age."""
        future = current_time + timedelta(hours=2)
        result = calculate_age_hours(future, current_time)
        assert result == pytest.approx(-2.0)

    def test_handles_naive_timestamps(self):
        """Should handle timezone-naive timestamps by assuming UTC."""
        naive_time = datetime(2024, 1, 15, 12, 0, 0)
        aware_time = datetime(2024, 1, 15, 13, 0, 0, tzinfo=timezone.utc)
        result = calculate_age_hours(naive_time, aware_time)
        assert result == pytest.approx(1.0)


class TestCalculateAgeFactor:
    """Tests for age decay factor calculation."""

    def test_fresh_data_factor_is_one(self):
        """Fresh data (0 hours) should have factor of 1.0."""
        assert calculate_age_factor(0) == 1.0

    def test_one_hour_decay(self):
        """One hour should decay by DECAY_RATE."""
        result = calculate_age_factor(1)
        assert result == pytest.approx(DECAY_RATE)

    def test_two_hour_decay(self):
        """Two hours should decay by DECAY_RATE^2."""
        result = calculate_age_factor(2)
        assert result == pytest.approx(DECAY_RATE**2)

    def test_24_hour_decay(self):
        """24 hours should decay significantly."""
        result = calculate_age_factor(24)
        assert result == pytest.approx(DECAY_RATE**24)
        # With 0.95 decay: 0.95^24 ≈ 0.29
        assert result < 0.35

    def test_negative_age_returns_one(self):
        """Negative age (future) should return 1.0."""
        assert calculate_age_factor(-1) == 1.0
        assert calculate_age_factor(-10) == 1.0

    def test_custom_decay_rate(self):
        """Should respect custom decay rate."""
        result = calculate_age_factor(1, decay_rate=0.9)
        assert result == pytest.approx(0.9)

    def test_very_old_data(self):
        """Very old data should have very small factor."""
        result = calculate_age_factor(100)
        assert result < 0.01


class TestCalculateEffectiveWeight:
    """Tests for effective weight calculation."""

    def test_all_ones(self):
        """All factors 1.0 should return base weight."""
        assert calculate_effective_weight(0.5, 1.0, 1.0) == 0.5

    def test_half_confidence(self):
        """Half confidence should halve weight."""
        assert calculate_effective_weight(0.5, 0.5, 1.0) == 0.25

    def test_half_age_factor(self):
        """Half age factor should halve weight."""
        assert calculate_effective_weight(0.5, 1.0, 0.5) == 0.25

    def test_combined_factors(self):
        """Combined factors should multiply."""
        result = calculate_effective_weight(0.5, 0.8, 0.9)
        assert result == pytest.approx(0.5 * 0.8 * 0.9)

    def test_zero_confidence(self):
        """Zero confidence should yield zero weight."""
        assert calculate_effective_weight(0.5, 0.0, 1.0) == 0.0


class TestFuseMeasurements:
    """Tests for the main fusion function."""

    def test_empty_sources_returns_none(self, current_time):
        """Empty sources list should return None."""
        result = fuse_measurements([], current_time=current_time)
        assert result is None

    def test_single_source(self, current_time):
        """Single source should return its value with confidence."""
        sources = [
            DataSource(
                source_name="resort_official",
                value=12.0,
                timestamp=current_time,
                confidence=1.0,
                weight=0.5,
            )
        ]
        result = fuse_measurements(sources, current_time=current_time)
        assert result is not None
        assert result.best_estimate == pytest.approx(12.0)
        assert result.confidence == pytest.approx(1.0)
        assert result.sources_used == 1

    def test_multiple_sources_weighted_average(self, current_time):
        """Multiple sources should produce weighted average."""
        sources = [
            DataSource(
                source_name="resort_official",
                value=12.0,
                timestamp=current_time,
                confidence=1.0,
                weight=0.5,
            ),
            DataSource(
                source_name="snotel",
                value=10.0,
                timestamp=current_time,
                confidence=1.0,
                weight=0.5,
            ),
        ]
        result = fuse_measurements(sources, current_time=current_time)
        assert result is not None
        # Equal weights, equal confidence, same time -> simple average
        assert result.best_estimate == pytest.approx(11.0)
        assert result.sources_used == 2

    def test_age_affects_weight(self, current_time, one_hour_ago, two_hours_ago):
        """Older data should have less influence."""
        sources = [
            DataSource(
                source_name="resort_official",
                value=10.0,
                timestamp=two_hours_ago,  # Older
                confidence=1.0,
                weight=0.5,
            ),
            DataSource(
                source_name="snotel",
                value=14.0,
                timestamp=current_time,  # Fresh
                confidence=1.0,
                weight=0.5,
            ),
        ]
        result = fuse_measurements(sources, current_time=current_time)
        assert result is not None
        # Newer data should pull average closer to 14
        assert result.best_estimate > 11.0  # More than simple average
        assert result.best_estimate < 14.0  # But not all the way to newer value

    def test_filters_old_data(self, current_time):
        """Data older than max_age_hours should be filtered."""
        old_time = current_time - timedelta(hours=25)
        sources = [
            DataSource(
                source_name="resort_official",
                value=12.0,
                timestamp=old_time,  # Too old
                confidence=1.0,
                weight=0.5,
            ),
        ]
        result = fuse_measurements(
            sources, max_age_hours=24, current_time=current_time
        )
        assert result is None

    def test_custom_max_age(self, current_time):
        """Should respect custom max_age_hours."""
        twelve_hours_ago = current_time - timedelta(hours=12)
        sources = [
            DataSource(
                source_name="resort_official",
                value=12.0,
                timestamp=twelve_hours_ago,
                confidence=1.0,
                weight=0.5,
            ),
        ]
        # Should be filtered with 6 hour max
        result = fuse_measurements(
            sources, max_age_hours=6, current_time=current_time
        )
        assert result is None

        # Should be included with 24 hour max
        result = fuse_measurements(
            sources, max_age_hours=24, current_time=current_time
        )
        assert result is not None

    def test_confidence_affects_weight(self, current_time):
        """Lower confidence should reduce influence."""
        sources = [
            DataSource(
                source_name="resort_official",
                value=10.0,
                timestamp=current_time,
                confidence=0.5,  # Low confidence
                weight=0.5,
            ),
            DataSource(
                source_name="snotel",
                value=14.0,
                timestamp=current_time,
                confidence=1.0,  # High confidence
                weight=0.5,
            ),
        ]
        result = fuse_measurements(sources, current_time=current_time)
        assert result is not None
        # High confidence source should dominate
        assert result.best_estimate > 12.0  # More than simple average

    def test_all_sources_filtered_returns_none(self, current_time):
        """If all sources are too old, should return None."""
        old_time = current_time - timedelta(hours=48)
        sources = [
            DataSource(
                source_name="resort_official",
                value=12.0,
                timestamp=old_time,
                confidence=1.0,
                weight=0.5,
            ),
            DataSource(
                source_name="snotel",
                value=10.0,
                timestamp=old_time,
                confidence=1.0,
                weight=0.4,
            ),
        ]
        result = fuse_measurements(
            sources, max_age_hours=24, current_time=current_time
        )
        assert result is None

    def test_fusion_result_fields(self, current_time):
        """FusionResult should contain all expected fields."""
        sources = [
            DataSource(
                source_name="resort_official",
                value=12.0,
                timestamp=current_time,
                confidence=0.9,
                weight=0.5,
            ),
            DataSource(
                source_name="snotel",
                value=11.0,
                timestamp=current_time,
                confidence=0.95,
                weight=0.4,
            ),
        ]
        result = fuse_measurements(sources, current_time=current_time)
        assert result is not None
        assert isinstance(result, FusionResult)
        assert hasattr(result, "best_estimate")
        assert hasattr(result, "confidence")
        assert hasattr(result, "sources_used")
        assert hasattr(result, "total_sources")
        assert result.total_sources == 2
        assert result.sources_used == 2

    def test_realistic_scenario(self, current_time, one_hour_ago, two_hours_ago):
        """Test with realistic multi-source scenario from spec."""
        sources = [
            DataSource(
                source_name="resort_official",
                value=12.0,
                timestamp=two_hours_ago,
                confidence=0.9,
                weight=0.5,
            ),
            DataSource(
                source_name="snotel",
                value=11.5,
                timestamp=one_hour_ago,
                confidence=0.95,
                weight=0.4,
            ),
            DataSource(
                source_name="weather_api",
                value=13.0,
                timestamp=current_time,
                confidence=0.7,
                weight=0.1,
            ),
        ]
        result = fuse_measurements(sources, current_time=current_time)
        assert result is not None
        # Result should be close to weighted average of ~11.7
        assert 11.0 < result.best_estimate < 12.5
        assert result.sources_used == 3
        assert result.confidence > 0.5


class TestFuseMeasurementsSimple:
    """Tests for simplified fusion returning tuple."""

    def test_returns_tuple(self, current_time):
        """Should return tuple of (estimate, confidence)."""
        sources = [
            DataSource(
                source_name="resort_official",
                value=12.0,
                timestamp=current_time,
                confidence=1.0,
                weight=0.5,
            ),
        ]
        result = fuse_measurements_simple(sources, current_time=current_time)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_empty_returns_none(self, current_time):
        """Empty sources should return None."""
        result = fuse_measurements_simple([], current_time=current_time)
        assert result is None

    def test_values_match_full_function(self, current_time):
        """Values should match full function."""
        sources = [
            DataSource(
                source_name="resort_official",
                value=12.0,
                timestamp=current_time,
                confidence=0.9,
                weight=0.5,
            ),
        ]
        full_result = fuse_measurements(sources, current_time=current_time)
        simple_result = fuse_measurements_simple(sources, current_time=current_time)
        assert simple_result is not None
        assert simple_result[0] == full_result.best_estimate
        assert simple_result[1] == full_result.confidence


class TestGetSourceWeight:
    """Tests for source weight lookup."""

    def test_known_sources(self):
        """Known sources should return correct weight."""
        assert get_source_weight("resort_official") == 0.5
        assert get_source_weight("snotel") == 0.4
        assert get_source_weight("weather_api") == 0.1

    def test_unknown_source_returns_default(self):
        """Unknown sources should return default of 0.1."""
        assert get_source_weight("unknown_source") == 0.1
        assert get_source_weight("random_api") == 0.1


class TestCreateDataSource:
    """Tests for DataSource factory function."""

    def test_creates_with_defaults(self, current_time):
        """Should create DataSource with default weight."""
        source = create_data_source(
            source_name="resort_official",
            value=12.0,
            timestamp=current_time,
            confidence=0.9,
        )
        assert source.source_name == "resort_official"
        assert source.value == 12.0
        assert source.timestamp == current_time
        assert source.confidence == 0.9
        assert source.weight == 0.5  # Default for resort_official

    def test_respects_custom_weight(self, current_time):
        """Should use custom weight when provided."""
        source = create_data_source(
            source_name="resort_official",
            value=12.0,
            timestamp=current_time,
            confidence=0.9,
            weight=0.8,
        )
        assert source.weight == 0.8


class TestDataSourceDataclass:
    """Tests for DataSource dataclass behavior."""

    def test_post_init_sets_weight(self, current_time):
        """Should set weight from SOURCE_WEIGHTS if not provided."""
        source = DataSource(
            source_name="snotel",
            value=10.0,
            timestamp=current_time,
            confidence=0.9,
        )
        assert source.weight == 0.4

    def test_unknown_source_gets_default_weight(self, current_time):
        """Unknown source should get 0.1 default weight."""
        source = DataSource(
            source_name="unknown",
            value=10.0,
            timestamp=current_time,
            confidence=0.9,
        )
        assert source.weight == 0.1

    def test_explicit_weight_preserved(self, current_time):
        """Explicit weight should not be overwritten."""
        source = DataSource(
            source_name="snotel",
            value=10.0,
            timestamp=current_time,
            confidence=0.9,
            weight=0.99,
        )
        assert source.weight == 0.99


class TestEdgeCases:
    """Edge case tests for robustness."""

    def test_zero_confidence_all_sources(self, current_time):
        """All sources with zero confidence should return None."""
        sources = [
            DataSource(
                source_name="resort_official",
                value=12.0,
                timestamp=current_time,
                confidence=0.0,
                weight=0.5,
            ),
            DataSource(
                source_name="snotel",
                value=10.0,
                timestamp=current_time,
                confidence=0.0,
                weight=0.4,
            ),
        ]
        result = fuse_measurements(sources, current_time=current_time)
        assert result is None

    def test_zero_weight_source(self, current_time):
        """Source with zero weight should not contribute."""
        sources = [
            DataSource(
                source_name="resort_official",
                value=12.0,
                timestamp=current_time,
                confidence=1.0,
                weight=0.0,
            ),
            DataSource(
                source_name="snotel",
                value=10.0,
                timestamp=current_time,
                confidence=1.0,
                weight=0.5,
            ),
        ]
        result = fuse_measurements(sources, current_time=current_time)
        assert result is not None
        # Only snotel should contribute
        assert result.best_estimate == pytest.approx(10.0)

    def test_negative_values(self, current_time):
        """Should handle negative measurement values."""
        sources = [
            DataSource(
                source_name="resort_official",
                value=-5.0,  # Could be temperature
                timestamp=current_time,
                confidence=1.0,
                weight=0.5,
            ),
        ]
        result = fuse_measurements(sources, current_time=current_time)
        assert result is not None
        assert result.best_estimate == pytest.approx(-5.0)

    def test_very_large_values(self, current_time):
        """Should handle very large values."""
        sources = [
            DataSource(
                source_name="resort_official",
                value=1000000.0,
                timestamp=current_time,
                confidence=1.0,
                weight=0.5,
            ),
        ]
        result = fuse_measurements(sources, current_time=current_time)
        assert result is not None
        assert result.best_estimate == pytest.approx(1000000.0)

    def test_confidence_capped_at_one(self, current_time):
        """Result confidence should not exceed 1.0."""
        sources = [
            DataSource(
                source_name="resort_official",
                value=12.0,
                timestamp=current_time,
                confidence=1.0,
                weight=2.0,  # Very high weight
            ),
        ]
        result = fuse_measurements(sources, current_time=current_time)
        assert result is not None
        assert result.confidence <= 1.0

    def test_mixed_timezones(self, current_time):
        """Should handle mixed timezone-aware and naive timestamps."""
        naive_time = datetime(2024, 1, 15, 11, 0, 0)  # 1 hour before current_time
        sources = [
            DataSource(
                source_name="resort_official",
                value=12.0,
                timestamp=naive_time,
                confidence=1.0,
                weight=0.5,
            ),
        ]
        result = fuse_measurements(sources, current_time=current_time)
        assert result is not None


class TestFusionResultDataclass:
    """Tests for FusionResult dataclass."""

    def test_creation(self):
        """Should create with all fields."""
        result = FusionResult(
            best_estimate=11.5,
            confidence=0.85,
            sources_used=2,
            total_sources=3,
        )
        assert result.best_estimate == 11.5
        assert result.confidence == 0.85
        assert result.sources_used == 2
        assert result.total_sources == 3
