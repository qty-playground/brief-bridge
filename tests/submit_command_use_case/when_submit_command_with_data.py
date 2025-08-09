"""When I submit command with data - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import json
import asyncio

# Simplified Architecture imports
from brief_bridge.use_cases.submit_command_use_case import SubmitCommandUseCase, CommandSubmissionRequest
from brief_bridge.repositories.client_repository import InMemoryClientRepository

def invoke(ctx: ScenarioContext, command_data: str) -> None:
    """
    Execute command submission through use case layer
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.WHEN
    # Can access input state from GIVEN phase, collect results here
    
    # Parse command data from docstring
    request_data = json.loads(command_data)
    
    # Create request object
    submission_request = CommandSubmissionRequest(
        target_client_id=request_data["target_client_id"],
        command_content=request_data["command_content"],
        command_type=request_data.get("command_type", "shell")
    )
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Command submission use case execution not implemented")