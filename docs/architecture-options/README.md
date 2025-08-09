# Architecture Options Guide

Brief Bridge provides **two architecture approaches** to suit different project needs and team preferences. Choose the approach that best fits your project requirements.

## 🏗️ Architecture Comparison

### 🚀 Simplified Architecture (Recommended for Most Cases)
**Pattern**: Framework ↔ UseCase ↔ Entity/Repository

**Best for**:
- Small to medium projects
- Rapid prototyping
- Learning BDD methodology
- Teams new to Clean Architecture
- Time-constrained projects

**Benefits**:
- ✅ Faster development and setup
- ✅ Easier to understand and maintain
- ✅ Still maintains good separation of concerns
- ✅ Full ScenarioContext BDD support
- ✅ Dependency injection where it matters

**Structure**:
```
brief_bridge/
├── entities/           # Business entities with logic
├── use_cases/         # Application logic with DI
├── repositories/      # Data access implementations
└── web/              # FastAPI controllers
```

### 🏛️ Clean Architecture (For Complex Projects)
**Pattern**: Full Clean Architecture with Domain/Application/Infrastructure layers

**Best for**:
- Large, complex business applications
- Long-term maintenance projects
- Teams experienced with Clean Architecture
- Projects with complex business rules
- Multiple external integrations

**Benefits**:
- ✅ Maximum flexibility and extensibility
- ✅ Clear separation of all concerns
- ✅ Testable at every layer
- ✅ Full ScenarioContext BDD support
- ✅ Complete dependency inversion

**Structure**:
```
brief_bridge/
├── domain/
│   ├── entities/      # Pure business entities
│   ├── value_objects/ # Immutable value types
│   ├── repositories/  # Repository interfaces
│   └── services/      # Domain services
├── application/
│   └── use_cases/     # Application orchestration
└── infrastructure/
    ├── repositories/  # Repository implementations
    └── web/          # External interfaces
```

## 🎯 Decision Matrix

| Factor | Simplified | Clean Architecture |
|--------|------------|-------------------|
| **Project Size** | Small-Medium | Medium-Large |
| **Team Size** | 1-5 developers | 5+ developers |
| **Complexity** | Low-Medium | High |
| **Learning Curve** | Gentle | Steep |
| **Development Speed** | Fast | Moderate |
| **Long-term Maintainability** | Good | Excellent |
| **Business Logic Complexity** | Simple-Medium | Complex |
| **External Integrations** | Few | Many |

## 📋 How to Choose

### Choose **Simplified Architecture** if you answer "Yes" to most:
- [ ] Is this a new project or prototype?
- [ ] Do you have fewer than 10 business entities?
- [ ] Is your team new to Clean Architecture?
- [ ] Do you need to deliver quickly?
- [ ] Are external integrations limited (< 5)?
- [ ] Is the business logic relatively straightforward?

### Choose **Clean Architecture** if you answer "Yes" to most:
- [ ] Is this a long-term strategic application?
- [ ] Do you have complex business rules and processes?
- [ ] Does your team have Clean Architecture experience?
- [ ] Are you integrating with many external systems?
- [ ] Do you expect significant future changes?
- [ ] Is testability at every layer critical?

## 🚀 Getting Started

### For Simplified Architecture:
1. Follow `prompts/simplified-architecture/` prompts
2. Read `docs/architecture-options/simplified-architecture/`
3. Start with `prompts/common/01-user-stories-to-features.md.prompt`
4. Use `prompts/simplified-architecture/02-walking-skeleton-simple.md.prompt`

### For Clean Architecture:
1. Follow `prompts/clean-architecture/` prompts  
2. Read `docs/architecture-options/clean-architecture/`
3. Start with `prompts/common/01-user-stories-to-features.md.prompt`
4. Use `prompts/clean-architecture/02-walking-skeleton-ca.md.prompt`

## 🔄 Can I Switch Later?

**Simplified → Clean Architecture**: ✅ Relatively straightforward upgrade path
**Clean Architecture → Simplified**: ⚠️ Possible but requires architectural refactoring

## 🧪 Both Architectures Include

- ✅ **Full BDD Support** with pytest-bdd
- ✅ **ScenarioContext Phase Management** (GIVEN→WHEN→THEN enforcement)
- ✅ **Screaming Architecture** SAM pattern for test modules
- ✅ **Test-Driven Development** methodology
- ✅ **Business logic separation** from framework concerns
- ✅ **Comprehensive validation prompts**

---

**Recommendation**: Start with **Simplified Architecture** for most projects. You can always evolve to Clean Architecture as complexity grows.