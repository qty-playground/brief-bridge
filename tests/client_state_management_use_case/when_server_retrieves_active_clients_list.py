"""When server retrieves active clients list - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Execute active clients list retrieval via API
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production chain using shared test client
    
    # Get all clients via API
    response = ctx.test_client.get("/clients/")
    
    # Store response for verification
    ctx.clients_list_response = response
    ctx.clients_list_response_status = response.status_code
    ctx.clients_list_response_data = response.json() if response.status_code == 200 else None