"""
Tests for Resort API endpoints.

Tests all resort-related endpoints including:
- List resorts
- List resorts with conditions
- Get resort by slug
- Get resort history
- Create resort
- Update resort
- Delete resort
"""

import pytest
from datetime import datetime, timedelta

from app.models.resort import Resort
from app.models.condition import Condition


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
        base_elevation_ft=9000,
        summit_elevation_ft=12000,
        vertical_drop_ft=3000,
        total_lifts=10,
        total_runs=50,
        is_active=True
    )
    db.add(resort)
    db.commit()
    db.refresh(resort)
    return resort


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
            base_elevation_ft=8120,
            summit_elevation_ft=11570,
            vertical_drop_ft=3450,
            total_lifts=31,
            total_runs=195,
            is_active=True
        ),
        Resort(
            name="Breckenridge Ski Resort",
            slug="breckenridge",
            latitude=39.4817,
            longitude=-106.0384,
            state="Colorado",
            region="Central",
            base_elevation_ft=9600,
            summit_elevation_ft=12998,
            vertical_drop_ft=3398,
            total_lifts=34,
            total_runs=187,
            is_active=True
        ),
        Resort(
            name="Jackson Hole",
            slug="jackson-hole",
            latitude=43.5875,
            longitude=-110.8275,
            state="Wyoming",
            region="Rocky Mountains",
            base_elevation_ft=6311,
            summit_elevation_ft=10450,
            vertical_drop_ft=4139,
            total_lifts=13,
            total_runs=133,
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
def resort_with_conditions(db, sample_resort):
    """Create a resort with condition data."""
    now = datetime.utcnow()
    conditions = [
        Condition(
            resort_id=sample_resort.id,
            time=now,
            new_snow_24h_in=8.0,
            temperature_f=25.0,
            wind_speed_mph=10.0,
            base_depth_in=72.0,
            snow_quality_score=85.0
        ),
        Condition(
            resort_id=sample_resort.id,
            time=now - timedelta(hours=6),
            new_snow_24h_in=4.0,
            temperature_f=28.0,
            wind_speed_mph=5.0,
            base_depth_in=68.0,
            snow_quality_score=75.0
        ),
    ]
    for condition in conditions:
        db.add(condition)
    db.commit()
    return sample_resort


class TestListResorts:
    """Tests for GET /api/v1/resorts/"""

    def test_list_resorts_empty(self, client):
        """Test listing resorts when database is empty."""
        response = client.get("/api/v1/resorts/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] == []
        assert data["pagination"]["total"] == 0

    def test_list_resorts_with_data(self, client, sample_resorts):
        """Test listing resorts with data."""
        response = client.get("/api/v1/resorts/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3
        assert data["pagination"]["total"] == 3
        assert data["data"][0]["name"] == "Breckenridge Ski Resort"

    def test_list_resorts_pagination(self, client, sample_resorts):
        """Test pagination."""
        response = client.get("/api/v1/resorts/?page=1&page_size=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["pagination"]["total"] == 3
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["total_pages"] == 2

    def test_list_resorts_filter_by_state(self, client, sample_resorts):
        """Test filtering by state."""
        response = client.get("/api/v1/resorts/?state=Wyoming")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Jackson Hole"

    def test_list_resorts_filter_by_region(self, client, sample_resorts):
        """Test filtering by region."""
        response = client.get("/api/v1/resorts/?region=Central")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2

    def test_list_resorts_invalid_page(self, client):
        """Test invalid page number."""
        response = client.get("/api/v1/resorts/?page=0")
        assert response.status_code == 422


class TestListResortsWithConditions:
    """Tests for GET /api/v1/resorts/with-conditions"""

    def test_list_resorts_with_conditions(self, client, resort_with_conditions):
        """Test listing resorts with their latest conditions."""
        response = client.get("/api/v1/resorts/with-conditions")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["latest_condition"] is not None
        assert data["data"][0]["latest_condition"]["new_snow_24h_in"] == 8.0
        assert data["data"][0]["quality_description"] is not None

    def test_filter_by_min_quality_score(self, client, resort_with_conditions):
        """Test filtering by minimum quality score."""
        response = client.get("/api/v1/resorts/with-conditions?min_quality_score=90")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 0

        response = client.get("/api/v1/resorts/with-conditions?min_quality_score=80")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1


class TestGetResort:
    """Tests for GET /api/v1/resorts/{resort_slug}"""

    def test_get_resort_by_slug(self, client, sample_resort):
        """Test getting a resort by slug."""
        response = client.get(f"/api/v1/resorts/{sample_resort.slug}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == sample_resort.name
        assert data["data"]["slug"] == sample_resort.slug

    def test_get_resort_not_found(self, client):
        """Test getting a resort that doesn't exist."""
        response = client.get("/api/v1/resorts/nonexistent-resort")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["error"]["message"].lower()

    def test_get_resort_with_conditions(self, client, resort_with_conditions):
        """Test getting resort with conditions included."""
        response = client.get(f"/api/v1/resorts/{resort_with_conditions.slug}?include_conditions=true")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["latest_condition"] is not None
        assert data["data"]["latest_condition"]["new_snow_24h_in"] == 8.0


class TestGetResortHistory:
    """Tests for GET /api/v1/resorts/{resort_slug}/history"""

    def test_get_resort_history(self, client, resort_with_conditions):
        """Test getting resort condition history."""
        response = client.get(f"/api/v1/resorts/{resort_with_conditions.slug}/history?hours=24")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["resort_slug"] == resort_with_conditions.slug
        assert data["data"]["count"] == 2
        assert len(data["data"]["conditions"]) == 2

    def test_get_history_not_found(self, client):
        """Test getting history for non-existent resort."""
        response = client.get("/api/v1/resorts/nonexistent/history")
        assert response.status_code == 404

    def test_get_history_custom_hours(self, client, resort_with_conditions):
        """Test getting history with custom hours parameter."""
        response = client.get(f"/api/v1/resorts/{resort_with_conditions.slug}/history?hours=1")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["count"] == 1


class TestCreateResort:
    """Tests for POST /api/v1/resorts/"""

    def test_create_resort(self, client):
        """Test creating a new resort."""
        resort_data = {
            "name": "New Test Resort",
            "slug": "new-test-resort",
            "latitude": 40.0,
            "longitude": -105.0,
            "state": "Colorado",
            "region": "Northern"
        }
        response = client.post("/api/v1/resorts/", json=resort_data)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == resort_data["name"]
        assert data["data"]["slug"] == resort_data["slug"]

    def test_create_resort_duplicate_slug(self, client, sample_resort):
        """Test creating a resort with duplicate slug."""
        resort_data = {
            "name": "Duplicate Resort",
            "slug": sample_resort.slug,
            "latitude": 40.0,
            "longitude": -105.0,
            "state": "Colorado",
            "region": "Northern"
        }
        response = client.post("/api/v1/resorts/", json=resort_data)
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "already exists" in data["error"]["message"].lower()

    def test_create_resort_invalid_data(self, client):
        """Test creating resort with invalid data."""
        resort_data = {
            "name": "Invalid Resort"
            # Missing required fields
        }
        response = client.post("/api/v1/resorts/", json=resort_data)
        assert response.status_code == 422


class TestUpdateResort:
    """Tests for PATCH /api/v1/resorts/{resort_slug}"""

    def test_update_resort(self, client, sample_resort):
        """Test updating a resort."""
        update_data = {
            "name": "Updated Resort Name",
            "total_lifts": 15
        }
        response = client.patch(f"/api/v1/resorts/{sample_resort.slug}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Updated Resort Name"
        assert data["data"]["total_lifts"] == 15
        assert data["data"]["slug"] == sample_resort.slug  # Slug unchanged

    def test_update_resort_not_found(self, client):
        """Test updating a non-existent resort."""
        update_data = {"name": "New Name"}
        response = client.patch("/api/v1/resorts/nonexistent", json=update_data)
        assert response.status_code == 404


class TestDeleteResort:
    """Tests for DELETE /api/v1/resorts/{resort_slug}"""

    def test_delete_resort(self, client, sample_resort):
        """Test soft deleting a resort."""
        response = client.delete(f"/api/v1/resorts/{sample_resort.slug}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["is_active"] is False

        # Verify resort is not listed in active resorts
        response = client.get("/api/v1/resorts/?active_only=true")
        assert len(response.json()["data"]) == 0

    def test_delete_resort_not_found(self, client):
        """Test deleting a non-existent resort."""
        response = client.delete("/api/v1/resorts/nonexistent")
        assert response.status_code == 404
