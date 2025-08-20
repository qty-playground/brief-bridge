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
        $statusCode = $null
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
        }
        
        Write-Error "Failed to submit result for command $CommandId`: $($_.Exception.Message)"
        
        # For ANY error (4xx, 5xx, network issues), submit a hardcoded error result to let AI know something is broken
        Write-Host "[RESULT] Submit failed, sending hardcoded error result" -ForegroundColor Red
        
        try {
            # Determine error message based on status code
            $errorMessage = if ($statusCode) {
                "CLIENT_SUBMIT_ERROR: HTTP $statusCode - Failed to submit original result to server. Original command may have executed successfully but result submission failed."
            } else {
                "CLIENT_SUBMIT_ERROR: Network/Connection failure - Failed to submit original result to server. Original command may have executed successfully but result submission failed."
            }
            
            $errorBody = @{
                command_id = $CommandId
                success = $false
                output = ""
                error = $errorMessage
                execution_time = $Result.execution_time
            }
            
            # Try once more with the error body, no retries
            $headers = @{ "Content-Type" = "application/json" }
            $jsonBody = $errorBody | ConvertTo-Json -Depth 10
            $errorResponse = Invoke-RestMethod -Uri "$ApiBase/commands/result" -Method "POST" -Body $jsonBody -Headers $headers -TimeoutSec 30
            
            Write-Host "[RESULT] Successfully submitted hardcoded error for command $CommandId" -ForegroundColor Yellow
            return $true
        }
        catch {
            Write-Error "Failed to submit hardcoded error result for command $CommandId`: $($_.Exception.Message)"
            # At this point, we've tried everything we can. Return false so the main loop can handle it.
            return $false
        }
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