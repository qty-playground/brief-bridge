"""Then registration response should contain - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import json

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify registration response contains expected data
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    expected_response = json.loads(ctx.expected_response_body)
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Registration response validation not implemented")