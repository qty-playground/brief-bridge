"""E2E tests for command submission flow through Web API"""

import pytest
from brief_bridge.entities.command import Command


class TestCommandSubmissionE2E:
    """End-to-end tests for command submission through Web API"""

        
    def test_client_command_retrieval(self, api_client, registered_client):
        """Test client retrieval of assigned commands"""
        client_id = registered_client["client_id"]
        
        # Submit a command
        command_data = {
            "target_client_id": client_id,
            "command_content": "ls -la",
            "command_type": "shell" 
        }
        
        submit_response = api_client.post("/commands/submit", json=command_data)
        assert submit_response.status_code == 200
        
        # Client retrieves their commands
        client_commands_response = api_client.get(f"/commands/client/{client_id}")
        assert client_commands_response.status_code == 200
        
        commands = client_commands_response.json()
        assert len(commands) == 1
        assert commands[0]["target_client_id"] == client_id
        assert commands[0]["content"] == "ls -la"
        
    def test_multiple_clients_isolation(self, api_client):
        """Test that commands are properly isolated between different clients"""
        # Register two different clients
        client_a_data = {"client_id": "client-a", "name": "Client A"}
        client_b_data = {"client_id": "client-b", "name": "Client B"}
        
        api_client.post("/clients/register", json=client_a_data)
        api_client.post("/clients/register", json=client_b_data)
        
        # Submit commands to both clients
        command_a = {
            "target_client_id": "client-a",
            "command_content": "echo 'Hello A'",
            "command_type": "shell"
        }
        command_b = {
            "target_client_id": "client-b", 
            "command_content": "echo 'Hello B'",
            "command_type": "shell"
        }
        
        api_client.post("/commands/submit", json=command_a)
        api_client.post("/commands/submit", json=command_b)
        
        # Verify each client only sees their own commands
        commands_a = api_client.get("/commands/client/client-a").json()
        commands_b = api_client.get("/commands/client/client-b").json()
        
        assert len(commands_a) == 1
        assert len(commands_b) == 1
        assert commands_a[0]["content"] == "echo 'Hello A'"
        assert commands_b[0]["content"] == "echo 'Hello B'"
        
    def test_invalid_client_command_submission(self, api_client):
        """Test command submission to non-existent client"""
        command_data = {
            "target_client_id": "nonexistent-client",
            "command_content": "echo 'test'",
            "command_type": "shell"
        }
        
        response = api_client.post("/commands/submit", json=command_data)
        assert response.status_code == 200  # API should return 200 but with failure status
        
        response_data = response.json()
        assert response_data["submission_successful"] is False
        assert "not found" in response_data["submission_message"].lower()
        
    def test_empty_command_content(self, api_client, registered_client):
        """Test validation of empty command content"""
        client_id = registered_client["client_id"]
        
        command_data = {
            "target_client_id": client_id,
            "command_content": "",
            "command_type": "shell"
        }
        
        response = api_client.post("/commands/submit", json=command_data)
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["submission_successful"] is False
        assert "empty" in response_data["submission_message"].lower()