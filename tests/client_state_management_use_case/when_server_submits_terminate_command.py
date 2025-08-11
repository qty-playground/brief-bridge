"""When server submits terminate command - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
from brief_bridge.entities.command import Command
from brief_bridge.repositories.command_repository import InMemoryCommandRepository
import asyncio

def invoke(ctx: ScenarioContext) -> None:
    """
    Execute terminate command submission through server
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production chain with hardcoded behavior
    if not hasattr(ctx, 'command_repository'):
        ctx.command_repository = InMemoryCommandRepository()
    
    async def submit_terminate():
        # Create terminate command
        command = Command.create_new_command(
            target_client_id=ctx.client_id,
            content="terminate",
            command_type="terminate"
        )
        
        # Save command (queue it)
        await ctx.command_repository.save_command(command)
        ctx.created_command = command
    
    asyncio.run(submit_terminate())