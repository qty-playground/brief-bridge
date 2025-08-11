"""Then response should include client - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext, expected_client_id: str) -> None:
    """
    Verify response contains expected client ID
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production verification
    assert hasattr(ctx, 'active_clients_response'), "Active clients response should exist"
    client_ids = [client.client_id for client in ctx.active_clients_response]
    assert expected_client_id in client_ids, f"Client {expected_client_id} should be in active clients but found: {client_ids}"