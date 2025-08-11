"""Given client is online - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: client.status_online - setup online client via API
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production chain using API calls
    # Register the client (defaults to online status)
    register_request = {
        "client_id": ctx.client_id,
        "name": f"test-client-{ctx.client_id}"
    }
    
    response = ctx.test_client.post("/clients/register", json=register_request)
    assert response.status_code == 200, f"Client registration should succeed, got {response.status_code}"
    
    # Ensure client is online (clients default to online after registration) 
    import asyncio
    
    async def ensure_online():
        client = await ctx.client_repository.find_client_by_id(ctx.client_id)
        if client:
            client.status = "online"  # Ensure online status
            await ctx.client_repository.save_registered_client(client)
    
    asyncio.run(ensure_online())