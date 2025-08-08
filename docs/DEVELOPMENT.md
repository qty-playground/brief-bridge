# Brief Bridge Development Guide

## Overview

Brief Bridge is a lightweight tool that enables AI coding assistants to execute commands on remote clients through HTTP polling. This guide covers the complete development approach using BDD (Behavior-Driven Development), simplified architecture (Framework ↔ UseCase ↔ Entity/Repository), and Test-Driven Development.

## Project Structure

```
brief-bridge/
├── README.md                           # Project overview and quick start
├── setup.py                           # Python package configuration
├── brief_bridge/                       # Main application (Simplified Architecture)
│   ├── entities/                       # Business entities (Client, Command, etc.)
│   ├── use_cases/                      # Use cases with dependency injection
│   ├── repositories/                   # Repository concrete implementations
│   └── web/                            # FastAPI web layer
├── tests/                              # BDD tests using pytest-bdd
│   ├── {feature_name}/                 # Per-feature test directories
│   │   ├── story.feature              # Gherkin feature file
│   │   ├── test_{feature_name}.py     # Step wrapper file
│   │   ├── given_*.py                 # Given step modules (Command Pattern)
│   │   ├── when_*.py                  # When step modules (Command Pattern)
│   │   └── then_*.py                  # Then step modules (Command Pattern)
│   └── conftest.py                     # pytest configuration + TestContext
├── docs/                               # Design documentation
│   ├── DEVELOPMENT.md                  # This file
│   ├── domain-model.md                 # Domain model with UML
│   ├── clean-architecture-structure.md # Simplified architecture design
│   ├── prd.md                          # Product requirements
│   └── user-stories/                   # Technical user stories
│       ├── submit_command_use_case.md
│       ├── register_client_use_case.md
│       └── ...
└── prompts/                            # AI assistant implementation prompts
    ├── README.md                       # Prompt usage guide
    ├── 00-overview.md.prompt           # Simplified architecture methodology
    ├── 01-user-stories-to-features.md.prompt
    ├── 02-walking-skeleton.md.prompt
    ├── 03-tdd-red-green-refactor.md.prompt
    ├── 04-iteration-cycle.md.prompt
    ├── validation/                     # Quality validation prompts
    │   ├── domain-model-check.md.prompt
    │   ├── clean-architecture-check.md.prompt
    │   └── test-responsibility-check.md.prompt
    └── reference/                      # Quick reference prompts
        ├── pytest-commands.md.prompt
        └── do-dont-rules.md.prompt
```

## Development Philosophy

### BDD (Behavior-Driven Development)
- **Business-focused**: All tests written in business language using Gherkin
- **Outside-in**: Start with user requirements, work inward to implementation
- **Specification by example**: Concrete scenarios define system behavior

### Simplified Architecture
- **Framework ↔ UseCase ↔ Entity/Repository**: Simple three-layer approach
- **Dependency injection**: External dependencies injected into UseCases
- **Testability focus**: Architecture serves testing, not theoretical purity

### Test-Driven Development
- **Red-Green-Refactor**: Systematic development cycle
- **One scenario at a time**: Focus on single behavior implementation
- **Quality through refactoring**: Continuous code quality improvement

## Core Domain Model

### Entities
- **Client**: Remote machine that can execute commands
- **Command**: Task submitted for execution on a client
- **ExecutionResult**: Output from command execution

### Simple Data Structures
- **Client ID**: String identifier for clients
- **Command ID**: String identifier for commands  
- **Client Info**: Dict with system information (OS, architecture, version)
- **Status**: String values ("ONLINE"/"OFFLINE")
- **Availability**: String values ("IDLE"/"BUSY")

### Business Rules
- **client.registration**: Clients register with system information
- **client.heartbeat**: Clients maintain connection through heartbeats
- **client.offline_detection**: Clients marked offline after timeout
- **command.target_validation**: Commands only sent to available clients
- **client.concurrency**: One command per client at a time
- **command.timeout**: Commands timeout after specified period
- **system.no_queue**: No command queuing - immediate execution only

## Development Workflow

### For Human Developers

#### 1. Understand the Domain
```bash
# Read core design documents
cat docs/domain-model.md
cat docs/clean-architecture-structure.md
cat docs/user-stories/submit_command_use_case.md
```

#### 2. Set Up Development Environment
```bash
# Install dependencies
pip install -e .
pip install pytest pytest-bdd

# Verify setup
pytest --collect-only
```

#### 3. Choose Implementation Approach
- **Manual TDD**: Follow BDD methodology manually
- **AI-Assisted**: Use prompts in `prompts/` directory

### For AI Assistants

#### Quick Start
```bash
# Begin implementation
User: @prompts/00-overview.md.prompt

# Start specific feature  
User: I want to implement submit_command_use_case
User: @prompts/01-user-stories-to-features.md.prompt
```

#### Complete Workflow
1. `00-overview.md.prompt` - Understand methodology
2. `01-user-stories-to-features.md.prompt` - Convert user story to feature
3. `02-walking-skeleton.md.prompt` - Build test infrastructure  
4. `03-tdd-red-green-refactor.md.prompt` - Implement scenarios
5. `validation/*` - Validate implementation quality
6. `04-iteration-cycle.md.prompt` - Move to next scenario/feature

## Development Rules

### Core Principles

**✅ DO:**
- Work on exactly one scenario at a time
- Use `pytest -m wip` during TDD development
- Follow RED-GREEN-REFACTOR cycle strictly
- Keep business logic in domain layer
- Validate with prompts after each scenario

**❌ DON'T:**
- Work on multiple scenarios simultaneously
- Skip TDD phases (RED, GREEN, REFACTOR)
- Put business logic in tests or infrastructure
- Run full test suite during TDD cycle
- Commit incomplete work

### Test Execution Strategy

**During Development:**
```bash
pytest -m wip              # Run current scenario only
```

**After Scenario Completion:**
```bash
pytest                     # Run all tests (must pass)
```

**Quality Validation:**
```bash
pytest --cov=brief_bridge  # Check code coverage
pytest --collect-only -m wip # Should be empty when done
```

## Architecture Guidelines

### Layer Responsibilities

**Domain Layer (`brief_bridge/domain/`)**
- Business entities and their behavior
- Value objects and business rules
- Repository interfaces (no implementations)
- Domain services for complex business logic
- **NO dependencies on outer layers**

**Application Layer (`brief_bridge/application/`)**
- Use cases that orchestrate domain logic
- Application services
- **Dependencies**: Domain layer only

**Infrastructure Layer (`brief_bridge/infrastructure/`)**
- Repository implementations
- Web framework (FastAPI) 
- Database adapters
- External service integrations
- **Dependencies**: Can import from all layers

### Dependency Rules

```python
# ✅ Correct: Use case depends on domain interface
from brief_bridge.domain.repositories.client_repository import ClientRepository

class SubmitCommandUseCase:
    def __init__(self, client_repo: ClientRepository):  # Interface
        self._client_repo = client_repo

# ❌ Wrong: Domain importing from outer layer
from brief_bridge.infrastructure.repositories.memory_client_repository import MemoryClientRepository
```

## Testing Strategy

### Test Structure

**Feature Files (`.feature`)**
- Written in business language (Gherkin)
- Focus on observable system behavior
- No implementation details

**Step Definitions (`.py`)**
- Given: Set up test preconditions
- When: Trigger system actions  
- Then: Verify observable outcomes
- Delegate to domain layer for business logic

### Scenario Lifecycle

**Development Phases:**
1. `@skip` - Not yet implemented
2. `@wip` - Currently being developed (only one at a time)
3. No marker - Complete and integrated

**Example:**
```gherkin
Feature: Submit Command
  
  # Complete scenario
  Scenario: Submit command to online client
    Given client "client-001" is online and idle
    # ...
    
  @wip  # Currently implementing
  Scenario: Submit command to offline client  
    Given client "client-002" is offline
    # ...
    
  @skip  # Future work
  Scenario: Submit command to busy client
    Given client "client-003" is busy
    # ...
```

## Quality Assurance

### Built-in Validations

**Domain Model Conformance**
- Entity structure matches design
- Business rules properly implemented
- Value objects correctly used

**Clean Architecture Compliance**
- Dependency direction preserved
- Layer boundaries maintained
- Business logic in correct layer

**Test Responsibility Boundaries**
- Tests orchestrate, don't implement
- Business logic in production code
- Observable outcomes only

### Validation Commands

```bash
# Check architecture violations
find brief_bridge/domain -name "*.py" -exec grep -l "from brief_bridge\.\(application\|infrastructure\)" {} \;

# Check for business logic in tests
grep -r "if.*status\|if.*availability" tests/*/given_steps.py

# Validate test structure
pytest --collect-only --quiet
```

## Common Development Patterns

### Entity Creation Pattern
```python
# Domain entity with business logic
@dataclass
class Client:
    _client_id: ClientId
    _status: ClientStatus
    _availability: ClientAvailability
    
    def assign_command(self, command: Command):
        """Business rule: client.concurrency"""
        if self.has_active_command():
            raise ClientBusyError("Client already executing command")
        self._current_command = command
```

### Repository Pattern
```python
# Domain interface
class ClientRepository(ABC):
    @abstractmethod
    async def find_by_id(self, client_id: ClientId) -> Optional[Client]:
        pass

# Infrastructure implementation  
class MemoryClientRepository(ClientRepository):
    async def find_by_id(self, client_id: ClientId) -> Optional[Client]:
        # Implementation details
```

### Use Case Pattern
```python
class SubmitCommandUseCase:
    def __init__(self, client_repo: ClientRepository):
        self._client_repo = client_repo  # Domain interface
        
    async def execute(self, request: SubmitCommandRequest) -> SubmitCommandResponse:
        # Orchestrate domain entities
        client = await self._client_repo.find_by_id(request.client_id)
        command = Command.create(request.content, client)
        # ... business logic delegation
```

## Documentation Standards

### Code Documentation
- Docstrings for all public methods
- Business rule names in comments
- Architecture decision rationale

### Test Documentation  
- Clear scenario descriptions
- Business-focused step definitions
- Comprehensive test coverage

### Design Documentation
- Keep `docs/` updated with implementation changes
- Document architecture decisions
- Maintain domain model accuracy

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Check Python path
python -c "import brief_bridge; print('OK')"
# Fix: pip install -e .
```

**Test Discovery Issues**
```bash
# Check test structure
pytest --collect-only -v
# Fix: Ensure __init__.py files exist
```

**Architecture Violations**
```bash
# Use validation prompts
User: @prompts/validation/clean-architecture-check.md.prompt
```

### Getting Help

**For methodology questions:**
- Read `prompts/00-overview.md.prompt`
- Check `prompts/reference/do-dont-rules.md.prompt`

**For technical issues:**
- Use validation prompts in `prompts/validation/`
- Check pytest commands in `prompts/reference/pytest-commands.md.prompt`

**For domain questions:**
- Review `docs/domain-model.md`
- Check relevant user stories in `docs/user-stories/`

## Success Criteria

### Per Scenario
- Test follows RED-GREEN-REFACTOR cycle
- Business rules properly enforced in domain layer
- Clean Architecture boundaries maintained
- All validation prompts pass

### Per Feature
- All scenarios implemented and passing
- Complete user story functionality
- No regressions in other features
- Code quality maintained

### Overall System
- All user stories implemented as BDD tests
- Complete Clean Architecture structure
- All business rules enforced
- Production-ready system

---

This development approach ensures systematic, high-quality implementation of Brief Bridge while maintaining clear architecture and comprehensive test coverage.