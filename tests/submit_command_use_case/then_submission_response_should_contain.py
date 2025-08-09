"""Then submission response should contain - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import json

def invoke(ctx: ScenarioContext, expected_response_body: str) -> None:
    """
    Verify submission response contains expected data
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    # Parse expected data from parameter
    expected_response = json.loads(expected_response_body)
    
    # GREEN Stage 1: Flexible validation - only check expected fields
    actual_response = ctx.submission_response
    
    # Only assert fields that are specified in the expected response
    if "command_id" in expected_response:
        # Special handling for command_id - just check it exists if expected
        assert actual_response.command_id is not None, "Expected command_id to be generated"
    if "target_client_id" in expected_response:
        assert actual_response.target_client_id == expected_response["target_client_id"], f"Expected target_client_id {expected_response['target_client_id']}, got {actual_response.target_client_id}"
    if "submission_successful" in expected_response:
        assert actual_response.submission_successful == expected_response["submission_successful"], f"Expected submission_successful {expected_response['submission_successful']}, got {actual_response.submission_successful}"
    if "submission_message" in expected_response:
        assert actual_response.submission_message == expected_response["submission_message"], f"Expected submission_message {expected_response['submission_message']}, got {actual_response.submission_message}"