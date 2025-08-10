"""Given ngrok is installed on the system - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: tunnel.prerequisites - verify ngrok installation
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Verify ngrok binary exists and is executable
    
    # GREEN Stage 1: Hardcoded fake implementation
    raise NotImplementedError("Ngrok installation check not implemented")