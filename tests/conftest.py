import pytest
from fastapi.testclient import TestClient

from brief_bridge.main import app
from brief_bridge.repositories.client_repository import InMemoryClientRepository
from brief_bridge.repositories.command_repository import InMemoryCommandRepository
from brief_bridge.web.dependencies import get_client_repository, get_command_repository


@pytest.fixture
def test_client():
    """Provide a test client for FastAPI with fresh repositories for each test."""
    # Create fresh repositories for this test
    client_repo = InMemoryClientRepository()
    command_repo = InMemoryCommandRepository()
    
    # Override dependencies to use test repositories
    app.dependency_overrides[get_client_repository] = lambda: client_repo
    app.dependency_overrides[get_command_repository] = lambda: command_repo
    
    client = TestClient(app)
    
    yield client
    
    # Clean up overrides after test
    app.dependency_overrides.clear()

# pytest_plugins will be populated during walking skeleton phase
