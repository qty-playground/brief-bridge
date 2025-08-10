"""Then client should automatically register with server - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify client automatically registers with server
    Command Pattern implementation for BDD step
    """
    ctx.phase = BDDPhase.THEN
    
    # GREEN Stage 1: Verify client registration occurred
    assert hasattr(ctx, "client_registered"), "Client registration status not tracked"
    assert ctx.client_registered == True, "Client should automatically register with server"
    
    # GREEN Stage 2: Verify registration logic in install script
    assert hasattr(ctx, "install_script_content"), "Install script content not found"
    assert ctx.install_script_content is not None, "Install script content should not be empty"
    
    # GREEN Stage 3: Verify script contains registration parameters
    # The install script should contain server URL and client parameters
    has_ps1_params = "ServerUrl" in ctx.install_script_content and "ClientId" in ctx.install_script_content
    has_bash_params = "SERVER_URL" in ctx.install_script_content and "CLIENT_ID" in ctx.install_script_content
    
    assert has_ps1_params or has_bash_params, "Install script should contain server URL and client ID parameters"