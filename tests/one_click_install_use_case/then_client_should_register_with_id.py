"""Then client should register with specified ID - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase

def invoke(ctx: ScenarioContext, client_id: str) -> None:
    """
    Verify client registers with the specified ID
    Command Pattern implementation for BDD step
    """
    ctx.phase = BDDPhase.THEN
    
    # GREEN Stage 1: Verify expected client ID matches the specified ID
    assert hasattr(ctx, "expected_client_id"), "Expected client ID not set"
    assert ctx.expected_client_id == client_id, f"Expected client ID {client_id}, got {ctx.expected_client_id}"
    
    # GREEN Stage 2: Verify client ID is embedded in install script
    assert hasattr(ctx, "client_id_embedded"), "Client ID embedding status not tracked"
    assert ctx.client_id_embedded == True, f"Client ID '{client_id}' should be embedded in install script"
    
    # GREEN Stage 3: Verify install script contains the custom client ID
    assert hasattr(ctx, "install_script_content"), "Install script content not found"
    assert ctx.install_script_content is not None, "Install script content should not be empty"
    assert client_id in ctx.install_script_content, f"Install script should contain client ID '{client_id}'"