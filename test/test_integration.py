"""
Integration tests for the complete agents.py workflow.
Tests end-to-end functionality and agent interactions.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import sys
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from agent.agents import (
    QueryGenerationAgent,
    WebSearchAgent,
    ReflectionAgent,
    FinalizationAgent,
    search_web,
    get_genai_client
)
from agent.state import (
    QueryGenerationInput,
    QueryGenerationOutput,
    WebSearchInput,
    WebSearchOutput,
    ReflectionInput,
    ReflectionOutput,
    FinalizationInput,
    FinalizationOutput,
    Source,
    Citation
)
from agent.configuration import Configuration


class TestAgentIntegration:
    """Test complete workflow integration between agents."""
    
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
                                
                                web_agent = WebSearchAgent(test_configuration)
                                
                                search_results = []
                                for i, query in enumerate(query_result.queries):
                                    search_input = WebSearchInput(
                                        search_query=query,
                                        query_id=i+1,
                                        current_date="January 15, 2024"
                                    )
                                    search_result = web_agent.run(search_input)
                                    search_results.append(search_result)
                                
                                assert len(search_results) == 2
                                assert all(isinstance(r, WebSearchOutput) for r in search_results)
                                assert all(len(r.sources) > 0 for r in search_results)
            
            # Step 3: Reflection on gathered research
            mock_completions.create.return_value = ReflectionOutput(
                is_sufficient=True,
                knowledge_gap="",
                follow_up_queries=[]
            )
            
            reflection_agent = ReflectionAgent(test_configuration)
            reflection_input = ReflectionInput(
                research_topic="quantum computing developments",
                summaries=[result.content for result in search_results],
                current_loop=1
            )
            reflection_result = reflection_agent.run(reflection_input)
            
            assert reflection_result.is_sufficient is True
            assert len(reflection_result.follow_up_queries) == 0
            
            # Step 4: Finalization
            all_sources = []
            for result in search_results:
                all_sources.extend(result.sources)
            
            mock_completions.create.return_value = FinalizationOutput(
                final_answer="Based on comprehensive research, quantum computing has made remarkable progress in 2024...",
                used_sources=all_sources[:3]
            )
            
            finalization_agent = FinalizationAgent(test_configuration)
            finalization_input = FinalizationInput(
                research_topic="quantum computing developments",
                summaries=[result.content for result in search_results],
                sources=all_sources,
                current_date="January 15, 2024"
            )
            final_result = finalization_agent.run(finalization_input)
            
            assert isinstance(final_result, FinalizationOutput)
            assert "remarkable progress" in final_result.final_answer
            assert len(final_result.used_sources) > 0
    
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
                                
                                web_agent = WebSearchAgent(test_configuration)
                                initial_search = web_agent.run(WebSearchInput(
                                    search_query=initial_query.queries[0],
                                    query_id=1,
                                    current_date="January 15, 2024"
                                ))
            
            # Reflection identifies need for more research
            mock_completions.create.return_value = ReflectionOutput(
                is_sufficient=False,
                knowledge_gap="Need specific information about FDA approvals and clinical trials",
                follow_up_queries=["AI healthcare FDA approvals 2024", "AI clinical trials results"]
            )
            
            reflection_agent = ReflectionAgent(test_configuration)
            reflection_result = reflection_agent.run(ReflectionInput(
                research_topic="AI in healthcare",
                summaries=[initial_search.content],
                current_loop=1
            ))
            
            assert reflection_result.is_sufficient is False
            assert len(reflection_result.follow_up_queries) == 2
            
            # Additional research based on reflection
            additional_searches = []
            for follow_up_query in reflection_result.follow_up_queries:
                with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                    with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
                        mock_response.text = f"Additional research about {follow_up_query}..."
                        mock_grounding.return_value = {
                            'status': 'success',
                            'response': mock_response,
                            'grounding_used': True,
                            'source': 'gemini_grounding'
                        }
                        
                        with patch('agent.agents.extract_sources_from_grounding') as mock_extract:
                            with patch('agent.agents.add_inline_citations') as mock_citations:
                                with patch('agent.agents.create_citations_from_grounding') as mock_create_citations:
                                    mock_extract.return_value = mock_sources
                                    mock_citations.return_value = f"Content about {follow_up_query}"
                                    mock_create_citations.return_value = []
                                    
                                    search_result = web_agent.run(WebSearchInput(
                                        search_query=follow_up_query,
                                        query_id=len(additional_searches) + 2,
                                        current_date="January 15, 2024"
                                    ))
                                    additional_searches.append(search_result)
            
            # Final reflection shows research is sufficient
            all_summaries = [initial_search.content] + [r.content for r in additional_searches]
            mock_completions.create.return_value = ReflectionOutput(
                is_sufficient=True,
                knowledge_gap="",
                follow_up_queries=[]
            )
            
            final_reflection = reflection_agent.run(ReflectionInput(
                research_topic="AI in healthcare",
                summaries=all_summaries,
                current_loop=2
            ))
            
            assert final_reflection.is_sufficient is True
            
            # Finalization with all gathered research
            all_sources = [initial_search.sources[0]] + [s for search in additional_searches for s in search.sources]
            mock_completions.create.return_value = FinalizationOutput(
                final_answer="Comprehensive analysis of AI in healthcare including FDA approvals and clinical trials...",
                used_sources=all_sources[:3]
            )
            
            finalization_agent = FinalizationAgent(test_configuration)
            final_result = finalization_agent.run(FinalizationInput(
                research_topic="AI in healthcare",
                summaries=all_summaries,
                sources=all_sources,
                current_date="January 15, 2024"
            ))
            
            assert "comprehensive analysis" in final_result.final_answer.lower()
            assert len(final_result.used_sources) > 0
    
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
                                
                                web_agent = WebSearchAgent(test_configuration)
                                search_input = WebSearchInput(
                                    search_query=query_result.queries[0],
                                    query_id=1,
                                    current_date=current_date
                                )
                                search_result = web_agent.run(search_input)
                                
                                # Verify search query was used correctly
                                assert query_result.queries[0] in search_input.search_query
                                assert len(search_result.sources) == 1
                                assert search_result.sources[0].title == "Energy Storage Research"
            
            # Reflection uses search content
            mock_completions.create.return_value = ReflectionOutput(
                is_sufficient=True,
                knowledge_gap="",
                follow_up_queries=[]
            )
            
            reflection_agent = ReflectionAgent(test_configuration)
            reflection_result = reflection_agent.run(ReflectionInput(
                research_topic=original_topic,
                summaries=[search_result.content],
                current_loop=1
            ))
            
            # Finalization uses all previous data
            mock_completions.create.return_value = FinalizationOutput(
                final_answer=f"Based on research about {original_topic}, significant progress has been made...",
                used_sources=search_result.sources
            )
            
            finalization_agent = FinalizationAgent(test_configuration)
            final_result = finalization_agent.run(FinalizationInput(
                research_topic=original_topic,
                summaries=[search_result.content],
                sources=search_result.sources,
                current_date=current_date
            ))
            
            # Verify data consistency throughout workflow
            assert original_topic in final_result.final_answer
            assert final_result.used_sources[0].title == "Energy Storage Research"
    
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
                
                assert len(results) == 1
                assert results[0]['source'] == 'gemini_grounding'
                assert results[0]['title'] == 'Test Source'
                assert results[0]['url'] == 'https://test.com'
    
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
                web_agent = WebSearchAgent(custom_config)
                assert web_agent.config == custom_config
    
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
                assert "capital of France" in query_result.queries[0]
                
                # Web search can still proceed with fallback query
                mock_genai_client = MagicMock()
                with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                    with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
                        mock_grounding.return_value = {
                            'status': 'error',
                            'error': 'Search failed',
                            'source': 'gemini_grounding'
                        }
                        
                        with patch('agent.agents.run_async_search') as mock_search:
                            mock_search.return_value = [
                                {'title': 'Fallback Result', 'url': 'https://fallback.com', 'snippet': 'Fallback content'}
                            ]
                            
                            mock_genai_client.models.generate_content.return_value.text = "Synthesized response"
                            
                            web_agent = WebSearchAgent(test_configuration)
                            search_result = web_agent.run(WebSearchInput(
                                search_query=query_result.queries[0],
                                query_id=1,
                                current_date="January 15, 2024"
                            ))
                            
                            # Should get fallback search result
                            assert isinstance(search_result, WebSearchOutput)
                            assert len(search_result.sources) > 0
                
                # Reflection can proceed with whatever content is available
                mock_completions.create.side_effect = None
                mock_completions.create.return_value = ReflectionOutput(
                    is_sufficient=True,
                    knowledge_gap="Limited information available",
                    follow_up_queries=[]
                )
                
                reflection_agent = ReflectionAgent(test_configuration)
                reflection_result = reflection_agent.run(ReflectionInput(
                    research_topic="test topic",
                    summaries=[search_result.content],
                    current_loop=1
                ))
                
                assert isinstance(reflection_result, ReflectionOutput)
                
                # Finalization can complete the workflow
                mock_completions.create.return_value = FinalizationOutput(
                    final_answer="Final answer based on limited research",
                    used_sources=search_result.sources
                )
                
                finalization_agent = FinalizationAgent(test_configuration)
                final_result = finalization_agent.run(FinalizationInput(
                    research_topic="test topic",
                    summaries=[search_result.content],
                    sources=search_result.sources,
                    current_date="January 15, 2024"
                ))
                
                assert isinstance(final_result, FinalizationOutput)
                assert "limited research" in final_result.final_answer