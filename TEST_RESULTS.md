============================= test session starts ==============================
platform linux -- Python 3.11.10, pytest-8.4.1, pluggy-1.6.0
rootdir: /mnt/c/Users/Anwender/Projects/deep_seek/deep_seek
plugins: mock-3.14.1, asyncio-1.1.0, anyio-4.10.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 15 items

test/test_web_search_agent.py ...............                            [100%]

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

test/test_web_search_agent.py::TestWebSearchAgent::test_run_grounding_without_search
test/test_web_search_agent.py::TestWebSearchAgent::test_run_citation_creation_error
test/test_web_search_agent.py::TestWebSearchAgent::test_fallback_search_exception
  /usr/local/lib/python3.11/unittest/mock.py:2133: RuntimeWarning: coroutine 'search_with_gemini_grounding' was never awaited
    setattr(_type, entry, MagicProxy(entry, self))
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 15 passed, 10 warnings in 0.17s ========================
[?1034h