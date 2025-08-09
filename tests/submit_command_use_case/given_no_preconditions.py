"""Given no preconditions - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

# Simplified Architecture imports
from brief_bridge.repositories.client_repository import InMemoryClientRepository
from brief_bridge.repositories.command_repository import InMemoryCommandRepository

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: test.setup - no preconditions needed
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.GIVEN
    # Set up empty repositories for WHEN phase to use
    
    # GREEN Stage 1: Setup empty repositories (no preconditions = clean state)
    ctx.test_client_repository = InMemoryClientRepository()
    ctx.test_command_repository = InMemoryCommandRepository()