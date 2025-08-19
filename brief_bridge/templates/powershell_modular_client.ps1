# Brief Bridge Modular PowerShell HTTP Polling Client
# Compatible with PowerShell 5.1 and later
# Enhanced with modular architecture and built-in functions

param(
    [string]$ServerUrl = "http://localhost:8000",
    [Parameter(Mandatory=$true)][string]$ClientId,
    [string]$ClientName = "Modular PowerShell Client",
    [int]$PollInterval = 5,
    [int]$IdleTimeoutMinutes = 10,
    [switch]$DebugMode
)

#region Core Configuration Module
$Global:BriefBridgeConfig = @{
    ServerUrl = $ServerUrl
    ClientId = $ClientId
    ClientName = $ClientName
    PollInterval = $PollInterval
    IdleTimeoutMinutes = $IdleTimeoutMinutes
    DebugMode = $DebugMode.IsPresent
    
    # API Configuration
    ApiBase = $ServerUrl
    MaxRetries = 3
    RetryDelay = 5
    MaxConsecutive404s = 3
    IdleTimeoutSeconds = $IdleTimeoutMinutes * 60
    
    # State tracking
    LastCommandTime = Get-Date
    Consecutive404Count = 0
    ShouldTerminate = $false
    ConsecutiveErrors = 0
    MaxConsecutiveErrors = 5
}
#endregion

#region Utility Functions Module
function Write-BriefBridgeLog {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Color = "White"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logPrefix = "[$timestamp] [$Level]"
    
    Write-Host "$logPrefix $Message" -ForegroundColor $Color
    
    if ($Global:BriefBridgeConfig.DebugMode -and $Level -eq "DEBUG") {
        Write-Host $Message -ForegroundColor DarkGray
    }
}

function Get-BriefBridgeSystemInfo {
    """Built-in function: Get comprehensive system information"""
    
    $systemInfo = [ordered]@{
        Hostname = $env:COMPUTERNAME ?? $env:HOSTNAME ?? "Unknown"
        Username = $env:USERNAME ?? $env:USER ?? "Unknown"
        OS = if ($IsWindows) { "Windows" } elseif ($IsLinux) { "Linux" } elseif ($IsMacOS) { "macOS" } else { "Unknown" }
        PowerShellVersion = $PSVersionTable.PSVersion.ToString()
        WorkingDirectory = (Get-Location).Path
        ProcessId = $PID
        ClientId = $Global:BriefBridgeConfig.ClientId
        ServerUrl = $Global:BriefBridgeConfig.ServerUrl
        UptimeSeconds = [math]::Round(((Get-Date) - [System.Diagnostics.Process]::GetCurrentProcess().StartTime).TotalSeconds, 2)
    }
    
    return $systemInfo | ConvertTo-Json -Depth 2
}

function Get-BriefBridgeBuiltInCommands {
    """Built-in function: List all available built-in commands"""
    
    $commands = @(
        @{ Name = "bb-system-info"; Description = "Get comprehensive system information" }
        @{ Name = "bb-commands"; Description = "List all built-in commands" }
        @{ Name = "bb-config"; Description = "Show current client configuration" }
        @{ Name = "bb-status"; Description = "Show client status and statistics" }
        @{ Name = "bb-test-connection"; Description = "Test connection to server" }
        @{ Name = "bb-ls"; Description = "Enhanced directory listing" }
        @{ Name = "bb-pwd"; Description = "Show current directory with additional info" }
        @{ Name = "bb-env"; Description = "Show environment variables" }
        @{ Name = "terminate"; Description = "Gracefully terminate the client" }
    )
    
    return $commands | ConvertTo-Json
}

function Get-BriefBridgeConfig {
    """Built-in function: Show current configuration"""
    return $Global:BriefBridgeConfig | ConvertTo-Json -Depth 2
}

function Get-BriefBridgeStatus {
    """Built-in function: Show client status and statistics"""
    
    $uptime = ((Get-Date) - [System.Diagnostics.Process]::GetCurrentProcess().StartTime)
    $idleTime = ((Get-Date) - $Global:BriefBridgeConfig.LastCommandTime)
    
    $status = [ordered]@{
        Status = if ($Global:BriefBridgeConfig.ShouldTerminate) { "Terminating" } else { "Running" }
        UptimeFormatted = "$($uptime.Hours)h $($uptime.Minutes)m $($uptime.Seconds)s"
        IdleTimeFormatted = "$([math]::Round($idleTime.TotalMinutes, 1)) minutes"
        IdleTimeoutMinutes = $Global:BriefBridgeConfig.IdleTimeoutMinutes
        Consecutive404s = $Global:BriefBridgeConfig.Consecutive404Count
        ConsecutiveErrors = $Global:BriefBridgeConfig.ConsecutiveErrors
        DebugMode = $Global:BriefBridgeConfig.DebugMode
        LastCommandTime = $Global:BriefBridgeConfig.LastCommandTime.ToString("yyyy-MM-dd HH:mm:ss")
    }
    
    return $status | ConvertTo-Json -Depth 2
}

function Test-BriefBridgeConnection {
    """Built-in function: Test connection to server"""
    
    try {
        $testUrl = "$($Global:BriefBridgeConfig.ApiBase)/health"
        $response = Invoke-RestMethod -Uri $testUrl -Method GET -TimeoutSec 10
        
        return @{
            success = $true
            server_url = $Global:BriefBridgeConfig.ApiBase
            response_time_ms = (Measure-Command { Invoke-RestMethod -Uri $testUrl -Method GET -TimeoutSec 10 }).TotalMilliseconds
            server_response = $response
        } | ConvertTo-Json
    }
    catch {
        return @{
            success = $false
            server_url = $Global:BriefBridgeConfig.ApiBase
            error = $_.Exception.Message
        } | ConvertTo-Json
    }
}

function Get-BriefBridgeEnhancedLS {
    """Built-in function: Enhanced directory listing"""
    param([string]$Path = ".")
    
    try {
        $items = Get-ChildItem -Path $Path | Sort-Object Name
        $result = @{
            current_directory = (Resolve-Path $Path).Path
            total_items = $items.Count
            items = @()
        }
        
        foreach ($item in $items) {
            $result.items += @{
                name = $item.Name
                type = if ($item.PSIsContainer) { "Directory" } else { "File" }
                size = if (-not $item.PSIsContainer) { $item.Length } else { $null }
                last_modified = $item.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
            }
        }
        
        return $result | ConvertTo-Json -Depth 3
    }
    catch {
        return @{ error = $_.Exception.Message } | ConvertTo-Json
    }
}

function Get-BriefBridgeEnhancedPWD {
    """Built-in function: Enhanced current directory info"""
    
    $currentDir = Get-Location
    try {
        $dirInfo = Get-Item $currentDir.Path
        $childItems = Get-ChildItem $currentDir.Path
        
        return @{
            current_directory = $currentDir.Path
            full_path = $dirInfo.FullName
            creation_time = $dirInfo.CreationTime.ToString("yyyy-MM-dd HH:mm:ss")
            last_access = $dirInfo.LastAccessTime.ToString("yyyy-MM-dd HH:mm:ss")
            child_count = $childItems.Count
            files_count = ($childItems | Where-Object { -not $_.PSIsContainer }).Count
            directories_count = ($childItems | Where-Object { $_.PSIsContainer }).Count
        } | ConvertTo-Json
    }
    catch {
        return @{
            current_directory = $currentDir.Path
            error = $_.Exception.Message
        } | ConvertTo-Json
    }
}

function Get-BriefBridgeEnvironment {
    """Built-in function: Get environment variables"""
    
    $envVars = [ordered]@{}
    Get-ChildItem Env: | ForEach-Object {
        $envVars[$_.Name] = $_.Value
    }
    
    return @{
        environment_variables = $envVars
        count = $envVars.Count
    } | ConvertTo-Json -Depth 2
}
#endregion

#region HTTP Request Module
function Invoke-BriefBridgeHttpRequest {
    param(
        [string]$Uri,
        [string]$Method = "GET",
        [hashtable]$Body = $null,
        [int]$Retries = $Global:BriefBridgeConfig.MaxRetries
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
            $Global:BriefBridgeConfig.Consecutive404Count = 0
            return $response
        }
        catch {
            $statusCode = $null
            if ($_.Exception.Response) {
                $statusCode = [int]$_.Exception.Response.StatusCode
            }
            
            # Track 404s specifically
            if ($statusCode -eq 404) {
                $Global:BriefBridgeConfig.Consecutive404Count++
                Write-BriefBridgeLog "HTTP 404 - Not Found (consecutive: $($Global:BriefBridgeConfig.Consecutive404Count)/$($Global:BriefBridgeConfig.MaxConsecutive404s))" "WARN" "Yellow"
                
                # Check if we've hit the limit
                if (Test-BriefBridge404Limit) {
                    $Global:BriefBridgeConfig.ShouldTerminate = $true
                    throw "Maximum consecutive 404s reached"
                }
            }
            
            Write-BriefBridgeLog "Request failed (attempt $($i + 1)/$Retries): $($_.Exception.Message)" "WARN" "Yellow"
            if ($i -eq $Retries - 1) {
                throw $_.Exception
            }
            Start-Sleep -Seconds $Global:BriefBridgeConfig.RetryDelay
        }
    }
}
#endregion

#region Lifecycle Management Module
function Test-BriefBridgeIdleTimeout {
    $idleTime = ((Get-Date) - $Global:BriefBridgeConfig.LastCommandTime).TotalSeconds
    
    if ($idleTime -ge $Global:BriefBridgeConfig.IdleTimeoutSeconds) {
        Write-BriefBridgeLog "Idle timeout reached ($([math]::Round($idleTime, 1))s >= $($Global:BriefBridgeConfig.IdleTimeoutSeconds)s)" "LIFECYCLE" "Yellow"
        Write-BriefBridgeLog "Client terminating due to inactivity" "LIFECYCLE" "Red"
        return $true
    }
    
    if ($Global:BriefBridgeConfig.DebugMode) {
        Write-BriefBridgeLog "Idle time: $([math]::Round($idleTime, 1))s / $($Global:BriefBridgeConfig.IdleTimeoutSeconds)s" "DEBUG" "DarkGray"
    }
    
    return $false
}

function Test-BriefBridge404Limit {
    if ($Global:BriefBridgeConfig.Consecutive404Count -ge $Global:BriefBridgeConfig.MaxConsecutive404s) {
        Write-BriefBridgeLog "Maximum consecutive 404s reached ($($Global:BriefBridgeConfig.Consecutive404Count))" "LIFECYCLE" "Yellow"
        Write-BriefBridgeLog "Client terminating due to server unavailability" "LIFECYCLE" "Red"
        return $true
    }
    return $false
}
#endregion

#region Command Execution Module
function Invoke-BriefBridgeCommand {
    param(
        [string]$Command,
        [int]$TimeoutSeconds = 30
    )
    
    $startTime = Get-Date
    
    try {
        # Check for terminate command
        if ($Command.Trim() -eq "terminate") {
            Write-BriefBridgeLog "Terminate command received from server" "LIFECYCLE" "Yellow"
            Write-BriefBridgeLog "Client terminating gracefully..." "LIFECYCLE" "Red"
            $Global:BriefBridgeConfig.ShouldTerminate = $true
            
            return @{
                success = $true
                output = "Client terminating gracefully on server request"
                error = $null
                execution_time = 0.1
            }
        }
        
        # Check for built-in commands
        $builtInResult = Invoke-BriefBridgeBuiltInCommand -Command $Command
        if ($builtInResult) {
            return $builtInResult
        }
        
        Write-BriefBridgeLog $Command "EXEC" "Yellow"
        
        # Update last command time for idle tracking
        $Global:BriefBridgeConfig.LastCommandTime = Get-Date
        
        # Execute command and capture output
        $output = Invoke-Expression $Command 2>&1 | Out-String
        
        $executionTime = ((Get-Date) - $startTime).TotalSeconds
        
        Write-BriefBridgeLog "Execution time: $([math]::Round($executionTime, 2))s" "SUCCESS" "Green"
        
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
        
        Write-BriefBridgeLog $errorMessage "ERROR" "Red"
        
        return @{
            success = $false
            output = $null
            error = $errorMessage
            execution_time = $executionTime
        }
    }
}

function Invoke-BriefBridgeBuiltInCommand {
    param([string]$Command)
    
    $cmd = $Command.Trim()
    $startTime = Get-Date
    
    try {
        $output = switch ($cmd) {
            "bb-system-info" { Get-BriefBridgeSystemInfo }
            "bb-commands" { Get-BriefBridgeBuiltInCommands }
            "bb-config" { Get-BriefBridgeConfig }
            "bb-status" { Get-BriefBridgeStatus }
            "bb-test-connection" { Test-BriefBridgeConnection }
            "bb-ls" { Get-BriefBridgeEnhancedLS }
            "bb-pwd" { Get-BriefBridgeEnhancedPWD }
            "bb-env" { Get-BriefBridgeEnvironment }
            default { return $null }  # Not a built-in command
        }
        
        $executionTime = ((Get-Date) - $startTime).TotalSeconds
        Write-BriefBridgeLog "Built-in command executed: $cmd" "BUILTIN" "Magenta"
        
        # Update last command time for idle tracking
        $Global:BriefBridgeConfig.LastCommandTime = Get-Date
        
        return @{
            success = $true
            output = $output
            error = $null
            execution_time = $executionTime
        }
    }
    catch {
        $executionTime = ((Get-Date) - $startTime).TotalSeconds
        Write-BriefBridgeLog "Built-in command error: $($_.Exception.Message)" "ERROR" "Red"
        
        return @{
            success = $false
            output = $null
            error = $_.Exception.Message
            execution_time = $executionTime
        }
    }
}
#endregion

#region Client Registration and Communication
function Register-BriefBridgeClient {
    try {
        $body = @{
            client_id = $Global:BriefBridgeConfig.ClientId
            name = $Global:BriefBridgeConfig.ClientName
        }
        
        $response = Invoke-BriefBridgeHttpRequest -Uri "$($Global:BriefBridgeConfig.ApiBase)/clients/register" -Method "POST" -Body $body
        Write-BriefBridgeLog "Client registered successfully" "REGISTER" "Green"
        return $true
    }
    catch {
        Write-BriefBridgeLog "Failed to register client: $($_.Exception.Message)" "ERROR" "Red"
        return $false
    }
}

function Submit-BriefBridgeCommandResult {
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
        
        $response = Invoke-BriefBridgeHttpRequest -Uri "$($Global:BriefBridgeConfig.ApiBase)/commands/result" -Method "POST" -Body $body
        Write-BriefBridgeLog "Submitted result for command $CommandId" "RESULT" "Cyan"
        return $true
    }
    catch {
        Write-BriefBridgeLog "Failed to submit result for command $CommandId : $($_.Exception.Message)" "ERROR" "Red"
        return $false
    }
}

function Get-BriefBridgePendingCommand {
    try {
        $body = @{
            client_id = $Global:BriefBridgeConfig.ClientId
        }
        
        $response = Invoke-BriefBridgeHttpRequest -Uri "$($Global:BriefBridgeConfig.ApiBase)/commands/poll" -Method "POST" -Body $body
        
        if ($response.command_id) {
            Write-BriefBridgeLog "Received command: $($response.command_id)" "POLL" "Magenta"
            return $response
        }
        
        return $null
    }
    catch {
        Write-BriefBridgeLog "Failed to poll for commands: $($_.Exception.Message)" "WARN" "Yellow"
        return $null
    }
}
#endregion

#region Main Client Logic
Write-Host "=== Brief Bridge Modular PowerShell Client ===" -ForegroundColor Green
Write-Host "Server: $($Global:BriefBridgeConfig.ServerUrl)" -ForegroundColor Cyan
Write-Host "Client ID: $($Global:BriefBridgeConfig.ClientId)" -ForegroundColor Cyan
Write-Host "Client Name: $($Global:BriefBridgeConfig.ClientName)" -ForegroundColor Cyan
Write-Host "Poll Interval: $($Global:BriefBridgeConfig.PollInterval) seconds" -ForegroundColor Cyan
Write-Host "Idle Timeout: $($Global:BriefBridgeConfig.IdleTimeoutMinutes) minutes" -ForegroundColor Cyan
Write-Host "Enhanced Features: Modular architecture, Built-in commands, Better error handling" -ForegroundColor Magenta
Write-Host "Built-in commands: bb-system-info, bb-commands, bb-status, bb-test-connection, bb-ls, bb-pwd, bb-env" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Register client
if (-not (Register-BriefBridgeClient)) {
    Write-BriefBridgeLog "Failed to register client. Exiting." "ERROR" "Red"
    exit 1
}

# Main polling loop with lifecycle management
Write-BriefBridgeLog "Starting polling loop..." "INFO" "Green"
Write-BriefBridgeLog "Monitoring idle timeout and server availability..." "LIFECYCLE" "Cyan"

try {
    while ($true -and -not $Global:BriefBridgeConfig.ShouldTerminate) {
        try {
            # Check lifecycle conditions before polling
            if (Test-BriefBridgeIdleTimeout) {
                break
            }
            
            if (Test-BriefBridge404Limit) {
                break
            }
            
            # Poll for pending commands
            $command = Get-BriefBridgePendingCommand
            
            if ($command) {
                # Reset error counter on successful poll
                $Global:BriefBridgeConfig.ConsecutiveErrors = 0
                
                # Execute the command
                $result = Invoke-BriefBridgeCommand -Command $command.command_content -TimeoutSeconds $command.timeout
                
                # Submit the result
                $submitted = Submit-BriefBridgeCommandResult -CommandId $command.command_id -Result $result
                
                if (-not $submitted) {
                    Write-BriefBridgeLog "Failed to submit result, but continuing..." "WARN" "Yellow"
                }
                
                # Check if command triggered termination
                if ($Global:BriefBridgeConfig.ShouldTerminate) {
                    Write-BriefBridgeLog "Termination triggered by command execution" "LIFECYCLE" "Yellow"
                    break
                }
            } else {
                # No commands available, reset error counter
                $Global:BriefBridgeConfig.ConsecutiveErrors = 0
            }
        }
        catch {
            $Global:BriefBridgeConfig.ConsecutiveErrors++
            Write-BriefBridgeLog "Polling error ($($Global:BriefBridgeConfig.ConsecutiveErrors)/$($Global:BriefBridgeConfig.MaxConsecutiveErrors)): $($_.Exception.Message)" "ERROR" "Red"
            
            if ($Global:BriefBridgeConfig.ConsecutiveErrors -ge $Global:BriefBridgeConfig.MaxConsecutiveErrors) {
                Write-BriefBridgeLog "Too many consecutive errors. Exiting." "LIFECYCLE" "Red"
                break
            }
            
            # Check if termination was triggered during error handling
            if ($Global:BriefBridgeConfig.ShouldTerminate) {
                Write-BriefBridgeLog "Termination triggered during error handling" "LIFECYCLE" "Yellow"
                break
            }
        }
        
        # Wait before next poll
        Start-Sleep -Seconds $Global:BriefBridgeConfig.PollInterval
    }
}
catch {
    Write-BriefBridgeLog "Fatal error in main loop: $($_.Exception.Message)" "ERROR" "Red"
}
finally {
    Write-BriefBridgeLog "Client shutting down..." "LIFECYCLE" "Yellow"
    Write-Host "Goodbye!" -ForegroundColor Green
}
#endregion