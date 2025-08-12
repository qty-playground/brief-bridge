import pytest
from fastapi.testclient import TestClient
from brief_bridge.main import app
from brief_bridge.web.dependencies import get_client_repository
from brief_bridge.repositories.client_repository import ClientRepository, InMemoryClientRepository


@pytest.fixture
def test_client_repository():
    """Create a fresh repository instance for each test"""
    return InMemoryClientRepository()


@pytest.fixture
def client(test_client_repository):
    """TestClient with dependency override for isolated testing"""
    app.dependency_overrides[get_client_repository] = lambda: test_client_repository
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_complete_client_registration_flow(client):
    """
    E2E Business Flow Test:
    1. Server started (handled by TestClient automatically)
    2. Client registers in the system and gets confirmation
    3. Server recognizes the client with specific ID  
    4. Client verifies registration through system endpoints
    """
    test_client_id: str = "test-client-001"
    test_client_name: str = "Test Client"
    
    # Business Action: Register new client
    registration_response = client.post("/clients/register", json={
        "client_id": test_client_id,
        "name": test_client_name
    })
    
    # Business Rule Verification: Registration successful
    assert registration_response.status_code == 200
    registration_data = registration_response.json()
    assert registration_data["success"] is True
    assert registration_data["client_id"] == test_client_id
    assert registration_data["name"] == test_client_name
    assert registration_data["status"] == "online"
    assert registration_data["message"] == "Client registered successfully"
    
    # Business Rule Verification: Server recognizes client by ID
    client_lookup_response = client.get(f"/clients/{test_client_id}")
    assert client_lookup_response.status_code == 200
    client_data = client_lookup_response.json()
    assert client_data["client_id"] == test_client_id
    assert client_data["name"] == test_client_name
    assert client_data["status"] == "online"
    
    # Business Rule Verification: Client appears in system registry
    all_clients_response = client.get("/clients/")
    assert all_clients_response.status_code == 200
    all_clients = all_clients_response.json()
    assert len(all_clients) == 1
    assert all_clients[0]["client_id"] == test_client_id
    assert all_clients[0]["name"] == test_client_name
    assert all_clients[0]["status"] == "online"


def test_lookup_unregistered_client_returns_not_found(client):
    """Business Rule: Attempting to find unregistered client should return 404"""
    unregistered_client_id: str = "nonexistent-client-id"
    response = client.get(f"/clients/{unregistered_client_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Client not found"


def test_system_health_and_api_availability(client):
    """System Health: Verify core system endpoints are operational"""
    # System health verification
    health_check_response = client.get("/health")
    assert health_check_response.status_code == 200
    assert health_check_response.json()["status"] == "healthy"
    
    # API availability verification
    api_root_response = client.get("/")
    assert api_root_response.status_code == 200
    response_data = api_root_response.json()
    assert response_data["service"] == "Brief Bridge"
    assert response_data["status"] == "active"
    assert "documentation" in response_data
    assert "prompts.md" in response_data["documentation"]["comprehensive_guide"]