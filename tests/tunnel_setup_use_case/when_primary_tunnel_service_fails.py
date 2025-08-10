"""When primary tunnel service fails - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Simulate primary tunnel service failure
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Trigger primary tunnel service failure
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Primary tunnel failure simulation not implemented")
