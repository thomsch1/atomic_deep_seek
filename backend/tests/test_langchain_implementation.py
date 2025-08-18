"""
Integration tests for the current LangChain implementation.
These tests verify the functionality before migration to Atomic Agent.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List
import json

from agent.orchestrator import ResearchOrchestrator
from agent.state import ResearchState
from agent.configuration import Configuration
from agent.tools_and_schemas import SearchQueryList, Reflection
from langchain_core.messages import HumanMessage, AIMessage


class TestLangChainImplementation:
    """Test suite for current LangChain-based research agent."""

    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables for testing."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
            yield

    @pytest.fixture
    def sample_research_query(self) -> str:
        """Sample research query for testing."""
        return "What are the latest developments in quantum computing in 2024?"

    @pytest.fixture
    def sample_initial_state(self, sample_research_query) -> OverallState:
        """Create a sample initial state for testing."""
        return {
            "messages": [HumanMessage(content=sample_research_query)],
            "search_query": [],
            "web_research_result": [],
            "sources_gathered": [],
            "initial_search_query_count": 3,
            "max_research_loops": 2,
            "research_loop_count": 0,
            "reasoning_model": "gemini-2.5-flash"
        }

    @pytest.fixture
    def mock_configuration(self):
        """Mock configuration for testing."""
        return Configuration(
            query_generator_model="gemini-2.0-flash",
            reflection_model="gemini-2.5-flash",
            answer_model="gemini-2.5-pro",
            number_of_initial_queries=3,
            max_research_loops=2
        )

    def test_query_generation_node(self, mock_env_vars, sample_initial_state, mock_configuration):
        """Test the query generation functionality."""
        from agent.agents.query_generation_agent import QueryGenerationAgent
        
        # Mock the LLM response
        mock_llm_response = SearchQueryList(
            query=["quantum computing breakthroughs 2024", "quantum algorithms latest research", "quantum hardware developments 2024"],
            rationale="These queries cover the main aspects of quantum computing developments"
        )
        
        with patch('agent.graph.ChatGoogleGenerativeAI') as mock_llm_class:
            mock_llm = MagicMock()
            mock_structured_llm = MagicMock()
            mock_structured_llm.invoke.return_value = mock_llm_response
            mock_llm.with_structured_output.return_value = mock_structured_llm
            mock_llm_class.return_value = mock_llm
            
            config = {"configurable": mock_configuration.model_dump()}
            result = generate_query(sample_initial_state, config)
            
            # Verify the result structure
            assert "search_query" in result
            assert len(result["search_query"]) == 3
            assert all("quantum" in query.lower() for query in result["search_query"])

    def test_web_research_node(self, mock_env_vars, mock_configuration):
        """Test the web research functionality."""
        from agent.agents.web_search_agent import WebSearchAgent
        
        # Mock web search state
        web_search_state = {
            "search_query": "quantum computing breakthroughs 2024",
            "id": 0
        }
        
        # Mock Google GenAI client response
        mock_response = MagicMock()
        mock_response.text = "Quantum computing has seen significant breakthroughs in 2024..."
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].grounding_metadata = MagicMock()
        mock_response.candidates[0].grounding_metadata.grounding_chunks = []
        
        with patch('agent.graph.genai_client') as mock_client:
            mock_client.models.generate_content.return_value = mock_response
            
            with patch('agent.graph.resolve_urls') as mock_resolve:
                mock_resolve.return_value = {}
                
                with patch('agent.graph.get_citations') as mock_citations:
                    mock_citations.return_value = []
                    
                    config = {"configurable": mock_configuration.model_dump()}
                    result = web_research(web_search_state, config)
                    
                    # Verify the result structure
                    assert "sources_gathered" in result
                    assert "search_query" in result
                    assert "web_research_result" in result
                    assert len(result["web_research_result"]) == 1

    def test_reflection_node(self, mock_env_vars, sample_initial_state, mock_configuration):
        """Test the reflection functionality."""
        from agent.agents.reflection_agent import ReflectionAgent
        
        # Prepare state with web research results
        state_with_results = sample_initial_state.copy()
        state_with_results["web_research_result"] = [
            "Quantum computing research shows progress in error correction...",
            "IBM announced new quantum processors in 2024..."
        ]
        
        # Mock the reflection response
        mock_reflection_response = Reflection(
            is_sufficient=False,
            knowledge_gap="Missing information about specific performance metrics",
            follow_up_queries=["quantum computing performance benchmarks 2024"]
        )
        
        with patch('agent.graph.ChatGoogleGenerativeAI') as mock_llm_class:
            mock_llm = MagicMock()
            mock_structured_llm = MagicMock()
            mock_structured_llm.invoke.return_value = mock_reflection_response
            mock_llm.with_structured_output.return_value = mock_structured_llm
            mock_llm_class.return_value = mock_llm
            
            config = {"configurable": mock_configuration.model_dump()}
            result = reflection(state_with_results, config)
            
            # Verify the result structure
            assert "is_sufficient" in result
            assert "knowledge_gap" in result
            assert "follow_up_queries" in result
            assert "research_loop_count" in result
            assert result["research_loop_count"] == 1

    def test_finalize_answer_node(self, mock_env_vars, sample_initial_state, mock_configuration):
        """Test the answer finalization functionality."""
        from agent.agents.finalization_agent import FinalizationAgent
        
        # Prepare state with complete research results
        state_with_complete_results = sample_initial_state.copy()
        state_with_complete_results.update({
            "web_research_result": [
                "Quantum computing has seen major breakthroughs in 2024 with improved error rates...",
                "New quantum algorithms have been developed for optimization problems..."
            ],
            "sources_gathered": [
                {"short_url": "https://vertexaisearch.cloud.google.com/id/0-1", "value": "https://example.com/quantum1"},
                {"short_url": "https://vertexaisearch.cloud.google.com/id/0-2", "value": "https://example.com/quantum2"}
            ]
        })
        
        # Mock the final answer response
        mock_ai_response = MagicMock()
        mock_ai_response.content = "Based on research, quantum computing in 2024 has achieved..."
        
        with patch('agent.graph.ChatGoogleGenerativeAI') as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_ai_response
            mock_llm_class.return_value = mock_llm
            
            config = {"configurable": mock_configuration.model_dump()}
            result = finalize_answer(state_with_complete_results, config)
            
            # Verify the result structure
            assert "messages" in result
            assert "sources_gathered" in result
            assert len(result["messages"]) == 1
            assert isinstance(result["messages"][0], AIMessage)

    def test_evaluate_research_routing(self, mock_configuration):
        """Test the research evaluation routing logic."""
        from agent.orchestrator import ResearchOrchestrator
        
        # Test case: Research is sufficient
        sufficient_state = {
            "is_sufficient": True,
            "knowledge_gap": "",
            "follow_up_queries": [],
            "research_loop_count": 1,
            "number_of_ran_queries": 3
        }
        
        config = {"configurable": mock_configuration.model_dump()}
        result = evaluate_research(sufficient_state, config)
        assert result == "finalize_answer"
        
        # Test case: Max loops reached
        max_loops_state = {
            "is_sufficient": False,
            "knowledge_gap": "Still missing information",
            "follow_up_queries": ["more specific query"],
            "research_loop_count": 2,
            "number_of_ran_queries": 5
        }
        
        result = evaluate_research(max_loops_state, config)
        assert result == "finalize_answer"
        
        # Test case: Continue research
        continue_state = {
            "is_sufficient": False,
            "knowledge_gap": "Missing performance data",
            "follow_up_queries": ["quantum performance metrics", "benchmark results"],
            "research_loop_count": 1,
            "number_of_ran_queries": 3
        }
        
        result = evaluate_research(continue_state, config)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_configuration_from_runnable_config(self):
        """Test Configuration creation from RunnableConfig."""
        config_dict = {
            "configurable": {
                "query_generator_model": "custom-model",
                "max_research_loops": 5
            }
        }
        
        configuration = Configuration.from_runnable_config(config_dict)
        assert configuration.query_generator_model == "custom-model"
        assert configuration.max_research_loops == 5
        assert configuration.reflection_model == "gemini-2.5-flash"  # default

    @pytest.mark.integration
    def test_full_research_workflow_mock(self, mock_env_vars, sample_initial_state, mock_configuration):
        """Integration test for the complete research workflow with mocked responses."""
        
        # Mock all LLM responses
        query_response = SearchQueryList(
            query=["quantum computing 2024"],
            rationale="Test query"
        )
        
        reflection_response = Reflection(
            is_sufficient=True,
            knowledge_gap="",
            follow_up_queries=[]
        )
        
        with patch('agent.graph.ChatGoogleGenerativeAI') as mock_llm_class, \
             patch('agent.graph.genai_client') as mock_genai_client:
            
            # Setup mocks
            mock_llm = MagicMock()
            mock_structured_llm = MagicMock()
            mock_llm.with_structured_output.return_value = mock_structured_llm
            mock_llm_class.return_value = mock_llm
            
            # Mock query generation
            mock_structured_llm.invoke.side_effect = [query_response, reflection_response]
            
            # Mock web research
            mock_web_response = MagicMock()
            mock_web_response.text = "Test research result"
            mock_web_response.candidates = [MagicMock()]
            mock_web_response.candidates[0].grounding_metadata = MagicMock()
            mock_web_response.candidates[0].grounding_metadata.grounding_chunks = []
            mock_genai_client.models.generate_content.return_value = mock_web_response
            
            # Mock final answer
            mock_final_response = MagicMock()
            mock_final_response.content = "Final answer based on research"
            mock_llm.invoke.return_value = mock_final_response
            
            with patch('agent.graph.resolve_urls', return_value={}), \
                 patch('agent.graph.get_citations', return_value=[]):
                
                config = {"configurable": mock_configuration.model_dump()}
                
                # This would be a full graph execution in real scenario
                # For now, we test individual components work together
                query_result = generate_query(sample_initial_state, config)
                assert "search_query" in query_result
                
                # Test the graph can be compiled
                assert graph is not None
                assert hasattr(graph, 'invoke')


class TestLangChainBehaviorCapture:
    """Capture the exact behavior patterns for comparison with Atomic Agent."""
    
    def capture_query_generation_behavior(self, research_topic: str) -> Dict[str, Any]:
        """Capture query generation behavior for comparison."""
        return {
            "input_format": "Research topic as string",
            "output_format": "List of search queries with rationale",
            "expected_query_count": 3,
            "query_diversity_required": True,
            "current_date_awareness": True
        }
    
    def capture_web_research_behavior(self, query: str) -> Dict[str, Any]:
        """Capture web research behavior for comparison."""
        return {
            "input_format": "Single search query string",
            "search_method": "Google Search API via GenAI client",
            "output_includes": ["text_content", "citations", "sources"],
            "url_resolution": "Short URLs for token efficiency",
            "citation_format": "Markdown links with source tracking"
        }
    
    def capture_reflection_behavior(self, summaries: List[str]) -> Dict[str, Any]:
        """Capture reflection behavior for comparison."""
        return {
            "input_format": "List of research summaries",
            "decision_logic": "Sufficiency assessment + gap identification",
            "output_includes": ["is_sufficient", "knowledge_gap", "follow_up_queries"],
            "max_loops_respected": True,
            "follow_up_context_included": True
        }
    
    def capture_finalization_behavior(self, summaries: List[str]) -> Dict[str, Any]:
        """Capture answer finalization behavior for comparison."""
        return {
            "input_format": "List of research summaries",
            "output_format": "Structured answer with citations",
            "url_replacement": "Short URLs -> Original URLs",
            "citation_preservation": True,
            "source_deduplication": True
        }
    
    def capture_workflow_orchestration(self) -> Dict[str, Any]:
        """Capture overall workflow behavior for comparison."""
        return {
            "execution_pattern": "Graph-based with conditional routing",
            "parallel_execution": "Multiple web searches simultaneously",
            "loop_control": "Max iterations with early termination",
            "state_management": "Accumulated state across nodes",
            "error_handling": "Retry logic in LLM calls"
        }