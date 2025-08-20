# PowerShell Testing Package

This package contains PowerShell-specific tests for the Brief Bridge project, isolated from general project tests to avoid unnecessary dependencies.

## Structure

```
tests/powershell/
├── __init__.py              # Package initialization
├── conftest.py              # PowerShell-specific fixtures
├── test_container.py        # Basic PowerShell container tests
├── test_module.py           # PowerShell functionality and file mounting tests
├── test_script.ps1          # Sample PowerShell script for testing
└── README.md               # This file
```

## Running Tests

### PowerShell Tests Only
```bash
python -m pytest tests/powershell/ -v
```

### All Tests Except PowerShell
```bash
python -m pytest tests/ --ignore=tests/powershell/ -v
```

### All Tests
```bash
python -m pytest tests/ -v
```

## Dependencies

PowerShell tests require additional dependencies that general tests don't need:
- `docker` - For container management
- `testcontainers` - For PowerShell container fixtures

## Prerequisites

1. **Docker**: Must be installed and running
2. **PowerShell Image**: Build with `./scripts/build-powershell-image.sh`

## Test Categories

### Container Tests (`test_container.py`)
- Basic PowerShell container functionality
- PowerShell version verification
- Container environment validation

### Module Tests (`test_module.py`)
- Basic PowerShell functionality testing
- Variable and object operations  
- File mounting and volume access
- PowerShell script execution via mounted files
- Container environment validation

## Fixtures

The `conftest.py` provides PowerShell-specific fixtures:
- `powershell_container`: Ready-to-use PowerShell container with proper error handling

## Benefits of Isolation

1. **Reduced Dependencies**: General tests don't need Docker or testcontainers
2. **Faster CI/CD**: Can run core tests without container overhead
3. **Clear Separation**: PowerShell functionality clearly isolated
4. **Optional Testing**: PowerShell tests can be skipped in environments without Docker