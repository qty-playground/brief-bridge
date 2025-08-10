"""Given client is already running - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: install.duplicate - setup existing client process
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Setup test environment with running client
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Existing client setup not implemented")
