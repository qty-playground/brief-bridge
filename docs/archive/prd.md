# Brief Bridge

A lightweight development companion tool that enables AI coding assistants to manage distributed clients in intranet environments through HTTP polling.

## Design Philosophy

Uses polling mechanism to ensure maximum compatibility - clients only need shell built-in HTTP functionality with no additional tools required.

## What It Does

### Typical Use Cases
- **Heterogeneous Development**: AI coding assistants test and verify code across different OS/architectures
- **Runtime Context Collection**: AI gathers real execution environment status, logs, error messages
- **Cross-Platform Debugging**: AI reproduces and diagnoses issues across multiple environments
- **Development Environment Sync**: AI assists in synchronizing dev environments and configurations between machines

### User Experience
```powershell
# Windows - One-line client startup
& ([scriptblock]::Create((Invoke-WebRequest 'https://your-public-endpoint.com/client.ps1').Content)) -Start
```

```bash
# Linux/macOS - One-line client startup
curl -sSL https://your-public-endpoint.com/client.sh | bash
```

Once started, clients automatically begin polling the server for tasks dispatched by AI coding assistants.

## Architecture

### Component Responsibilities

**AI Coding Assistant**
- Analyzes development requirements, generates specific execution commands
- Parses runtime context, provides intelligent suggestions

**HTTP Server** 
- Manages client registration and status
- Command queue and result collection
- Provides AI Coding Assistant API interface

**Public Endpoint**
- Network tunneling and routing
- Provides stable external access point

**Client Nodes**
- Environment detection and command execution
- Runtime context collection and reporting
- Lightweight polling and status sync

```
AI Coding Assistant <-> HTTP Server <-> Public Endpoint <-> Client (Polling)
```

### Implementation (MVP)
- **HTTP Server**: FastAPI (memory-based storage)
- **Client**: Pure Shell (PowerShell `Invoke-WebRequest`, curl + bash)
- **Public Endpoint**: ngrok, Cloudflare Tunnel, etc.
- **Communication**: HTTP RESTful API

## MVP Core Features

### Core Validation: AI Coding Assistant Command Execution Loop
Complete flow: AI Coding Assistant sends command → Client executes → Returns result

### Server Side
- **Client Registration**: Records online clients
- **Command Distribution**: Receives AI commands, pushes to specified clients  
- **Result Collection**: Receives and returns execution results to AI
- **Basic APIs**: `/register`, `/commands`, `/results`

### Client Side  
- **Polling**: Periodically checks for new commands
- **Execution**: Executes shell commands and captures output
- **Reporting**: Returns results to server
- **One-line Startup**: Direct execution, no installation required

### AI Integration
- **Self-learning API**: GET `/` - Provides usage instructions for AI to learn bridge usage
- **Command API**: POST `/commands` - Submit commands, GET `/commands/{id}` - Query results
- **Basic Commands**: Supports common shell commands (`ls`, `pwd`, `echo`, etc.)

## API Reference

#### Core APIs
```
GET  /                     # AI gets bridge usage instructions
POST /clients/register     # Client registration
GET  /clients/{id}/commands # Client gets commands  
POST /clients/{id}/results  # Client returns results
POST /commands             # AI submits new commands
GET  /commands/{id}        # AI queries execution results
GET  /clients              # AI queries available clients
```

## Development Roadmap

### Phase 1: Core Components
- HTTP Server basic architecture
- Client polling mechanism
- Command execution and result return
- One-line startup script

### Phase 2: Integration Layer  
- AI Coding Assistant API integration
- Complete Client-Server integration
- Basic error handling

### Phase 3: Enhancement
- Web dashboard 
- Security mechanisms (API token)
- Retry logic and stability improvements

## Success Metrics

- **Startup time** < 1 minute
- **Client registration success rate** > 95%
- **Command execution success rate** > 90%
- **Polling latency** < 30 seconds

## Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

## License

MIT License