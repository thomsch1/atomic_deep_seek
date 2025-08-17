============================= test session starts ==============================
platform linux -- Python 3.11.10, pytest-8.4.1, pluggy-1.6.0
rootdir: /mnt/c/Users/Anwender/Projects/deep_seek/deep_seek
plugins: mock-3.14.1, asyncio-1.1.0, anyio-4.10.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 21 items

test/test_search_functions.py ........FF....F......                      [100%]

=================================== FAILURES ===================================
___________________ TestSearchWeb.test_fallback_to_searchapi ___________________

self = <test.test_search_functions.TestSearchWeb object at 0x7fa8cd0b9050>
mock_environment = {'GEMINI_API_KEY': 'test-gemini-key-12345', 'GOOGLE_API_KEY': 'test-google-key-12345', 'GOOGLE_SEARCH_ENGINE_ID': 'test-engine-id-12345', 'SEARCHAPI_API_KEY': 'test-searchapi-key-12345'}

    @pytest.mark.asyncio
    async def test_fallback_to_searchapi(self, mock_environment):
        """Test fallback to SearchAPI.io."""
        # Mock failures for Gemini and Google Custom Search
        with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
            mock_grounding.return_value = {'status': 'error', 'error': 'Failed'}
    
            with patch.dict('os.environ', {'GOOGLE_SEARCH_ENGINE_ID': ''}):
                with patch('httpx.AsyncClient') as mock_client_class:
                    mock_client = AsyncMock()
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json = MagicMock(return_value={
                        "organic_results": [
                            {
                                "title": "SearchAPI Result",
                                "link": "https://searchapi-result.com",
                                "snippet": "SearchAPI quantum computing info..."
                            }
                        ]
                    })
                    mock_client.get = AsyncMock(return_value=mock_response)
                    mock_client_class.return_value.__aenter__.return_value = mock_client
    
                    results = await search_web("quantum computing")
    
>                   assert len(results) == 1
E                   assert 0 == 1
E                    +  where 0 = len([])

test/test_search_functions.py:210: AssertionError
----------------------------- Captured stdout call -----------------------------
❌ Gemini Google Search grounding failed: Failed
🔄 Falling back to Google Custom Search API...
__________________ TestSearchWeb.test_fallback_to_duckduckgo ___________________

self = <test.test_search_functions.TestSearchWeb object at 0x7fa8cd0b1a90>
mock_environment = {'GEMINI_API_KEY': 'test-gemini-key-12345', 'GOOGLE_API_KEY': 'test-google-key-12345', 'GOOGLE_SEARCH_ENGINE_ID': 'test-engine-id-12345', 'SEARCHAPI_API_KEY': 'test-searchapi-key-12345'}

    @pytest.mark.asyncio
    async def test_fallback_to_duckduckgo(self, mock_environment):
        """Test fallback to DuckDuckGo search."""
        # Mock failures for previous search methods
        with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
            mock_grounding.return_value = {'status': 'error', 'error': 'Failed'}
    
            with patch.dict('os.environ', {'GOOGLE_SEARCH_ENGINE_ID': '', 'SEARCHAPI_API_KEY': ''}):
                with patch('httpx.AsyncClient') as mock_client_class:
                    mock_client = AsyncMock()
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json = MagicMock(return_value={
                        "AbstractText": "Quantum computing is a type of computation...",
                        "Heading": "Quantum Computing",
                        "AbstractURL": "https://en.wikipedia.org/wiki/Quantum_computing",
                        "RelatedTopics": [
                            {
                                "Text": "Quantum algorithms description",
                                "FirstURL": "https://example.com/quantum-algorithms"
                            }
                        ]
                    })
                    mock_client.get = AsyncMock(return_value=mock_response)
                    mock_client_class.return_value.__aenter__.return_value = mock_client
    
                    results = await search_web("quantum computing")
    
>                   assert len(results) >= 1
E                   assert 0 >= 1
E                    +  where 0 = len([])

test/test_search_functions.py:242: AssertionError
----------------------------- Captured stdout call -----------------------------
❌ Gemini Google Search grounding failed: Failed
🔄 Falling back to Google Custom Search API...
_________________ TestSearchWeb.test_searchapi_non_200_status __________________

self = <test.test_search_functions.TestSearchWeb object at 0x7fa8cd0ba150>
mock_environment = {'GEMINI_API_KEY': 'test-gemini-key-12345', 'GOOGLE_API_KEY': 'test-google-key-12345', 'GOOGLE_SEARCH_ENGINE_ID': 'test-engine-id-12345', 'SEARCHAPI_API_KEY': 'test-searchapi-key-12345'}

    @pytest.mark.asyncio
    async def test_searchapi_non_200_status(self, mock_environment):
        """Test SearchAPI.io non-200 status code handling."""
        with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
            mock_grounding.return_value = {'status': 'error', 'error': 'Failed'}
    
            with patch.dict('os.environ', {'GOOGLE_SEARCH_ENGINE_ID': ''}):
                with patch('httpx.AsyncClient') as mock_client_class:
                    mock_client = AsyncMock()
                    mock_response = MagicMock()
                    mock_response.status_code = 404
                    mock_client.get = AsyncMock(return_value=mock_response)
                    mock_client_class.return_value.__aenter__.return_value = mock_client
    
                    results = await search_web("quantum computing")
    
                    # Should fallback to DuckDuckGo or knowledge base
>                   assert len(results) >= 1
E                   assert 0 >= 1
E                    +  where 0 = len([])

test/test_search_functions.py:337: AssertionError
----------------------------- Captured stdout call -----------------------------
❌ Gemini Google Search grounding failed: Failed
🔄 Falling back to Google Custom Search API...
=============================== warnings summary ===============================
../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/_internal/_config.py:323
../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/_internal/_config.py:323
  /home/thomas/.local/lib/python3.11/site-packages/pydantic/_internal/_config.py:323: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/fields.py:1093
../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/fields.py:1093
../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/fields.py:1093
../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/fields.py:1093
../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/fields.py:1093
  /home/thomas/.local/lib/python3.11/site-packages/pydantic/fields.py:1093: PydanticDeprecatedSince20: Using extra keyword arguments on `Field` is deprecated and will be removed. Use `json_schema_extra` instead. (Extra keys: 'metadata'). Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warn(

test/test_search_functions.py::TestSearchWeb::test_knowledge_base_fallback_france
test/test_search_functions.py::TestSearchWeb::test_knowledge_base_fallback_python
test/test_search_functions.py::TestSearchWeb::test_knowledge_base_fallback_generic
  /mnt/c/Users/Anwender/Projects/deep_seek/deep_seek/backend/src/agent/agents.py:341: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    response.raise_for_status()
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

test/test_search_functions.py::TestRunAsyncSearch::test_run_async_search_new_loop
  /home/thomas/.local/lib/python3.11/site-packages/_pytest/logging.py:815: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    with (
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

test/test_search_functions.py::TestRunAsyncSearch::test_run_async_search_running_loop
  /usr/local/lib/python3.11/unittest/mock.py:2133: RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited
    setattr(_type, entry, MagicProxy(entry, self))
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

test/test_search_functions.py::TestRunAsyncSearch::test_run_async_search_with_num_results
  /home/thomas/.local/lib/python3.11/site-packages/_pytest/unraisableexception.py:67: PytestUnraisableExceptionWarning: Exception ignored in: <coroutine object AsyncMockMixin._execute_mock_call at 0x7fa8cd0aef40>
  
  Traceback (most recent call last):
    File "<string>", line 1, in <lambda>
  KeyError: '__import__'
  
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.
    warnings.warn(pytest.PytestUnraisableExceptionWarning(msg))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED test/test_search_functions.py::TestSearchWeb::test_fallback_to_searchapi
FAILED test/test_search_functions.py::TestSearchWeb::test_fallback_to_duckduckgo
FAILED test/test_search_functions.py::TestSearchWeb::test_searchapi_non_200_status
================== 3 failed, 18 passed, 13 warnings in 0.28s ===================
[?1034h