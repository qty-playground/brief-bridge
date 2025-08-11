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
    
    # GREEN Stage 2: Production chain with real business logic
    async def execute_polling():
        # Simulate client polling by updating last_seen timestamp
        client = await ctx.client_repository.find_client_by_id(ctx.client_id)
        if client:
            # Record timestamp before polling (for verification)
            ctx.timestamp_before_polling = datetime.now(timezone.utc)
            
            # Business rule: client.activity_tracking - use real domain method
            client.update_activity()
            
            # Save updated client
            await ctx.client_repository.save_registered_client(client)
            
            # Store updated client for assertions
            ctx.updated_client = client
    
    asyncio.run(execute_polling())