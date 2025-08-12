#!/bin/bash

# Build PowerShell Container Image for Brief Bridge Editor Testing
# This script builds a clean PowerShell container image for running tests

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

IMAGE_NAME="powershell-image"
DOCKERFILE_PATH="tests/Dockerfile"

echo -e "${YELLOW}🐳 Building PowerShell container image...${NC}"

# Check if Dockerfile exists
if [ ! -f "$DOCKERFILE_PATH" ]; then
    echo -e "${RED}❌ Error: Dockerfile not found at $DOCKERFILE_PATH${NC}"
    exit 1
fi

# Get current architecture
ARCH=$(uname -m)
echo -e "${YELLOW}📋 Detected architecture: $ARCH${NC}"

# Clean up existing images to ensure fresh build
echo -e "${YELLOW}🧹 Cleaning up existing PowerShell images...${NC}"
docker image rm $IMAGE_NAME 2>/dev/null || true
docker image rm mcr.microsoft.com/powershell:latest 2>/dev/null || true

# Build the image with fresh cache
echo -e "${YELLOW}🔨 Building fresh PowerShell image...${NC}"
docker build \
    --no-cache \
    --platform linux/$ARCH \
    -f $DOCKERFILE_PATH \
    -t $IMAGE_NAME \
    tests/

# Verify the build was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PowerShell image built successfully!${NC}"
    
    # Show image info
    echo -e "${YELLOW}📦 Image details:${NC}"
    docker image ls $IMAGE_NAME
    
    # Test basic functionality
    echo -e "${YELLOW}🧪 Testing basic PowerShell functionality...${NC}"
    if docker run --rm $IMAGE_NAME pwsh -c 'Write-Output "PowerShell $($PSVersionTable.PSVersion) is working!"'; then
        echo -e "${GREEN}✅ PowerShell container is working correctly!${NC}"
    else
        echo -e "${RED}⚠️  Warning: PowerShell container may have issues${NC}"
    fi
else
    echo -e "${RED}❌ Failed to build PowerShell image${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Build complete! You can now run tests with: python -m pytest tests/test_powershell_container.py${NC}"