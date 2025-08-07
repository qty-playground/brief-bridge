# Brief Bridge Implementation Prompts

## Overview

These prompts guide AI assistants through systematic BDD implementation of Brief Bridge using pytest-bdd and Clean Architecture principles.

## Prompt Structure

```
prompts/
├── 00-overview.md.prompt                    # Methodology overview
├── 01-user-stories-to-features.md.prompt   # Phase 1: Convert user stories
├── 02-walking-skeleton.md.prompt           # Phase 2: Build test infrastructure  
├── 03-tdd-red-green-refactor.md.prompt     # Phase 3: TDD implementation
├── 04-iteration-cycle.md.prompt            # Phase 4: Next scenario/feature
├── validation/
│   ├── domain-model-check.md.prompt        # Validate domain conformance
│   ├── clean-architecture-check.md.prompt  # Validate CA compliance  
│   └── test-responsibility-check.md.prompt # Validate test boundaries
└── reference/
    ├── pytest-commands.md.prompt           # Pytest execution reference
    └── do-dont-rules.md.prompt             # Implementation rules
```

## Usage Instructions

### Starting a New Implementation

```
User: I want to implement Brief Bridge BDD, starting with submit_command_use_case
User: @prompts/01-user-stories-to-features.md.prompt
```

### Continuing from Existing Work

**If you have feature files but need test infrastructure:**
```
User: @prompts/02-walking-skeleton.md.prompt
```

**If you're ready for TDD implementation:**
```
User: @prompts/03-tdd-red-green-refactor.md.prompt
```

**If you've completed a scenario and need next steps:**
```
User: @prompts/04-iteration-cycle.md.prompt
```

### Quality Validation

**After completing any scenario:**
```
User: @prompts/validation/domain-model-check.md.prompt
User: @prompts/validation/clean-architecture-check.md.prompt  
User: @prompts/validation/test-responsibility-check.md.prompt
```

## Key Features

### 📋 Systematic Approach
Each prompt provides:
- Clear objectives and prerequisites
- Required reading list with specific files
- Step-by-step instructions
- Validation checklists
- Next step guidance

### 🔗 Seamless Flow
- Each prompt guides to the next logical step
- Validation prompts can be used at any time
- Reference prompts provide quick lookups

### 📚 Document Integration
Every prompt specifies exactly which project documents to read:
- `docs/user-stories/` - Technical specifications
- `docs/domain-model.md` - Business rules and entities
- `docs/clean-architecture-structure.md` - Code organization
- Existing test and implementation files

## Example Workflow

### Complete Feature Implementation
1. `01-user-stories-to-features.md.prompt` - Convert user story
2. `02-walking-skeleton.md.prompt` - Build test skeleton
3. `03-tdd-red-green-refactor.md.prompt` - Implement first scenario
4. `validation/*` - Validate scenario completion
5. `04-iteration-cycle.md.prompt` - Move to next scenario
6. Repeat steps 3-5 until feature complete

### Problem Diagnosis
```
User: My tests contain business logic, how do I fix this?
User: @prompts/validation/test-responsibility-check.md.prompt
```

### Quick Reference
```
User: What pytest commands should I use?
User: @prompts/reference/pytest-commands.md.prompt
```

## Prompt Design Principles

### 🎯 Focused Scope
Each prompt addresses exactly one phase or concern, avoiding information overload.

### 📖 Required Reading
Every prompt specifies exactly which documents must be read before proceeding.

### ✅ Validation Built-in
Clear checklists and validation criteria ensure quality at each step.

### 🔄 Reusable
Prompts can be used independently or as part of complete workflow.

## File Naming Convention

- `.md.prompt` extension clearly identifies prompt files
- Numeric prefixes (00-04) indicate phase sequence
- Descriptive names indicate purpose and scope

## Success Criteria

Implementation is complete when:
- All user story scenarios pass as BDD tests
- All validation prompts pass without issues
- Clean Architecture principles maintained
- All business rules properly enforced
- System ready for production use

---

**Pro Tip**: Always start with `00-overview.md.prompt` to understand the complete methodology before diving into specific phases.