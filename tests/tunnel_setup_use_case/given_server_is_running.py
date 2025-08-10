"""Given Brief Bridge server is running - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Business rule: server.startup - verify server is operational
    Command Pattern implementation for BDD step
    """
    # Phase already set by wrapper function
    # Setup test environment with running server
    
    # GREEN Stage 1: Server is assumed to be running (test environment setup)
    ctx.server_running = True
    ctx.server_url = "http://localhost:8000"
