============================= test session starts ==============================
platform linux -- Python 3.11.10, pytest-8.4.1, pluggy-1.6.0
rootdir: /mnt/c/Users/Anwender/Projects/deep_seek/deep_seek
plugins: mock-3.14.1, asyncio-1.1.0, anyio-4.10.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 6 items

test/test_integration.py FFFFFF                                          [100%]

=================================== FAILURES ===================================
_______________ TestAgentIntegration.test_full_research_workflow _______________

self = <test.test_integration.TestAgentIntegration object at 0x7fcc1948f6d0>
mock_environment = {'GEMINI_API_KEY': 'test-gemini-key-12345', 'GOOGLE_API_KEY': 'test-google-key-12345', 'GOOGLE_SEARCH_ENGINE_ID': 'test-engine-id-12345', 'SEARCHAPI_API_KEY': 'test-searchapi-key-12345'}
test_configuration = Configuration(query_generator_model='gemini-2.5-flash', reflection_model='gemini-2.5-flash', answer_model='gemini-2.5-...ry_delay=1.0, http_verify_ssl=True, rate_limit_requests_per_minute=60, rate_limit_burst=10, connection_pool_maxsize=20)

    def test_full_research_workflow(self, mock_environment, test_configuration):
        """Test complete research workflow from query generation to finalization."""
        # Mock all missing Google GenAI types classes
        with patch('google.generativeai.types.GoogleSearch', create=True) as mock_google_search, \
             patch('google.generativeai.types.Tool', create=True) as mock_tool, \
             patch('google.generativeai.types.GoogleSearchRetrieval', create=True) as mock_google_search_retrieval, \
             patch('google.generativeai.types.DynamicRetrievalConfig', create=True) as mock_dynamic_retrieval_config, \
             patch('google.generativeai.types.DynamicRetrievalConfigMode', create=True) as mock_dynamic_retrieval_config_mode, \
             patch('google.generativeai.types.GenerateContentConfig', create=True) as mock_generate_content_config, \
             patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_google_search.return_value = MagicMock()
            mock_tool.return_value = MagicMock()
            mock_google_search_retrieval.return_value = MagicMock()
            mock_dynamic_retrieval_config.return_value = MagicMock()
            mock_dynamic_retrieval_config_mode.MODE_DYNAMIC = 'MODE_DYNAMIC'
            mock_generate_content_config.return_value = MagicMock()
    
            # Setup mock configurations
            mock_agent_config = MagicMock()
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_client.chat.completions = mock_completions
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
    
            # Mock Gemini client for WebSearchAgent
            mock_genai_client = MagicMock()
    
            # Step 1: Query Generation
            mock_completions.create.return_value = QueryGenerationOutput(
                queries=["quantum computing advances 2024", "quantum algorithm improvements"],
                rationale="Comprehensive queries for quantum computing research"
            )
    
            query_agent = QueryGenerationAgent(test_configuration)
            query_input = QueryGenerationInput(
                research_topic="quantum computing developments",
                number_of_queries=2,
                current_date="January 15, 2024"
            )
            query_result = query_agent.run(query_input)
    
            assert len(query_result.queries) == 2
            assert "quantum computing" in query_result.queries[0]
    
            # Step 2: Web Search for each query
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
                    mock_response = MagicMock()
                    mock_response.text = "Quantum computing has achieved significant milestones in 2024..."
    
                    mock_grounding.return_value = {
                        'status': 'success',
                        'response': mock_response,
                        'grounding_used': True,
                        'source': 'gemini_grounding'
                    }
    
                    with patch('agent.agents.extract_sources_from_grounding') as mock_extract:
                        with patch('agent.agents.add_inline_citations') as mock_citations:
                            with patch('agent.agents.create_citations_from_grounding') as mock_create_citations:
                                mock_sources = [
                                    Source(title="Quantum Research 2024", url="https://quantum.com", short_url="q1", label="Source 1")
                                ]
                                mock_extract.return_value = mock_sources
                                mock_citations.return_value = "Research content with citations"
                                mock_create_citations.return_value = [
                                    Citation(start_index=0, end_index=20, segments=mock_sources)
                                ]
    
>                               web_agent = WebSearchAgent(test_configuration)
                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

test/test_integration.py:112: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
backend/src/agent/base/base_research_agent.py:29: in __init__
    self._initialize_agent_config()
backend/src/agent/agents/web_search_agent.py:33: in _initialize_agent_config
    self.client = get_genai_client()
                  ^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    def get_genai_client():
        """Get configured GenAI client."""
        import os
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be set")
>       return genai.Client(api_key=api_key)
               ^^^^^^^^^^^^
E       AttributeError: module 'google.generativeai' has no attribute 'Client'

backend/src/agent/agents/web_search_agent.py:24: AttributeError
___________ TestAgentIntegration.test_workflow_with_reflection_loop ____________

self = <test.test_integration.TestAgentIntegration object at 0x7fcc1931a7d0>
mock_environment = {'GEMINI_API_KEY': 'test-gemini-key-12345', 'GOOGLE_API_KEY': 'test-google-key-12345', 'GOOGLE_SEARCH_ENGINE_ID': 'test-engine-id-12345', 'SEARCHAPI_API_KEY': 'test-searchapi-key-12345'}
test_configuration = Configuration(query_generator_model='gemini-2.5-flash', reflection_model='gemini-2.5-flash', answer_model='gemini-2.5-...ry_delay=1.0, http_verify_ssl=True, rate_limit_requests_per_minute=60, rate_limit_burst=10, connection_pool_maxsize=20)

    def test_workflow_with_reflection_loop(self, mock_environment, test_configuration):
        """Test workflow that requires additional research loops."""
        # Mock all missing Google GenAI types classes
        with patch('google.generativeai.types.GoogleSearch', create=True) as mock_google_search, \
             patch('google.generativeai.types.Tool', create=True) as mock_tool, \
             patch('google.generativeai.types.GoogleSearchRetrieval', create=True) as mock_google_search_retrieval, \
             patch('google.generativeai.types.DynamicRetrievalConfig', create=True) as mock_dynamic_retrieval_config, \
             patch('google.generativeai.types.DynamicRetrievalConfigMode', create=True) as mock_dynamic_retrieval_config_mode, \
             patch('google.generativeai.types.GenerateContentConfig', create=True) as mock_generate_content_config, \
             patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_google_search.return_value = MagicMock()
            mock_tool.return_value = MagicMock()
            mock_google_search_retrieval.return_value = MagicMock()
            mock_dynamic_retrieval_config.return_value = MagicMock()
            mock_dynamic_retrieval_config_mode.MODE_DYNAMIC = 'MODE_DYNAMIC'
            mock_generate_content_config.return_value = MagicMock()
    
            # Setup mock configurations
            mock_agent_config = MagicMock()
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_client.chat.completions = mock_completions
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
    
            mock_genai_client = MagicMock()
    
            # Initial query generation
            mock_completions.create.return_value = QueryGenerationOutput(
                queries=["AI healthcare applications"],
                rationale="Initial query for AI in healthcare"
            )
    
            query_agent = QueryGenerationAgent(test_configuration)
            initial_query = query_agent.run(QueryGenerationInput(
                research_topic="AI in healthcare",
                number_of_queries=1,
                current_date="January 15, 2024"
            ))
    
            # Initial web search
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
                    mock_response = MagicMock()
                    mock_response.text = "AI is being used in healthcare for diagnosis..."
    
                    mock_grounding.return_value = {
                        'status': 'success',
                        'response': mock_response,
                        'grounding_used': True,
                        'source': 'gemini_grounding'
                    }
    
                    with patch('agent.agents.extract_sources_from_grounding') as mock_extract:
                        with patch('agent.agents.add_inline_citations') as mock_citations:
                            with patch('agent.agents.create_citations_from_grounding') as mock_create_citations:
                                mock_sources = [Source(title="AI Healthcare", url="https://ai-health.com", short_url="ah1", label="Source 1")]
                                mock_extract.return_value = mock_sources
                                mock_citations.return_value = "AI healthcare content"
                                mock_create_citations.return_value = []
    
>                               web_agent = WebSearchAgent(test_configuration)
                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

test/test_integration.py:230: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
backend/src/agent/base/base_research_agent.py:29: in __init__
    self._initialize_agent_config()
backend/src/agent/agents/web_search_agent.py:33: in _initialize_agent_config
    self.client = get_genai_client()
                  ^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    def get_genai_client():
        """Get configured GenAI client."""
        import os
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be set")
>       return genai.Client(api_key=api_key)
               ^^^^^^^^^^^^
E       AttributeError: module 'google.generativeai' has no attribute 'Client'

backend/src/agent/agents/web_search_agent.py:24: AttributeError
_______________ TestAgentIntegration.test_cross_agent_data_flow ________________

self = <test.test_integration.TestAgentIntegration object at 0x7fcc1931ae10>
mock_environment = {'GEMINI_API_KEY': 'test-gemini-key-12345', 'GOOGLE_API_KEY': 'test-google-key-12345', 'GOOGLE_SEARCH_ENGINE_ID': 'test-engine-id-12345', 'SEARCHAPI_API_KEY': 'test-searchapi-key-12345'}
test_configuration = Configuration(query_generator_model='gemini-2.5-flash', reflection_model='gemini-2.5-flash', answer_model='gemini-2.5-...ry_delay=1.0, http_verify_ssl=True, rate_limit_requests_per_minute=60, rate_limit_burst=10, connection_pool_maxsize=20)

    def test_cross_agent_data_flow(self, mock_environment, test_configuration):
        """Test that data flows correctly between different agents."""
        # Mock all missing Google GenAI types classes
        with patch('google.generativeai.types.GoogleSearch', create=True) as mock_google_search, \
             patch('google.generativeai.types.Tool', create=True) as mock_tool, \
             patch('google.generativeai.types.GoogleSearchRetrieval', create=True) as mock_google_search_retrieval, \
             patch('google.generativeai.types.DynamicRetrievalConfig', create=True) as mock_dynamic_retrieval_config, \
             patch('google.generativeai.types.DynamicRetrievalConfigMode', create=True) as mock_dynamic_retrieval_config_mode, \
             patch('google.generativeai.types.GenerateContentConfig', create=True) as mock_generate_content_config, \
             patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_google_search.return_value = MagicMock()
            mock_tool.return_value = MagicMock()
            mock_google_search_retrieval.return_value = MagicMock()
            mock_dynamic_retrieval_config.return_value = MagicMock()
            mock_dynamic_retrieval_config_mode.MODE_DYNAMIC = 'MODE_DYNAMIC'
            mock_generate_content_config.return_value = MagicMock()
    
            mock_agent_config = MagicMock()
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_client.chat.completions = mock_completions
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
    
            # Test specific data preservation across agents
            original_topic = "renewable energy storage solutions"
            current_date = "March 10, 2024"
    
            # Query generation preserves topic
            mock_completions.create.return_value = QueryGenerationOutput(
                queries=["renewable energy storage 2024", "battery technology advances"],
                rationale=f"Queries for researching {original_topic}"
            )
    
            query_agent = QueryGenerationAgent(test_configuration)
            query_result = query_agent.run(QueryGenerationInput(
                research_topic=original_topic,
                number_of_queries=2,
                current_date=current_date
            ))
    
            # Verify topic is referenced in rationale
            assert original_topic in query_result.rationale
    
            # Web search uses generated queries
            mock_genai_client = MagicMock()
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
                    mock_response = MagicMock()
                    mock_response.text = "Renewable energy storage has improved significantly..."
    
                    mock_grounding.return_value = {
                        'status': 'success',
                        'response': mock_response,
                        'grounding_used': True,
                        'source': 'gemini_grounding'
                    }
    
                    with patch('agent.agents.extract_sources_from_grounding') as mock_extract:
                        with patch('agent.agents.add_inline_citations') as mock_citations:
                            with patch('agent.agents.create_citations_from_grounding') as mock_create_citations:
                                expected_sources = [
                                    Source(title="Energy Storage Research", url="https://energy.com", short_url="e1", label="Source 1")
                                ]
                                mock_extract.return_value = expected_sources
                                mock_citations.return_value = mock_response.text
                                mock_create_citations.return_value = []
    
>                               web_agent = WebSearchAgent(test_configuration)
                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

test/test_integration.py:383: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
backend/src/agent/base/base_research_agent.py:29: in __init__
    self._initialize_agent_config()
backend/src/agent/agents/web_search_agent.py:33: in _initialize_agent_config
    self.client = get_genai_client()
                  ^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    def get_genai_client():
        """Get configured GenAI client."""
        import os
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be set")
>       return genai.Client(api_key=api_key)
               ^^^^^^^^^^^^
E       AttributeError: module 'google.generativeai' has no attribute 'Client'

backend/src/agent/agents/web_search_agent.py:24: AttributeError
____________ TestAgentIntegration.test_search_function_integration _____________

self = <test.test_integration.TestAgentIntegration object at 0x7fcc1931b410>
mock_environment = {'GEMINI_API_KEY': 'test-gemini-key-12345', 'GOOGLE_API_KEY': 'test-google-key-12345', 'GOOGLE_SEARCH_ENGINE_ID': 'test-engine-id-12345', 'SEARCHAPI_API_KEY': 'test-searchapi-key-12345'}

    @pytest.mark.asyncio
    async def test_search_function_integration(self, mock_environment):
        """Test integration of search functions with real async behavior."""
        with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
            # Test successful grounding
            mock_response = MagicMock()
            mock_response.text = "Test response about quantum computing"
    
            mock_grounding.return_value = {
                'status': 'success',
                'response': mock_response,
                'grounding_used': True,
                'source': 'gemini_grounding'
            }
    
            with patch('agent.agents.extract_sources_from_grounding') as mock_extract:
                mock_extract.return_value = [
                    Source(title="Test Source", url="https://test.com", short_url="t1", label="Source 1")
                ]
    
                results = await search_web("quantum computing")
    
>               assert len(results) == 1
E               AssertionError: assert 5 == 1
E                +  where 5 = len([{'snippet': 'A quantum computer is a computer that uses quantum mechanical phenomena in an essential way: a quantum c...ers', 'source': 'duckduckgo', 'title': 'Classes of computers', 'url': 'https://duckduckgo.com/c/Classes_of_computers'}])

test/test_integration.py:450: AssertionError
----------------------------- Captured stdout call -----------------------------
2025-08-18 23:04:48 [N/A] ERROR search.gemini_grounding: Failed to initialize Gemini client: module 'google.generativeai' has no attribute 'Client'
2025-08-18 23:04:48 [N/A] WARNING search.manager: gemini_grounding provider not available
2025-08-18 23:04:48 [N/A] INFO search.manager: Initialized google_custom provider
2025-08-18 23:04:48 [N/A] INFO search.manager: Initialized searchapi provider
2025-08-18 23:04:48 [N/A] INFO search.manager: Initialized duckduckgo provider
2025-08-18 23:04:48 [N/A] INFO search.manager: Initialized knowledge fallback provider
2025-08-18 23:04:48 [N/A] INFO search.manager: Search manager initialized with 3 providers
2025-08-18 23:04:48 [N/A] INFO search.manager: Executing search with sequential strategy: 'quantum computing'
2025-08-18 23:04:48 [N/A] INFO search.manager: Trying google_custom provider
2025-08-18 23:04:48 [N/A] INFO search.google_custom: Attempting search: 'quantum computing' (max 5 results)
2025-08-18 23:04:48 [N/A] INFO agent.http_client: HTTP client initialized with 100 max connections
2025-08-18 23:04:48 [N/A] ERROR search.google_custom: ❌ Search failed: HTTP 400: {
  "error": {
    "code": 400,
    "message": "API key not valid. Please pass a valid API key.",
    "errors": [
      {
        "message": "API key not valid. Please pass a valid API key.",
        "domain": "global",
        "reason": "badRequest"
      }
    ],
    "status": "INVALID_ARGUMENT",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "API_KEY_INVALID",
        "domain": "googleapis.com",
        "metadata": {
          "service": "customsearch.googleapis.com"
        }
      },
      {
        "@type": "type.googleapis.com/google.rpc.LocalizedMessage",
        "locale": "en-US",
        "message": "API key not valid. Please pass a valid API key."
      }
    ]
  }
}

2025-08-18 23:04:48 [N/A] INFO search.google_custom: 🔄 Falling back to next provider
2025-08-18 23:04:48 [N/A] INFO search.manager: 🔄 google_custom failed, trying next provider
2025-08-18 23:04:48 [N/A] INFO search.manager: Trying searchapi provider
2025-08-18 23:04:48 [N/A] INFO search.searchapi: Attempting search: 'quantum computing' (max 5 results)
2025-08-18 23:04:49 [N/A] ERROR search.searchapi: ❌ Search failed: SearchAPI returned status 401: {
  "error": "Invalid API key."
}
2025-08-18 23:04:49 [N/A] INFO search.searchapi: 🔄 Falling back to next provider
2025-08-18 23:04:49 [N/A] INFO search.manager: 🔄 searchapi failed, trying next provider
2025-08-18 23:04:49 [N/A] INFO search.manager: Trying duckduckgo provider
2025-08-18 23:04:49 [N/A] INFO search.duckduckgo: Attempting search: 'quantum computing' (max 5 results)
2025-08-18 23:04:49 [N/A] INFO search.duckduckgo: ✅ Search returned 5 results
2025-08-18 23:04:49 [N/A] INFO search.manager: ✅ duckduckgo provided 5 results
------------------------------ Captured log call -------------------------------
ERROR    search.gemini_grounding:logging_config.py:156 Failed to initialize Gemini client: module 'google.generativeai' has no attribute 'Client'
WARNING  search.manager:logging_config.py:152 gemini_grounding provider not available
INFO     search.manager:logging_config.py:148 Initialized google_custom provider
INFO     search.manager:logging_config.py:148 Initialized searchapi provider
INFO     search.manager:logging_config.py:148 Initialized duckduckgo provider
INFO     search.manager:logging_config.py:148 Initialized knowledge fallback provider
INFO     search.manager:logging_config.py:148 Search manager initialized with 3 providers
INFO     search.manager:logging_config.py:148 Executing search with sequential strategy: 'quantum computing'
INFO     search.manager:logging_config.py:148 Trying google_custom provider
INFO     search.google_custom:logging_config.py:148 Attempting search: 'quantum computing' (max 5 results)
INFO     agent.http_client:http_client.py:102 HTTP client initialized with 100 max connections
ERROR    search.google_custom:logging_config.py:134 ❌ Search failed: HTTP 400: {
  "error": {
    "code": 400,
    "message": "API key not valid. Please pass a valid API key.",
    "errors": [
      {
        "message": "API key not valid. Please pass a valid API key.",
        "domain": "global",
        "reason": "badRequest"
      }
    ],
    "status": "INVALID_ARGUMENT",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "API_KEY_INVALID",
        "domain": "googleapis.com",
        "metadata": {
          "service": "customsearch.googleapis.com"
        }
      },
      {
        "@type": "type.googleapis.com/google.rpc.LocalizedMessage",
        "locale": "en-US",
        "message": "API key not valid. Please pass a valid API key."
      }
    ]
  }
}

INFO     search.google_custom:logging_config.py:126 🔄 Falling back to next provider
INFO     search.manager:logging_config.py:126 🔄 google_custom failed, trying next provider
INFO     search.manager:logging_config.py:148 Trying searchapi provider
INFO     search.searchapi:logging_config.py:148 Attempting search: 'quantum computing' (max 5 results)
ERROR    search.searchapi:logging_config.py:134 ❌ Search failed: SearchAPI returned status 401: {
  "error": "Invalid API key."
}
INFO     search.searchapi:logging_config.py:126 🔄 Falling back to next provider
INFO     search.manager:logging_config.py:126 🔄 searchapi failed, trying next provider
INFO     search.manager:logging_config.py:148 Trying duckduckgo provider
INFO     search.duckduckgo:logging_config.py:148 Attempting search: 'quantum computing' (max 5 results)
INFO     search.duckduckgo:logging_config.py:122 ✅ Search returned 5 results
INFO     search.manager:logging_config.py:122 ✅ duckduckgo provided 5 results
_____________ TestAgentIntegration.test_configuration_propagation ______________

self = <test.test_integration.TestAgentIntegration object at 0x7fcc1931bcd0>
mock_environment = {'GEMINI_API_KEY': 'test-gemini-key-12345', 'GOOGLE_API_KEY': 'test-google-key-12345', 'GOOGLE_SEARCH_ENGINE_ID': 'test-engine-id-12345', 'SEARCHAPI_API_KEY': 'test-searchapi-key-12345'}

    def test_configuration_propagation(self, mock_environment):
        """Test that configuration is properly propagated to all agents."""
        # Mock all missing Google GenAI types classes
        with patch('google.generativeai.types.GoogleSearch', create=True) as mock_google_search, \
             patch('google.generativeai.types.Tool', create=True) as mock_tool, \
             patch('google.generativeai.types.GoogleSearchRetrieval', create=True) as mock_google_search_retrieval, \
             patch('google.generativeai.types.DynamicRetrievalConfig', create=True) as mock_dynamic_retrieval_config, \
             patch('google.generativeai.types.DynamicRetrievalConfigMode', create=True) as mock_dynamic_retrieval_config_mode, \
             patch('google.generativeai.types.GenerateContentConfig', create=True) as mock_generate_content_config, \
             patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_google_search.return_value = MagicMock()
            mock_tool.return_value = MagicMock()
            mock_google_search_retrieval.return_value = MagicMock()
            mock_dynamic_retrieval_config.return_value = MagicMock()
            mock_dynamic_retrieval_config_mode.MODE_DYNAMIC = 'MODE_DYNAMIC'
            mock_generate_content_config.return_value = MagicMock()
    
            custom_config = Configuration(
                query_generator_model="gemini-2.5-flash",
                reflection_model="gemini-1.5-pro",
                answer_model="gemini-2.0-flash",
                number_of_initial_queries=5,
                max_research_loops=3
            )
    
            mock_agent_config = MagicMock()
            mock_agent_config_class.return_value = mock_agent_config
    
            # Test all agents receive correct configuration
            query_agent = QueryGenerationAgent(custom_config)
            assert query_agent.config == custom_config
            assert query_agent.config.query_generator_model == "gemini-2.5-flash"
    
            reflection_agent = ReflectionAgent(custom_config)
            assert reflection_agent.config == custom_config
            assert reflection_agent.config.reflection_model == "gemini-1.5-pro"
    
            finalization_agent = FinalizationAgent(custom_config)
            assert finalization_agent.config == custom_config
            assert finalization_agent.config.answer_model == "gemini-2.0-flash"
    
            mock_genai_client = MagicMock()
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
>               web_agent = WebSearchAgent(custom_config)
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

test/test_integration.py:498: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
backend/src/agent/base/base_research_agent.py:29: in __init__
    self._initialize_agent_config()
backend/src/agent/agents/web_search_agent.py:33: in _initialize_agent_config
    self.client = get_genai_client()
                  ^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    def get_genai_client():
        """Get configured GenAI client."""
        import os
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be set")
>       return genai.Client(api_key=api_key)
               ^^^^^^^^^^^^
E       AttributeError: module 'google.generativeai' has no attribute 'Client'

backend/src/agent/agents/web_search_agent.py:24: AttributeError
__________ TestAgentIntegration.test_error_propagation_across_agents ___________

self = <test.test_integration.TestAgentIntegration object at 0x7fcc19324410>
mock_environment = {'GEMINI_API_KEY': 'test-gemini-key-12345', 'GOOGLE_API_KEY': 'test-google-key-12345', 'GOOGLE_SEARCH_ENGINE_ID': 'test-engine-id-12345', 'SEARCHAPI_API_KEY': 'test-searchapi-key-12345'}
test_configuration = Configuration(query_generator_model='gemini-2.5-flash', reflection_model='gemini-2.5-flash', answer_model='gemini-2.5-...ry_delay=1.0, http_verify_ssl=True, rate_limit_requests_per_minute=60, rate_limit_burst=10, connection_pool_maxsize=20)

    def test_error_propagation_across_agents(self, mock_environment, test_configuration):
        """Test how errors propagate and are handled across the agent workflow."""
        # Mock all missing Google GenAI types classes
        with patch('google.generativeai.types.GoogleSearch', create=True) as mock_google_search, \
             patch('google.generativeai.types.Tool', create=True) as mock_tool, \
             patch('google.generativeai.types.GoogleSearchRetrieval', create=True) as mock_google_search_retrieval, \
             patch('google.generativeai.types.DynamicRetrievalConfig', create=True) as mock_dynamic_retrieval_config, \
             patch('google.generativeai.types.DynamicRetrievalConfigMode', create=True) as mock_dynamic_retrieval_config_mode, \
             patch('google.generativeai.types.GenerateContentConfig', create=True) as mock_generate_content_config, \
             patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_google_search.return_value = MagicMock()
            mock_tool.return_value = MagicMock()
            mock_google_search_retrieval.return_value = MagicMock()
            mock_dynamic_retrieval_config.return_value = MagicMock()
            mock_dynamic_retrieval_config_mode.MODE_DYNAMIC = 'MODE_DYNAMIC'
            mock_generate_content_config.return_value = MagicMock()
    
            mock_agent_config = MagicMock()
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_client.chat.completions = mock_completions
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
    
            # Query generation fails, uses fallback
            mock_completions.create.side_effect = Exception("Query generation failed")
    
            with patch('builtins.print'):
                query_agent = QueryGenerationAgent(test_configuration)
                query_result = query_agent.run(QueryGenerationInput(
                    research_topic="test topic",
                    number_of_queries=3,
                    current_date="January 15, 2024"
                ))
    
                # Should get fallback query
                assert isinstance(query_result, QueryGenerationOutput)
>               assert "capital of France" in query_result.queries[0]
E               AssertionError: assert 'capital of France' in 'What is test topic?'

test/test_integration.py:538: AssertionError
=============================== warnings summary ===============================
../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/_internal/_config.py:323
../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/_internal/_config.py:323
  /home/thomas/.local/lib/python3.11/site-packages/pydantic/_internal/_config.py:323: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

../../../../../../../home/thomas/.local/lib/python3.11/site-packages/pydantic/fields.py:1093: 15 warnings
  /home/thomas/.local/lib/python3.11/site-packages/pydantic/fields.py:1093: PydanticDeprecatedSince20: Using extra keyword arguments on `Field` is deprecated and will be removed. Use `json_schema_extra` instead. (Extra keys: 'metadata'). Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warn(

test/test_integration.py: 11 warnings
  /mnt/c/Users/Anwender/Projects/deep_seek/deep_seek/backend/src/agent/configuration.py:162: DeprecationWarning: from_gemini is deprecated and will be removed in a future version. Please use from_genai or from_provider instead. Install google-genai with: pip install google-genai
  Example migration:
    # Old way
    from instructor import from_gemini
    import google.generativeai as genai
    client = from_gemini(genai.GenerativeModel('gemini-1.5-flash'))
  
    # New way
    from instructor import from_genai
    from google import genai
    client = from_genai(genai.Client())
    # OR use from_provider
    client = instructor.from_provider('google/gemini-1.5-flash')
    client = instructor.from_gemini(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED test/test_integration.py::TestAgentIntegration::test_full_research_workflow
FAILED test/test_integration.py::TestAgentIntegration::test_workflow_with_reflection_loop
FAILED test/test_integration.py::TestAgentIntegration::test_cross_agent_data_flow
FAILED test/test_integration.py::TestAgentIntegration::test_search_function_integration
FAILED test/test_integration.py::TestAgentIntegration::test_configuration_propagation
FAILED test/test_integration.py::TestAgentIntegration::test_error_propagation_across_agents
======================== 6 failed, 28 warnings in 1.32s ========================
[?1034h