# Brief Bridge

A lightweight tool that bridges AI coding assistants with distributed clients through HTTP polling.

## Real-World Example

You're developing on macOS with Claude Code, but need to write PowerShell 5.1 compatible scripts:

1. **Start a Windows client**: Run the one-liner on your Windows machine
2. **Ask Claude Code**: "Test this PowerShell script on Windows"
3. **Claude executes remotely**: Gets real PowerShell 5.1 output and compatibility issues
4. **Iterate faster**: Fix issues without leaving your macOS environment

## Quick Start

### Installation with pipx (Recommended)

```bash
pipx install brief-bridge
```

### Start the Server

```bash
brief-bridge
```

This will start Brief Bridge on port 2266 with helpful guidance for AI assistants.

### For AI Assistants

Tell your AI assistant: **"Please visit http://localhost:2266/ to see what APIs are available"**

**Important**: AI assistants should use `localhost` URLs for all API calls. Only remote clients need tunnel URLs for installation.

### Client Installation

**Windows PowerShell**
```powershell
irm http://localhost:2266/install.ps1 | iex
```

**Linux/macOS Bash**
```bash
curl -sSL http://localhost:2266/install.sh | bash
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

## 🏗️ Development Architecture Choice

Brief Bridge supports **two architecture approaches** for implementation:

### 🚀 **Simplified Architecture** (Recommended)
**Best for**: Most projects, rapid development, learning BDD
- Pattern: `Framework ↔ UseCase ↔ Entity/Repository`
- Faster development with good separation of concerns
- Full BDD support with ScenarioContext phase management

### 🏛️ **Clean Architecture** 
**Best for**: Complex business logic, long-term strategic systems  
- Pattern: `Domain → Application → Infrastructure`
- Maximum flexibility and maintainability
- Full BDD support with ScenarioContext phase management

### 🎯 Quick Decision
**Choose Simplified if**:
- Small-medium project (< 10 business entities)
- Team new to Clean Architecture
- Need fast delivery

**Choose Clean Architecture if**:
- Complex business rules and workflows
- Long-term strategic application
- Team experienced with layered architecture

> **Both architectures include the same BDD testing approach** with pytest-bdd, ScenarioContext phase management (GIVEN→WHEN→THEN enforcement), and Screaming Architecture test organization.

## API

```bash
GET  /                     # Complete API guide for AI assistants
GET  /docs                 # Interactive Swagger documentation
POST /tunnel/setup         # Setup ngrok tunnel  
POST /commands/submit      # Submit command to client
GET  /commands/            # List all commands and results
GET  /clients/             # List registered clients
GET  /install.ps1          # PowerShell client install script
```

### CLI Options

```bash
brief-bridge --help        # Show all options
brief-bridge --port 8080   # Custom port
brief-bridge --external    # Accept external connections
brief-bridge --reload      # Development mode with auto-reload
```

## Use Cases

- **Cross-platform development**: Write PowerShell on macOS, test on Windows
- **Real environment testing**: Debug issues in actual target environments  
- **Runtime context collection**: Get OS-specific logs, error messages, system info
- **Compatibility verification**: Ensure scripts work across different OS versions

## Development

Brief Bridge is developed using BDD (Behavior-Driven Development), Clean Architecture, and Test-Driven Development methodologies.

### For Developers
- **[Development Guide](docs/DEVELOPMENT.md)** - Comprehensive development documentation
- **[Domain Model](docs/domain-model.md)** - Business entities and rules
- **[Architecture Structure](docs/clean-architecture-structure.md)** - Code organization
- **[User Stories](docs/user-stories/)** - Technical specifications

### For AI Assistants  
- **[Implementation Prompts](prompts/README.md)** - Systematic BDD implementation guide
- **Quick Start**: `@prompts/00-overview.md.prompt`

### Project Structure
```
brief-bridge/
├── brief_bridge/           # Clean Architecture implementation
│   ├── domain/             # Business logic
│   ├── application/        # Use cases  
│   └── infrastructure/     # External concerns
├── tests/                  # BDD tests with pytest-bdd
├── docs/                   # Design documentation
└── prompts/                # AI assistant implementation guides
```

## Status

🚧 **MVP in development** - Core polling mechanism and command execution

## License

[MIT](LICENSE)