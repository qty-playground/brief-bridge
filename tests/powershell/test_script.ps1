# Simple PowerShell test script for Brief Bridge
# This script demonstrates basic PowerShell functionality

param(
    [string]$Message = "Hello from Brief Bridge PowerShell Test"
)

# Display version information
Write-Output "PowerShell Version: $($PSVersionTable.PSVersion)"
Write-Output "Platform: $($PSVersionTable.Platform)"

# Display the message
Write-Output $Message

# Test basic operations
$numbers = @(1, 2, 3, 4, 5)
$sum = ($numbers | Measure-Object -Sum).Sum
Write-Output "Sum of numbers 1-5: $sum"

# Test object creation
$testObject = [PSCustomObject]@{
    Name = "Brief Bridge Test"
    Version = "1.0.0"
    Date = Get-Date
    Success = $true
}

Write-Output "Test Object: $($testObject | ConvertTo-Json -Compress)"

# Exit successfully
exit 0