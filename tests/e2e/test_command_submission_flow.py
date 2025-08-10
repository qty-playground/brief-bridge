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
        
    def test_base64_encoded_command_submission(self, api_client, registered_client):
        """Test submission and execution of base64 encoded commands"""
        client_id = registered_client["client_id"]
        
        # Base64 encoded version of: echo "Message with 'single' and \"double\" quotes"
        base64_command = "ZWNobyAiTWVzc2FnZSB3aXRoICdzaW5nbGUnIGFuZCBcImRvdWJsZVwiIHF1b3RlcyI="
        
        command_data = {
            "target_client_id": client_id,
            "command_content": base64_command,
            "command_type": "shell",
            "encoding": "base64"
        }
        
        response = api_client.post("/commands/submit", json=command_data)
        assert response.status_code == 200
        
        # Verify the command is stored correctly
        commands_response = api_client.get(f"/commands/client/{client_id}")
        assert commands_response.status_code == 200
        
        commands = commands_response.json()
        assert len(commands) == 1
        
        command = commands[0]
        assert command["encoding"] == "base64"
        assert command["content"] == "echo \"Message with 'single' and \\\"double\\\" quotes\""
        
    def test_invalid_base64_command_submission(self, api_client, registered_client):
        """Test handling of invalid base64 encoded commands"""
        client_id = registered_client["client_id"]
        
        command_data = {
            "target_client_id": client_id,
            "command_content": "invalid-base64-string!!!",
            "command_type": "shell", 
            "encoding": "base64"
        }
        
        response = api_client.post("/commands/submit", json=command_data)
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["submission_successful"] is False
        assert "base64" in response_data["submission_message"].lower()
        
    def test_base64_multiline_script_submission(self, api_client, registered_client):
        """Test submission of base64 encoded multi-line scripts"""
        client_id = registered_client["client_id"]
        
        # Base64 encoded multi-line script
        multiline_script_b64 = "IyEvYmluL2Jhc2gKZWNobyAiU3RhcnRpbmcgc2NyaXB0Li4uIgpWQVI9InZhbHVlIHdpdGggJ3F1b3RlcyciCmVjaG8gIlZhcmlhYmxlOiAkVkFSIgplY2hvICJTY3JpcHQgY29tcGxldGVkIg=="
        
        command_data = {
            "target_client_id": client_id,
            "command_content": multiline_script_b64,
            "command_type": "shell",
            "encoding": "base64"
        }
        
        response = api_client.post("/commands/submit", json=command_data)
        assert response.status_code == 200
        
        # Verify the decoded command is stored correctly
        commands_response = api_client.get(f"/commands/client/{client_id}")
        commands = commands_response.json()
        
        assert len(commands) == 1
        command = commands[0]
        assert command["encoding"] == "base64"
        assert "#!/bin/bash" in command["content"]
        assert "echo \"Starting script...\"" in command["content"]
        
    def test_backward_compatibility_regular_commands(self, api_client, registered_client):
        """Test that regular commands still work without encoding field"""
        client_id = registered_client["client_id"]
        
        command_data = {
            "target_client_id": client_id,
            "command_content": "echo 'regular command'",
            "command_type": "shell"
            # No encoding field - should work as before
        }
        
        response = api_client.post("/commands/submit", json=command_data)
        assert response.status_code == 200
        
        commands_response = api_client.get(f"/commands/client/{client_id}")
        commands = commands_response.json()
        
        assert len(commands) == 1
        command = commands[0]
        assert command.get("encoding") is None  # Should be None for regular commands
        assert command["content"] == "echo 'regular command'"