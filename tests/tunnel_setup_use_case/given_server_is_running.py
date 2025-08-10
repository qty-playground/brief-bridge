"""Given Brief Bridge server is running - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: server.startup - verify server is operational
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Verify server is running and responding
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Server running verification not implemented")
