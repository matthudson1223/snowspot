"""
Tests for Forecasts API endpoints.

Tests all forecast-related endpoints including:
- Get resort forecasts
"""

import pytest
from datetime import datetime, timedelta, date, timezone

from app.models.resort import Resort
from app.models.forecast import WeatherForecast


@pytest.fixture
def sample_resort(db):
    """Create a sample resort for testing."""
    resort = Resort(
        name="Test Mountain Resort",
        slug="test-mountain-resort",
        latitude=39.6403,
        longitude=-106.3742,
        state="Colorado",
        region="Central",
        is_active=True
    )
    db.add(resort)
    db.commit()
    db.refresh(resort)
    return resort


@pytest.fixture
def resort_with_forecasts(db, sample_resort):
    """Create a resort with forecast data."""
    today = date.today()

    forecasts = []
    for day_offset in range(7):
        forecast_date = today + timedelta(days=day_offset)
        forecast = WeatherForecast(
            resort_id=sample_resort.id,
            forecast_for=forecast_date,
            forecasted_at=datetime.now(timezone.utc),
            high_temp_f=35 - day_offset,
            low_temp_f=20 - day_offset,
            precipitation_probability=50 + (day_offset * 5),
            expected_snowfall_in=2.0 + day_offset,
            wind_speed_mph=10 + day_offset,
            conditions="Snowy" if day_offset < 3 else "Partly Cloudy"
        )
        forecasts.append(forecast)
        db.add(forecast)

    db.commit()
    for forecast in forecasts:
        db.refresh(forecast)
    return sample_resort


class TestGetResortForecasts:
    """Tests for GET /api/v1/forecasts/{resort_id}"""

    def test_get_forecasts(self, client, resort_with_forecasts):
        """Test getting forecasts for a resort."""
        response = client.get(f"/api/v1/forecasts/{resort_with_forecasts.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 7  # Default 7 days
        assert "forecast days" in data["message"].lower()

    def test_get_forecasts_custom_days(self, client, resort_with_forecasts):
        """Test getting forecasts with custom number of days."""
        response = client.get(f"/api/v1/forecasts/{resort_with_forecasts.id}?days=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3

    def test_get_forecasts_resort_not_found(self, client):
        """Test getting forecasts for non-existent resort."""
        response = client.get("/api/v1/forecasts/99999")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["error"]["message"].lower()

    def test_get_forecasts_no_data(self, client, sample_resort):
        """Test getting forecasts when no forecast data exists."""
        response = client.get(f"/api/v1/forecasts/{sample_resort.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 0
        assert "0 forecast days" in data["message"].lower()

    def test_get_forecasts_max_days(self, client, resort_with_forecasts):
        """Test getting forecasts with maximum days."""
        response = client.get(f"/api/v1/forecasts/{resort_with_forecasts.id}?days=14")
        assert response.status_code == 200
        data = response.json()
        # Should return up to 7 (what we have)
        assert len(data["data"]) == 7

    def test_get_forecasts_invalid_days(self, client, resort_with_forecasts):
        """Test getting forecasts with invalid days parameter."""
        # Test days < 1
        response = client.get(f"/api/v1/forecasts/{resort_with_forecasts.id}?days=0")
        assert response.status_code == 422

        # Test days > 14
        response = client.get(f"/api/v1/forecasts/{resort_with_forecasts.id}?days=15")
        assert response.status_code == 422

    def test_forecast_data_structure(self, client, resort_with_forecasts):
        """Test that forecast data has correct structure."""
        response = client.get(f"/api/v1/forecasts/{resort_with_forecasts.id}?days=1")
        assert response.status_code == 200
        data = response.json()

        forecast = data["data"][0]
        assert "forecast_for" in forecast
        assert "high_temp_f" in forecast
        assert "low_temp_f" in forecast
        assert "precipitation_probability" in forecast
        assert "expected_snowfall_in" in forecast
        assert "wind_speed_mph" in forecast
        assert "conditions" in forecast

    def test_forecasts_ordered_by_date(self, client, resort_with_forecasts):
        """Test that forecasts are returned in chronological order."""
        response = client.get(f"/api/v1/forecasts/{resort_with_forecasts.id}")
        assert response.status_code == 200
        data = response.json()

        # Check that dates are in ascending order
        dates = [f["forecast_for"] for f in data["data"]]
        assert dates == sorted(dates)

    def test_forecast_values(self, client, resort_with_forecasts):
        """Test that forecast values are as expected."""
        response = client.get(f"/api/v1/forecasts/{resort_with_forecasts.id}?days=3")
        assert response.status_code == 200
        data = response.json()

        # Check first forecast
        first_forecast = data["data"][0]
        assert first_forecast["high_temp_f"] == 35
        assert first_forecast["low_temp_f"] == 20
        assert first_forecast["expected_snowfall_in"] == 2.0
        assert first_forecast["conditions"] == "Snowy"
