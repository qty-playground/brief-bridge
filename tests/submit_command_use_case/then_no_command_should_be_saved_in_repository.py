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
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Repository empty state verification not implemented")