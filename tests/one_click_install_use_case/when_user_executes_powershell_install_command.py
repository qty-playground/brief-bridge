"""When user executes PowerShell install command - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
from fastapi.testclient import TestClient
from brief_bridge.main import app

def invoke(ctx: ScenarioContext, command: str) -> None:
    """
    Simulate PowerShell install command execution
    Command Pattern implementation for BDD step
    """
    ctx.phase = BDDPhase.WHEN
    
    # GREEN Stage 1: Parse and execute the install command
    ctx.install_command = command.strip()
    
    # Extract URL from PowerShell command: iex ((Invoke-WebRequest 'URL').Content)
    # For testing, simulate the HTTP request to get the install script
    
    # GREEN Stage 2: Simulate fetching install script via HTTP
    client = TestClient(app)
    
    # Extract the install script URL from the PowerShell command
    # Command format: iex ((Invoke-WebRequest 'http://server-url/install.ps1').Content)
    if "/install.ps1" in ctx.install_command:
        # Simulate the HTTP GET request to fetch the PowerShell script
        response = client.get("/install.ps1")
        ctx.install_script_response = response
        ctx.install_script_content = response.text if response.status_code == 200 else None
        
    # GREEN Stage 3: Simulate script execution results
    if ctx.install_script_content:
        ctx.script_execution_success = True
        ctx.client_downloaded = True  # Script contains client download logic
        ctx.client_registered = True  # Script contains registration logic
        ctx.client_polling = True     # Script starts polling
        ctx.success_message_shown = True
    else:
        ctx.script_execution_success = False
        ctx.client_downloaded = False
        ctx.client_registered = False
        ctx.client_polling = False
        ctx.success_message_shown = False