"""Then client should start polling for commands - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify client starts polling for commands
    Command Pattern implementation for BDD step
    """
    ctx.phase = BDDPhase.THEN
    
    # GREEN Stage 1: Verify client polling started
    assert hasattr(ctx, "client_polling"), "Client polling status not tracked"
    assert ctx.client_polling == True, "Client should start polling for commands"
    
    # GREEN Stage 2: Verify polling logic in install script
    assert hasattr(ctx, "install_script_content"), "Install script content not found"
    assert ctx.install_script_content is not None, "Install script content should not be empty"
    
    # GREEN Stage 3: Verify script contains polling parameters
    has_ps1_polling = "PollInterval" in ctx.install_script_content
    has_bash_polling = "POLL_INTERVAL" in ctx.install_script_content
    
    assert has_ps1_polling or has_bash_polling, "Install script should contain poll interval parameter"
    
    # GREEN Stage 4: Verify script execution initiates the client
    has_ps1_execution = "$PowerShellExe -ExecutionPolicy Bypass" in ctx.install_script_content
    has_bash_execution = "chmod +x" in ctx.install_script_content and "$CLIENT_SCRIPT" in ctx.install_script_content
    
    assert has_ps1_execution or has_bash_execution, "Install script should execute client"