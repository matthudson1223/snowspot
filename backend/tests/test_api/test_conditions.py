"""
Tests for Conditions API endpoints.

Tests all condition-related endpoints including:
- Get latest conditions for all resorts
- Get conditions by resort
- Get latest condition for a resort
- Create condition
- Bulk create conditions
- Compare conditions
- Powder alert
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.resort import Resort
from app.models.condition import Condition


@pytest.fixture
def sample_resorts(db):
    """Create multiple sample resorts for testing."""
    resorts = [
        Resort(
            name="Vail Mountain",
            slug="vail-mountain",
            latitude=39.6061,
            longitude=-106.3550,
            state="Colorado",
            region="Central",
            is_active=True
        ),
        Resort(
            name="Breckenridge",
            slug="breckenridge",
            latitude=39.4817,
            longitude=-106.0384,
            state="Colorado",
            region="Central",
            is_active=True
        ),
        Resort(
            name="Jackson Hole",
            slug="jackson-hole",
            latitude=43.5875,
            longitude=-110.8275,
            state="Wyoming",
            region="Rocky Mountains",
            is_active=True
        ),
    ]
    for resort in resorts:
        db.add(resort)
    db.commit()
    for resort in resorts:
        db.refresh(resort)
    return resorts


@pytest.fixture
def resorts_with_conditions(db, sample_resorts):
    """Create resorts with various condition data."""
    now = datetime.utcnow()

    # Epic powder conditions for Vail
    db.add(Condition(
        resort_id=sample_resorts[0].id,
        time=now,
        new_snow_24h_in=14.0,
        temperature_f=22.0,
        wind_speed_mph=5.0,
        base_depth_in=100.0,
        humidity_percent=25,
        snow_quality_score=Decimal("95.0")
    ))

    # Good conditions for Breckenridge
    db.add(Condition(
        resort_id=sample_resorts[1].id,
        time=now - timedelta(hours=2),
        new_snow_24h_in=4.0,
        temperature_f=28.0,
        wind_speed_mph=10.0,
        base_depth_in=85.0,
        humidity_percent=35,
        snow_quality_score=Decimal("68.0")
    ))

    # Poor conditions for Jackson Hole
    db.add(Condition(
        resort_id=sample_resorts[2].id,
        time=now - timedelta(days=1),
        new_snow_24h_in=0.0,
        temperature_f=40.0,
        wind_speed_mph=35.0,
        base_depth_in=45.0,
        humidity_percent=80,
        snow_quality_score=Decimal("12.0")
    ))

    # Historical data for Vail
    for hours_ago in [6, 12, 18]:
        db.add(Condition(
            resort_id=sample_resorts[0].id,
            time=now - timedelta(hours=hours_ago),
            new_snow_24h_in=2.0,
            temperature_f=25.0,
            wind_speed_mph=8.0,
            base_depth_in=95.0,
            snow_quality_score=Decimal("60.0")
        ))

    db.commit()
    return sample_resorts


class TestGetLatestConditions:
    """Tests for GET /api/v1/conditions/latest"""

    def test_get_latest_conditions_empty(self, client, sample_resorts):
        """Test getting latest conditions with no condition data."""
        response = client.get("/api/v1/conditions/latest")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3  # 3 resorts but no conditions

    def test_get_latest_conditions(self, client, resorts_with_conditions):
        """Test getting latest conditions for all resorts."""
        response = client.get("/api/v1/conditions/latest")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3

        # Check first resort has condition data
        vail_data = next(r for r in data["data"] if r["resort_slug"] == "vail-mountain")
        assert vail_data["condition"] is not None
        assert vail_data["condition"]["new_snow_24h_in"] == 14.0
        assert vail_data["quality_description"] is not None

    def test_filter_by_state(self, client, resorts_with_conditions):
        """Test filtering by state."""
        response = client.get("/api/v1/conditions/latest?state=Wyoming")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["resort_slug"] == "jackson-hole"

    def test_filter_by_min_quality_score(self, client, resorts_with_conditions):
        """Test filtering by minimum quality score."""
        response = client.get("/api/v1/conditions/latest?min_quality_score=90")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["resort_slug"] == "vail-mountain"

    def test_pagination(self, client, resorts_with_conditions):
        """Test pagination of latest conditions."""
        response = client.get("/api/v1/conditions/latest?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total"] == 3
        assert data["pagination"]["total_pages"] == 2


class TestGetConditionsByResort:
    """Tests for GET /api/v1/conditions/resort/{resort_id}"""

    def test_get_conditions_by_resort(self, client, resorts_with_conditions):
        """Test getting conditions for a specific resort."""
        resort_id = resorts_with_conditions[0].id
        response = client.get(f"/api/v1/conditions/resort/{resort_id}?hours=24")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 4  # 1 current + 3 historical

    def test_get_conditions_resort_not_found(self, client):
        """Test getting conditions for non-existent resort."""
        response = client.get("/api/v1/conditions/resort/99999")
        assert response.status_code == 404

    def test_get_conditions_custom_hours(self, client, resorts_with_conditions):
        """Test getting conditions with custom time range."""
        resort_id = resorts_with_conditions[0].id
        response = client.get(f"/api/v1/conditions/resort/{resort_id}?hours=12")
        assert response.status_code == 200
        data = response.json()
        # Should get current + 6hr + 12hr ago
        assert len(data["data"]) >= 2

    def test_get_conditions_pagination(self, client, resorts_with_conditions):
        """Test pagination of resort conditions."""
        resort_id = resorts_with_conditions[0].id
        response = client.get(f"/api/v1/conditions/resort/{resort_id}?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total"] == 4


class TestGetLatestConditionForResort:
    """Tests for GET /api/v1/conditions/{resort_id}/latest"""

    def test_get_latest_condition(self, client, resorts_with_conditions):
        """Test getting latest condition for a resort."""
        resort_id = resorts_with_conditions[0].id
        response = client.get(f"/api/v1/conditions/{resort_id}/latest")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["new_snow_24h_in"] == 14.0
        assert data["data"]["quality_description"] is not None

    def test_get_latest_condition_resort_not_found(self, client):
        """Test getting latest condition for non-existent resort."""
        response = client.get("/api/v1/conditions/99999/latest")
        assert response.status_code == 404

    def test_get_latest_condition_no_data(self, client, sample_resorts):
        """Test getting latest condition when no conditions exist."""
        resort_id = sample_resorts[0].id
        response = client.get(f"/api/v1/conditions/{resort_id}/latest")
        assert response.status_code == 404


class TestCreateCondition:
    """Tests for POST /api/v1/conditions/"""

    def test_create_condition(self, client, sample_resorts):
        """Test creating a new condition."""
        condition_data = {
            "resort_id": sample_resorts[0].id,
            "new_snow_24h_in": 8.0,
            "temperature_f": 25.0,
            "wind_speed_mph": 10.0,
            "base_depth_in": 75.0,
            "humidity_percent": 30
        }
        response = client.post("/api/v1/conditions/", json=condition_data)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["new_snow_24h_in"] == 8.0
        # Quality score should be automatically calculated
        assert data["data"]["snow_quality_score"] is not None
        assert data["data"]["quality_description"] is not None

    def test_create_condition_resort_not_found(self, client):
        """Test creating condition for non-existent resort."""
        condition_data = {
            "resort_id": 99999,
            "new_snow_24h_in": 8.0,
            "temperature_f": 25.0
        }
        response = client.post("/api/v1/conditions/", json=condition_data)
        assert response.status_code == 404

    def test_create_condition_partial_data(self, client, sample_resorts):
        """Test creating condition with partial data."""
        condition_data = {
            "resort_id": sample_resorts[0].id,
            "new_snow_24h_in": 5.0,
            "temperature_f": 28.0
            # Missing wind, humidity
        }
        response = client.post("/api/v1/conditions/", json=condition_data)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        # Score should still be calculated with available data
        assert data["data"]["snow_quality_score"] is not None

    def test_create_condition_invalid_data(self, client):
        """Test creating condition with invalid data."""
        condition_data = {
            "new_snow_24h_in": 8.0
            # Missing required resort_id
        }
        response = client.post("/api/v1/conditions/", json=condition_data)
        assert response.status_code == 422


class TestBulkCreateConditions:
    """Tests for POST /api/v1/conditions/bulk"""

    def test_bulk_create_conditions(self, client, sample_resorts):
        """Test bulk creating conditions."""
        conditions_data = [
            {
                "resort_id": sample_resorts[0].id,
                "new_snow_24h_in": 8.0,
                "temperature_f": 25.0,
                "wind_speed_mph": 10.0
            },
            {
                "resort_id": sample_resorts[1].id,
                "new_snow_24h_in": 5.0,
                "temperature_f": 28.0,
                "wind_speed_mph": 15.0
            }
        ]
        response = client.post("/api/v1/conditions/bulk", json=conditions_data)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert "Successfully created 2" in data["message"]

    def test_bulk_create_empty_list(self, client):
        """Test bulk create with empty list."""
        response = client.post("/api/v1/conditions/bulk", json=[])
        assert response.status_code == 400

    def test_bulk_create_too_many(self, client, sample_resorts):
        """Test bulk create with too many conditions."""
        conditions_data = [
            {
                "resort_id": sample_resorts[0].id,
                "new_snow_24h_in": 5.0,
                "temperature_f": 25.0
            }
        ] * 101  # Over the limit of 100
        response = client.post("/api/v1/conditions/bulk", json=conditions_data)
        assert response.status_code == 400

    def test_bulk_create_invalid_resort(self, client, sample_resorts):
        """Test bulk create with invalid resort ID."""
        conditions_data = [
            {
                "resort_id": sample_resorts[0].id,
                "new_snow_24h_in": 8.0,
                "temperature_f": 25.0
            },
            {
                "resort_id": 99999,  # Invalid
                "new_snow_24h_in": 5.0,
                "temperature_f": 28.0
            }
        ]
        response = client.post("/api/v1/conditions/bulk", json=conditions_data)
        assert response.status_code == 400
        assert "not found" in response.json()["error"]["message"].lower()


class TestCompareConditions:
    """Tests for GET /api/v1/conditions/compare"""

    def test_compare_conditions(self, client, resorts_with_conditions):
        """Test comparing conditions across resorts."""
        resort_ids = [r.id for r in resorts_with_conditions[:2]]
        response = client.get(f"/api/v1/conditions/compare?resort_ids={resort_ids[0]}&resort_ids={resort_ids[1]}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        # Should be sorted by quality score descending
        assert float(data["data"][0]["condition"]["snow_quality_score"]) >= float(data["data"][1]["condition"]["snow_quality_score"])

    def test_compare_too_many_resorts(self, client, resorts_with_conditions):
        """Test comparing more than 10 resorts."""
        resort_ids = "&resort_ids=".join(str(i) for i in range(1, 12))
        response = client.get(f"/api/v1/conditions/compare?resort_ids={resort_ids}")
        assert response.status_code == 400

    def test_compare_no_resorts_found(self, client):
        """Test comparing with invalid resort IDs."""
        response = client.get("/api/v1/conditions/compare?resort_ids=99999")
        assert response.status_code == 404


class TestPowderAlert:
    """Tests for GET /api/v1/conditions/powder-alert"""

    def test_powder_alert(self, client, resorts_with_conditions):
        """Test getting powder alert resorts."""
        response = client.get("/api/v1/conditions/powder-alert?min_new_snow=6&min_quality=70")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1  # Only Vail has 14" and quality 95
        assert data["data"][0]["resort_slug"] == "vail-mountain"

    def test_powder_alert_no_results(self, client, resorts_with_conditions):
        """Test powder alert with high thresholds."""
        response = client.get("/api/v1/conditions/powder-alert?min_new_snow=20&min_quality=90")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 0
        assert "No resorts" in data["message"]

    def test_powder_alert_filter_by_state(self, client, resorts_with_conditions):
        """Test powder alert filtered by state."""
        response = client.get("/api/v1/conditions/powder-alert?state=Wyoming&min_quality=0")
        assert response.status_code == 200
        data = response.json()
        # Wyoming has poor conditions, won't meet default powder criteria

    def test_powder_alert_default_parameters(self, client, resorts_with_conditions):
        """Test powder alert with default parameters."""
        response = client.get("/api/v1/conditions/powder-alert")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Default is 6" and quality 70
        assert len(data["data"]) >= 1
