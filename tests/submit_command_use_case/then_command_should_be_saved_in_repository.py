"""Then command should be saved in repository - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import json

# Simplified Architecture imports
from brief_bridge.repositories.command_repository import CommandRepository

def invoke(ctx: ScenarioContext, expected_command_data: str) -> None:
    """
    Verify command was properly saved in repository
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    # Parse expected data from parameter
    expected_command = json.loads(expected_command_data)
    
    # GREEN Stage 1: Real business rule verification - command.persistence
    import asyncio
    
    # Get the saved command from repository using the command_id from response
    command_id = ctx.submission_response.command_id
    saved_command = asyncio.run(ctx.command_repository.find_command_by_id(command_id))
    
    assert saved_command is not None, f"Command {command_id} should be saved in repository but not found"
    
    # Verify saved command matches expected attributes
    if "target_client_id" in expected_command:
        assert saved_command.target_client_id == expected_command["target_client_id"], f"Expected target_client_id {expected_command['target_client_id']}, got {saved_command.target_client_id}"
    if "content" in expected_command:
        assert saved_command.content == expected_command["content"], f"Expected content {expected_command['content']}, got {saved_command.content}"
    if "type" in expected_command:
        assert saved_command.type == expected_command["type"], f"Expected type {expected_command['type']}, got {saved_command.type}"
    if "status" in expected_command:
        assert saved_command.status == expected_command["status"], f"Expected status {expected_command['status']}, got {saved_command.status}"