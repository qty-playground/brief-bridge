"""Install script generation use case"""
from typing import Dict, Any, Optional


class InstallScriptUseCase:
    """Use case for generating client install scripts"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        
    def generate_powershell_script(self, client_id: Optional[str] = None, 
                                 client_name: Optional[str] = None,
                                 poll_interval: int = 5,
                                 debug: bool = False) -> str:
        """Generate PowerShell install script"""
        
        # Read the base PowerShell client script
        script_content = self._get_powershell_client_base()
        
        # Generate install wrapper script
        install_script = f"""
# Brief Bridge One-Click PowerShell Installer
# Auto-generated from {self.server_url}

Write-Host "Brief Bridge Client Installer" -ForegroundColor Green
Write-Host "Downloading and starting client..." -ForegroundColor Cyan

# Default parameters
$ServerUrl = "{self.server_url}"
$ClientId = "{client_id or '$env:COMPUTERNAME'}"
$ClientName = "{client_name or 'PowerShell Client'}"
$PollInterval = {poll_interval}
$Debug = ${str(debug).lower()}

# Download client script to temp location
$TempPath = "$env:TEMP\\BriefBridgeClient.ps1"
Write-Host "Downloading client script to $TempPath" -ForegroundColor Yellow

# Embedded client script content
$ClientScript = @'
{script_content}
'@

# Save client script
$ClientScript | Out-File -FilePath $TempPath -Encoding UTF8

# Execute client
Write-Host "Starting Brief Bridge client..." -ForegroundColor Green
if ($Debug) {{
    & powershell -ExecutionPolicy Bypass -File $TempPath -ServerUrl $ServerUrl -ClientId $ClientId -ClientName "$ClientName" -PollInterval $PollInterval -Debug
}} else {{
    & powershell -ExecutionPolicy Bypass -File $TempPath -ServerUrl $ServerUrl -ClientId $ClientId -ClientName "$ClientName" -PollInterval $PollInterval
}}
"""
        
        return install_script
    
    def generate_bash_script(self, client_id: Optional[str] = None,
                           client_name: Optional[str] = None, 
                           poll_interval: int = 5,
                           debug: bool = False) -> str:
        """Generate Bash install script"""
        
        install_script = f"""#!/bin/bash
# Brief Bridge One-Click Bash Installer
# Auto-generated from {self.server_url}

set -euo pipefail

echo "Brief Bridge Client Installer"
echo "Downloading and starting client..."

# Default parameters
SERVER_URL="{self.server_url}"
CLIENT_ID="{client_id or '$(hostname)'}"
CLIENT_NAME="{client_name or 'Bash Client'}"
POLL_INTERVAL={poll_interval}
DEBUG={str(debug).lower()}

# Download location
INSTALL_DIR="$HOME/.brief-bridge"
CLIENT_SCRIPT="$INSTALL_DIR/brief-client.sh"

# Create install directory
mkdir -p "$INSTALL_DIR"

# Download client script
echo "Downloading client script..."
curl -sSL "{self.server_url}/client/download/linux" -o "$CLIENT_SCRIPT"
chmod +x "$CLIENT_SCRIPT"

# Execute client
echo "Starting Brief Bridge client..."
if [ "$DEBUG" = "true" ]; then
    "$CLIENT_SCRIPT" --server "$SERVER_URL" --client-id "$CLIENT_ID" --client-name "$CLIENT_NAME" --poll-interval $POLL_INTERVAL --debug
else
    "$CLIENT_SCRIPT" --server "$SERVER_URL" --client-id "$CLIENT_ID" --client-name "$CLIENT_NAME" --poll-interval $POLL_INTERVAL
fi
"""
        
        return install_script
    
    def _get_powershell_client_base(self) -> str:
        """Get the base PowerShell client script content"""
        # In real implementation, this would read from the actual client file
        # For now, return a placeholder that refers to the actual implementation
        return """
# This would contain the actual PowerShell client script content
# For testing, we reference the existing windows-client/BriefBridgeClient.ps1
param(
    [string]$ServerUrl = "http://localhost:8000",
    [Parameter(Mandatory=$true)][string]$ClientId,
    [string]$ClientName = "",
    [int]$PollInterval = 5,
    [switch]$Debug
)

Write-Host "Brief Bridge Client Starting..." -ForegroundColor Green
Write-Host "Server: $ServerUrl" -ForegroundColor Cyan
Write-Host "Client ID: $ClientId" -ForegroundColor Cyan

# Placeholder - would contain full client implementation
Write-Host "Client functionality placeholder - install successful!" -ForegroundColor Green
"""