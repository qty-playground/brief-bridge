"""Given Brief Bridge server is running locally - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: server.startup - initialize local server instance
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Setup test environment with local server
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Local server setup not implemented")