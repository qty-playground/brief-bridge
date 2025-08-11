"""When client polls server for commands - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
from datetime import datetime, timezone

def invoke(ctx: ScenarioContext) -> None:
    """
    Execute client polling request to server via API
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 2: Production chain using shared test client
    
    # Record timestamp before polling (for verification)
    ctx.timestamp_before_polling = datetime.now(timezone.utc)
    
    # Call API endpoint that updates client activity
    response = ctx.test_client.get(f"/commands/client/{ctx.client_id}")
    
    # Store response for verification
    ctx.polling_response = response
    ctx.polling_response_status = response.status_code
    ctx.polling_response_data = response.json() if response.status_code == 200 else None