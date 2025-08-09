"""Then no command should be saved in repository - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

# Simplified Architecture imports
from brief_bridge.repositories.command_repository import CommandRepository

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify no command was saved to repository (for error cases)
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    # GREEN Stage 1: Real business rule verification - repository.empty_state
    import asyncio
    
    # Verify repository remains empty when command submission fails
    all_commands = asyncio.run(ctx.test_command_repository.get_all_commands())
    assert len(all_commands) == 0, f"Repository should be empty, but contains {len(all_commands)} commands"