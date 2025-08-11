"""Then response should not include client - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext, excluded_client_id: str) -> None:
    """
    Verify response does not contain excluded client ID
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production verification
    assert hasattr(ctx, 'active_clients_response'), "Active clients response should exist"
    client_ids = [client.client_id for client in ctx.active_clients_response]
    assert excluded_client_id not in client_ids, f"Client {excluded_client_id} should NOT be in active clients but was found in: {client_ids}"