"""Given client has status - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: client.status_management - setup client with specific status via API
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
    
    # Then directly set status using repository (since no API exists for this test setup)
    import asyncio
    
    async def setup_status():
        client = await ctx.client_repository.find_client_by_id(ctx.client_id)
        if client:
            client.status = ctx.status  # Override status
            await ctx.client_repository.save_registered_client(client)
    
    asyncio.run(setup_status())