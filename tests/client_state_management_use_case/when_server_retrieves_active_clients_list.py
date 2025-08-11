"""When server retrieves active clients list - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import asyncio

def invoke(ctx: ScenarioContext) -> None:
    """
    Execute active clients list retrieval
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production chain
    async def retrieve_active_clients():
        all_clients = await ctx.client_repository.get_all_registered_clients()
        active_clients = [client for client in all_clients if client.status == "online"]
        ctx.active_clients_response = active_clients
    
    asyncio.run(retrieve_active_clients())