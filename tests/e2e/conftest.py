"""E2E test fixtures and configuration"""

import pytest
from fastapi.testclient import TestClient
from brief_bridge.main import app
from brief_bridge.web.dependencies import get_client_repository, get_command_repository
from brief_bridge.repositories.client_repository import ClientRepository, InMemoryClientRepository  
from brief_bridge.repositories.command_repository import CommandRepository, InMemoryCommandRepository


@pytest.fixture
def test_client_repository():
    """Create a fresh client repository instance for each E2E test"""
    return InMemoryClientRepository()


@pytest.fixture  
def test_command_repository():
    """Create a fresh command repository instance for each E2E test"""
    return InMemoryCommandRepository()


@pytest.fixture
def api_client(test_client_repository, test_command_repository):
    """TestClient with dependency overrides for isolated E2E testing"""
    app.dependency_overrides[get_client_repository] = lambda: test_client_repository
    app.dependency_overrides[get_command_repository] = lambda: test_command_repository
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def registered_client(api_client):
    """Pre-register a test client for E2E tests"""
    client_data = {
        "client_id": "e2e-test-client",
        "name": "E2E Test Client"
    }
    
    response = api_client.post("/clients/register", json=client_data)
    assert response.status_code == 200
    
    return client_data