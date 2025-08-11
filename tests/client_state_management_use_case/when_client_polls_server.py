"""When client polls server for commands - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Execute client polling request to server
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function - ctx.phase = BDDPhase.WHEN
    # Can access input state from GIVEN phase, collect results here
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Client polling execution not implemented")