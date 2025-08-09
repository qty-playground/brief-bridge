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
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Command repository verification not implemented")