"""Given tunnel is already setup and running - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: tunnel.status - establish existing tunnel state
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Setup test environment with active tunnel
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Existing tunnel setup not implemented")
