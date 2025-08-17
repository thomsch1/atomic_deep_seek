"""
End-to-End Integration Tests for the Deep Search AI system.
Tests complete workflows, real API interactions, and system integration.
"""

import pytest
import asyncio
import httpx
from typing import Dict, Any, List
from unittest.mock import patch
import os
import time

from agent.app import app
from agent.orchestrator import ResearchOrchestrator
from agent.configuration import Configuration
from agent.state import Source, Message


@pytest.mark.e2e
@pytest.mark.asyncio
class TestEndToEndIntegration:
    """End-to-end integration tests."""
    
    @pytest.fixture
    def config(self):
        """Test configuration with mocked external services."""
        return Configuration()
    
    @pytest.fixture
    async def client(self):
        """HTTP client for testing API endpoints."""
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.fixture
    def mock_gemini_responses(self):
        """Mock responses for Gemini API calls."""
        return {
            'query_generation': {
                'queries': [
                    'renewable energy trends 2024',
                    'solar wind power innovations',
                    'clean energy market analysis'
                ]
            },
            'web_search': {
                'sources': [
                    Source(
                        url="https://example.com/renewable-2024",
                        title="Renewable Energy Trends 2024",
                        content="Solar and wind power continue to dominate renewable energy growth...",
                        raw_content="<html>Solar and wind power...</html>"
                    ),
                    Source(
                        url="https://example.com/clean-energy-market",
                        title="Clean Energy Market Analysis",
                        content="The clean energy market is expected to reach $2.15 trillion by 2025...",
                        raw_content="<html>The clean energy market...</html>"
                    )
                ]
            },
            'reflection': {
                'research_sufficient': True,
                'analysis': 'The gathered sources provide comprehensive coverage of renewable energy trends and market analysis.',
                'additional_queries': []
            },
            'finalization': {
                'final_answer': '''Based on current research, renewable energy trends in 2024 show significant developments:

**Key Trends:**
1. **Solar Dominance**: Solar power installations continue to lead renewable energy growth
2. **Wind Power Innovation**: Offshore wind technology is advancing rapidly  
3. **Market Expansion**: Clean energy market projected to reach $2.15 trillion by 2025
4. **Technology Integration**: Smart grid integration improving energy efficiency

**Market Impact:**
The renewable energy sector is experiencing unprecedented growth driven by technological advances and favorable policies.

**Sources:**
- Renewable Energy Trends 2024 (https://example.com/renewable-2024)
- Clean Energy Market Analysis (https://example.com/clean-energy-market)'''
            }
        }
    
    async def test_complete_research_workflow(self, client, mock_gemini_responses):
        """Test complete research workflow from API request to final response."""
        # Mock all external API calls
        with patch('agent.agents.QueryGenerationAgent.run') as mock_query, \
             patch('agent.agents.WebSearchAgent.run') as mock_search, \
             patch('agent.agents.ReflectionAgent.run') as mock_reflect, \
             patch('agent.agents.FinalizationAgent.run') as mock_final:
            
            # Setup mock responses
            mock_query.return_value = mock_gemini_responses['query_generation']
            mock_search.return_value = mock_gemini_responses['web_search']
            mock_reflect.return_value = mock_gemini_responses['reflection']
            mock_final.return_value = mock_gemini_responses['finalization']
            
            # Make research request
            request_payload = {
                "question": "What are the latest trends in renewable energy?",
                "initial_search_query_count": 3,
                "max_research_loops": 2,
                "reasoning_model": "gemini-2.0-flash-exp"
            }
            
            response = await client.post("/research", json=request_payload)
            
            # Verify successful response
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert "final_answer" in data
            assert "sources" in data
            assert "research_loops_executed" in data
            assert "total_queries" in data
            
            # Verify content quality
            assert len(data["final_answer"]) > 100  # Substantial answer
            assert "renewable energy" in data["final_answer"].lower()
            assert len(data["sources"]) == 2  # Two sources from mock
            assert data["research_loops_executed"] >= 1
            assert data["total_queries"] >= 3
            
            # Verify sources contain required fields
            for source in data["sources"]:
                assert "url" in source
                assert "title" in source
                assert "content" in source
                assert source["url"].startswith("https://")
    
    async def test_multi_loop_research_workflow(self, client, mock_gemini_responses):
        """Test research workflow that requires multiple reflection loops."""
        call_count = {'reflect': 0}
        
        def mock_reflection(*args, **kwargs):
            call_count['reflect'] += 1
            if call_count['reflect'] == 1:
                # First reflection suggests more research
                return {
                    'research_sufficient': False,
                    'analysis': 'Need more information about energy storage technologies.',
                    'additional_queries': ['battery storage renewable energy', 'grid scale energy storage']
                }
            else:
                # Second reflection confirms sufficient research
                return mock_gemini_responses['reflection']
        
        with patch('agent.agents.QueryGenerationAgent.run') as mock_query, \
             patch('agent.agents.WebSearchAgent.run') as mock_search, \
             patch('agent.agents.ReflectionAgent.run', side_effect=mock_reflection), \
             patch('agent.agents.FinalizationAgent.run') as mock_final:
            
            mock_query.return_value = mock_gemini_responses['query_generation']
            mock_search.return_value = mock_gemini_responses['web_search']
            mock_final.return_value = mock_gemini_responses['finalization']
            
            request_payload = {
                "question": "What are renewable energy storage solutions?",
                "max_research_loops": 3
            }
            
            response = await client.post("/research", json=request_payload)
            
            assert response.status_code == 200
            data = response.json()
            
            # Should have executed 2 research loops
            assert data["research_loops_executed"] == 2
            assert call_count['reflect'] == 2
    
    async def test_error_handling_workflow(self, client):
        """Test error handling in the research workflow."""
        # Mock query generation failure
        with patch('agent.agents.QueryGenerationAgent.run', 
                  side_effect=Exception("Gemini API error")):
            
            request_payload = {
                "question": "Test question that will fail"
            }
            
            response = await client.post("/research", json=request_payload)
            
            assert response.status_code == 500
            error_data = response.json()
            assert "detail" in error_data
            assert "error" in error_data["detail"].lower()
    
    async def test_api_validation_workflow(self, client):
        """Test API request validation."""
        # Test missing required field
        invalid_payload = {
            "initial_search_query_count": 3
            # Missing 'question' field
        }
        
        response = await client.post("/research", json=invalid_payload)
        assert response.status_code == 422
        
        # Test invalid parameter types
        invalid_types_payload = {
            "question": "Valid question",
            "initial_search_query_count": "invalid",  # Should be int
            "max_research_loops": "also invalid"      # Should be int
        }
        
        response = await client.post("/research", json=invalid_types_payload)
        assert response.status_code == 422
    
    async def test_concurrent_request_handling(self, client, mock_gemini_responses):
        """Test handling multiple concurrent research requests."""
        with patch('agent.agents.QueryGenerationAgent.run') as mock_query, \
             patch('agent.agents.WebSearchAgent.run') as mock_search, \
             patch('agent.agents.ReflectionAgent.run') as mock_reflect, \
             patch('agent.agents.FinalizationAgent.run') as mock_final:
            
            # Setup mocks
            mock_query.return_value = mock_gemini_responses['query_generation']
            mock_search.return_value = mock_gemini_responses['web_search']
            mock_reflect.return_value = mock_gemini_responses['reflection']
            mock_final.return_value = mock_gemini_responses['finalization']
            
            # Create multiple concurrent requests
            request_payload = {
                "question": "What is artificial intelligence?",
                "max_research_loops": 1
            }
            
            # Send 5 concurrent requests
            tasks = [
                client.post("/research", json=request_payload) 
                for _ in range(5)
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All requests should succeed
            successful_responses = [r for r in responses if not isinstance(r, Exception)]
            assert len(successful_responses) == 5
            
            for response in successful_responses:
                assert response.status_code == 200
                data = response.json()
                assert "final_answer" in data
    
    async def test_different_effort_levels(self, client, mock_gemini_responses):
        """Test different effort level configurations."""
        with patch('agent.agents.QueryGenerationAgent.run') as mock_query, \
             patch('agent.agents.WebSearchAgent.run') as mock_search, \
             patch('agent.agents.ReflectionAgent.run') as mock_reflect, \
             patch('agent.agents.FinalizationAgent.run') as mock_final:
            
            # Setup mocks
            mock_query.return_value = mock_gemini_responses['query_generation']
            mock_search.return_value = mock_gemini_responses['web_search']
            mock_reflect.return_value = mock_gemini_responses['reflection']
            mock_final.return_value = mock_gemini_responses['finalization']
            
            effort_configs = [
                {"initial_search_query_count": 1, "max_research_loops": 1},   # Low
                {"initial_search_query_count": 3, "max_research_loops": 3},   # Medium  
                {"initial_search_query_count": 5, "max_research_loops": 10}   # High
            ]
            
            for config in effort_configs:
                request_payload = {
                    "question": "What is quantum computing?",
                    **config
                }
                
                response = await client.post("/research", json=request_payload)
                assert response.status_code == 200
                
                data = response.json()
                assert "final_answer" in data
                assert data["total_queries"] >= config["initial_search_query_count"]
    
    async def test_model_selection_workflow(self, client, mock_gemini_responses):
        """Test different model selection options."""
        models = ["gemini-2.0-flash-exp", "gemini-2.5-flash", "gemini-2.5-pro"]
        
        for model in models:
            with patch('agent.agents.QueryGenerationAgent.run') as mock_query, \
                 patch('agent.agents.WebSearchAgent.run') as mock_search, \
                 patch('agent.agents.ReflectionAgent.run') as mock_reflect, \
                 patch('agent.agents.FinalizationAgent.run') as mock_final:
                
                # Setup mocks
                mock_query.return_value = mock_gemini_responses['query_generation']
                mock_search.return_value = mock_gemini_responses['web_search']
                mock_reflect.return_value = mock_gemini_responses['reflection']
                mock_final.return_value = mock_gemini_responses['finalization']
                
                request_payload = {
                    "question": f"Test question for {model}",
                    "reasoning_model": model
                }
                
                response = await client.post("/research", json=request_payload)
                assert response.status_code == 200
                
                data = response.json()
                assert "final_answer" in data


@pytest.mark.integration
@pytest.mark.asyncio
class TestSystemIntegration:
    """Integration tests for system components."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator for integration testing."""
        return ResearchOrchestrator()
    
    async def test_orchestrator_agent_integration(self, orchestrator):
        """Test orchestrator integrates correctly with all agents."""
        # Verify all agents are accessible
        assert orchestrator.query_agent is not None
        assert orchestrator.search_agent is not None
        assert orchestrator.reflection_agent is not None
        assert orchestrator.finalization_agent is not None
        
        # Verify agents have correct configuration
        assert orchestrator.query_agent.config is not None
        assert orchestrator.search_agent.config is not None
        assert orchestrator.reflection_agent.config is not None
        assert orchestrator.finalization_agent.config is not None
    
    async def test_state_management_integration(self, orchestrator):
        """Test state management across the research workflow."""
        # Mock all agent responses
        mock_sources = [
            Source(
                url="https://test.com/article",
                title="Test Article",
                content="Test content about the research topic",
                raw_content="<html>Test content</html>"
            )
        ]
        
        with patch.object(orchestrator.query_agent, 'generate_queries',
                         return_value={'queries': ['test query 1', 'test query 2']}), \
             patch.object(orchestrator.search_agent, 'search',
                         return_value={'sources': mock_sources}), \
             patch.object(orchestrator.reflection_agent, 'reflect',
                         return_value={'research_sufficient': True, 'analysis': 'Good coverage'}), \
             patch.object(orchestrator.finalization_agent, 'finalize',
                         return_value={'final_answer': 'Comprehensive test answer with citations.'}):
            
            result = await orchestrator.run_research_async(
                question="Test integration question",
                initial_search_query_count=2,
                max_research_loops=2
            )
            
            # Verify state is properly maintained throughout workflow
            assert isinstance(result, dict)
            assert 'final_answer' in result
            assert 'sources_gathered' in result
            assert 'research_loops_executed' in result
            assert 'total_queries' in result
            
            # Verify data consistency
            assert len(result['sources_gathered']) == 1
            assert result['sources_gathered'][0]['url'] == mock_sources[0].url
    
    async def test_configuration_integration(self):
        """Test configuration system integration."""
        # Test default configuration
        default_orchestrator = ResearchOrchestrator()
        assert default_orchestrator.config is not None
        
        # Test custom configuration
        custom_config = {"custom_setting": "test_value"}
        custom_orchestrator = ResearchOrchestrator(config=custom_config)
        assert custom_orchestrator.config is not None
        
        # Verify agents receive configuration
        assert default_orchestrator.query_agent.config is not None
        assert custom_orchestrator.query_agent.config is not None
    
    @pytest.mark.performance
    async def test_performance_integration(self, orchestrator):
        """Test system performance under load."""
        # Mock fast responses for performance testing
        mock_sources = [Source(url="https://fast-test.com", title="Fast", content="Quick", raw_content="")]
        
        with patch.object(orchestrator.query_agent, 'generate_queries',
                         return_value={'queries': ['fast query']}), \
             patch.object(orchestrator.search_agent, 'search',
                         return_value={'sources': mock_sources}), \
             patch.object(orchestrator.reflection_agent, 'reflect',
                         return_value={'research_sufficient': True, 'analysis': 'Fast'}), \
             patch.object(orchestrator.finalization_agent, 'finalize',
                         return_value={'final_answer': 'Fast answer'}):
            
            start_time = time.time()
            
            # Run multiple research requests
            tasks = [
                orchestrator.run_research_async(
                    question=f"Performance test {i}",
                    initial_search_query_count=1,
                    max_research_loops=1
                )
                for i in range(10)
            ]
            
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Verify all completed successfully
            assert len(results) == 10
            assert all('final_answer' in result for result in results)
            
            # Performance assertion - should complete within reasonable time
            assert total_time < 5.0  # 5 seconds for 10 concurrent requests
    
    def test_thread_pool_integration(self, orchestrator):
        """Test thread pool integration."""
        # Verify thread pool is initialized
        assert orchestrator._thread_pool is not None
        assert not orchestrator._thread_pool._shutdown
        
        # Verify cleanup works
        orchestrator._cleanup_thread_pool()
        assert orchestrator._thread_pool._shutdown