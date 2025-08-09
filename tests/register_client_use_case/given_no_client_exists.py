"""Given no client exists with id - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

# Simplified Architecture imports
from brief_bridge.repositories.client_repository import ClientRepository, InMemoryClientRepository

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: test.precondition - ensure client does not exist
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.GIVEN
    # Can access input state set in GIVEN phase
    
    # GREEN Stage 1: Hardcoded implementation - assume no client exists
    # This is setup verification, no actual action needed in Stage 1
    pass