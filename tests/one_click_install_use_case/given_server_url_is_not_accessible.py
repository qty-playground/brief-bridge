"""Given server URL is not accessible - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: install.failure - simulate unreachable server
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Setup test environment with unreachable server
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Unreachable server simulation not implemented")
