FROM mcr.microsoft.com/powershell:latest

# Set working directory
WORKDIR /app

# Install additional tools if needed
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Set PowerShell as the default shell
SHELL ["pwsh", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# Default command
CMD ["pwsh"]