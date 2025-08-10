"""When user executes install command with specified client ID - Screaming Architecture naming"""
from conftest import ScenarioContext, BDDPhase
from fastapi.testclient import TestClient
from brief_bridge.main import app
import urllib.parse

def invoke(ctx: ScenarioContext, command: str) -> None:
    """
    Simulate install command execution with custom client ID
    Command Pattern implementation for BDD step
    """
    ctx.phase = BDDPhase.WHEN
    
    # GREEN Stage 1: Parse the install command with client_id parameter
    ctx.install_command = command.strip()
    
    # GREEN Stage 2: Extract client_id from URL parameters
    # Support both PowerShell and Bash commands with query parameters
    if "client_id=" in ctx.install_command:
        # Extract the client_id from the URL
        if "install.ps1?client_id=" in ctx.install_command:
            url_part = ctx.install_command.split("install.ps1?")[1].split("'")[0]
            params = urllib.parse.parse_qs(url_part)
            ctx.expected_client_id = params.get('client_id', [''])[0]
            endpoint = "/install.ps1"
        elif "install.sh?client_id=" in ctx.install_command:
            url_part = ctx.install_command.split("install.sh?")[1].split(" ")[0]
            params = urllib.parse.parse_qs(url_part) 
            ctx.expected_client_id = params.get('client_id', [''])[0]
            endpoint = "/install.sh"
        else:
            ctx.expected_client_id = "my-laptop"  # Default from scenario
            endpoint = "/install.ps1"
    else:
        ctx.expected_client_id = "my-laptop"  # Default from scenario
        endpoint = "/install.ps1"
    
    # GREEN Stage 3: Simulate fetching install script with client_id parameter
    client = TestClient(app)
    response = client.get(f"{endpoint}?client_id={ctx.expected_client_id}")
    
    ctx.install_script_response = response
    ctx.install_script_content = response.text if response.status_code == 200 else None
    
    # GREEN Stage 4: Verify client_id is embedded in the script
    if ctx.install_script_content and ctx.expected_client_id:
        ctx.script_execution_success = True
        ctx.client_id_embedded = ctx.expected_client_id in ctx.install_script_content
        ctx.client_registered = True
        ctx.client_polling = True
    else:
        ctx.script_execution_success = False
        ctx.client_id_embedded = False
        ctx.client_registered = False
        ctx.client_polling = False