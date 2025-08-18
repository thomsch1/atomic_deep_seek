# File-by-File Refactor Plan: Backend Agents Module

## Overview
This plan details the systematic refactoring of each file in `@backend/src/agent/` along with corresponding test migrations from `@test/` to `@backend/src/agent/test/`. Each file will be analyzed, refactored, and tested incrementally.

---

## Phase 1: Core Infrastructure Files

### 1.1 **Create `backend/src/agent/logging_config.py`**
**New File** - No existing counterpart
- **Purpose**: Centralized logging configuration
- **Content**: 
  - Replace all `print()` statements with structured logging
  - Configurable log levels, formatters, and handlers
  - Request correlation ID support
- **Test**: Create `backend/src/agent/test/test_logging_config.py`
  - Test log level configuration
  - Test formatter output
  - Test correlation ID injection

### 1.2 **Create `backend/src/agent/http_client.py`** 
**New File** - No existing counterpart
- **Purpose**: Singleton HTTP client with connection pooling
- **Content**:
  - HTTPx AsyncClient with connection pooling
  - Configurable timeouts and retry policies
  - Async context management
- **Test**: Create `backend/src/agent/test/test_http_client.py`
  - Test singleton pattern
  - Test connection pooling
  - Test timeout handling
  - Test retry mechanisms

### 1.3 **Enhance `backend/src/agent/configuration.py`**
**Existing File** - Read existing tests from `test/conftest.py` (configuration fixtures)
- **Current**: Model configuration, API key management
- **Add**:
  - HTTP timeout and retry settings
  - Rate limiting configuration  
  - Connection pool settings
  - Environment variable validation
- **Test**: Update `backend/src/agent/test/test_configuration.py`
  - Migrate relevant parts from `test/conftest.py`
  - Test new configuration options
  - Test validation logic

---

## Phase 2: Search Architecture

### 2.1 **Create `backend/src/agent/search/` Directory Structure**

#### 2.1.1 `backend/src/agent/search/base_provider.py`
**New File** - Extract from `agents.py`
- **Content**: Abstract base class for search providers
- **Test**: `backend/src/agent/test/test_search_base_provider.py`

#### 2.1.2 `backend/src/agent/search/gemini_search.py` 
**Refactor from `agents.py` lines 206-268** - Read `test/test_search_functions.py:24-100`
- **Extract Functions**:
  - `search_with_gemini_grounding()` (lines 206-268)
  - Related grounding utilities
- **Test**: Create `backend/src/agent/test/test_gemini_search.py`
  - Migrate tests from `test_search_functions.py:TestSearchWithGeminiGrounding`
  - Test grounding metadata processing
  - Test API error handling

#### 2.1.3 `backend/src/agent/search/google_custom_search.py`
**Extract from `agents.py` lines 325-357** - Read `test/test_search_functions.py:150-183`
- **Extract**: Google Custom Search API integration
- **Test**: Create `backend/src/agent/test/test_google_custom_search.py`
  - Migrate relevant tests from `test_search_functions.py`
  - Test API key handling
  - Test HTTP error responses

#### 2.1.4 `backend/src/agent/search/searchapi_provider.py`
**Extract from `agents.py` lines 359-385** - Read `test/test_search_functions.py:185-223`
- **Extract**: SearchAPI.io integration
- **Test**: Create `backend/src/agent/test/test_searchapi_provider.py`

#### 2.1.5 `backend/src/agent/search/duckduckgo_search.py`
**Extract from `agents.py` lines 390-430** - Read `test/test_search_functions.py:225-267`
- **Extract**: DuckDuckGo API integration  
- **Test**: Create `backend/src/agent/test/test_duckduckgo_search.py`

#### 2.1.6 `backend/src/agent/search/fallback_provider.py`
**Extract from `agents.py` lines 432-457** - Read `test/test_search_functions.py:269-322`
- **Extract**: Knowledge-based fallback logic
- **Test**: Create `backend/src/agent/test/test_fallback_provider.py`

### 2.2 **Create `backend/src/agent/search_manager.py`**
**Refactor from `agents.py` lines 271-475** - Read `test/test_search_functions.py:102-395`
- **Purpose**: Orchestrate search provider chain
- **Content**:
  - Provider chain management
  - Circuit breaker pattern
  - Rate limiting and caching
- **Test**: Create `backend/src/agent/test/test_search_manager.py`
  - Migrate tests from `TestSearchWeb` in `test_search_functions.py`
  - Test provider failover logic
  - Test rate limiting

---

## Phase 3: Citation Processing

### 3.1 **Create `backend/src/agent/citation/` Directory**

#### 3.1.1 `backend/src/agent/citation/grounding_processor.py`
**Extract from `agents.py` lines 106-203** - Read `test/test_utility_functions.py`
- **Extract Functions**:
  - `extract_sources_from_grounding()` (lines 106-132)
  - `create_citations_from_grounding()` (lines 135-203)
- **Test**: Create `backend/src/agent/test/test_grounding_processor.py`
  - Test source extraction
  - Test citation creation
  - Test metadata validation

#### 3.1.2 `backend/src/agent/citation/citation_formatter.py` 
**Extract from `agents.py` lines 53-103** - Read `test/test_utility_functions.py`
- **Extract Functions**:
  - `add_inline_citations()` (lines 53-103)
- **Test**: Create `backend/src/agent/test/test_citation_formatter.py`

#### 3.1.3 `backend/src/agent/citation/validation.py`
**New File** - Extract validation logic from citation functions
- **Purpose**: Comprehensive input validation for citations
- **Test**: Create `backend/src/agent/test/test_citation_validation.py`

### 3.2 **Update `backend/src/agent/utils.py`**
**Existing File** - Read `test/test_utility_functions.py`
- **Current**: `get_research_topic()`, `resolve_urls()`, `insert_citation_markers()`, `get_citations()`
- **Remove**: Citation functions (moved to citation module)
- **Keep**: General utilities
- **Test**: Update `backend/src/agent/test/test_utils.py`
  - Migrate relevant tests from `test/test_utility_functions.py`
  - Remove citation-related tests

---

## Phase 4: Agent Classes

### 4.1 **Create `backend/src/agent/base/` Directory**

#### 4.1.1 `backend/src/agent/base/base_research_agent.py`
**New File** - Extract common patterns from agent classes
- **Purpose**: Common agent functionality and patterns
- **Test**: Create `backend/src/agent/test/test_base_research_agent.py`

#### 4.1.2 `backend/src/agent/base/error_handling.py` 
**Extract from various agent error handling** - Read `test/test_error_handling.py`
- **Purpose**: Standardized error handling patterns
- **Test**: Create `backend/src/agent/test/test_error_handling.py`
  - Migrate tests from existing `test/test_error_handling.py`

### 4.2 **Create `backend/src/agent/agents/` Directory**

#### 4.2.1 `backend/src/agent/agents/query_generation_agent.py`
**Extract from `agents.py` lines 478-514** - Read `test/test_query_generation_agent.py`
- **Extract**: `QueryGenerationAgent` class
- **Test**: Create `backend/src/agent/test/test_query_generation_agent.py`
  - Migrate all tests from existing `test/test_query_generation_agent.py`
  - Update import paths
  - Test new error handling patterns

#### 4.2.2 `backend/src/agent/agents/web_search_agent.py`
**Extract from `agents.py` lines 517-682** - Read `test/test_web_search_agent.py`
- **Extract**: `WebSearchAgent` class and methods
- **Test**: Create `backend/src/agent/test/test_web_search_agent.py`
  - Migrate all tests from existing `test/test_web_search_agent.py` (507 lines)
  - Update mocking strategies for new search manager
  - Test integration with new search providers

#### 4.2.3 `backend/src/agent/agents/reflection_agent.py`
**Extract from `agents.py` lines 685-717** - Read `test/test_reflection_agent.py`
- **Extract**: `ReflectionAgent` class
- **Test**: Create `backend/src/agent/test/test_reflection_agent.py`
  - Migrate tests from existing `test/test_reflection_agent.py`
  - Test new error handling

#### 4.2.4 `backend/src/agent/agents/finalization_agent.py`
**Extract from `agents.py` lines 720-755** - Read `test/test_finalization_agent.py`
- **Extract**: `FinalizationAgent` class
- **Test**: Create `backend/src/agent/test/test_finalization_agent.py`
  - Migrate tests from existing `test/test_finalization_agent.py`

---

## Phase 5: Support Files

### 5.1 **Keep Unchanged Files**
These files have minimal/no changes and tests stay in original location:

#### 5.1.1 `backend/src/agent/state.py`
**Existing File** - No changes needed
- **Content**: Pydantic models for state management
- **Test**: Keep tests in integration tests

#### 5.1.2 `backend/src/agent/prompts.py` 
**Existing File** - No changes needed
- **Content**: Prompt templates and instructions
- **Test**: No specific tests needed (used by agent tests)

#### 5.1.3 Files Not Related to Agents Refactor
- `backend/src/agent/app.py` - No changes
- `backend/src/agent/graph.py` - No changes  
- `backend/src/agent/orchestrator.py` - No changes
- `backend/src/agent/profiling_orchestrator.py` - No changes
- `backend/src/agent/quality_validator.py` - No changes
- `backend/src/agent/tools_and_schemas.py` - No changes

---

## Phase 6: Test Infrastructure

### 6.1 **Create `backend/src/agent/test/conftest.py`**
**Migrate from `test/conftest.py`** - Read existing `test/conftest.py`
- **Content**: 
  - Core fixtures for agent testing
  - Mock configurations for new architecture
  - HTTP client mocks
  - Search provider mocks
- **Source**: Migrate relevant fixtures from existing `test/conftest.py`

### 6.2 **Handle Integration Tests**
**Read `test/test_integration.py`**
- **Decision**: Keep in original `test/` location (tests full workflow)
- **Updates**: Update import paths to point to new module structure

### 6.3 **Legacy Compatibility**
- **Keep `backend/src/agent/agents.py`** initially with deprecated warnings
- **Provide backward-compatible imports** during transition period
- **Phase out after all tests pass and integration is verified**

---

## Migration Execution Order

1. **Phase 1**: Infrastructure (logging, http_client, configuration)
2. **Phase 2**: Search providers and manager  
3. **Phase 3**: Citation processing
4. **Phase 4**: Agent classes
5. **Phase 5**: Support files review
6. **Phase 6**: Test infrastructure and integration verification

## Success Criteria

- ✅ All existing tests pass with new architecture
- ✅ New modular tests provide better coverage
- ✅ Import paths updated throughout codebase
- ✅ Backward compatibility maintained during transition
- ✅ Performance improvements verified
- ✅ Code quality metrics improved (complexity, maintainability)

## Risk Mitigation

- **Incremental migration** - one module at a time
- **Parallel development** - new modules alongside existing ones
- **Comprehensive testing** at each phase
- **Rollback plan** for each phase if issues arise
- **Integration testing** after each major phase