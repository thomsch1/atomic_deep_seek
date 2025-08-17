# Migration Testing Framework

This directory contains comprehensive tests to verify that the functionality remains equivalent between the LangChain and Atomic Agent implementations.

## Test Structure

### Core Test Files

1. **`test_langchain_implementation.py`**
   - Integration tests for the current LangChain-based implementation
   - Tests each node in the research graph individually
   - Captures behavioral patterns for comparison
   - Validates current functionality before migration

2. **`test_atomic_agent_implementation.py`**
   - Equivalent tests for the Atomic Agent implementation
   - Tests each atomic agent individually
   - Validates the new modular architecture
   - Ensures feature parity with LangChain version

3. **`test_migration_comparison.py`**
   - Comparison framework to verify equivalent functionality
   - Automated comparison of outputs and behaviors
   - Performance benchmarking between implementations
   - Migration readiness assessment

4. **`conftest.py`**
   - Shared pytest fixtures and configuration
   - Mock setup for consistent testing
   - Helper functions for test validation

## Test Categories

### Functional Tests
- **Query Generation**: Verify both implementations generate equivalent search queries
- **Web Research**: Ensure search results and citations are processed identically
- **Reflection**: Validate decision-making logic for research sufficiency
- **Finalization**: Confirm final answers maintain the same structure and citations

### Integration Tests
- **Full Workflow**: End-to-end testing of complete research process
- **Error Handling**: Verify both implementations handle errors gracefully
- **Performance**: Compare execution times and resource usage

### Comparison Tests
- **Output Schema**: Verify outputs contain equivalent information
- **Behavioral Patterns**: Compare how each implementation processes inputs
- **Migration Readiness**: Assess if Atomic Agent version is ready for deployment

## Running the Tests

### Prerequisites
```bash
cd backend
pip install -e .
pip install pytest pytest-asyncio pytest-mock
```

### Run Individual Test Suites
```bash
# Test current LangChain implementation
pytest tests/test_langchain_implementation.py -v

# Test Atomic Agent implementation (after conversion)
pytest tests/test_atomic_agent_implementation.py -v

# Run comparison tests
pytest tests/test_migration_comparison.py -v
```

### Run All Tests
```bash
pytest tests/ -v
```

### Generate Migration Report
```bash
python tests/test_migration_comparison.py
```

This generates `migration_comparison_report.json` with detailed analysis.

## Test Validation

### Success Criteria

The migration is considered successful if:

1. **Functionality Match ≥ 90%**: All core features work identically
2. **Output Schema Compatibility**: Outputs contain equivalent information
3. **Performance Acceptable**: New implementation is not >2x slower
4. **Error Handling Equivalent**: Both handle failures gracefully
5. **Maintainability Score ≥ 6**: Code quality improvements achieved

### Expected Differences

Some differences are expected and acceptable:

- **State Management**: TypedDict → Pydantic models
- **Orchestration**: Graph nodes → Python control flow
- **Output Structure**: Minor field name changes (mapped automatically)
- **Error Messages**: Different underlying frameworks may produce different error text

### Key Metrics Tracked

- **Execution Time**: Performance comparison
- **Memory Usage**: Resource consumption
- **Output Accuracy**: Correctness of results
- **Error Rate**: Frequency of failures
- **Code Coverage**: Test completeness

## Migration Workflow

### Phase 1: Baseline Testing
1. Run LangChain tests to establish baseline functionality
2. Document expected behaviors and outputs
3. Identify critical functionality that must be preserved

### Phase 2: Implementation Testing
1. Implement Atomic Agent version
2. Run equivalent tests on new implementation
3. Compare outputs and identify discrepancies

### Phase 3: Validation
1. Run comparison tests
2. Generate migration report
3. Address any identified issues
4. Verify acceptance criteria are met

### Phase 4: Deployment Readiness
1. All tests passing
2. Performance within acceptable range
3. Migration report shows readiness
4. Manual validation of critical paths

## Troubleshooting

### Common Issues

**Test Import Errors**
- Ensure all dependencies are installed
- Check that `PYTHONPATH` includes the src directory

**Mock Failures**
- Verify API keys are properly mocked
- Check that external service calls are patched

**Comparison Failures**
- Review output schema mappings in comparison tests
- Adjust tolerance levels for acceptable differences

**Performance Issues**
- Profile both implementations to identify bottlenecks
- Consider async improvements for Atomic Agent version

### Debugging Tips

1. **Enable Verbose Logging**
   ```bash
   pytest tests/ -v -s --log-cli-level=DEBUG
   ```

2. **Run Single Test**
   ```bash
   pytest tests/test_migration_comparison.py::test_query_generation_comparison -v
   ```

3. **Generate Detailed Report**
   ```python
   # Add to test to save intermediate results
   with open('debug_output.json', 'w') as f:
       json.dump(test_results, f, indent=2)
   ```

## Contributing

When adding new functionality:

1. **Add tests to both implementations**
2. **Update comparison framework**
3. **Document expected behaviors**
4. **Update this README**

### Test Naming Convention
- `test_[component]_[implementation]` for individual tests
- `test_[component]_comparison` for comparison tests
- `test_[scenario]_integration` for end-to-end tests

## Migration Report

The comparison framework generates a comprehensive report including:

- **Individual Test Results**: Pass/fail for each component
- **Performance Metrics**: Execution time comparisons
- **Output Schema Analysis**: Field-by-field comparison
- **Behavioral Differences**: Key implementation differences
- **Migration Readiness**: Go/no-go recommendation
- **Action Items**: Specific issues to address

This report should be reviewed before proceeding with the migration to ensure all critical functionality is preserved.