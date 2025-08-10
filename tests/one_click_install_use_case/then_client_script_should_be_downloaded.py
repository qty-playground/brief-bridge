"""Then client script should be downloaded - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify client script was successfully downloaded
    Command Pattern implementation for BDD step
    """
    ctx.phase = BDDPhase.THEN
    
    # GREEN Stage 1: Verify script download occurred
    assert hasattr(ctx, "client_downloaded"), "Client download status not tracked"
    assert ctx.client_downloaded == True, "Client script should be downloaded"
    
    # GREEN Stage 2: Verify install script was fetched
    assert hasattr(ctx, "install_script_response"), "Install script HTTP response not found"
    assert ctx.install_script_response.status_code == 200, "Install script should be accessible via HTTP"
    
    # GREEN Stage 3: Verify script content contains download logic
    assert hasattr(ctx, "install_script_content"), "Install script content not found"
    assert ctx.install_script_content is not None, "Install script content should not be empty"
    
    # Support both PowerShell and Bash scripts
    has_ps1_download = "BriefBridgeClient.ps1" in ctx.install_script_content
    has_bash_download = "curl" in ctx.install_script_content or "brief-client.sh" in ctx.install_script_content
    
    assert has_ps1_download or has_bash_download, "Install script should reference client script download"