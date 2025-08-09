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
    
    # Get expected data from cross-phase storage
    response_body = ctx.get_cross_phase_data('expected_response_body')
    if not response_body:
        raise ValueError("Expected response body not provided")
    
    expected_response = json.loads(response_body)
    
    # GREEN Stage 1: Simple validation with production response
    actual_response = ctx.registration_response
    assert actual_response.client_id == expected_response["client_id"], f"Expected client_id {expected_response['client_id']}, got {actual_response.client_id}"
    assert actual_response.client_name == expected_response["client_name"], f"Expected client_name {expected_response['client_name']}, got {actual_response.client_name}"
    assert actual_response.client_status == expected_response["client_status"], f"Expected client_status {expected_response['client_status']}, got {actual_response.client_status}"
    assert actual_response.registration_successful == expected_response["registration_successful"], f"Expected registration_successful {expected_response['registration_successful']}, got {actual_response.registration_successful}"
    if "registration_message" in expected_response:
        assert actual_response.registration_message == expected_response["registration_message"], f"Expected registration_message {expected_response['registration_message']}, got {actual_response.registration_message}"