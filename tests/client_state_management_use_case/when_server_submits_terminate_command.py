"""When server submits terminate command - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Execute terminate command submission through server API
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production chain using shared test client
    
    # Submit terminate command via API
    command_request = {
        "target_client_id": ctx.client_id,
        "command_content": "terminate",
        "command_type": "terminate"
    }
    
    response = ctx.test_client.post("/commands/submit", json=command_request)
    
    # Store response for verification
    ctx.submit_response = response
    ctx.submit_response_status = response.status_code
    ctx.submit_response_data = response.json() if response.status_code == 200 else None