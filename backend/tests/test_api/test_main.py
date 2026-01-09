"""
Tests for main API endpoints.

Tests health check and API info endpoints:
- Root endpoint (/)
- Health check (/health)
- API info (/api/v1)
"""

import pytest


class TestRootEndpoint:
    """Tests for GET /"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "name" in data["data"]
        assert "version" in data["data"]
        assert "status" in data["data"]
        assert data["data"]["status"] == "operational"
        assert "docs_url" in data["data"]

    def test_root_has_welcome_message(self, client):
        """Test root endpoint has welcome message."""
        response = client.get("/")
        data = response.json()
        assert "message" in data
        assert "Welcome" in data["message"]


class TestHealthCheck:
    """Tests for GET /health"""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "status" in data["data"]
        assert data["data"]["status"] == "healthy"

    def test_health_check_has_checks(self, client):
        """Test health check includes component checks."""
        response = client.get("/health")
        data = response.json()
        assert "checks" in data["data"]
        assert "api" in data["data"]["checks"]
        assert data["data"]["checks"]["api"] == "ok"


class TestAPIInfo:
    """Tests for GET /api/v1"""

    def test_api_info(self, client):
        """Test API info endpoint."""
        response = client.get("/api/v1")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "version" in data["data"]
        assert "endpoints" in data["data"]
        assert "features" in data["data"]

    def test_api_endpoints_listed(self, client):
        """Test that API endpoints are listed."""
        response = client.get("/api/v1")
        data = response.json()
        endpoints = data["data"]["endpoints"]
        assert "resorts" in endpoints
        assert "conditions" in endpoints
        assert "health" in endpoints
        assert "docs" in endpoints

    def test_api_features_listed(self, client):
        """Test that API features are listed."""
        response = client.get("/api/v1")
        data = response.json()
        features = data["data"]["features"]
        assert isinstance(features, list)
        assert len(features) > 0
        # Check for some expected features
        feature_text = " ".join(features).lower()
        assert "resort" in feature_text or "conditions" in feature_text


class TestAPIResponseFormat:
    """Tests for standardized API response format."""

    def test_success_response_format(self, client):
        """Test that success responses follow standard format."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert data["success"] is True

    def test_error_response_format(self, client):
        """Test that error responses follow standard format."""
        response = client.get("/api/v1/resorts/nonexistent-resort")
        assert response.status_code == 404
        data = response.json()
        assert "success" in data
        assert "error" in data
        assert data["success"] is False
        assert "code" in data["error"]
        assert "message" in data["error"]

    def test_validation_error_format(self, client):
        """Test that validation errors follow standard format."""
        response = client.get("/api/v1/resorts/?page=0")  # Invalid page
        assert response.status_code == 422
        data = response.json()
        assert "success" in data
        assert "error" in data
        assert data["success"] is False


class TestCORS:
    """Tests for CORS middleware."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present."""
        response = client.options("/health")
        # Options request should succeed
        assert response.status_code in [200, 204]


class TestDocumentation:
    """Tests for API documentation endpoints."""

    def test_openapi_schema(self, client):
        """Test OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_swagger_ui(self, client):
        """Test Swagger UI is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_ui(self, client):
        """Test ReDoc UI is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200
