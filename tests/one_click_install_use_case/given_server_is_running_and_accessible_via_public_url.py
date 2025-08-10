"""Given server is running and accessible via public URL - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Setup server running state and public URL accessibility
    Command Pattern implementation for BDD step
    """
    ctx.phase = BDDPhase.GIVEN
    
    # GREEN Stage 1: Setup test server state
    ctx.server_running = True
    ctx.public_url = "https://abc123def.ngrok.io"  # Mock ngrok URL
    ctx.server_url = ctx.public_url
    ctx.install_ps1_url = f"{ctx.public_url}/install.ps1"
    
    # GREEN Stage 2: Mock server accessibility
    ctx.server_accessible = True
    ctx.tunnel_status = "active"