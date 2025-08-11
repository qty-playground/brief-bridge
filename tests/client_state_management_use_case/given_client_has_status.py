"""Given client has status - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
from brief_bridge.entities.client import Client
from brief_bridge.repositories.client_repository import InMemoryClientRepository
import asyncio

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: client.status_management - setup client with specific status
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production chain with hardcoded behavior
    if not hasattr(ctx, 'client_repository'):
        ctx.client_repository = InMemoryClientRepository()
    
    # Create client and set specific status
    client = Client.register_new_client(ctx.client_id, None)
    client.status = ctx.status  # Override status
    
    # Save to repository
    asyncio.run(ctx.client_repository.save_registered_client(client))
    ctx.test_client = client