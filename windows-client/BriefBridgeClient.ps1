#requires -version 5.1

<#
.SYNOPSIS
    Brief Bridge Client for Windows PowerShell 5.1

.DESCRIPTION
    A PowerShell client that connects to Brief Bridge server to receive and execute commands.
    Supports command polling, execution, and result reporting back to the server.

.PARAMETER ServerUrl
    Brief Bridge server URL (default: http://localhost:8000)

.PARAMETER ClientId
    Unique client identifier (required)

.PARAMETER ClientName
    Human-readable client name (optional)

.PARAMETER PollInterval
    Polling interval in seconds (default: 5)

.PARAMETER LogPath
    Path to log file (optional)

.PARAMETER Debug
    Enable debug logging

.EXAMPLE
    .\BriefBridgeClient.ps1 -ClientId "win-client-001"

.EXAMPLE  
    .\BriefBridgeClient.ps1 -ServerUrl "http://192.168.1.100:8000" -ClientId "laptop-001" -ClientName "My Windows Laptop" -Debug

.EXAMPLE
    .\BriefBridgeClient.ps1 -ClientId "ci-runner" -PollInterval 2 -LogPath "C:\Logs\brief-bridge-client.log"
#>

[CmdletBinding()]
param(
    [string]$ServerUrl = "http://localhost:8000",
    [Parameter(Mandatory=$true)]
    [string]$ClientId,
    [string]$ClientName = "",
    [int]$PollInterval = 5,
    [string]$LogPath = "",
    [switch]$Debug
)

# Global variables
$script:ClientRegistered = $false
$script:ShouldStop = $false

# Enhanced logging function
function Write-Log {
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet("INFO", "WARN", "ERROR", "DEBUG")]
        [string]$Level,
        
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [string]$LogFile = $LogPath
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$Level] $timestamp - $Message"
    
    # Color output based on level
    switch ($Level) {
        "INFO"  { Write-Host $logEntry -ForegroundColor Green }
        "WARN"  { Write-Host $logEntry -ForegroundColor Yellow }
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "DEBUG" { 
            if ($Debug) { 
                Write-Host $logEntry -ForegroundColor Cyan 
            }
        }
    }
    
    # Write to log file if specified
    if ($LogFile) {
        try {
            # Ensure directory exists
            $logDir = Split-Path $LogFile -Parent
            if ($logDir -and !(Test-Path $logDir)) {
                New-Item -ItemType Directory -Path $logDir -Force | Out-Null
            }
            Add-Content -Path $LogFile -Value $logEntry -Encoding UTF8
        }
        catch {
            Write-Warning "Failed to write to log file: $_"
        }
    }
}

# Test server connectivity
function Test-ServerConnectivity {
    Write-Log -Level "DEBUG" -Message "Testing connectivity to $ServerUrl"
    
    try {
        $response = Invoke-RestMethod -Uri "$ServerUrl/health" -Method GET -TimeoutSec 10 -ErrorAction Stop
        Write-Log -Level "INFO" -Message "Server connectivity verified"
        return $true
    }
    catch {
        Write-Log -Level "ERROR" -Message "Failed to connect to server: $($_.Exception.Message)"
        return $false
    }
}

# Register client with server
function Register-Client {
    Write-Log -Level "INFO" -Message "Registering client '$ClientId' with server $ServerUrl"
    
    $registrationData = @{
        client_id = $ClientId
        name = if ($ClientName) { $ClientName } else { "PowerShell-Client-$ClientId" }
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$ServerUrl/clients/register" -Method POST -Body ($registrationData | ConvertTo-Json) -ContentType "application/json" -ErrorAction Stop
        
        if ($response.success -eq $true) {
            Write-Log -Level "INFO" -Message "Client registration successful"
            Write-Log -Level "DEBUG" -Message "Registration response: $($response | ConvertTo-Json -Compress)"
            $script:ClientRegistered = $true
            return $true
        }
        else {
            Write-Log -Level "ERROR" -Message "Registration failed: $($response.message)"
            return $false
        }
    }
    catch {
        Write-Log -Level "ERROR" -Message "Failed to register client: $($_.Exception.Message)"
        if ($_.Exception.Response) {
            Write-Log -Level "DEBUG" -Message "HTTP Status: $($_.Exception.Response.StatusCode)"
        }
        return $false
    }
}

# Get pending commands for this client
function Get-PendingCommands {
    Write-Log -Level "DEBUG" -Message "Polling for commands for client '$ClientId'"
    
    try {
        $commands = Invoke-RestMethod -Uri "$ServerUrl/commands/client/$ClientId" -Method GET -ErrorAction Stop
        
        if ($commands -and $commands.Count -gt 0) {
            # Filter for processing commands (ones marked by server when we poll)
            $processingCommands = $commands | Where-Object { $_.status -eq "processing" }
            
            if ($processingCommands -and $processingCommands.Count -gt 0) {
                Write-Log -Level "INFO" -Message "Found $($processingCommands.Count) command(s) to execute"
                return $processingCommands
            }
        }
        
        Write-Log -Level "DEBUG" -Message "No pending commands found"
        return @()
    }
    catch {
        Write-Log -Level "WARN" -Message "Failed to get commands: $($_.Exception.Message)"
        return $null
    }
}

# Execute a single command
function Invoke-Command {
    param(
        [Parameter(Mandatory=$true)]
        [PSObject]$CommandObject
    )
    
    $commandId = $CommandObject.command_id
    $content = $CommandObject.content
    $type = $CommandObject.type
    
    Write-Log -Level "INFO" -Message "Executing command: $commandId"
    Write-Log -Level "DEBUG" -Message "Command content: $content"
    Write-Log -Level "DEBUG" -Message "Command type: $type"
    
    $startTime = Get-Date
    $output = ""
    $error = $null
    $success = $false
    
    try {
        switch ($type) {
            "shell" {
                Write-Log -Level "DEBUG" -Message "Executing PowerShell command: $content"
                
                # Execute command in a script block for better error handling
                $result = Invoke-Expression $content 2>&1
                
                if ($result) {
                    if ($result -is [System.Array]) {
                        $output = $result -join "`n"
                    } else {
                        $output = $result.ToString()
                    }
                }
                
                $success = $true
                Write-Log -Level "INFO" -Message "Command executed successfully"
                Write-Log -Level "DEBUG" -Message "Command output: $output"
            }
            "powershell" {
                Write-Log -Level "DEBUG" -Message "Executing PowerShell script: $content"
                
                $scriptBlock = [ScriptBlock]::Create($content)
                $result = & $scriptBlock 2>&1
                
                if ($result) {
                    if ($result -is [System.Array]) {
                        $output = $result -join "`n"
                    } else {
                        $output = $result.ToString()
                    }
                }
                
                $success = $true
                Write-Log -Level "INFO" -Message "PowerShell script executed successfully"
                Write-Log -Level "DEBUG" -Message "Script output: $output"
            }
            default {
                $error = "Unsupported command type: $type"
                Write-Log -Level "WARN" -Message $error
            }
        }
    }
    catch {
        $success = $false
        $error = $_.Exception.Message
        Write-Log -Level "WARN" -Message "Command execution failed: $error"
        Write-Log -Level "DEBUG" -Message "Full error: $($_ | Out-String)"
    }
    
    $endTime = Get-Date
    $executionTime = ($endTime - $startTime).TotalSeconds
    
    # Submit result back to server
    Submit-CommandResult -CommandId $commandId -Output $output -Error $error -ExecutionTime $executionTime -Success $success
}

# Submit command execution result back to server
function Submit-CommandResult {
    param(
        [Parameter(Mandatory=$true)]
        [string]$CommandId,
        
        [string]$Output = "",
        [string]$Error = $null,
        [double]$ExecutionTime = 0.0,
        [bool]$Success = $false
    )
    
    Write-Log -Level "DEBUG" -Message "Submitting result for command: $CommandId"
    
    $resultData = @{
        command_id = $CommandId
        output = $Output
        error = $Error
        execution_time = $ExecutionTime
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$ServerUrl/commands/result" -Method POST -Body ($resultData | ConvertTo-Json) -ContentType "application/json" -ErrorAction Stop
        
        if ($response.status -eq "success") {
            Write-Log -Level "INFO" -Message "Command result submitted successfully"
            Write-Log -Level "DEBUG" -Message "Result response: $($response | ConvertTo-Json -Compress)"
        }
        else {
            Write-Log -Level "WARN" -Message "Result submission returned non-success status: $($response.status)"
        }
    }
    catch {
        Write-Log -Level "ERROR" -Message "Failed to submit command result: $($_.Exception.Message)"
        Write-Log -Level "DEBUG" -Message "Result data was: $($resultData | ConvertTo-Json -Compress)"
    }
}

# Main polling loop
function Start-CommandPolling {
    Write-Log -Level "INFO" -Message "Starting command polling (interval: ${PollInterval}s)"
    Write-Log -Level "INFO" -Message "Press Ctrl+C to stop"
    
    # Setup signal handler for graceful shutdown
    [Console]::TreatControlCAsInput = $false
    [Console]::CancelKeyPress.Add({
        param($sender, $e)
        $e.Cancel = $true
        $script:ShouldStop = $true
        Write-Log -Level "INFO" -Message "Shutdown requested by user"
    })
    
    while (-not $script:ShouldStop) {
        try {
            $commands = Get-PendingCommands
            
            if ($commands -and $commands.Count -gt 0) {
                foreach ($command in $commands) {
                    if ($script:ShouldStop) { break }
                    Invoke-Command -CommandObject $command
                }
            }
        }
        catch {
            Write-Log -Level "ERROR" -Message "Error in polling loop: $($_.Exception.Message)"
        }
        
        if (-not $script:ShouldStop) {
            Start-Sleep -Seconds $PollInterval
        }
    }
    
    Write-Log -Level "INFO" -Message "Command polling stopped"
}

# Display startup banner
function Show-StartupBanner {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Blue
    Write-Host "  Brief Bridge Client v1.0.0" -ForegroundColor Blue  
    Write-Host "  Windows PowerShell 5.1" -ForegroundColor Blue
    Write-Host "================================" -ForegroundColor Blue
    Write-Host ""
}

# Main execution
function Main {
    Show-StartupBanner
    
    # Validate PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        Write-Log -Level "ERROR" -Message "PowerShell 5.1 or higher is required. Current version: $($PSVersionTable.PSVersion)"
        exit 1
    }
    
    Write-Log -Level "INFO" -Message "Brief Bridge Client starting..."
    Write-Log -Level "INFO" -Message "Server: $ServerUrl"
    Write-Log -Level "INFO" -Message "Client ID: $ClientId"
    Write-Log -Level "INFO" -Message "Client Name: $(if ($ClientName) { $ClientName } else { "PowerShell-Client-$ClientId" })"
    Write-Log -Level "INFO" -Message "Poll Interval: ${PollInterval}s"
    Write-Log -Level "INFO" -Message "PowerShell Version: $($PSVersionTable.PSVersion)"
    
    if ($LogPath) {
        Write-Log -Level "INFO" -Message "Logging to: $LogPath"
    }
    
    # Test server connectivity
    if (-not (Test-ServerConnectivity)) {
        Write-Log -Level "ERROR" -Message "Cannot connect to server. Exiting."
        exit 1
    }
    
    # Register client
    if (-not (Register-Client)) {
        Write-Log -Level "ERROR" -Message "Failed to register client. Exiting."
        exit 1
    }
    
    # Start main polling loop
    Start-CommandPolling
    
    Write-Log -Level "INFO" -Message "Client shutdown complete"
}

# Execute main function
Main