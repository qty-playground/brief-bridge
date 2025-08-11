"""Then command should be queued for client - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
import asyncio

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify command is queued for client to receive
    Command Pattern implementation for BDD step
    """
    # GREEN Stage 1: Production verification
    async def verify_queued():
        pending_commands = await ctx.command_repository.get_pending_commands_for_client(ctx.client_id)
        assert len(pending_commands) > 0, "No pending commands found for client"
        assert pending_commands[0].command_id == ctx.created_command.command_id, "Command not found in client's pending queue"
    
    asyncio.run(verify_queued())