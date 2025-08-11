"""When system performs status check - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import asyncio

def invoke(ctx: ScenarioContext) -> None:
    """
    Execute system-wide status check with configured threshold
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production chain
    async def check_status():
        client = await ctx.client_repository.find_client_by_id(ctx.client_id)
        if client:
            client.check_and_update_status(ctx.offline_threshold_seconds)
            await ctx.client_repository.save_registered_client(client)
            ctx.updated_client = client
    
    asyncio.run(check_status())