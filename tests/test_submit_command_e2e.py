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


def test_complete_command_submission_flow(client):
    """
    E2E Business Flow Test:
    1. Register a client in the system
    2. Submit command to registered client successfully
    3. Verify command was saved and can be retrieved
    4. Verify command appears in client's command list
    """
    test_client_id = "test-client-001"
    test_command_content = "echo 'Hello from AI assistant'"
    
    # Setup: Register client first
    registration_response = client.post("/clients/register", json={
        "client_id": test_client_id,
        "name": "Test Client"
    })
    assert registration_response.status_code == 200
    assert registration_response.json()["success"] is True
    
    # Business Action: Submit command to registered client
    submit_response = client.post("/commands/submit", json={
        "target_client_id": test_client_id,
        "command_content": test_command_content,
        "command_type": "shell"
    })
    
    # Business Rule Verification: Command submission successful
    assert submit_response.status_code == 200
    submit_data = submit_response.json()
    assert submit_data["submission_successful"] is True
    assert submit_data["target_client_id"] == test_client_id
    assert submit_data["submission_message"] == "Command submitted successfully"
    assert submit_data["command_id"] is not None
    
    command_id = submit_data["command_id"]
    
    # Business Rule Verification: Command can be retrieved by ID
    command_lookup_response = client.get(f"/commands/{command_id}")
    assert command_lookup_response.status_code == 200
    command_data = command_lookup_response.json()
    assert command_data["command_id"] == command_id
    assert command_data["target_client_id"] == test_client_id
    assert command_data["content"] == test_command_content
    assert command_data["type"] == "shell"
    assert command_data["status"] == "pending"
    
    # Business Rule Verification: Command appears in system command list
    all_commands_response = client.get("/commands/")
    assert all_commands_response.status_code == 200
    all_commands = all_commands_response.json()
    assert len(all_commands) == 1
    assert all_commands[0]["command_id"] == command_id
    assert all_commands[0]["target_client_id"] == test_client_id
    assert all_commands[0]["content"] == test_command_content
    
    # Business Rule Verification: Command appears in client's command list
    client_commands_response = client.get(f"/commands/client/{test_client_id}")
    assert client_commands_response.status_code == 200
    client_commands = client_commands_response.json()
    assert len(client_commands) == 1
    assert client_commands[0]["command_id"] == command_id
    assert client_commands[0]["target_client_id"] == test_client_id


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


def test_submit_command_with_minimal_information(client):
    """Business Rule: Submit command with minimal information should use defaults"""
    test_client_id = "minimal-client"
    test_command_content = "pwd"
    
    # Setup: Register client first
    registration_response = client.post("/clients/register", json={
        "client_id": test_client_id,
        "name": "Minimal Client"
    })
    assert registration_response.status_code == 200
    
    # Business Action: Submit command with minimal information (no command_type)
    submit_response = client.post("/commands/submit", json={
        "target_client_id": test_client_id,
        "command_content": test_command_content
        # command_type should default to "shell"
    })
    
    # Business Rule Verification: Command submission successful with defaults
    assert submit_response.status_code == 200
    submit_data = submit_response.json()
    assert submit_data["submission_successful"] is True
    assert submit_data["target_client_id"] == test_client_id
    assert submit_data["command_id"] is not None
    
    command_id = submit_data["command_id"]
    
    # Business Rule Verification: Command saved with default type
    command_lookup_response = client.get(f"/commands/{command_id}")
    assert command_lookup_response.status_code == 200
    command_data = command_lookup_response.json()
    assert command_data["content"] == test_command_content
    assert command_data["type"] == "shell"  # Default type applied
    assert command_data["status"] == "pending"


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


def test_multiple_commands_for_same_client(client):
    """Business Flow: Multiple commands can be submitted to same client"""
    test_client_id = "multi-command-client"
    
    # Setup: Register client
    registration_response = client.post("/clients/register", json={
        "client_id": test_client_id,
        "name": "Multi Command Client"
    })
    assert registration_response.status_code == 200
    
    # Submit multiple commands
    command_contents = ["ls -la", "pwd", "whoami"]
    command_ids = []
    
    for content in command_contents:
        submit_response = client.post("/commands/submit", json={
            "target_client_id": test_client_id,
            "command_content": content,
            "command_type": "shell"
        })
        assert submit_response.status_code == 200
        submit_data = submit_response.json()
        assert submit_data["submission_successful"] is True
        command_ids.append(submit_data["command_id"])
    
    # Verify all commands appear in client's command list
    client_commands_response = client.get(f"/commands/client/{test_client_id}")
    assert client_commands_response.status_code == 200
    client_commands = client_commands_response.json()
    assert len(client_commands) == 3
    
    # Verify each command has correct content
    retrieved_contents = [cmd["content"] for cmd in client_commands]
    for expected_content in command_contents:
        assert expected_content in retrieved_contents