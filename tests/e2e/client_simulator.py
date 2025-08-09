"""Client simulator for E2E testing"""

import asyncio
import time
from typing import Optional, Callable, Dict, Any
from fastapi.testclient import TestClient


class ClientSimulator:
    """Simulates a client that polls for commands and submits results"""
    
    def __init__(self, api_client: TestClient, client_id: str):
        self.api_client = api_client
        self.client_id = client_id
        self.is_running = False
        self.command_handler: Optional[Callable] = None
        
    def set_command_handler(self, handler: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """Set a custom command handler function
        
        Handler should take command dict and return result dict with:
        - output: str (optional)
        - error: str (optional) 
        - execution_time: float (optional)
        """
        self.command_handler = handler
        
    def default_command_handler(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Default handler that simulates successful command execution"""
        command_content = command.get("content", "")
        
        # Simulate different commands
        if "echo" in command_content:
            # Extract text from echo command
            if "'" in command_content:
                output = command_content.split("'")[1]
            else:
                output = command_content.replace("echo ", "")
        elif "pwd" in command_content:
            output = "/home/client"  
        elif "ls" in command_content:
            output = "file1.txt\nfile2.txt\ndirectory/"
        else:
            output = f"Command executed: {command_content}"
            
        return {
            "output": output,
            "error": None,
            "execution_time": 0.1  # Simulate quick execution
        }
        
    async def poll_and_execute_commands(self, poll_interval: float = 0.2, max_polls: int = 50):
        """Poll for commands and execute them"""
        polls = 0
        
        while polls < max_polls and self.is_running:
            polls += 1
            
            # Poll for commands
            response = self.api_client.get(f"/commands/client/{self.client_id}")
            
            if response.status_code == 200:
                commands = response.json()
                
                if commands:
                    command = commands[0]  # Should only be one due to single execution
                    command_id = command["command_id"]
                    
                    # Execute command using handler
                    handler = self.command_handler or self.default_command_handler
                    result = handler(command)
                    
                    # Submit result back to server
                    result_data = {
                        "command_id": command_id,
                        "output": result.get("output"),
                        "error": result.get("error"),
                        "execution_time": result.get("execution_time", 0.1)
                    }
                    
                    submit_response = self.api_client.post("/commands/result", json=result_data)
                    
                    if submit_response.status_code == 200:
                        return True  # Successfully executed command
                        
            await asyncio.sleep(poll_interval)
            
        return False  # No command found or execution failed
        
    def start_background_polling(self, poll_interval: float = 0.2, max_polls: int = 50):
        """Start polling in background thread"""
        import threading
        
        self.is_running = True
        
        def run_polling():
            asyncio.run(self.poll_and_execute_commands(poll_interval, max_polls))
            
        thread = threading.Thread(target=run_polling, daemon=True)
        thread.start()
        return thread
        
    def stop_polling(self):
        """Stop background polling"""
        self.is_running = False


class MultiClientSimulator:
    """Manages multiple client simulators for testing"""
    
    def __init__(self, api_client: TestClient):
        self.api_client = api_client
        self.clients: Dict[str, ClientSimulator] = {}
        
    def add_client(self, client_id: str, custom_handler: Optional[Callable] = None) -> ClientSimulator:
        """Add a client simulator"""
        client = ClientSimulator(self.api_client, client_id)
        if custom_handler:
            client.set_command_handler(custom_handler)
        self.clients[client_id] = client
        return client
        
    def start_all_clients(self, poll_interval: float = 0.2, max_polls: int = 50):
        """Start all client simulators in background"""
        threads = []
        for client in self.clients.values():
            thread = client.start_background_polling(poll_interval, max_polls)
            threads.append(thread)
        return threads
        
    def stop_all_clients(self):
        """Stop all client simulators"""
        for client in self.clients.values():
            client.stop_polling()


def create_delayed_handler(delay_seconds: float, result_override: Optional[str] = None):
    """Create a command handler with specific delay"""
    def handler(command: Dict[str, Any]) -> Dict[str, Any]:
        time.sleep(delay_seconds)
        
        output = result_override
        if not output:
            command_content = command.get("content", "")
            if "echo" in command_content and "'" in command_content:
                output = command_content.split("'")[1] 
            else:
                output = f"Executed: {command_content}"
                
        return {
            "output": output,
            "error": None,
            "execution_time": delay_seconds
        }
    return handler


def create_error_handler(error_message: str, delay_seconds: float = 0.1):
    """Create a command handler that returns an error"""
    def handler(command: Dict[str, Any]) -> Dict[str, Any]:
        time.sleep(delay_seconds)
        return {
            "output": None,
            "error": error_message,
            "execution_time": delay_seconds
        }
    return handler