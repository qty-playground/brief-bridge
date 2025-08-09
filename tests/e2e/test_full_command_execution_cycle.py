"""E2E tests for full command execution cycle with client simulation"""

import pytest
import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor


class TestFullCommandExecutionE2E:
    """E2E tests that simulate the complete command execution lifecycle"""

    def test_command_execution_with_client_simulation(self, api_client, registered_client):
        """Test complete command execution cycle with simulated client"""
        client_id = registered_client["client_id"]
        
        def simulate_client_execution():
            """Simulate a client picking up and executing commands"""
            time.sleep(0.1)  # Wait for command to be submitted
            
            # Client polls for commands
            commands_response = api_client.get(f"/commands/client/{client_id}")
            if commands_response.status_code == 200:
                commands = commands_response.json()
                if commands:
                    command = commands[0]
                    command_id = command["command_id"]
                    
                    # Simulate command execution
                    time.sleep(0.5)  # Simulate execution time
                    
                    # For now, we'll need to manually mark the command as completed
                    # since we don't have the result submission API yet
                    # This will be updated when we add the client result submission API
                    
        # Start client simulation in background
        with ThreadPoolExecutor() as executor:
            client_future = executor.submit(simulate_client_execution)
            
            # Submit command
            command_data = {
                "target_client_id": client_id,
                "command_content": "echo 'E2E Test'",
                "command_type": "shell"
            }
            
            start_time = time.time()
            response = api_client.post("/commands/submit", json=command_data)
            end_time = time.time()
            
            # Wait for client simulation to complete
            client_future.result()
            
        # Verify response
        assert response.status_code == 200
        response_data = response.json()
        
        # The response should contain execution results
        assert response_data["submission_successful"] is True
        assert response_data["target_client_id"] == client_id
        assert "command_id" in response_data
        
        # Should have execution result (from our use case simulation)
        assert "result" in response_data
        
        # Should have reasonable execution time (less than timeout)
        execution_time = end_time - start_time
        assert execution_time < 30  # Should not timeout
        
    def test_command_timeout_scenario(self, api_client, registered_client):
        """Test command submission timeout when no client responds"""
        client_id = registered_client["client_id"]
        
        # Submit command without any client simulation
        command_data = {
            "target_client_id": client_id,
            "command_content": "echo 'timeout test'",
            "command_type": "shell"
        }
        
        start_time = time.time()
        response = api_client.post("/commands/submit", json=command_data)
        end_time = time.time()
        
        # Should have timed out after the configured wait time
        execution_time = end_time - start_time
        assert execution_time >= 2  # Our test uses short timeout
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["submission_successful"] is False
        assert "timeout" in response_data["submission_message"].lower()

    def test_multiple_concurrent_commands(self, api_client):
        """Test multiple commands to different clients executing concurrently"""
        # Register multiple clients
        clients = []
        for i in range(3):
            client_data = {"client_id": f"client-{i}", "name": f"Client {i}"}
            api_client.post("/clients/register", json=client_data)
            clients.append(client_data["client_id"])
        
        def simulate_client_for_id(client_id):
            """Simulate client execution for a specific client"""
            time.sleep(0.1)
            # In a real scenario, this would poll and execute commands
            # For now, our use case handles the simulation
            pass
        
        # Start simulations for all clients
        with ThreadPoolExecutor() as executor:
            futures = []
            
            # Start client simulations
            for client_id in clients:
                future = executor.submit(simulate_client_for_id, client_id)
                futures.append(future)
            
            # Submit commands to all clients concurrently
            command_futures = []
            for i, client_id in enumerate(clients):
                command_data = {
                    "target_client_id": client_id,
                    "command_content": f"echo 'Client {i} command'",
                    "command_type": "shell"
                }
                
                future = executor.submit(api_client.post, "/commands/submit", json=command_data)
                command_futures.append(future)
            
            # Collect all results
            responses = [f.result() for f in command_futures]
            
            # Wait for client simulations to complete
            for f in futures:
                f.result()
        
        # Verify all commands were successful
        for i, response in enumerate(responses):
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["submission_successful"] is True
            assert response_data["target_client_id"] == f"client-{i}"