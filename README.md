# Brief Bridge

A lightweight tool that bridges AI coding assistants with distributed clients through HTTP polling.

## Real-World Example

You're developing on macOS with Claude Code, but need to write PowerShell 5.1 compatible scripts:

1. **Start a Windows client**: Run the one-liner on your Windows machine
2. **Ask Claude Code**: "Test this PowerShell script on Windows"
3. **Claude executes remotely**: Gets real PowerShell 5.1 output and compatibility issues
4. **Iterate faster**: Fix issues without leaving your macOS environment

## Quick Start

**Windows**
```powershell
& ([scriptblock]::Create((Invoke-WebRequest 'https://your-endpoint.com/client.ps1').Content))
```

**Linux/macOS**
```bash
curl -sSL https://your-endpoint.com/client.sh | bash
```

## What it does

- AI coding assistants execute commands on remote machines
- Zero installation - pure shell scripts
- Works behind firewalls via tunneling
- Collect runtime context from heterogeneous environments

## Architecture

```
AI Assistant → HTTP Server → Public Endpoint → Clients (polling)
```

## API

```bash
GET  /                    # Usage instructions
POST /commands           # Submit command  
GET  /commands/{id}      # Get result
GET  /clients            # List clients
```

## Use Cases

- **Cross-platform development**: Write PowerShell on macOS, test on Windows
- **Real environment testing**: Debug issues in actual target environments  
- **Runtime context collection**: Get OS-specific logs, error messages, system info
- **Compatibility verification**: Ensure scripts work across different OS versions

## Status

🚧 **MVP in development** - Core polling mechanism and command execution

## License

MIT