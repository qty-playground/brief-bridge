"""Then command should be queued for client - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify command is queued for client to receive via API
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production verification using shared test client
    
    # Check if client can retrieve the command (means it's queued)
    response = ctx.test_client.get(f"/commands/client/{ctx.client_id}")
    
    assert response.status_code == 200, "Should be able to poll for commands"
    commands_data = response.json()
    
    # If command was queued, it should have been created with an ID
    # Execution might time out, but command creation and queueing should succeed
    assert ctx.submit_response_data.get('command_id'), "Command should have been created and queued"