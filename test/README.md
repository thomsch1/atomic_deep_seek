# Comprehensive Test Suite for agents.py

This directory contains a comprehensive test suite for the `backend/src/agent/agents.py` file. The tests provide extensive coverage of all functions, classes, and edge cases.

## Test Structure

### Configuration and Fixtures
- **`conftest.py`** - Test configuration, fixtures, and shared test utilities
  - Mock environment variables
  - Mock clients and responses
  - Sample data for all agent types
  - Helper functions for validation

### Core Function Tests
- **`test_utility_functions.py`** - Tests for utility functions
  - `get_genai_client()` - API client creation and validation
  - `add_inline_citations()` - Citation insertion logic
  - `extract_sources_from_grounding()` - Source extraction from metadata
  - `create_citations_from_grounding()` - Citation object creation

- **`test_search_functions.py`** - Tests for search functionality
  - `search_with_gemini_grounding()` - Primary search using Gemini API
  - `search_web()` - Complete search fallback chain
  - `run_async_search()` - Async/sync wrapper functionality

### Agent Class Tests
- **`test_query_generation_agent.py`** - QueryGenerationAgent tests
  - Query generation from research topics
  - Input validation and error handling
  - Fallback behavior for API failures

- **`test_web_search_agent.py`** - WebSearchAgent tests
  - Gemini grounding integration
  - Fallback search mechanisms
  - Citation and source processing
  - Error handling in search operations

- **`test_reflection_agent.py`** - ReflectionAgent tests
  - Research sufficiency analysis
  - Knowledge gap identification
  - Follow-up query generation
  - Edge cases and error scenarios

- **`test_finalization_agent.py`** - FinalizationAgent tests
  - Answer synthesis and finalization
  - Source citation and usage
  - Content formatting and validation
  - Error recovery mechanisms

### Integration and Error Tests
- **`test_integration.py`** - End-to-end workflow tests
  - Complete research workflows
  - Agent interaction testing
  - Data flow validation
  - Multi-loop research scenarios

- **`test_error_handling.py`** - Comprehensive error scenario tests
  - Network failures and timeouts
  - API errors and malformed responses
  - Data corruption handling
  - Resource management
  - Concurrency error handling
  - Memory and performance edge cases

## Test Coverage

The test suite provides comprehensive coverage including:

### Functionality Coverage
- ✅ All public functions and methods
- ✅ All class constructors and properties
- ✅ Success paths and normal operations
- ✅ Error paths and exception handling
- ✅ Edge cases and boundary conditions

### Scenario Coverage
- ✅ API success responses with grounding data
- ✅ API responses without grounding (knowledge-based)
- ✅ API failures and fallback mechanisms
- ✅ Network timeouts and connection errors
- ✅ Malformed data and corruption handling
- ✅ Resource exhaustion scenarios
- ✅ Concurrency and async error handling

### Data Coverage
- ✅ Valid input data scenarios
- ✅ Empty and null input handling
- ✅ Unicode and special character handling
- ✅ Large data volume processing
- ✅ Malformed JSON and response handling

## Running the Tests

### Prerequisites
```bash
pip install pytest pytest-asyncio
```

### Environment Setup
The tests use mock environment variables automatically. No real API keys are required.

### Running All Tests
```bash
# From the test directory
pytest

# From project root
pytest test/

# With verbose output
pytest -v test/
```

### Running Specific Test Files
```bash
pytest test/test_utility_functions.py
pytest test/test_search_functions.py
pytest test/test_query_generation_agent.py
pytest test/test_web_search_agent.py
pytest test/test_reflection_agent.py
pytest test/test_finalization_agent.py
pytest test/test_integration.py
pytest test/test_error_handling.py
```

### Running with Coverage
```bash
pip install pytest-cov
pytest --cov=agent.agents test/
pytest --cov=agent.agents --cov-report=html test/
```

## Test Features

### Mocking Strategy
- **External APIs**: All API calls (Gemini, Google Search, etc.) are mocked
- **Environment Variables**: Consistent mock environment for all tests
- **Network Requests**: HTTP clients and responses are mocked
- **File System**: No real file system interactions required

### Async Testing
- Proper async function testing with `pytest.mark.asyncio`
- Event loop management for concurrent operations
- Async mock objects for realistic async behavior

### Parametrized Testing
- Multiple input scenarios tested systematically
- Edge case exploration through parameter variations
- Configuration testing across different model combinations

### Error Simulation
- Comprehensive error scenario simulation
- Network failure simulation
- API error response testing
- Resource exhaustion testing

## Test Data

All test data is generated through fixtures and helper functions:
- **Sample Inputs**: Realistic input data for all agent types
- **Mock Responses**: Properly structured API responses
- **Error Scenarios**: Comprehensive error condition simulation
- **Edge Cases**: Boundary condition testing data

## Key Testing Principles

1. **No Simplification**: Tests maintain complexity to match real-world scenarios
2. **Comprehensive Coverage**: All code paths and error conditions tested
3. **Realistic Mocking**: Mocks closely match actual API behavior
4. **Isolation**: Tests are independent and don't affect each other
5. **Deterministic**: Tests produce consistent results across runs

## Expected Test Results

When all tests pass, you can be confident that:
- All agent functions work correctly under normal conditions
- Error handling is robust and graceful
- Data flow between agents is correct
- API fallback mechanisms function properly
- Resource management is appropriate
- The system handles edge cases without crashing

## Contributing

When adding new tests:
1. Follow the existing naming conventions
2. Use appropriate fixtures from `conftest.py`
3. Test both success and failure scenarios
4. Include edge cases and boundary conditions
5. Document complex test scenarios
6. Ensure tests are deterministic and isolated