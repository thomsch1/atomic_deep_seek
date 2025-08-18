============================= test session starts ==============================
platform linux -- Python 3.11.10, pytest-8.4.1, pluggy-1.6.0
rootdir: /mnt/c/Users/Anwender/Projects/deep_seek/deep_seek/backend
configfile: pyproject.toml
plugins: mock-3.14.1, asyncio-1.1.0, anyio-4.10.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 11 items

backend/src/agent/test/test_base_research_agent.py ..........F           [100%]

=================================== FAILURES ===================================
__________ TestInstructorBasedAgent.test_format_prompt_safely_failure __________

self = <agent.test.test_base_research_agent.TestInstructorBasedAgent object at 0x7fd79395f990>
mock_environment = {'GEMINI_API_KEY': 'test_gemini_key', 'GOOGLE_API_KEY': 'test_google_key', 'GOOGLE_SEARCH_ENGINE_ID': 'test_search_engine_id', 'SEARCHAPI_API_KEY': 'test_searchapi_key'}
test_configuration = Configuration(query_generator_model='gemini-2.5-flash', reflection_model='gemini-2.5-flash', answer_model='gemini-2.5-...ry_delay=1.0, http_verify_ssl=True, rate_limit_requests_per_minute=60, rate_limit_burst=10, connection_pool_maxsize=20)

    def test_format_prompt_safely_failure(self, mock_environment, test_configuration):
        """Test prompt formatting failure."""
        agent = TestInstructorAgent(test_configuration)
    
        template = "Hello {name}, today is {missing_var}"
    
        with patch('builtins.print'):  # Suppress error prints
            result = agent._format_prompt_safely(
                template,
                name="Alice",
                research_topic="test topic"
            )
    
        # Should return fallback with available info
>       assert "Template formatting failed" in result
E       AssertionError: assert 'Template formatting failed' in 'Please help with: test topic'

backend/src/agent/test/test_base_research_agent.py:163: AssertionError
=============================== warnings summary ===============================
../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/_internal/_config.py:323
../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/_internal/_config.py:323
  /home/thomas/.local/lib/python3.11/site-packages/pydantic/_internal/_config.py:323: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/fields.py:1093: 15 warnings
  /home/thomas/.local/lib/python3.11/site-packages/pydantic/fields.py:1093: PydanticDeprecatedSince20: Using extra keyword arguments on `Field` is deprecated and will be removed. Use `json_schema_extra` instead. (Extra keys: 'metadata'). Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warn(

backend/src/agent/test/test_base_research_agent.py:19
  /mnt/c/Users/Anwender/Projects/deep_seek/deep_seek/backend/src/agent/test/test_base_research_agent.py:19: PytestCollectionWarning: cannot collect test class 'TestResearchAgent' because it has a __init__ constructor (from: src/agent/test/test_base_research_agent.py)
    class TestResearchAgent(BaseResearchAgent[dict, dict]):

backend/src/agent/test/test_base_research_agent.py:32
  /mnt/c/Users/Anwender/Projects/deep_seek/deep_seek/backend/src/agent/test/test_base_research_agent.py:32: PytestCollectionWarning: cannot collect test class 'TestInstructorAgent' because it has a __init__ constructor (from: src/agent/test/test_base_research_agent.py)
    class TestInstructorAgent(InstructorBasedAgent[dict, dict]):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED backend/src/agent/test/test_base_research_agent.py::TestInstructorBasedAgent::test_format_prompt_safely_failure
================== 1 failed, 10 passed, 19 warnings in 0.41s ===================
[?1034h