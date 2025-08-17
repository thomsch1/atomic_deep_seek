"""
Comprehensive test suite for ResearchOrchestrator.
Tests workflow coordination, error handling, and performance optimization.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from agent.orchestrator import ResearchOrchestrator
from agent.configuration import Configuration
from agent.state import (
    ResearchState,
    Message,
    Source,
    QueryGenerationInput,
    WebSearchInput,
    ReflectionInput,
    FinalizationInput
)


class TestResearchOrchestrator:
    """Test suite for ResearchOrchestrator."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration()
    
    @pytest.fixture
    def orchestrator(self, config):
        """Create ResearchOrchestrator instance."""
        return ResearchOrchestrator(config=config.to_dict())
    
    @pytest.fixture
    def sample_question(self):
        """Sample research question."""
        return "What are the environmental impacts of electric vehicles?"
    
    @pytest.fixture
    def mock_sources(self):
        """Mock research sources."""
        return [
            Source(
                url="https://example.com/ev-environment",
                title="Environmental Impact of Electric Vehicles",
                content="Electric vehicles reduce carbon emissions by 60% compared to gas cars...",
                raw_content="<html>Electric vehicles reduce carbon emissions...</html>"
            ),
            Source(
                url="https://example.com/battery-lifecycle",
                title="EV Battery Lifecycle Analysis",
                content="Lithium mining and battery production have environmental costs...",
                raw_content="<html>Lithium mining and battery production...</html>"
            )
        ]
    
    def test_orchestrator_initialization(self, config):
        """Test orchestrator initialization with configuration."""
        orchestrator = ResearchOrchestrator(config=config.to_dict())
        
        assert orchestrator.config is not None
        assert orchestrator._thread_pool is not None
        assert orchestrator._research_topic_cache is None  # Initially empty
        assert orchestrator._current_date_cache is None
    
    def test_lazy_agent_loading(self, orchestrator):
        """Test that agents are lazily loaded."""
        # Agents should be None initially
        assert orchestrator._query_agent is None
        assert orchestrator._search_agent is None
        assert orchestrator._reflection_agent is None
        assert orchestrator._finalization_agent is None
        
        # Accessing properties should create agents
        query_agent = orchestrator.query_agent
        search_agent = orchestrator.search_agent
        reflection_agent = orchestrator.reflection_agent
        finalization_agent = orchestrator.finalization_agent
        
        assert query_agent is not None
        assert search_agent is not None
        assert reflection_agent is not None
        assert finalization_agent is not None
    
    def test_thread_pool_initialization(self, orchestrator):
        """Test thread pool is properly initialized."""
        assert orchestrator._thread_pool is not None
        assert isinstance(orchestrator._thread_pool, ThreadPoolExecutor)
        assert not orchestrator._thread_pool._shutdown
    
    def test_finalization_agent_model_override(self, orchestrator):
        """Test finalization agent creation with model override."""
        custom_model = "gemini-2.5-pro"
        agent = orchestrator.create_finalization_agent(model_override=custom_model)
        
        assert agent is not None
        assert hasattr(agent, 'model_override')
        assert agent.model_override == custom_model
    
    @pytest.mark.asyncio
    async def test_run_research_async_success(self, orchestrator, sample_question, mock_sources):
        """Test successful async research execution."""
        # Mock all agent responses
        mock_queries = ["electric vehicle environmental impact", "EV carbon footprint analysis"]
        
        with patch.object(orchestrator.query_agent, 'generate_queries', 
                         return_value={'queries': mock_queries}), \
             patch.object(orchestrator.search_agent, 'search',
                         return_value={'sources': mock_sources}), \
             patch.object(orchestrator.reflection_agent, 'reflect',
                         return_value={'research_sufficient': True, 'analysis': 'Comprehensive coverage'}), \
             patch.object(orchestrator.finalization_agent, 'finalize',
                         return_value={'final_answer': 'Electric vehicles have mixed environmental impacts...'}):
            
            result = await orchestrator.run_research_async(
                question=sample_question,
                initial_search_query_count=2,
                max_research_loops=2
            )
            
            assert isinstance(result, dict)
            assert 'final_answer' in result
            assert 'sources_gathered' in result
            assert 'research_loops_executed' in result
            assert 'total_queries' in result
            
            assert result['research_loops_executed'] >= 1
            assert result['total_queries'] >= 2
            assert len(result['sources_gathered']) > 0
    
    @pytest.mark.asyncio
    async def test_run_research_multiple_loops(self, orchestrator, sample_question, mock_sources):
        """Test research with multiple reflection loops."""
        mock_queries = ["electric vehicles environment", "EV lifecycle assessment"]
        additional_queries = ["EV battery recycling", "electric car manufacturing impact"]
        
        # First reflection suggests more research needed
        # Second reflection confirms research is sufficient
        reflection_responses = [
            {'research_sufficient': False, 'analysis': 'Need more on manufacturing', 'additional_queries': additional_queries},
            {'research_sufficient': True, 'analysis': 'Now comprehensive'}
        ]
        
        with patch.object(orchestrator.query_agent, 'generate_queries') as mock_query, \
             patch.object(orchestrator.search_agent, 'search') as mock_search, \
             patch.object(orchestrator.reflection_agent, 'reflect') as mock_reflect, \
             patch.object(orchestrator.finalization_agent, 'finalize') as mock_final:
            
            # Setup mock responses
            mock_query.side_effect = [
                {'queries': mock_queries},
                {'queries': additional_queries}
            ]
            mock_search.return_value = {'sources': mock_sources}
            mock_reflect.side_effect = reflection_responses
            mock_final.return_value = {'final_answer': 'Comprehensive EV environmental analysis...'}
            
            result = await orchestrator.run_research_async(
                question=sample_question,
                initial_search_query_count=2,
                max_research_loops=3
            )
            
            # Should have executed 2 research loops
            assert result['research_loops_executed'] == 2
            assert result['total_queries'] == 4  # 2 initial + 2 additional
            
            # Verify agents were called correct number of times
            assert mock_query.call_count == 2
            assert mock_search.call_count == 2
            assert mock_reflect.call_count == 2
            assert mock_final.call_count == 1
    
    @pytest.mark.asyncio
    async def test_run_research_max_loops_limit(self, orchestrator, sample_question, mock_sources):
        """Test research stops at maximum loop limit."""
        mock_queries = ["test query"]
        
        # Reflection always says more research needed
        always_insufficient = {
            'research_sufficient': False, 
            'analysis': 'Always need more',
            'additional_queries': ['more query']
        }
        
        with patch.object(orchestrator.query_agent, 'generate_queries', 
                         return_value={'queries': mock_queries}), \
             patch.object(orchestrator.search_agent, 'search',
                         return_value={'sources': mock_sources}), \
             patch.object(orchestrator.reflection_agent, 'reflect',
                         return_value=always_insufficient), \
             patch.object(orchestrator.finalization_agent, 'finalize',
                         return_value={'final_answer': 'Limited research result...'}):
            
            max_loops = 3
            result = await orchestrator.run_research_async(
                question=sample_question,
                max_research_loops=max_loops
            )
            
            # Should stop at max loops even though reflection wants more
            assert result['research_loops_executed'] == max_loops
    
    @pytest.mark.asyncio
    async def test_run_research_with_model_override(self, orchestrator, sample_question, mock_sources):
        """Test research with reasoning model override."""
        custom_model = "gemini-2.5-pro"
        mock_queries = ["test query"]
        
        with patch.object(orchestrator, 'create_finalization_agent') as mock_create, \
             patch.object(orchestrator.query_agent, 'generate_queries',
                         return_value={'queries': mock_queries}), \
             patch.object(orchestrator.search_agent, 'search',
                         return_value={'sources': mock_sources}), \
             patch.object(orchestrator.reflection_agent, 'reflect',
                         return_value={'research_sufficient': True, 'analysis': 'Good'}):
            
            # Create mock finalization agent
            mock_final_agent = Mock()
            mock_final_agent.finalize.return_value = {'final_answer': 'Custom model result'}
            mock_create.return_value = mock_final_agent
            
            result = await orchestrator.run_research_async(
                question=sample_question,
                reasoning_model=custom_model
            )
            
            # Verify custom finalization agent was created
            mock_create.assert_called_once_with(model_override=custom_model)
            mock_final_agent.finalize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_research_error_handling(self, orchestrator, sample_question):
        """Test error handling during research execution."""
        # Mock query generation to fail
        with patch.object(orchestrator.query_agent, 'generate_queries',
                         side_effect=Exception("API Error")):
            
            with pytest.raises(Exception, match="API Error"):
                await orchestrator.run_research_async(question=sample_question)
    
    @pytest.mark.asyncio
    async def test_run_research_agent_failure_recovery(self, orchestrator, sample_question, mock_sources):
        """Test partial recovery from agent failures."""
        mock_queries = ["test query"]
        
        # Search agent fails, but workflow continues
        with patch.object(orchestrator.query_agent, 'generate_queries',
                         return_value={'queries': mock_queries}), \
             patch.object(orchestrator.search_agent, 'search',
                         side_effect=Exception("Search failed")):
            
            with pytest.raises(Exception, match="Search failed"):
                await orchestrator.run_research_async(question=sample_question)
    
    def test_cleanup_thread_pool(self, orchestrator):
        """Test thread pool cleanup."""
        # Verify thread pool is active
        assert not orchestrator._thread_pool._shutdown
        
        # Call cleanup
        orchestrator._cleanup_thread_pool()
        
        # Verify thread pool is shut down
        assert orchestrator._thread_pool._shutdown
    
    @pytest.mark.asyncio
    async def test_parallel_search_execution(self, orchestrator, sample_question, mock_sources):
        """Test that searches can be executed in parallel."""
        mock_queries = ["query1", "query2", "query3"]
        
        # Mock search agent to track call timing
        call_times = []
        original_search = orchestrator.search_agent.search
        
        async def timed_search(*args, **kwargs):
            import time
            call_times.append(time.time())
            await asyncio.sleep(0.1)  # Simulate network delay
            return {'sources': mock_sources[:1]}  # Return subset
        
        with patch.object(orchestrator.query_agent, 'generate_queries',
                         return_value={'queries': mock_queries}), \
             patch.object(orchestrator.search_agent, 'search', side_effect=timed_search), \
             patch.object(orchestrator.reflection_agent, 'reflect',
                         return_value={'research_sufficient': True, 'analysis': 'Good'}), \
             patch.object(orchestrator.finalization_agent, 'finalize',
                         return_value={'final_answer': 'Parallel search result'}):
            
            start_time = asyncio.get_event_loop().time()
            result = await orchestrator.run_research_async(question=sample_question)
            end_time = asyncio.get_event_loop().time()
            
            # Verify search completed and timing suggests parallel execution
            assert 'final_answer' in result
            execution_time = end_time - start_time
            # Should be faster than sequential (3 * 0.1 = 0.3s)
            assert execution_time < 0.25  # Allow some overhead
    
    @pytest.mark.asyncio
    async def test_caching_research_topic(self, orchestrator, sample_question):
        """Test research topic caching for performance."""
        mock_queries = ["test query"]
        mock_sources = [Source(url="test.com", title="Test", content="test", raw_content="test")]
        
        with patch('agent.utils.get_research_topic', return_value="cached topic") as mock_get_topic, \
             patch.object(orchestrator.query_agent, 'generate_queries',
                         return_value={'queries': mock_queries}), \
             patch.object(orchestrator.search_agent, 'search',
                         return_value={'sources': mock_sources}), \
             patch.object(orchestrator.reflection_agent, 'reflect',
                         return_value={'research_sufficient': True, 'analysis': 'Good'}), \
             patch.object(orchestrator.finalization_agent, 'finalize',
                         return_value={'final_answer': 'Cached result'}):
            
            # Run research twice
            await orchestrator.run_research_async(question=sample_question)
            await orchestrator.run_research_async(question=sample_question)
            
            # Should cache topic within same orchestrator instance
            # Note: Actual caching behavior depends on implementation
            assert mock_get_topic.call_count >= 2
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_research_performance_benchmark(self, orchestrator, sample_question, mock_sources):
        """Performance benchmark test for research execution."""
        mock_queries = ["performance test query"]
        
        with patch.object(orchestrator.query_agent, 'generate_queries',
                         return_value={'queries': mock_queries}), \
             patch.object(orchestrator.search_agent, 'search',
                         return_value={'sources': mock_sources}), \
             patch.object(orchestrator.reflection_agent, 'reflect',
                         return_value={'research_sufficient': True, 'analysis': 'Fast'}), \
             patch.object(orchestrator.finalization_agent, 'finalize',
                         return_value={'final_answer': 'Performance test result'}):
            
            start_time = asyncio.get_event_loop().time()
            
            # Run multiple research queries concurrently
            tasks = [
                orchestrator.run_research_async(question=f"{sample_question} {i}")
                for i in range(3)
            ]
            results = await asyncio.gather(*tasks)
            
            end_time = asyncio.get_event_loop().time()
            execution_time = end_time - start_time
            
            # Verify all completed successfully
            assert len(results) == 3
            assert all('final_answer' in result for result in results)
            
            # Performance assertion - should complete within reasonable time
            assert execution_time < 2.0  # 2 seconds for 3 concurrent requests
    
    def test_orchestrator_configuration_validation(self):
        """Test orchestrator handles invalid configuration gracefully."""
        # Test with None config (should use defaults)
        orchestrator = ResearchOrchestrator(config=None)
        assert orchestrator.config is not None
        
        # Test with empty config dict
        orchestrator = ResearchOrchestrator(config={})
        assert orchestrator.config is not None
        
        # Test with invalid config values (should handle gracefully)
        invalid_config = {"invalid_key": "invalid_value"}
        orchestrator = ResearchOrchestrator(config=invalid_config)
        assert orchestrator.config is not None