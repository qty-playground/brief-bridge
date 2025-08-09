# Brief Bridge Test Kits

This directory contains client scripts and testing utilities for manual QA verification of the Brief Bridge system.

## Directory Structure

```
testkits/
├── clients/                    # Client scripts for different platforms
│   ├── brief-client.sh        # Linux/macOS client script
│   └── brief-client.ps1       # Windows PowerShell client script (future)
├── scenarios/                  # Test scenarios and data
└── README.md                  # This file
```

## Client Usage

### Linux/macOS Client
```bash
./testkits/clients/brief-client.sh --server http://localhost:8000 --client-id test-client-001
```

### Features
- Automatic client registration with server
- Continuous polling for pending commands  
- Command execution with result reporting
- Graceful error handling and logging
- Configurable polling intervals

## Testing Scenarios

See individual scenario files in `scenarios/` directory for specific test cases and expected behaviors.