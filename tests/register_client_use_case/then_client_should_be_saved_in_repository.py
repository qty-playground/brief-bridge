"""Then client should be saved in repository - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import json

# Simplified Architecture imports
from brief_bridge.repositories.client_repository import ClientRepository

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify client was properly saved in repository
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    expected_client_data = json.loads(ctx.expected_client_data)
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Client repository verification not implemented")