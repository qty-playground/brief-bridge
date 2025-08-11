"""Then client status should be updated to - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext, expected_status: str) -> None:
    """
    Verify client status has been updated to new value via API
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 2: Production verification using shared test client
    
    # Get current client status
    response = ctx.test_client.get(f"/clients/{ctx.client_id}")
    
    assert response.status_code == 200, f"Should find client {ctx.client_id}"
    client_data = response.json()
    
    assert client_data['status'] == expected_status, f"Client status should be updated to {expected_status} but was {client_data['status']}"