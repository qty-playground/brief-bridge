"""Given client is registered with status - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: client.registration - setup registered client via API
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 2: Production chain using shared test client
    
    # Register client via API
    register_request = {
        "client_id": ctx.client_id,
        "name": f"test-client-{ctx.client_id}"
    }
    
    response = ctx.test_client.post("/clients/register", json=register_request)
    
    # Store registration response
    ctx.register_response = response
    ctx.register_response_status = response.status_code
    ctx.register_response_data = response.json() if response.status_code == 200 else None
    
    # Verify registration succeeded
    assert response.status_code == 200, f"Client registration should succeed, got {response.status_code}"