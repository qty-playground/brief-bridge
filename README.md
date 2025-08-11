# Brief Bridge

A functional tool that bridges AI coding assistants with distributed clients through HTTP polling, featuring client lifecycle management and monitoring.

## Real-World Example

You're developing on macOS with Claude Code, but need to write PowerShell 5.1 compatible scripts:

1. **Start a Windows client**: Run the one-liner on your Windows machine
2. **Ask Claude Code**: "Test this PowerShell script on Windows"
3. **Claude executes remotely**: Gets real PowerShell 5.1 output and compatibility issues
4. **Iterate faster**: Fix issues without leaving your macOS environment

## Quick Start

### Installation

```bash
pipx install brief-bridge
```

### Start the Server

```bash
brief-bridge
```

This will start Brief Bridge on port 8000 with comprehensive API documentation.

### Setup Public Tunnel (for Remote Clients)

```bash
curl -X POST http://localhost:8000/tunnel/setup -H "Content-Type: application/json" -d '{"provider": "ngrok"}'
```

### For AI Assistants

Tell your AI assistant: **"Please visit http://localhost:8000/ to see what APIs are available"**

**Important**: AI assistants should use `localhost` URLs for all API calls. Only remote clients need tunnel URLs for installation.

### Client Installation

**Windows PowerShell (Basic)**
```powershell
irm https://your-tunnel-url/install.ps1 | iex
```

**Windows PowerShell (with Custom Timeout)**
```powershell
irm "https://your-tunnel-url/install.ps1?client_id=my-client&idle_timeout_minutes=5" | iex
```

**Linux/macOS Bash**
```bash
curl -sSL https://your-tunnel-url/install.sh | bash
```

## Key Features

- **Client Lifecycle Management**
  - Configurable idle timeout (default 10 minutes)
  - Auto-stop after 3 consecutive connection failures
  - Server-side terminate command support
  - UUID-based unique temporary files
- **Real-time Monitoring**
  - Client activity tracking with `last_seen` timestamps
  - Live status monitoring and health checks
- **Zero Installation** - Pure shell scripts with automatic cleanup
- **Firewall Friendly** - Works behind corporate firewalls via tunneling
- **Multi-Platform** - Windows PowerShell, Linux/macOS Bash support

## Architecture

```
AI Assistant → HTTP Server (localhost) → Public Tunnel → Remote Clients (polling)
```

**Design Philosophy**: Simplified Architecture with BDD testing
- Fast development with clear separation of concerns  
- Use cases handle business logic
- Repositories manage data persistence
- Comprehensive BDD test coverage with pytest-bdd

## API

```bash
GET  /                        # Complete API guide for AI assistants  
GET  /docs                    # Interactive Swagger documentation
POST /tunnel/setup            # Setup ngrok tunnel for remote access
GET  /tunnel/status           # Check tunnel status and public URL
POST /commands/submit         # Submit command to client
GET  /commands/              # List all commands with execution results
POST /commands/poll           # Client polling endpoint (used by clients)
GET  /commands/client/{id}    # Get pending commands for specific client
GET  /clients/               # List registered clients with last_seen timestamps
POST /clients/register        # Register new client (used by install scripts)
GET  /install.ps1            # PowerShell client install script with parameters
GET  /install.sh             # Bash client install script
```

### PowerShell Install Script Parameters

```bash
GET /install.ps1?client_id=my-client&idle_timeout_minutes=5&poll_interval=3&debug=true
```

**Available Parameters:**
- `client_id` - Custom client identifier (defaults to hostname)
- `client_name` - Human-readable client name
- `idle_timeout_minutes` - Auto-shutdown timeout in minutes (default: 10)
- `poll_interval` - Command polling interval in seconds (default: 5)  
- `debug` - Enable verbose debug output (default: false)

### Command Submission

Simple command submission via JSON:

```json
{
  "target_client_id": "my-client",
  "command_content": "Get-Process | Where-Object {$_.ProcessName -like 'powershell*'}",
  "command_type": "shell"
}
```

## Client Lifecycle Management

Brief Bridge includes client lifecycle management:

### Automatic Timeout Protection
- **Idle Timeout**: Clients automatically terminate after configurable period (default: 10 minutes)
- **Connection Failure Protection**: Auto-stop after 3 consecutive HTTP 404 errors
- **Server Terminate**: Graceful shutdown via `terminate` command from server

### Monitoring Features
- **Real-time Status**: `last_seen` timestamps for all clients
- **Health Monitoring**: Track client activity and connection health
- **Unique Sessions**: UUID-based temporary files prevent conflicts

### Example: Send Terminate Command
```bash
curl -X POST http://localhost:8000/commands/submit \
  -H "Content-Type: application/json" \
  -d '{"target_client_id": "my-client", "command_content": "terminate", "command_type": "shell"}'
```

## Use Cases

- **Cross-platform Development**: Write PowerShell on macOS, test on Windows
- **Production Debugging**: Execute diagnostic commands on live systems  
- **Automated Testing**: Run tests across heterogeneous environments
- **System Administration**: Manage distributed infrastructure remotely
- **Compliance Auditing**: Collect system information across multiple machines

## Development

Brief Bridge uses systematic BDD (Behavior-Driven Development) with AI-assisted implementation.

### For Developers
See **[Development Guide](prompts/README.md)** for complete BDD implementation workflow.

Quick start: `@prompts/00-overview.md.prompt`

### Development Server
```bash
brief-bridge --reload --external
```

## Status

✅ **Functional MVP** - Core features working with client lifecycle management, monitoring, and tunnel support

## License

[MIT](LICENSE)