============================= test session starts ==============================
platform linux -- Python 3.11.10, pytest-8.4.1, pluggy-1.6.0
rootdir: /mnt/c/Users/Anwender/Projects/deep_seek/deep_seek
plugins: mock-3.14.1, asyncio-1.1.0, anyio-4.10.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 0 items / 1 error

==================================== ERRORS ====================================
__________________ ERROR collecting test/test_integration.py ___________________
ImportError while importing test module '/mnt/c/Users/Anwender/Projects/deep_seek/deep_seek/test/test_integration.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/local/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
test/test_integration.py:16: in <module>
    from agent.agents import (
E   ImportError: cannot import name 'search_web' from 'agent.agents' (/mnt/c/Users/Anwender/Projects/deep_seek/deep_seek/backend/src/agent/agents/__init__.py)
=============================== warnings summary ===============================
../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/_internal/_config.py:323
../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/_internal/_config.py:323
  /home/thomas/.local/lib/python3.11/site-packages/pydantic/_internal/_config.py:323: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/fields.py:1093: 15 warnings
  /home/thomas/.local/lib/python3.11/site-packages/pydantic/fields.py:1093: PydanticDeprecatedSince20: Using extra keyword arguments on `Field` is deprecated and will be removed. Use `json_schema_extra` instead. (Extra keys: 'metadata'). Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
ERROR test/test_integration.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
======================== 17 warnings, 1 error in 0.33s =========================
[?1034h