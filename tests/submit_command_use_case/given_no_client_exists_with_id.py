"""Given no client exists with id - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

# Simplified Architecture imports
from brief_bridge.repositories.client_repository import InMemoryClientRepository

def invoke(ctx: ScenarioContext, client_id: str) -> None:
    """
    Business rule: test.precondition - ensure client does not exist
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.GIVEN
    # Can access input state set in GIVEN phase
    
    # GREEN Stage 1: Setup empty repositories (no client registered)
    test_client_repository = InMemoryClientRepository()
    
    # Setup command repository as well
    from brief_bridge.repositories.command_repository import InMemoryCommandRepository
    test_command_repository = InMemoryCommandRepository()
    
    # Store empty repositories in context for WHEN phase
    ctx.test_client_repository = test_client_repository
    ctx.test_command_repository = test_command_repository