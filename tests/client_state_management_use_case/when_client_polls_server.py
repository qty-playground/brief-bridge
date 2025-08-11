"""When client polls server for commands - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
from datetime import datetime, timezone
import asyncio

def invoke(ctx: ScenarioContext) -> None:
    """
    Execute client polling request to server
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.WHEN
    # Can access input state from GIVEN phase, collect results here
    
    # GREEN Stage 1: Production chain with hardcoded behavior
    async def execute_polling():
        # Simulate client polling by updating last_seen timestamp
        client = await ctx.client_repository.find_client_by_id(ctx.client_id)
        if client:
            # Record timestamp before polling (for verification)
            ctx.timestamp_before_polling = datetime.now(timezone.utc)
            
            # Update client activity (this will be the real logic later)
            client.last_seen = datetime.now(timezone.utc)  # Hardcoded update for now
            
            # Save updated client
            await ctx.client_repository.save_registered_client(client)
            
            # Store updated client for assertions
            ctx.updated_client = client
    
    asyncio.run(execute_polling())