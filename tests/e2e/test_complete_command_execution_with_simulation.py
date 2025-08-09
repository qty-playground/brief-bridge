"""Complete E2E tests with client simulation framework"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .client_simulator import ClientSimulator, MultiClientSimulator, create_delayed_handler, create_error_handler


class TestCompleteCommandExecutionE2E:
    """E2E tests using client simulation framework"""
    
    def test_single_client_command_execution(self, api_client):
        """Test complete command execution cycle with real client simulation"""
        # Register client
        client_id = "simulation-client-001"
        api_client.post("/clients/register", json={"client_id": client_id, "name": "Simulation Client"})
        
        # Create client simulator
        simulator = ClientSimulator(api_client, client_id)
        
        # Start client simulation in background
        thread = simulator.start_background_polling(poll_interval=0.1, max_polls=30)
        
        try:
            # Submit command
            command_data = {
                "target_client_id": client_id,
                "command_content": "echo 'Hello Simulation'",
                "command_type": "shell"
            }
            
            start_time = time.time()
            response = api_client.post("/commands/submit", json=command_data)
            end_time = time.time()
            
            # Should complete quickly with simulation
            execution_time = end_time - start_time
            assert execution_time < 5  # Should not timeout
            
            # Verify response
            assert response.status_code == 200
            response_data = response.json()
            
            assert response_data["submission_successful"] is True
            assert response_data["target_client_id"] == client_id
            assert response_data["result"] == "Hello Simulation"
            assert response_data["execution_time"] is not None
            assert response_data["error"] is None
            
        finally:
            simulator.stop_polling()
            thread.join(timeout=1)
            
    def test_command_execution_with_custom_delay(self, api_client):
        """Test command execution with custom delay handler"""
        client_id = "delay-client-001"
        api_client.post("/clients/register", json={"client_id": client_id, "name": "Delay Client"})
        
        # Create simulator with 1-second delay
        simulator = ClientSimulator(api_client, client_id)
        simulator.set_command_handler(create_delayed_handler(1.0, "Delayed result"))
        
        thread = simulator.start_background_polling(poll_interval=0.1)
        
        try:
            command_data = {
                "target_client_id": client_id, 
                "command_content": "sleep 1",
                "command_type": "shell"
            }
            
            start_time = time.time()
            response = api_client.post("/commands/submit", json=command_data)
            end_time = time.time()
            
            execution_time = end_time - start_time
            assert execution_time >= 1.0  # Should take at least 1 second
            assert execution_time < 5.0   # But not timeout
            
            response_data = response.json()
            assert response_data["submission_successful"] is True
            assert response_data["result"] == "Delayed result"
            assert response_data["execution_time"] >= 1.0
            
        finally:
            simulator.stop_polling()
            thread.join(timeout=2)
            
    def test_command_execution_error_handling(self, api_client):
        """Test command execution with error simulation"""
        client_id = "error-client-001"
        api_client.post("/clients/register", json={"client_id": client_id, "name": "Error Client"})
        
        # Create simulator that returns errors
        simulator = ClientSimulator(api_client, client_id)
        simulator.set_command_handler(create_error_handler("Command failed: permission denied"))
        
        thread = simulator.start_background_polling(poll_interval=0.1)
        
        try:
            command_data = {
                "target_client_id": client_id,
                "command_content": "rm -rf /",
                "command_type": "shell"
            }
            
            response = api_client.post("/commands/submit", json=command_data)
            
            # Should return failure with error
            assert response.status_code == 200
            response_data = response.json()
            
            assert response_data["submission_successful"] is False
            assert "Command failed: permission denied" in response_data["submission_message"]
            assert response_data["error"] == "Command failed: permission denied"
            assert response_data["result"] is None
            
        finally:
            simulator.stop_polling()
            thread.join(timeout=1)
            
    def test_multiple_clients_isolated_execution(self, api_client):
        """Test multiple clients executing commands independently"""
        # Setup multiple clients
        multi_sim = MultiClientSimulator(api_client)
        
        # Register and add clients with different delays
        for i in range(3):
            client_id = f"multi-client-{i}"
            api_client.post("/clients/register", json={"client_id": client_id, "name": f"Multi Client {i}"})
            
            # Different delays to test isolation
            delay = 0.5 + (i * 0.3)  # 0.5s, 0.8s, 1.1s
            custom_result = f"Result from client {i}"
            handler = create_delayed_handler(delay, custom_result)
            
            multi_sim.add_client(client_id, handler)
        
        # Start all clients
        threads = multi_sim.start_all_clients(poll_interval=0.1)
        
        try:
            # Submit commands to all clients concurrently
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                
                for i in range(3):
                    client_id = f"multi-client-{i}"
                    command_data = {
                        "target_client_id": client_id,
                        "command_content": f"echo 'Command {i}'",
                        "command_type": "shell"
                    }
                    
                    future = executor.submit(api_client.post, "/commands/submit", json=command_data)
                    futures.append((i, future))
                
                # Collect results
                results = {}
                for i, future in futures:
                    response = future.result()
                    assert response.status_code == 200
                    results[i] = response.json()
            
            # Verify all commands executed independently
            for i in range(3):
                result = results[i]
                assert result["submission_successful"] is True
                assert result["target_client_id"] == f"multi-client-{i}"
                assert result["result"] == f"Result from client {i}"
                assert result["execution_time"] >= (0.5 + i * 0.3)  # Verify delays
                
        finally:
            multi_sim.stop_all_clients()
            for thread in threads:
                thread.join(timeout=2)
                
    def test_command_timeout_without_client(self, api_client):
        """Test command timeout when no client is available"""
        client_id = "offline-client"
        api_client.post("/clients/register", json={"client_id": client_id, "name": "Offline Client"})
        
        # Don't start any client simulator - command should timeout
        command_data = {
            "target_client_id": client_id,
            "command_content": "echo 'will timeout'",
            "command_type": "shell"
        }
        
        start_time = time.time()
        response = api_client.post("/commands/submit", json=command_data)
        end_time = time.time()
        
        # Should have timed out
        execution_time = end_time - start_time
        assert execution_time >= 2.0  # At least our short timeout
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["submission_successful"] is False
        assert "timeout" in response_data["submission_message"].lower()
        
    def test_client_single_command_execution_mechanism(self, api_client):
        """Test that client only gets one command at a time"""
        client_id = "single-exec-client"
        api_client.post("/clients/register", json={"client_id": client_id, "name": "Single Exec Client"})
        
        # Submit multiple commands
        for i in range(3):
            command_data = {
                "target_client_id": client_id,
                "command_content": f"echo 'command {i}'",
                "command_type": "shell"
            }
            # Don't wait for completion - just submit
            api_client.post("/commands/submit", json=command_data)
        
        # Client should only get one command when polling
        response = api_client.get(f"/commands/client/{client_id}")
        assert response.status_code == 200
        
        commands = response.json()
        assert len(commands) == 1  # Only one command returned
        
        # That command should be marked as processing
        command = commands[0]
        assert command["status"] == "processing"