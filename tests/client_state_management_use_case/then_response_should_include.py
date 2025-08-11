"""Then response should include client - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext, expected_client_id: str) -> None:
    """
    Verify response contains expected client ID via API response
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production verification using API response
    assert ctx.clients_list_response_status == 200, f"Clients list should succeed, got {ctx.clients_list_response_status}"
    assert ctx.clients_list_response_data is not None, "Should have response data"
    
    client_ids = [client['client_id'] for client in ctx.clients_list_response_data]
    assert expected_client_id in client_ids, f"Client {expected_client_id} should be in clients list but found: {client_ids}"