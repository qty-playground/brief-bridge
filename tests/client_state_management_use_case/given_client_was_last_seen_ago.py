"""Given client was last seen X seconds ago - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
from datetime import datetime, timezone, timedelta

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: client.activity_tracking - setup client last activity time via API
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production chain using API calls
    # First register the client
    register_request = {
        "client_id": ctx.client_id,
        "name": f"test-client-{ctx.client_id}"
    }
    
    response = ctx.test_client.post("/clients/register", json=register_request)
    assert response.status_code == 200, f"Client registration should succeed, got {response.status_code}"
    
    # Then directly manipulate last_seen using repository (since no API exists for this test setup)
    import asyncio
    
    async def setup_last_seen():
        client = await ctx.client_repository.find_client_by_id(ctx.client_id)
        if client:
            past_time = datetime.now(timezone.utc) - timedelta(seconds=ctx.last_seen_seconds_ago)
            client.last_seen = past_time
            await ctx.client_repository.save_registered_client(client)
    
    asyncio.run(setup_last_seen())