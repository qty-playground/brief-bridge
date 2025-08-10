"""When user executes install command again - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Execute install command when client already exists
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Execute duplicate install attempt
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Duplicate install execution not implemented")
