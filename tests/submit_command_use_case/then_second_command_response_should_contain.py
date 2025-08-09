from conftest import ScenarioContext, BDDPhase
import json


def invoke(ctx: ScenarioContext, expected_response_body: str) -> None:
    """Verify second command response contains expected data"""
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    # Parse expected response from parameter
    expected_response = json.loads(expected_response_body)
    
    # Get second command response from results storage
    assert 'second_command_response' in ctx._results, "Should have second_command_response from previous step"
    actual_response = ctx._results['second_command_response']
    
    # Verify each expected field matches actual response
    for field, expected_value in expected_response.items():
        actual_value = getattr(actual_response, field, None)
        assert actual_value == expected_value, f"Expected {field} to be {expected_value}, got {actual_value}"