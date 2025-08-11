"""Given client is registered with status - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
from brief_bridge.entities.client import Client

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: client.registration - create test client with specific status
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.GIVEN
    # Can access input state set in GIVEN phase
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Client registration with status not implemented")