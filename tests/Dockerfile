FROM mcr.microsoft.com/powershell/test-deps:ubuntu-18.04

# Set working directory
WORKDIR /app

# Set PowerShell as the default shell for subsequent RUN commands
SHELL ["pwsh", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# Install Pester testing framework globally
RUN Install-Module -Name Pester -Force -SkipPublisherCheck -Scope AllUsers; \
    Write-Host "Pester version: $(Get-Module -ListAvailable -Name Pester | Select-Object -ExpandProperty Version)"

# Verify Pester installation
RUN Import-Module Pester; \
    Write-Host "Pester successfully imported and ready for testing"

# Default command
CMD ["pwsh"]