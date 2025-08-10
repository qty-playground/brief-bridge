"""Then response should contain expected data - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import json

def invoke(ctx: ScenarioContext, expected_response: str) -> None:
    """
    Verify response contains expected JSON structure
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Assert response matches expected JSON
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Response content verification not implemented")
