"""Install script generation use case"""
from typing import Dict, Any, Optional


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
    
    
    def _get_powershell_client_base(self) -> str:
        """Get the base PowerShell client script content"""
        # Enhanced PowerShell client with lifecycle management
        return """
# Brief Bridge PowerShell HTTP Polling Client
# Compatible with PowerShell 5.1 and later
param(
    [string]$ServerUrl = "http://localhost:8000",
    [Parameter(Mandatory=$true)][string]$ClientId,
    [string]$ClientName = "PowerShell Client",
    [int]$PollInterval = 5,
    [int]$IdleTimeoutMinutes = 10,
    [switch]$DebugMode
)

# Configuration
$ApiBase = "$ServerUrl"
$MaxRetries = 3
$RetryDelay = 5
$MaxConsecutive404s = 3
$IdleTimeoutSeconds = $IdleTimeoutMinutes * 60

Write-Host "=== Brief Bridge PowerShell Client ===" -ForegroundColor Green
Write-Host "Server: $ServerUrl" -ForegroundColor Cyan
Write-Host "Client ID: $ClientId" -ForegroundColor Cyan
Write-Host "Client Name: $ClientName" -ForegroundColor Cyan
Write-Host "Poll Interval: $PollInterval seconds" -ForegroundColor Cyan
Write-Host "Idle Timeout: $IdleTimeoutMinutes minutes" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Lifecycle tracking variables
$lastCommandTime = Get-Date
$consecutive404Count = 0
$shouldTerminate = $false

# Function to check idle timeout
function Test-IdleTimeout {
    $idleTime = ((Get-Date) - $lastCommandTime).TotalSeconds
    
    if ($idleTime -ge $IdleTimeoutSeconds) {
        Write-Host "[LIFECYCLE] Idle timeout reached ($([math]::Round($idleTime, 1))s >= $IdleTimeoutSeconds s)" -ForegroundColor Yellow
        Write-Host "[LIFECYCLE] Client terminating due to inactivity" -ForegroundColor Red
        return $true
    }
    
    if ($DebugMode) {
        Write-Host "[DEBUG] Idle time: $([math]::Round($idleTime, 1))s / $IdleTimeoutSeconds s" -ForegroundColor DarkGray
    }
    
    return $false
}

# Function to handle 404 tracking
function Test-404Limit {
    if ($consecutive404Count -ge $MaxConsecutive404s) {
        Write-Host "[LIFECYCLE] Maximum consecutive 404s reached ($consecutive404Count)" -ForegroundColor Yellow
        Write-Host "[LIFECYCLE] Client terminating due to server unavailability" -ForegroundColor Red
        return $true
    }
    return $false
}

# Function to make HTTP requests with enhanced error handling
function Invoke-HttpRequest {
    param(
        [string]$Uri,
        [string]$Method = "GET",
        [hashtable]$Body = $null,
        [int]$Retries = $MaxRetries
    )
    
    for ($i = 0; $i -lt $Retries; $i++) {
        try {
            $headers = @{ "Content-Type" = "application/json" }
            
            if ($Body) {
                $jsonBody = $Body | ConvertTo-Json -Depth 10
                $response = Invoke-RestMethod -Uri $Uri -Method $Method -Body $jsonBody -Headers $headers -TimeoutSec 30
            } else {
                $response = Invoke-RestMethod -Uri $Uri -Method $Method -Headers $headers -TimeoutSec 30
            }
            
            # Reset 404 counter on successful request
            $global:consecutive404Count = 0
            return $response
        }
        catch {
            $statusCode = $null
            if ($_.Exception.Response) {
                $statusCode = [int]$_.Exception.Response.StatusCode
            }
            
            # Track 404s specifically
            if ($statusCode -eq 404) {
                $global:consecutive404Count++
                Write-Warning "HTTP 404 - Not Found (consecutive: $global:consecutive404Count/$MaxConsecutive404s)"
                
                # Check if we've hit the limit
                if (Test-404Limit) {
                    $global:shouldTerminate = $true
                    throw "Maximum consecutive 404s reached"
                }
            }
            
            Write-Warning "Request failed (attempt $($i + 1)/$Retries): $($_.Exception.Message)"
            if ($i -eq $Retries - 1) {
                throw $_.Exception
            }
            Start-Sleep -Seconds $RetryDelay
        }
    }
}

# Function to register client
function Register-Client {
    try {
        $body = @{
            client_id = $ClientId
            name = $ClientName
        }
        
        $response = Invoke-HttpRequest -Uri "$ApiBase/clients/register" -Method "POST" -Body $body
        Write-Host "[REGISTER] Client registered successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to register client: $($_.Exception.Message)"
        return $false
    }
}

# Function to execute PowerShell command
function Invoke-PowerShellCommand {
    param(
        [string]$Command,
        [int]$TimeoutSeconds = 30
    )
    
    $startTime = Get-Date
    
    try {
        # Check for terminate command
        if ($Command.Trim() -eq "terminate") {
            Write-Host "[LIFECYCLE] Terminate command received from server" -ForegroundColor Yellow
            Write-Host "[LIFECYCLE] Client terminating gracefully..." -ForegroundColor Red
            $global:shouldTerminate = $true
            
            return @{
                success = $true
                output = "Client terminating gracefully on server request"
                error = $null
                execution_time = 0.1
            }
        }
        
        Write-Host "[EXEC] $Command" -ForegroundColor Yellow
        
        # Update last command time for idle tracking
        $global:lastCommandTime = Get-Date
        
        # Execute command and capture output
        $output = Invoke-Expression $Command 2>&1 | Out-String
        
        $executionTime = ((Get-Date) - $startTime).TotalSeconds
        
        Write-Host "[SUCCESS] Execution time: $([math]::Round($executionTime, 2))s" -ForegroundColor Green
        
        return @{
            success = $true
            output = $output.Trim()
            error = $null
            execution_time = $executionTime
        }
    }
    catch {
        $executionTime = ((Get-Date) - $startTime).TotalSeconds
        $errorMessage = $_.Exception.Message
        
        Write-Host "[ERROR] $errorMessage" -ForegroundColor Red
        
        return @{
            success = $false
            output = $null
            error = $errorMessage
            execution_time = $executionTime
        }
    }
}

# Function to submit command result
function Submit-CommandResult {
    param(
        [string]$CommandId,
        [hashtable]$Result
    )
    
    try {
        $body = @{
            command_id = $CommandId
            success = $Result.success
            output = $Result.output
            error = $Result.error
            execution_time = $Result.execution_time
        }
        
        $response = Invoke-HttpRequest -Uri "$ApiBase/commands/result" -Method "POST" -Body $body
        Write-Host "[RESULT] Submitted result for command $CommandId" -ForegroundColor Cyan
        return $true
    }
    catch {
        Write-Error "Failed to submit result for command $CommandId`: $($_.Exception.Message)"
        return $false
    }
}

# Function to poll for commands
function Get-PendingCommand {
    try {
        $body = @{
            client_id = $ClientId
        }
        
        $response = Invoke-HttpRequest -Uri "$ApiBase/commands/poll" -Method "POST" -Body $body
        
        if ($response.command_id) {
            Write-Host "[POLL] Received command: $($response.command_id)" -ForegroundColor Magenta
            return $response
        }
        
        return $null
    }
    catch {
        Write-Warning "Failed to poll for commands: $($_.Exception.Message)"
        return $null
    }
}

# Register client
if (-not (Register-Client)) {
    Write-Error "Failed to register client. Exiting."
    exit 1
}

# Main polling loop with lifecycle management
$consecutiveErrors = 0
$maxConsecutiveErrors = 5

Write-Host "Starting polling loop..." -ForegroundColor Green
Write-Host "[LIFECYCLE] Monitoring idle timeout and server availability..." -ForegroundColor Cyan

try {
    while ($true -and -not $shouldTerminate) {
        try {
            # Check lifecycle conditions before polling
            if (Test-IdleTimeout) {
                break
            }
            
            if (Test-404Limit) {
                break
            }
            
            # Poll for pending commands
            $command = Get-PendingCommand
            
            if ($command) {
                # Reset error counter on successful poll
                $consecutiveErrors = 0
                
                # Execute the command
                $result = Invoke-PowerShellCommand -Command $command.command_content -TimeoutSeconds $command.timeout
                
                # Submit the result
                $submitted = Submit-CommandResult -CommandId $command.command_id -Result $result
                
                if (-not $submitted) {
                    Write-Warning "Failed to submit result, but continuing..."
                }
                
                # Check if command triggered termination
                if ($shouldTerminate) {
                    Write-Host "[LIFECYCLE] Termination triggered by command execution" -ForegroundColor Yellow
                    break
                }
            } else {
                # No commands available, reset error counter
                $consecutiveErrors = 0
            }
        }
        catch {
            $consecutiveErrors++
            Write-Error "Polling error ($consecutiveErrors/$maxConsecutiveErrors): $($_.Exception.Message)"
            
            if ($consecutiveErrors -ge $maxConsecutiveErrors) {
                Write-Error "[LIFECYCLE] Too many consecutive errors. Exiting."
                break
            }
            
            # Check if termination was triggered during error handling
            if ($shouldTerminate) {
                Write-Host "[LIFECYCLE] Termination triggered during error handling" -ForegroundColor Yellow
                break
            }
        }
        
        # Wait before next poll
        Start-Sleep -Seconds $PollInterval
    }
}
catch {
    Write-Error "Fatal error in main loop: $($_.Exception.Message)"
}
finally {
    Write-Host "[LIFECYCLE] Client shutting down..." -ForegroundColor Yellow
    Write-Host "Goodbye!" -ForegroundColor Green
}
"""