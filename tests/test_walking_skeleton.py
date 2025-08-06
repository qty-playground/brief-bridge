import pytest


def test_health_check(test_client):
    """Test the health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "brief-bridge"


def test_root_endpoint(test_client):
    """Test the root endpoint returns usage instructions."""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    
    # Check basic info
    assert data["title"] == "Brief Bridge"
    assert data["version"] == "0.1.0"
    assert "description" in data
    
    # Check usage instructions structure
    assert "real_world_example" in data
    assert "quick_start" in data
    assert "features" in data
    assert "api_endpoints" in data
    assert "use_cases" in data
    
    # Check API endpoints are documented
    endpoints = data["api_endpoints"]
    assert "GET /" in endpoints
    assert "POST /commands" in endpoints
    assert "GET /commands/{id}" in endpoints
    assert "GET /clients" in endpoints
    
    # Check OpenAPI documentation links
    api_docs = data["api_documentation"]
    assert "openapi_json" in api_docs
    assert "swagger_ui" in api_docs
    assert "redoc" in api_docs
    # Should dynamically use the test client's base URL
    assert "/openapi.json" in api_docs["openapi_json"]
    assert "/docs" in api_docs["swagger_ui"]
    assert "/redoc" in api_docs["redoc"]