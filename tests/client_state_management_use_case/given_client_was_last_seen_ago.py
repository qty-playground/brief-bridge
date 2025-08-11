"""Given client was last seen X seconds ago - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
from brief_bridge.entities.client import Client
from brief_bridge.repositories.client_repository import InMemoryClientRepository
from datetime import datetime, timezone, timedelta
import asyncio

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: client.activity_tracking - setup client last activity time
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production chain with hardcoded behavior
    if not hasattr(ctx, 'client_repository'):
        ctx.client_repository = InMemoryClientRepository()
    
    # Create client with old last_seen timestamp
    client = Client.register_new_client(ctx.client_id, None)
    past_time = datetime.now(timezone.utc) - timedelta(seconds=ctx.last_seen_seconds_ago)
    client.last_seen = past_time
    
    # Save to repository
    asyncio.run(ctx.client_repository.save_registered_client(client))
    ctx.test_client = client