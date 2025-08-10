"""Then user should see success message - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext) -> None:
    """
    Verify user sees success message
    Command Pattern implementation for BDD step
    """
    ctx.phase = BDDPhase.THEN
    
    # GREEN Stage 1: Verify success message was shown
    assert hasattr(ctx, "success_message_shown"), "Success message status not tracked"
    assert ctx.success_message_shown == True, "User should see success message"
    
    # GREEN Stage 2: Verify install script contains user feedback
    assert hasattr(ctx, "install_script_content"), "Install script content not found"
    assert ctx.install_script_content is not None, "Install script content should not be empty"
    
    # GREEN Stage 3: Verify script contains success indicators
    assert "Brief Bridge Client Installer" in ctx.install_script_content, "Install script should show installer name"
    
    has_ps1_feedback = "Write-Host" in ctx.install_script_content
    has_bash_feedback = "echo" in ctx.install_script_content
    
    assert has_ps1_feedback or has_bash_feedback, "Install script should contain user feedback messages"