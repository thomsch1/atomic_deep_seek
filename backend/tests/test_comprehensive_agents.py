"""
Comprehensive test suite for all Atomic Agents in the Deep Search AI system.
Tests individual agent functionality, error handling, and integration points.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from agent.agents import (
    QueryGenerationAgent,
    WebSearchAgent, 
    ReflectionAgent,
    FinalizationAgent
)
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


class TestQueryGenerationAgent:
    """Test suite for QueryGenerationAgent."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration()
    
    @pytest.fixture
    def agent(self, config):
        """Create QueryGenerationAgent instance."""
        return QueryGenerationAgent(config)
    
    @pytest.fixture
    def sample_input(self):
        """Create sample input for query generation."""
        return QueryGenerationInput(
            messages=[
                Message(role="user", content="What are the latest trends in renewable energy?")
            ],
            current_date="2024-01-15",
            research_topic="renewable energy trends",
            search_query_count=3
        )
    
    @pytest.mark.asyncio
    async def test_generate_search_queries_success(self, agent, sample_input):
        """Test successful query generation."""
        with patch.object(agent, 'run', return_value={
            'queries': [
                'renewable energy trends 2024',
                'solar wind power innovations',
                'clean energy market analysis'
            ]
        }) as mock_run:
            result = await agent.generate_queries(sample_input)
            
            assert 'queries' in result
            assert len(result['queries']) == 3
            assert all(isinstance(query, str) for query in result['queries'])
            mock_run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_queries_validation(self, agent):
        """Test input validation for query generation."""
        invalid_input = QueryGenerationInput(
            messages=[],  # Empty messages should be handled
            current_date="2024-01-15",
            research_topic="test",
            search_query_count=0  # Invalid count
        )
        
        with pytest.raises((ValueError, AssertionError)):
            await agent.generate_queries(invalid_input)
    
    @pytest.mark.asyncio
    async def test_generate_queries_error_handling(self, agent, sample_input):
        """Test error handling during query generation."""
        with patch.object(agent, 'run', side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                await agent.generate_queries(sample_input)


class TestWebSearchAgent:
    """Test suite for WebSearchAgent."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration()
    
    @pytest.fixture
    def agent(self, config):
        """Create WebSearchAgent instance."""
        return WebSearchAgent(config)
    
    @pytest.fixture
    def sample_input(self):
        """Create sample input for web search."""
        return WebSearchInput(
            search_queries=[
                "renewable energy trends 2024",
                "solar wind power innovations"
            ],
            current_date="2024-01-15"
        )
    
    @pytest.fixture
    def mock_sources(self):
        """Create mock search results."""
        return [
            Source(
                url="https://example.com/renewable-trends",
                title="Renewable Energy Trends 2024",
                content="Solar and wind power are leading the renewable energy sector...",
                raw_content="<html>Solar and wind power...</html>"
            ),
            Source(
                url="https://example.com/innovations",
                title="Clean Energy Innovations",
                content="New battery technologies are revolutionizing energy storage...",
                raw_content="<html>New battery technologies...</html>"
            )
        ]
    
    @pytest.mark.asyncio
    async def test_web_search_success(self, agent, sample_input, mock_sources):
        """Test successful web search execution."""
        with patch.object(agent, 'run', return_value={
            'sources': mock_sources
        }) as mock_run:
            result = await agent.search(sample_input)
            
            assert 'sources' in result
            assert len(result['sources']) == 2
            assert all(isinstance(source, Source) for source in result['sources'])
            mock_run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_query_validation(self, agent):
        """Test validation of search queries."""
        invalid_input = WebSearchInput(
            search_queries=[],  # Empty queries
            current_date="2024-01-15"
        )
        
        # Should handle empty queries gracefully
        with patch.object(agent, 'run', return_value={'sources': []}):
            result = await agent.search(invalid_input)
            assert result['sources'] == []
    
    @pytest.mark.asyncio
    async def test_source_content_parsing(self, agent, sample_input):
        """Test source content extraction and parsing."""
        mock_response = {
            'sources': [
                Source(
                    url="https://test.com",
                    title="Test Article",
                    content="Clean extracted content",
                    raw_content="<html><body><h1>Test Article</h1><p>Clean extracted content</p></body></html>"
                )
            ]
        }
        
        with patch.object(agent, 'run', return_value=mock_response):
            result = await agent.search(sample_input)
            source = result['sources'][0]
            
            assert source.title == "Test Article"
            assert "Clean extracted content" in source.content
            assert source.url.startswith("https://")
    
    @pytest.mark.asyncio
    async def test_search_error_handling(self, agent, sample_input):
        """Test error handling during web search."""
        with patch.object(agent, 'run', side_effect=Exception("Network Error")):
            with pytest.raises(Exception):
                await agent.search(sample_input)


class TestReflectionAgent:
    """Test suite for ReflectionAgent."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration()
    
    @pytest.fixture
    def agent(self, config):
        """Create ReflectionAgent instance."""
        return ReflectionAgent(config)
    
    @pytest.fixture
    def sample_input(self):
        """Create sample input for reflection."""
        return ReflectionInput(
            messages=[
                Message(role="user", content="What are the latest trends in renewable energy?")
            ],
            research_topic="renewable energy trends",
            sources_gathered=[
                Source(
                    url="https://example.com/solar",
                    title="Solar Power Advances",
                    content="Solar technology has improved significantly...",
                    raw_content="<html>Solar technology...</html>"
                ),
                Source(
                    url="https://example.com/wind",
                    title="Wind Energy Growth",
                    content="Wind power capacity has doubled in recent years...",
                    raw_content="<html>Wind power...</html>"
                )
            ],
            search_queries_used=["solar energy 2024", "wind power growth"],
            current_date="2024-01-15"
        )
    
    @pytest.mark.asyncio
    async def test_reflection_analysis_success(self, agent, sample_input):
        """Test successful reflection and gap analysis."""
        mock_response = {
            'research_sufficient': True,
            'analysis': 'The gathered sources provide comprehensive coverage of renewable energy trends.',
            'additional_queries': []
        }
        
        with patch.object(agent, 'run', return_value=mock_response):
            result = await agent.reflect(sample_input)
            
            assert 'research_sufficient' in result
            assert 'analysis' in result
            assert isinstance(result['research_sufficient'], bool)
            assert isinstance(result['analysis'], str)
    
    @pytest.mark.asyncio
    async def test_reflection_identifies_gaps(self, agent, sample_input):
        """Test reflection identifying research gaps."""
        mock_response = {
            'research_sufficient': False,
            'analysis': 'Missing information about energy storage technologies.',
            'additional_queries': ['battery storage renewable energy', 'grid scale energy storage']
        }
        
        with patch.object(agent, 'run', return_value=mock_response):
            result = await agent.reflect(sample_input)
            
            assert result['research_sufficient'] is False
            assert 'additional_queries' in result
            assert len(result['additional_queries']) > 0
    
    @pytest.mark.asyncio
    async def test_reflection_quality_assessment(self, agent):
        """Test reflection with poor quality sources."""
        poor_input = ReflectionInput(
            messages=[Message(role="user", content="Test question")],
            research_topic="test topic",
            sources_gathered=[
                Source(url="https://low-quality.com", title="Poor Source", content="Minimal content", raw_content="")
            ],
            search_queries_used=["test query"],
            current_date="2024-01-15"
        )
        
        mock_response = {
            'research_sufficient': False,
            'analysis': 'Sources lack depth and credibility.',
            'additional_queries': ['authoritative sources test topic']
        }
        
        with patch.object(agent, 'run', return_value=mock_response):
            result = await agent.reflect(poor_input)
            
            assert result['research_sufficient'] is False
            assert 'lack' in result['analysis'].lower() or 'poor' in result['analysis'].lower()


class TestFinalizationAgent:
    """Test suite for FinalizationAgent."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration()
    
    @pytest.fixture
    def agent(self, config):
        """Create FinalizationAgent instance."""
        return FinalizationAgent(config)
    
    @pytest.fixture
    def sample_input(self):
        """Create sample input for finalization."""
        return FinalizationInput(
            messages=[
                Message(role="user", content="What are the latest trends in renewable energy?")
            ],
            research_topic="renewable energy trends",
            sources_gathered=[
                Source(
                    url="https://example.com/solar-2024",
                    title="Solar Energy Advances 2024",
                    content="Solar panel efficiency has reached new heights with perovskite technology...",
                    raw_content="<html>Solar panel efficiency...</html>"
                ),
                Source(
                    url="https://example.com/wind-power",
                    title="Wind Power Market Growth",
                    content="Offshore wind installations have tripled in the past two years...",
                    raw_content="<html>Offshore wind...</html>"
                )
            ],
            research_loops_executed=2,
            total_queries=4,
            current_date="2024-01-15"
        )
    
    @pytest.mark.asyncio
    async def test_finalization_success(self, agent, sample_input):
        """Test successful answer synthesis and finalization."""
        mock_response = {
            'final_answer': '''Based on the latest research, renewable energy trends in 2024 include:

1. **Solar Technology Advances**: Perovskite solar cells are achieving unprecedented efficiency rates
2. **Offshore Wind Growth**: Installation capacity has tripled, driven by improved turbine technology
3. **Energy Storage Integration**: Grid-scale battery systems are becoming cost-competitive

These developments indicate a significant acceleration in renewable energy adoption globally.

**Sources:**
- Solar Energy Advances 2024 (https://example.com/solar-2024)
- Wind Power Market Growth (https://example.com/wind-power)'''
        }
        
        with patch.object(agent, 'run', return_value=mock_response):
            result = await agent.finalize(sample_input)
            
            assert 'final_answer' in result
            assert isinstance(result['final_answer'], str)
            assert len(result['final_answer']) > 100  # Substantial answer
            assert 'https://example.com/solar-2024' in result['final_answer']  # Citations included
    
    @pytest.mark.asyncio
    async def test_finalization_with_citations(self, agent, sample_input):
        """Test that finalization includes proper citations."""
        mock_response = {
            'final_answer': '''Renewable energy trends show significant growth.

**Sources:**
- Solar Energy Advances 2024 (https://example.com/solar-2024)
- Wind Power Market Growth (https://example.com/wind-power)'''
        }
        
        with patch.object(agent, 'run', return_value=mock_response):
            result = await agent.finalize(sample_input)
            
            # Verify all source URLs are cited
            for source in sample_input.sources_gathered:
                assert source.url in result['final_answer']
    
    @pytest.mark.asyncio
    async def test_finalization_model_override(self, config):
        """Test finalization agent with model override."""
        custom_model = "gemini-2.0-flash-exp"
        agent = FinalizationAgent(config, model_override=custom_model)
        
        # Verify model override is applied
        assert hasattr(agent, 'model_override')
        assert agent.model_override == custom_model
    
    @pytest.mark.asyncio
    async def test_finalization_empty_sources(self, agent):
        """Test finalization with no sources."""
        empty_input = FinalizationInput(
            messages=[Message(role="user", content="Test question")],
            research_topic="test",
            sources_gathered=[],
            research_loops_executed=1,
            total_queries=1,
            current_date="2024-01-15"
        )
        
        mock_response = {
            'final_answer': 'I was unable to find sufficient information to answer your question.'
        }
        
        with patch.object(agent, 'run', return_value=mock_response):
            result = await agent.finalize(empty_input)
            
            assert 'unable to find' in result['final_answer'].lower()


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests for agent interactions."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Configuration()
    
    @pytest.mark.asyncio
    async def test_agent_workflow_integration(self, config):
        """Test complete agent workflow integration."""
        # Create all agents
        query_agent = QueryGenerationAgent(config)
        search_agent = WebSearchAgent(config) 
        reflection_agent = ReflectionAgent(config)
        finalization_agent = FinalizationAgent(config)
        
        # Mock each agent's response
        mock_queries = ['renewable energy 2024', 'solar wind power']
        mock_sources = [
            Source(url="https://test.com", title="Test", content="Test content", raw_content="<html>Test</html>")
        ]
        mock_reflection = {'research_sufficient': True, 'analysis': 'Good coverage'}
        mock_final = {'final_answer': 'Comprehensive renewable energy analysis with citations.'}
        
        with patch.object(query_agent, 'run', return_value={'queries': mock_queries}), \
             patch.object(search_agent, 'run', return_value={'sources': mock_sources}), \
             patch.object(reflection_agent, 'run', return_value=mock_reflection), \
             patch.object(finalization_agent, 'run', return_value=mock_final):
            
            # Simulate workflow
            query_input = QueryGenerationInput(
                messages=[Message(role="user", content="Test question")],
                current_date="2024-01-15",
                research_topic="test",
                search_query_count=2
            )
            queries = await query_agent.generate_queries(query_input)
            
            search_input = WebSearchInput(
                search_queries=queries['queries'],
                current_date="2024-01-15"
            )
            sources = await search_agent.search(search_input)
            
            reflection_input = ReflectionInput(
                messages=[Message(role="user", content="Test question")],
                research_topic="test",
                sources_gathered=sources['sources'],
                search_queries_used=queries['queries'],
                current_date="2024-01-15"
            )
            reflection = await reflection_agent.reflect(reflection_input)
            
            finalization_input = FinalizationInput(
                messages=[Message(role="user", content="Test question")],
                research_topic="test", 
                sources_gathered=sources['sources'],
                research_loops_executed=1,
                total_queries=2,
                current_date="2024-01-15"
            )
            final_result = await finalization_agent.finalize(finalization_input)
            
            # Verify workflow completion
            assert 'queries' in queries
            assert 'sources' in sources
            assert 'research_sufficient' in reflection
            assert 'final_answer' in final_result