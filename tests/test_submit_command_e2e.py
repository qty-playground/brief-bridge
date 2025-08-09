import pytest
from fastapi.testclient import TestClient
from brief_bridge.main import app
from brief_bridge.web.dependencies import get_client_repository, get_command_repository
from brief_bridge.repositories.client_repository import ClientRepository, InMemoryClientRepository
from brief_bridge.repositories.command_repository import CommandRepository, InMemoryCommandRepository


@pytest.fixture
def test_client_repository():
    """Create a fresh client repository instance for each test"""
    return InMemoryClientRepository()


@pytest.fixture
def test_command_repository():
    """Create a fresh command repository instance for each test"""
    return InMemoryCommandRepository()


@pytest.fixture
def client(test_client_repository, test_command_repository):
    """TestClient with dependency overrides for isolated testing"""
    app.dependency_overrides[get_client_repository] = lambda: test_client_repository
    app.dependency_overrides[get_command_repository] = lambda: test_command_repository
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()



def test_submit_command_to_unregistered_client_returns_error(client):
    """Business Rule: Attempting to submit command to unregistered client should fail"""
    unregistered_client_id = "nonexistent-client"
    
    # Business Action: Submit command to unregistered client
    submit_response = client.post("/commands/submit", json={
        "target_client_id": unregistered_client_id,
        "command_content": "echo 'test'",
        "command_type": "shell"
    })
    
    # Business Rule Verification: Command submission should fail
    assert submit_response.status_code == 200  # HTTP success but business failure
    submit_data = submit_response.json()
    assert submit_data["submission_successful"] is False
    assert submit_data["target_client_id"] == unregistered_client_id
    assert submit_data["submission_message"] == "Target client not found"
    assert submit_data["command_id"] is None
    
    # Business Rule Verification: No command should be saved
    all_commands_response = client.get("/commands/")
    assert all_commands_response.status_code == 200
    all_commands = all_commands_response.json()
    assert len(all_commands) == 0


def test_submit_command_with_empty_content_returns_error(client):
    """Business Rule: Attempting to submit command with empty content should fail"""
    test_client_id = "valid-client"
    
    # Setup: Register client first
    registration_response = client.post("/clients/register", json={
        "client_id": test_client_id,
        "name": "Valid Client"
    })
    assert registration_response.status_code == 200
    
    # Business Action: Submit command with empty content
    submit_response = client.post("/commands/submit", json={
        "target_client_id": test_client_id,
        "command_content": "",
        "command_type": "shell"
    })
    
    # Business Rule Verification: Command submission should fail
    assert submit_response.status_code == 200  # HTTP success but business failure
    submit_data = submit_response.json()
    assert submit_data["submission_successful"] is False
    assert submit_data["target_client_id"] == test_client_id
    assert submit_data["submission_message"] == "Command content cannot be empty"
    assert submit_data["command_id"] is None
    
    # Business Rule Verification: No command should be saved
    all_commands_response = client.get("/commands/")
    assert all_commands_response.status_code == 200
    all_commands = all_commands_response.json()
    assert len(all_commands) == 0



def test_lookup_nonexistent_command_returns_not_found(client):
    """Business Rule: Attempting to find nonexistent command should return 404"""
    nonexistent_command_id = "nonexistent-command-uuid"
    response = client.get(f"/commands/{nonexistent_command_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Command not found"


def test_get_commands_for_nonexistent_client_returns_empty_list(client):
    """Business Rule: Getting commands for nonexistent client should return empty list"""
    nonexistent_client_id = "nonexistent-client"
    response = client.get(f"/commands/client/{nonexistent_client_id}")
    assert response.status_code == 200
    commands = response.json()
    assert len(commands) == 0


