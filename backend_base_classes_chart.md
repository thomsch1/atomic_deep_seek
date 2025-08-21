# Base Classes Connection Chart - backend/src/agent/base/

This chart shows the connections and interplays between all classes and components in the `backend/src/agent/base/` module.

## 🏗️ Module Structure Overview

```
backend/src/agent/base/
├── __init__.py           # Module exports
├── base_research_agent.py # Abstract base classes  
└── error_handling.py     # Error handling framework
```

## 📊 Class Hierarchy and Relationships

### Core Class Inheritance Tree
```
┌─────────────────────────────────────┐
│            ABC (Python)             │
│         (Abstract Base Class)       │
└─────────────┬───────────────────────┘
              │
              │ inherits
              ▼
┌─────────────────────────────────────┐
│        BaseResearchAgent            │
│     Generic[InputType, OutputType]  │
│                                     │
│ ┌─ Abstract Methods:               │
│ │  • _initialize_agent_config()    │
│ │  • run(input_data) -> output     │
│ │  • _create_fallback_response()   │
│ │                                  │
│ ├─ Concrete Methods:               │
│ │  • _handle_error()               │
│ │  • _validate_input()             │
│ └─ Properties: config              │
└─────────────┬───────────────────────┘
              │
              │ inherits
              ▼
┌─────────────────────────────────────┐
│       InstructorBasedAgent          │
│     Generic[InputType, OutputType]  │
│                                     │
│ ├─ Additional Methods:              │
│ │  • _safe_llm_call()              │
│ │  • _format_prompt_safely()       │
│ └─ Properties: agent_config         │
└─────────────────────────────────────┘
```

### Error Handling Class Hierarchy
```
┌─────────────────────────────────────┐
│           Exception                 │
│         (Python Built-in)           │
└─────────────┬───────────────────────┘
              │
              │ inherits
              ▼
┌─────────────────────────────────────┐
│           AgentError                │
│      (Base Agent Exception)         │
│                                     │
│ ├─ Properties:                      │
│ │  • message: str                   │
│ │  • error_type: ErrorType          │
│ │  • original_error: Exception?     │
└─────────────┬───────────────────────┘
              │
    ┌─────────┼─────────┬─────────────┐
    │         │         │             │
    ▼         ▼         ▼             ▼
┌─────────┐ ┌─────────┐ ┌─────────────┐ ┌─────────────┐
│Network  │ │   API   │ │Configuration│ │   Future    │
│ Error   │ │  Error  │ │   Error     │ │  Errors     │
└─────────┘ └─────────┘ └─────────────┘ └─────────────┘
```

### Error Type Classification System
```
┌─────────────────────────────────────┐
│           ErrorType (Enum)          │
│                                     │
│ ├─ NETWORK_ERROR                    │
│ ├─ API_ERROR                        │  
│ ├─ CONFIGURATION_ERROR              │
│ ├─ DATA_CORRUPTION_ERROR            │
│ ├─ TIMEOUT_ERROR                    │
│ ├─ AUTHENTICATION_ERROR             │
│ ├─ RATE_LIMIT_ERROR                 │
│ └─ UNKNOWN_ERROR                    │
└─────────────────────────────────────┘
```

## 🔄 Functional Relationships and Data Flow

### Decorator Pattern Implementation
```
Function/Method
      │
      ▼
┌─────────────────────────────────────┐
│     @handle_agent_errors            │
│   (Synchronous Decorator)           │
│                                     │
│ ┌─ Error Classification:             │
│ │  classify_error(exception)        │
│ │         │                        │
│ │         ▼                        │
│ │   ErrorType mapping              │
│ │                                  │
│ ├─ Logging & Fallback:              │
│ │  • Print error context           │
│ │  • Return fallback_value         │
│ │  • Or raise AgentError           │
└─────────────────────────────────────┘

Function/Method (async)
      │
      ▼
┌─────────────────────────────────────┐
│   @handle_async_agent_errors        │
│    (Asynchronous Decorator)         │
│                                     │
│ └─ Same logic as sync version       │
│    but handles async operations     │
└─────────────────────────────────────┘
```

### Retry Mechanism Architecture
```
┌─────────────────────────────────────┐
│          RetryConfig                │
│                                     │
│ ├─ max_attempts: int                │
│ ├─ base_delay: float                │
│ ├─ max_delay: float                 │
│ ├─ exponential_base: float          │
│ └─ retriable_errors: List[ErrorType]│
└─────────────┬───────────────────────┘
              │
              │ configures
              ▼
┌─────────────────────────────────────┐
│         @with_retry                 │
│      (Retry Decorator)              │
│                                     │
│ ┌─ Attempt Loop:                    │
│ │  for attempt in max_attempts:     │
│ │    try: function()                │
│ │    except error:                  │
│ │      if retriable:                │
│ │        exponential_backoff()      │
│ │      else: raise                  │
│ └─ Dual Mode: sync/async            │
└─────────────────────────────────────┘
```

## 🎯 Integration Patterns

### Agent Implementation Pattern
```
Concrete Agent Class
      │
      │ inherits
      ▼
┌─────────────────────────────────────┐
│     InstructorBasedAgent            │
│                                     │
│ ┌─ Initialization:                  │
│ │  __init__(config)                 │
│ │    └─ calls _initialize_agent_config() │
│ │                                   │
│ ├─ Method Execution:                │
│ │  @handle_agent_errors             │
│ │  def run(input_data):             │
│ │    ├─ _validate_input()           │
│ │    ├─ _safe_llm_call()            │
│ │    └─ _create_fallback_response() │
│ │                                   │
│ └─ Error Recovery:                  │
│    _handle_error(e, context)        │
│      └─ prints + fallback          │
└─────────────────────────────────────┘
```

### Utility Functions Ecosystem
```
┌─────────────────────────────────────┐
│      safe_format_template()         │
│                                     │
│ ├─ Input: template + kwargs         │
│ ├─ Safe string formatting           │
│ └─ Fallback on error               │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│   validate_response_structure()     │
│                                     │
│ ├─ Input: response + expected_attrs │
│ ├─ Validates object structure       │
│ └─ Returns: boolean                 │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│     safe_getattr_chain()            │
│                                     │
│ ├─ Input: obj + "attr.path"         │
│ ├─ Safe nested attribute access     │
│ └─ Returns: value or default        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│       classify_error()              │
│                                     │
│ ├─ Input: Exception                 │
│ ├─ Maps to ErrorType                │
│ └─ Used by error decorators         │
└─────────────────────────────────────┘
```

## 🔗 Cross-Module Dependencies

### External Dependencies Flow
```
┌─────────────────────────────────────┐
│       External Libraries            │
│                                     │
│ ├─ httpx (HTTP errors)              │
│ ├─ asyncio (async operations)       │
│ ├─ functools (decorators)           │
│ └─ typing (type hints)              │
└─────────────┬───────────────────────┘
              │
              │ used by
              ▼
┌─────────────────────────────────────┐
│       error_handling.py             │
│                                     │
│ ├─ Error classification             │
│ ├─ Decorator implementation         │
│ └─ Utility functions                │
└─────────────┬───────────────────────┘
              │
              │ imported by
              ▼
┌─────────────────────────────────────┐
│    base_research_agent.py           │
│                                     │
│ ├─ Uses error handling decorators   │
│ ├─ Implements agent base classes    │
│ └─ Provides agent abstractions      │
└─────────────┬───────────────────────┘
              │
              │ exported through
              ▼
┌─────────────────────────────────────┐
│           __init__.py               │
│                                     │
│ ├─ Public API exports               │
│ ├─ All base classes                 │
│ └─ All error handling components    │
└─────────────────────────────────────┘
```

## 💡 Key Design Patterns

### 1. **Template Method Pattern**
- `BaseResearchAgent.run()` defines the algorithm structure
- Concrete agents implement specific steps via abstract methods
- Common error handling and validation logic is shared

### 2. **Decorator Pattern** 
- Error handling decorators wrap methods with consistent behavior
- Retry decorators add resilience without changing core logic
- Multiple decorators can be composed together

### 3. **Strategy Pattern**
- Different error types use different handling strategies
- Retry configurations define different retry strategies
- Fallback mechanisms provide alternative strategies

### 4. **Factory Pattern (Implicit)**
- `classify_error()` acts as a factory for ErrorType enums
- Configuration objects create appropriate behaviors

### 5. **Chain of Responsibility**
- Error handling flows through classification → logging → fallback
- Retry attempts follow a sequential chain with backoff

## 🛡️ Error Resilience Architecture

### Multi-Layer Error Handling
```
Agent Method Call
      │
      ▼
┌─────────────────────────────────────┐
│    Layer 1: Method Decorators       │
│  @handle_agent_errors / @with_retry │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│    Layer 2: Agent Base Methods      │
│     _handle_error() + validation    │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│    Layer 3: Utility Functions       │
│  safe_* functions + error classify  │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│     Layer 4: Fallback Responses     │
│   _create_fallback_response()       │
└─────────────────────────────────────┘
```

## 📈 Usage Patterns in the System

### Typical Agent Implementation
```python
class MyAgent(InstructorBasedAgent[MyInput, MyOutput]):
    @handle_agent_errors(context="my operation")  # Layer 1
    def run(self, input_data: MyInput) -> MyOutput:
        if not self._validate_input(input_data):     # Layer 2
            return self._create_fallback_response()   # Layer 4
        
        prompt = safe_format_template(template, **data)  # Layer 3
        return self._safe_llm_call(prompt, MyOutput)     # Layer 2
```

This architecture provides a robust, extensible foundation for building research agents with comprehensive error handling, retry mechanisms, and consistent patterns across the entire system.