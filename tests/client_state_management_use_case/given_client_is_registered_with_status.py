"""Given client is registered with status - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
from brief_bridge.entities.client import Client
from brief_bridge.repositories.client_repository import InMemoryClientRepository
import asyncio

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: client.registration - create test client with specific status
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.GIVEN
    # Can access input state set in GIVEN phase
    
    # GREEN Stage 1: Production chain with hardcoded values
    if not hasattr(ctx, 'client_repository'):
        ctx.client_repository = InMemoryClientRepository()
    
    # Create real client with hardcoded implementation
    client = Client.register_new_client(ctx.client_id, None)
    client.status = ctx.status  # Use requested status
    
    # Save to repository
    asyncio.run(ctx.client_repository.save_registered_client(client))
    
    # Store for later steps
    ctx.test_client = client