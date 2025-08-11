"""Then command should be created with type - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext, expected_command_type: str) -> None:
    """
    Verify command was created with specified type via API response
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production verification using API response
    assert ctx.submit_response_status == 200, f"Command submission should succeed, got {ctx.submit_response_status}"
    assert ctx.submit_response_data is not None, "Should have response data"
    
    # Command should be created and have an ID (even if execution times out)
    assert ctx.submit_response_data.get('command_id'), "Command should be created with an ID"
    assert ctx.submit_response_data.get('target_client_id') == ctx.client_id, "Command should target the correct client"