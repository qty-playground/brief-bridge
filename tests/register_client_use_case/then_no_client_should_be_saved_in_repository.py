"""Then no client should be saved in repository - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

# Simplified Architecture imports
from brief_bridge.repositories.client_repository import ClientRepository

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify no client was saved to repository (for error cases)
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.THEN
    # Read-only access to all state for assertions
    
    # GREEN Stage 1: Simple verification that repository remains empty
    import asyncio
    all_clients = asyncio.run(ctx.test_repository.get_all_registered_clients())
    assert len(all_clients) == 0, f"Repository should be empty, but contains {len(all_clients)} clients"