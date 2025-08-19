"""Install script generation use case"""
from typing import Dict, Any, Optional
import os


class InstallScriptUseCase:
    """Use case for generating client install scripts"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        
    def generate_powershell_script(self, client_id: Optional[str] = None, 
                                 client_name: Optional[str] = None,
                                 poll_interval: int = 5,
                                 idle_timeout_minutes: int = 10,
                                 debug: bool = False) -> str:
        """Generate PowerShell install script"""
        
        # Read the base PowerShell client script
        script_content = self._get_powershell_client_base()
        
        # Generate client ID logic
        if client_id:
            client_id_logic = f'$ClientId = "{client_id}"'
        else:
            client_id_logic = '''# Auto-detect client ID based on platform
if ($env:COMPUTERNAME) {
    $ClientId = $env:COMPUTERNAME
} elseif ($env:HOSTNAME) {
    $ClientId = $env:HOSTNAME  
} elseif ($env:USER) {
    $ClientId = "$env:USER-$(Get-Random -Maximum 9999)"
} else {
    $ClientId = "pwsh-client-$(Get-Random -Maximum 9999)"
}'''

        # Generate install wrapper script
        install_script = f"""
# Brief Bridge One-Click PowerShell Installer
# Auto-generated from {self.server_url}

Write-Host "Brief Bridge Client Installer" -ForegroundColor Green
Write-Host "Downloading and starting client..." -ForegroundColor Cyan

# Default parameters
$ServerUrl = "{self.server_url}"
$ClientName = "{client_name or 'PowerShell Client'}"
$PollInterval = {poll_interval}
$DebugMode = ${str(debug).lower()}

# Cross-platform client ID detection
{client_id_logic}

# Generate unique filename with UUID to avoid conflicts with multiple clients
$ScriptUuid = [System.Guid]::NewGuid().ToString("N").Substring(0,8)

# Download client script to temp location (cross-platform path)
if ($IsLinux -or $IsMacOS) {{
    $TempPath = "/tmp/BriefBridgeClient_$ScriptUuid.ps1"
}} else {{
    $TempPath = "$env:TEMP\\BriefBridgeClient_$ScriptUuid.ps1"
}}
Write-Host "Downloading client script to $TempPath" -ForegroundColor Yellow

# Embedded client script content
$ClientScript = @'
{script_content}
'@

# Save client script
$ClientScript | Out-File -FilePath $TempPath -Encoding UTF8

# Detect PowerShell executable (pwsh on Linux/macOS, powershell on Windows)
$PowerShellExe = "powershell"
if (Get-Command "pwsh" -ErrorAction SilentlyContinue) {{
    $PowerShellExe = "pwsh"
}}
Write-Host "Using PowerShell executable: $PowerShellExe" -ForegroundColor Yellow

# Execute client
Write-Host "Starting Brief Bridge client..." -ForegroundColor Green
if ($DebugMode -eq "true") {{
    & $PowerShellExe -ExecutionPolicy Bypass -File $TempPath -ServerUrl $ServerUrl -ClientId $ClientId -ClientName "$ClientName" -PollInterval $PollInterval -IdleTimeoutMinutes {idle_timeout_minutes} -DebugMode
}} else {{
    & $PowerShellExe -ExecutionPolicy Bypass -File $TempPath -ServerUrl $ServerUrl -ClientId $ClientId -ClientName "$ClientName" -PollInterval $PollInterval -IdleTimeoutMinutes {idle_timeout_minutes}
}}
"""
        
        return install_script
    
    def generate_modular_powershell_script(self, client_id: Optional[str] = None, 
                                         client_name: Optional[str] = None,
                                         poll_interval: int = 5,
                                         idle_timeout_minutes: int = 10,
                                         debug: bool = False) -> str:
        """Generate Modular PowerShell install script with enhanced functionality"""
        
        # Read the modular PowerShell client script
        script_content = self._get_modular_powershell_client_base()
        
        # Generate client ID logic
        if client_id:
            client_id_logic = f'$ClientId = "{client_id}"'
        else:
            client_id_logic = '''# Auto-detect client ID based on platform
if ($env:COMPUTERNAME) {
    $ClientId = $env:COMPUTERNAME
} elseif ($env:HOSTNAME) {
    $ClientId = $env:HOSTNAME  
} elseif ($env:USER) {
    $ClientId = "$env:USER-$(Get-Random -Maximum 9999)"
} else {
    $ClientId = "pwsh-modular-client-$(Get-Random -Maximum 9999)"
}'''

        # Generate enhanced install wrapper script
        install_script = f"""
# Brief Bridge One-Click Modular PowerShell Installer
# Auto-generated from {self.server_url}
# Enhanced with modular architecture and built-in functions

Write-Host "=== Brief Bridge Modular Client Installer ===" -ForegroundColor Green
Write-Host "This is the enhanced modular version with reusable functions" -ForegroundColor Cyan
Write-Host "Downloading and starting modular client..." -ForegroundColor Cyan

# Default parameters
$ServerUrl = "{self.server_url}"
$ClientName = "{client_name or 'Modular PowerShell Client'}"
$PollInterval = {poll_interval}
$DebugMode = ${str(debug).lower()}

# Cross-platform client ID detection
{client_id_logic}

# Generate unique filename with UUID to avoid conflicts with multiple clients
$ScriptUuid = [System.Guid]::NewGuid().ToString("N").Substring(0,8)

# Download client script to temp location (cross-platform path)
if ($IsLinux -or $IsMacOS) {{
    $TempPath = "/tmp/BriefBridgeModularClient_$ScriptUuid.ps1"
}} else {{
    $TempPath = "$env:TEMP\\BriefBridgeModularClient_$ScriptUuid.ps1"
}}
Write-Host "Downloading modular client script to $TempPath" -ForegroundColor Yellow

# Embedded modular client script content
$ClientScript = @'
{script_content}
'@

# Save client script
$ClientScript | Out-File -FilePath $TempPath -Encoding UTF8

# Detect PowerShell executable (pwsh on Linux/macOS, powershell on Windows)
$PowerShellExe = "powershell"
if (Get-Command "pwsh" -ErrorAction SilentlyContinue) {{
    $PowerShellExe = "pwsh"
}}
Write-Host "Using PowerShell executable: $PowerShellExe" -ForegroundColor Yellow

# Execute modular client
Write-Host "Starting Brief Bridge modular client..." -ForegroundColor Green
Write-Host "Enhanced features: Modular functions, Built-in commands, Better error handling" -ForegroundColor Magenta

if ($DebugMode -eq "true") {{
    & $PowerShellExe -ExecutionPolicy Bypass -File $TempPath -ServerUrl $ServerUrl -ClientId $ClientId -ClientName "$ClientName" -PollInterval $PollInterval -IdleTimeoutMinutes {idle_timeout_minutes} -DebugMode
}} else {{
    & $PowerShellExe -ExecutionPolicy Bypass -File $TempPath -ServerUrl $ServerUrl -ClientId $ClientId -ClientName "$ClientName" -PollInterval $PollInterval -IdleTimeoutMinutes {idle_timeout_minutes}
}}
"""
        
        return install_script
    
    def generate_bash_script(self, client_id: Optional[str] = None, 
                           client_name: Optional[str] = None,
                           poll_interval: int = 5,
                           idle_timeout_minutes: int = 10,
                           debug: bool = False) -> str:
        """Generate Bash install script"""
        
        # Read the base Bash client script
        script_content = self._get_bash_client_base()
        
        # Generate client ID logic
        if client_id:
            client_id_logic = f'CLIENT_ID="{client_id}"'
        else:
            client_id_logic = '''# Auto-detect client ID based on platform
if [ -n "$COMPUTERNAME" ]; then
    CLIENT_ID="$COMPUTERNAME"
elif [ -n "$HOSTNAME" ]; then
    CLIENT_ID="$HOSTNAME"  
elif [ -n "$USER" ]; then
    CLIENT_ID="$USER-$RANDOM"
else
    CLIENT_ID="bash-client-$RANDOM"
fi'''

        # Generate install wrapper script
        install_script = f"""#!/bin/bash
# Brief Bridge One-Click Bash Installer
# Auto-generated from {self.server_url}

echo "Brief Bridge Client Installer"
echo "Downloading and starting client..."

# Default parameters
SERVER_URL="{self.server_url}"
CLIENT_NAME="{client_name or 'Bash Client'}"
POLL_INTERVAL={poll_interval}
DEBUG_MODE="{str(debug).lower()}"

# Cross-platform client ID detection
{client_id_logic}

# Generate unique filename with UUID to avoid conflicts with multiple clients
SCRIPT_UUID=$(openssl rand -hex 4 2>/dev/null || echo $RANDOM)

# Download client script to temp location
TEMP_PATH="/tmp/BriefBridgeClient_$SCRIPT_UUID.sh"
echo "Downloading client script to $TEMP_PATH"

# Embedded client script content
cat > "$TEMP_PATH" << 'EOF'
{script_content}
EOF

# Make script executable
chmod +x "$TEMP_PATH"

# Execute client
echo "Starting Brief Bridge client..."
if [ "$DEBUG_MODE" = "true" ]; then
    bash "$TEMP_PATH" --server-url "$SERVER_URL" --client-id "$CLIENT_ID" --client-name "$CLIENT_NAME" --poll-interval $POLL_INTERVAL --idle-timeout-minutes {idle_timeout_minutes} --debug
else
    bash "$TEMP_PATH" --server-url "$SERVER_URL" --client-id "$CLIENT_ID" --client-name "$CLIENT_NAME" --poll-interval $POLL_INTERVAL --idle-timeout-minutes {idle_timeout_minutes}
fi
"""
        
        return install_script
    
    def _get_bash_client_base(self) -> str:
        """Get the base Bash client script content"""
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "templates", 
            "bash_client.sh"
        )
        
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Bash client template not found at {template_path}")
    
    def _get_powershell_client_base(self) -> str:
        """Get the base PowerShell client script content"""
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "templates", 
            "powershell_client.ps1"
        )
        
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"PowerShell client template not found at {template_path}")
    
    def _get_modular_powershell_client_base(self) -> str:
        """Get the modular PowerShell client script content"""
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "templates", 
            "powershell_modular_client.ps1"
        )
        
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Modular PowerShell client template not found at {template_path}")