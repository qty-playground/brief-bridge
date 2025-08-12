# Scripts Directory

This directory contains utility scripts for the Brief Bridge project.

## PowerShell Container Scripts

### build-powershell-image.sh

Builds a clean PowerShell container image for testing the Brief Bridge Editor PowerShell module.

**Usage:**
```bash
./scripts/build-powershell-image.sh
```

**What it does:**
- 🧹 Cleans up existing PowerShell images to ensure fresh build
- 📋 Automatically detects the current architecture (arm64/amd64) 
- 🔨 Builds a new PowerShell container with curl and jq installed
- 🧪 Tests basic PowerShell functionality to verify the image works
- ✅ Provides clear success/failure feedback with colored output

**Requirements:**
- Docker must be installed and running
- The `tests/Dockerfile` must exist in the project root

**Output:**
- Creates a Docker image tagged as `powershell-image:latest`
- Shows image details and size information
- Runs a basic PowerShell test to verify functionality

**Example output:**
```
🐳 Building PowerShell container image...
📋 Detected architecture: arm64
🧹 Cleaning up existing PowerShell images...
🔨 Building fresh PowerShell image...
✅ PowerShell image built successfully!
📦 Image details:
REPOSITORY         TAG       IMAGE ID       CREATED          SIZE
powershell-image   latest    41703b97c5bd   2 seconds ago    311MB
🧪 Testing basic PowerShell functionality...
PowerShell 7.4.2 is working!
✅ PowerShell container is working correctly!
🎉 Build complete! You can now run tests with: python -m pytest tests/test_powershell_container.py
```

**Troubleshooting:**
- If the build fails, check that Docker is running
- If you see platform warnings, the script will still work but may use emulation
- The built image includes PowerShell 7.4.2 with curl and jq utilities

**Integration with Tests:**
After running this script, you can execute the PowerShell module tests:
```bash
python -m pytest tests/test_powershell_container.py -v
```

This will test the Brief Bridge Editor PowerShell module by:
- Mounting the module files into the container
- Importing the PowerShell module
- Running the `Get-BriefBridgeVersion` cmdlet
- Verifying all regression tests pass