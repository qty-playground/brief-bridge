# Brief Bridge - Implementation Guide for AI Assistants

## Implementation Methodology

This guide outlines a systematic 4-phase approach for implementing Brief Bridge using BDD (Behavior-Driven Development) with pytest-bdd, following Clean Architecture principles.

## Phase 1: Synchronize User Stories to Feature Files

### Objective
Convert user stories to Gherkin feature files with consistent naming and structure.

### Tasks
1. **Feature File Creation**
   - Convert each user story from `docs/user-stories/` to a corresponding `.feature` file
   - Place feature files in `tests/<feature>/story.feature`
   - Ensure `<feature>` names are valid Python module names (lowercase, underscores only)

2. **Naming Convention**
   - User Story: `submit_command_use_case.md`
   - Feature Directory: `tests/submit_command_use_case/`
   - Feature File: `tests/submit_command_use_case/story.feature`
   - Feature Name: Must be importable as Python module

3. **Content Mapping**
   - Copy "Test Scenarios" from user stories to Gherkin scenarios
   - Maintain exact scenario names and step definitions
   - Preserve all Given/When/Then steps exactly as specified

4. **Scenario Marking Strategy**
   - **ALL scenarios initially marked with `@skip`**
   - This prevents pytest from executing any scenarios until ready
   - One feature file may contain multiple scenarios for the same business rule scope

**Example Feature File Structure**:
```gherkin
Feature: Submit Command
  
  @skip
  Scenario: Submit command to online idle client
    Given client "client-001" exists with status "ONLINE" and availability "IDLE"
    When I POST to "/commands" with:
      """
      {
        "client_id": "client-001",
        "content": "echo 'hello world'"
      }
      """
    Then response status code should be 201
    
  @skip  
  Scenario: Submit command to offline client
    Given client "client-002" exists with status "OFFLINE"
    When I POST to "/commands" with:
      """
      {
        "client_id": "client-002", 
        "content": "ls -la"
      }
      """
    Then response status code should be 400
```

### Validation Criteria
- [ ] Each user story has corresponding feature file
- [ ] Feature directory names are valid Python modules
- [ ] All scenarios from user stories are included
- [ ] **ALL scenarios marked with @skip initially**
- [ ] Gherkin syntax is valid

## Phase 2: Create Testing Walking Skeleton

### Objective
Build pytest-bdd infrastructure without real implementation - just the testing framework shell.

### Tasks
1. **Main Test Orchestrator**
   - Create `tests/<feature>/test_<feature>.py` as the main pytest-bdd file
   - Import and organize all step definitions
   - Link feature file to step implementations
   - No business logic implementation yet

2. **Step Definition Structure**
   - Each step implementation goes in `tests/<feature>/<step_type>.py`
   - Files: `given_steps.py`, `when_steps.py`, `then_steps.py`
   - Follow Command Pattern for step implementations
   - All steps should raise `NotImplementedError("Step not implemented")`

3. **Directory Structure Example**
   ```
   tests/
   ├── submit_command_use_case/
   │   ├── __init__.py
   │   ├── story.feature
   │   ├── test_submit_command_use_case.py  # Main orchestrator
   │   ├── given_steps.py                   # Given step implementations
   │   ├── when_steps.py                    # When step implementations
   │   └── then_steps.py                    # Then step implementations
   ```

4. **Step Implementation Template**
   ```python
   # given_steps.py
   from pytest_bdd import given
   
   @given('client "{client_id}" exists with status "{status}" and availability "{availability}"')
   def given_client_exists_with_status(client_id, status, availability):
       raise NotImplementedError("Step not implemented")
   ```

### Validation Criteria
- [ ] All feature files have corresponding test orchestrators
- [ ] All steps from user stories have skeleton implementations
- [ ] All step functions raise NotImplementedError
- [ ] Tests can be discovered by pytest (but will fail)
- [ ] Directory structure follows naming conventions

## Phase 3: TDD RED-GREEN-REFACTOR Cycle

### Objective
Implement production code using Test-Driven Development methodology with Clean Architecture.

### Scenario Selection and Marking
1. **Select First Scenario**: Always start with the first scenario in the feature file
2. **Change Mark from @skip to @wip**: This allows isolated execution of the current scenario
3. **Work within Business Rule Scope**: All scenarios in one feature file address the same business rule

**Example Scenario Activation**:
```gherkin
Feature: Submit Command
  
  @wip  # Changed from @skip to @wip
  Scenario: Submit command to online idle client
    Given client "client-001" exists with status "ONLINE" and availability "IDLE"
    # ... rest of scenario
    
  @skip  # Still skipped
  Scenario: Submit command to offline client
    # ... scenario content
```

### 3.1 RED Phase (Failing Tests)
- **Run pytest with WIP marker only**: `pytest -m wip`
- Confirm selected scenario fails with NotImplementedError
- Focus on making that single scenario pass
- **Never run multiple scenarios simultaneously**

### 3.2 GREEN Phase (Two-Stage Implementation)

**Run only WIP scenario**: `pytest -m wip` during both GREEN stages

#### GREEN Stage 1: Basic Test Passing (Infrastructure Shell)
- Create minimal Clean Architecture **structure** only
- **Ignore business rules** completely
- **Ignore proper implementation** - focus on making test pass
- Build the CA skeleton with hardcoded/fake implementations
- Goal: Test passes with minimal CA structure in place

**Example GREEN Stage 1**:
```python
# Create CA shell structure - no business logic yet
from brief_bridge.domain.entities.client import Client
from brief_bridge.domain.value_objects.client_id import ClientId
from brief_bridge.infrastructure.persistence.memory.memory_client_repository import MemoryClientRepository

@given('client "{client_id}" exists with status "{status}" and availability "{availability}"')
def given_client_exists_with_status(client_id, status, availability, client_repository):
    # Hardcoded fake client - no business rules
    fake_client = Client.create_fake(client_id, status, availability)  # Minimal factory
    asyncio.run(client_repository.save(fake_client))
```

#### GREEN Stage 2: Business Rule Implementation
- **Now implement the specific business rule** for current scenario
- Reference `docs/domain-model.md` for the exact business rule being tested
- Replace hardcoded logic with proper business logic
- **Only implement business rules tested by current scenario**
- Keep CA structure from Stage 1, enhance with real logic

**Example GREEN Stage 2**:
```python
# Same CA structure, now with proper business rule validation
@given('client "{client_id}" exists with status "{status}" and availability "{availability}"')
def given_client_exists_with_status(client_id, status, availability, client_repository):
    # Now with proper business rule: client.registration
    client_info = ClientInfo(os="Linux", architecture="x86_64", version="Ubuntu 20.04")
    client = Client(
        client_id=ClientId(client_id),
        client_info=client_info
    )
    # Business rule: client.heartbeat - set proper status
    if status == "ONLINE":
        client.mark_online()
    elif status == "OFFLINE":
        client.mark_offline()
    
    asyncio.run(client_repository.save(client))
```

### 3.3 REFACTOR Phase (Code Quality Improvement)
- **Continue running only WIP scenario**: `pytest -m wip` during refactoring
- Clean Architecture structure already exists from GREEN Stage 1
- Business rules already implemented from GREEN Stage 2  
- **Focus on code quality improvements only**
- Remove code smells, improve readability
- **Do not change functionality or add new features**

**Refactor Examples**:
```python
# Before refactoring (from GREEN Stage 2)
@given('client "{client_id}" exists with status "{status}" and availability "{availability}"')
def given_client_exists_with_status(client_id, status, availability, client_repository):
    client_info = ClientInfo(os="Linux", architecture="x86_64", version="Ubuntu 20.04")
    client = Client(client_id=ClientId(client_id), client_info=client_info)
    # Duplicate logic for status setting
    if status == "ONLINE":
        client.mark_online()
    elif status == "OFFLINE":
        client.mark_offline()
    asyncio.run(client_repository.save(client))

# After refactoring (improved readability)
@given('client "{client_id}" exists with status "{status}" and availability "{availability}"')
def given_client_exists_with_status(client_id, status, availability, client_repository):
    client_info = ClientInfo.create_default_linux()  # Extract method
    client = Client(client_id=ClientId(client_id), client_info=client_info)
    client.set_status(ClientStatus(status))  # Simplified status handling
    asyncio.run(client_repository.save(client))
```

**Refactor Focus Areas**:
- Extract methods for better readability
- Simplify conditional logic
- Remove duplicate code
- Improve variable naming
- **Maintain same functionality and test behavior**

### Validation Criteria for Phase 3

#### GREEN Stage 1 Validation
- [ ] Test passes with `pytest -m wip`
- [ ] Clean Architecture structure created (empty shells)
- [ ] No business rule implementation yet
- [ ] Minimal hardcoded/fake implementations only

#### GREEN Stage 2 Validation  
- [ ] Test still passes with `pytest -m wip`
- [ ] Business rule for current scenario implemented
- [ ] Real business logic replaces hardcoded logic
- [ ] Only current scenario's business rule addressed

#### REFACTOR Validation
- [ ] Test still passes with `pytest -m wip`
- [ ] Code quality improved (readability, structure)
- [ ] No functionality changes
- [ ] Business rules preserved

### Scenario Completion Process
1. **Remove WIP Mark**: Change `@wip` back to no marker (or `@completed` if preferred)
2. **Run Full Test Suite**: Execute `pytest` (without markers) to ensure no regressions
3. **All tests must pass**: Both completed scenario and any previously implemented scenarios
4. **Complete Scenario Validation Checklist** (see below)

**Example Completed Scenario**:
```gherkin
Feature: Submit Command
  
  # No marker - ready for full test runs
  Scenario: Submit command to online idle client
    Given client "client-001" exists with status "ONLINE" and availability "IDLE"
    # ... rest of scenario
    
  @skip  # Next scenario to implement
  Scenario: Submit command to offline client
    # ... scenario content
```

## Scenario Completion Validation Checklist

### 1. Domain Model Conformance Check
**Objective**: Ensure implementation aligns with domain design documents

#### Validation Steps
- [ ] **Entity Structure**: Compare implemented entities with `docs/domain-model.md` class diagram
- [ ] **Value Objects**: Verify all value objects match domain specifications
- [ ] **Business Rules**: Cross-reference implemented rules with domain model business rules
- [ ] **Relationships**: Validate entity relationships match multiplicity constraints
- [ ] **Method Signatures**: Ensure entity methods align with domain model definitions

#### Domain Model Deviation Protocol
**If implementation differs from domain model:**
1. **Document the difference**: What was implemented vs. what was designed?
2. **Analyze the cause**: 
   - Was the domain model incomplete/incorrect?
   - Was the implementation wrong?
   - Did new requirements emerge?
3. **Make decision**:
   - **Update domain model** if design was incomplete
   - **Fix implementation** if code doesn't follow design
   - **Document exception** if justified deviation
4. **Update relevant documentation**

**Example Domain Model Check**:
```python
# Domain Model says: Client has client_id, status, availability
# Implementation check:
class Client:
    def __init__(self, client_id: ClientId, client_info: ClientInfo):
        self._client_id = client_id     # ✅ Matches domain model
        self._status = ClientStatus     # ✅ Matches domain model  
        self._availability = ...        # ✅ Matches domain model
        self._extra_field = ...         # ❌ Not in domain model - needs discussion
```

### 2. Clean Architecture Compliance Check
**Objective**: Verify dependency directions and layer boundaries

#### Layer Dependency Validation
- [ ] **Domain Layer**: Has NO dependencies on outer layers
- [ ] **Application Layer**: Only depends on Domain layer
- [ ] **Infrastructure Layer**: Can depend on Domain and Application layers
- [ ] **No circular dependencies**: Between any layers or components

#### Import Statement Analysis
```bash
# Check domain layer purity
find brief_bridge/domain -name "*.py" -exec grep -l "from brief_bridge\.(application\|infrastructure)" {} \;
# Should return NO files

# Check application layer dependencies  
find brief_bridge/application -name "*.py" -exec grep -l "from brief_bridge\.infrastructure" {} \;
# Should return NO files
```

#### Repository Pattern Validation
- [ ] **Repository interfaces** defined in Domain layer
- [ ] **Repository implementations** in Infrastructure layer
- [ ] **Use cases** depend only on repository interfaces
- [ ] **Dependency injection** properly configured

**Example Clean Architecture Check**:
```python
# ✅ Correct: Use case depends on repository interface (Domain)
from brief_bridge.domain.repositories.client_repository import ClientRepository

class SubmitCommandUseCase:
    def __init__(self, client_repo: ClientRepository):  # Interface from Domain
        self._client_repo = client_repo

# ❌ Wrong: Use case depends on concrete implementation (Infrastructure)
from brief_bridge.infrastructure.persistence.memory.memory_client_repository import MemoryClientRepository
```

### 3. Test Code Responsibility Check
**Objective**: Ensure tests only orchestrate data, production code handles logic

#### Test Step Responsibility Validation
- [ ] **Given steps**: Only set up test data, no business logic
- [ ] **When steps**: Only trigger production code, no logic implementation  
- [ ] **Then steps**: Only assert results, no calculation or processing
- [ ] **No business rules in tests**: All business logic in production code

#### Business Logic Leak Detection
**❌ Bad Example (Business logic in test)**:
```python
@given('client "{client_id}" exists with status "{status}"')
def given_client_exists(client_id, status):
    # Wrong: Test implementing business rule validation
    if status not in ["ONLINE", "OFFLINE", "BUSY"]:
        raise ValueError("Invalid status")  # This belongs in production code
    
    # Wrong: Test calculating derived values
    availability = "IDLE" if status == "ONLINE" else "UNAVAILABLE"  # Business logic
    fake_clients[client_id] = {"status": status, "availability": availability}
```

**✅ Good Example (Tests only orchestrate)**:
```python
@given('client "{client_id}" exists with status "{status}"')
def given_client_exists(client_id, status, client_repository):
    # Correct: Just pass data to production code
    client_info = ClientInfo.create_default()
    client = Client(ClientId(client_id), client_info)
    client.set_status(ClientStatus(status))  # Production code handles validation
    asyncio.run(client_repository.save(client))
```

#### Test Data vs Business Logic Separation
- [ ] **Test data**: Hardcoded values, example inputs, mock objects
- [ ] **Business calculations**: Always in domain entities or services
- [ ] **Validation logic**: Always in domain layer, never in tests
- [ ] **State transitions**: Handled by domain entities, not test steps

### Completion Validation Summary
- [ ] **Full pytest run passes**: `pytest` (no markers)
- [ ] **Domain model conformance**: Implementation matches design
- [ ] **Clean Architecture compliance**: Dependencies flow correctly
- [ ] **Test responsibility boundaries**: Tests orchestrate, production code implements
- [ ] **No regressions**: Previously implemented scenarios still pass
- [ ] **Documentation updated**: If domain model was modified

**Only after ALL validation criteria pass should the scenario be considered complete.**

## Phase 4: Next Iteration Cycle

### Objective
Repeat Phase 3 for next scenario until entire feature file is complete.

### Next Scenario Selection Within Feature
1. **Select Next @skip Scenario**: Choose the next scenario marked with `@skip` in current feature file
2. **Change Mark to @wip**: Enable isolated execution for the new scenario
3. **Maintain Business Rule Focus**: All scenarios within one feature file serve the same business rule

### Process
1. **Mark Next Scenario**: Change `@skip` to `@wip` for next scenario
2. **Return to RED**: Run `pytest -m wip` - new scenario should fail
3. **Apply GREEN**: Minimal implementation for new scenario
4. **Apply REFACTOR**: Extend/modify CA components as needed
5. **Complete Scenario**: Remove `@wip` mark and run full `pytest`
6. **Validate**: Ensure all implemented scenarios still pass

**Example Iteration Progress**:
```gherkin
Feature: Submit Command
  
  # Completed scenario 1
  Scenario: Submit command to online idle client
    # ... implemented
    
  @wip  # Currently working on scenario 2
  Scenario: Submit command to offline client
    # ... being implemented
    
  @skip  # Future scenario 3
  Scenario: Submit command to busy client
    # ... not yet started
```

### Feature Completion Criteria
- [ ] All scenarios in feature file pass
- [ ] All business rules for the feature are implemented
- [ ] Clean Architecture structure is maintained
- [ ] Code quality is acceptable

### Next Feature Selection
After completing one feature file:
1. Select next user story/feature file
2. Return to Phase 1 if new structure needed
3. Return to Phase 3 if using existing test structure

## Implementation Rules

### DO
- ✅ Implement exactly one scenario at a time
- ✅ Follow RED-GREEN-REFACTOR strictly  
- ✅ **Use `pytest -m wip` during TDD cycle**
- ✅ **Run full `pytest` after each completed scenario**
- ✅ Mark scenarios with `@skip` initially, `@wip` during work
- ✅ Remove markers when scenario is complete
- ✅ Reference domain model for business rules
- ✅ Keep Clean Architecture boundaries clear
- ✅ Validate tests pass after each phase

### DON'T
- ❌ Implement multiple scenarios simultaneously
- ❌ Skip the RED phase
- ❌ **Run full test suite during TDD cycle**
- ❌ **Leave `@wip` markers on completed scenarios**
- ❌ **Work on unmarked scenarios**
- ❌ Add features not required by current scenario
- ❌ Break existing passing tests
- ❌ Implement business rules before GREEN phase

## Pytest Execution Strategy

### During TDD Implementation
```bash
# Only run current work-in-progress scenario
pytest -m wip
```

### After Scenario Completion
```bash
# Run all tests to ensure no regressions
pytest
```

### Validation Commands
```bash
# Check no skipped scenarios are accidentally running
pytest --collect-only | grep -E "@(skip|wip)"

# Verify marker usage
pytest -m skip --collect-only  # Should list unimplemented scenarios
pytest -m wip --collect-only   # Should list current scenario (max 1)
```

## Success Metrics

### Per Scenario
- Test changes from RED → GREEN → stays GREEN after REFACTOR
- Business rule properly enforced
- Clean Architecture maintained

### Per Feature
- All scenarios pass
- Feature completely implements corresponding user story
- No regression in other features

### Overall System
- All user stories implemented as passing BDD tests
- Clean Architecture structure complete
- All business rules enforced
- System ready for production

---

**Remember**: This methodology prioritizes working software over perfect design. Build incrementally, validate continuously, and refactor fearlessly.