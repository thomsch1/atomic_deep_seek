"""
Tests for the refactored WebSearchAgent.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import sys
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_src))

from agent.agents.web_search_agent import WebSearchAgent
from agent.state import WebSearchInput, WebSearchOutput, Source, Citation
from agent.configuration import Configuration


class TestWebSearchAgent:
    """Test the refactored WebSearchAgent class."""
    
    def test_agent_initialization(self, mock_environment, test_configuration):
        """Test agent initialization with valid configuration."""
        with patch('agent.agents.web_search_agent.get_genai_client') as mock_get_client:
            with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
                with patch('agent.agents.web_search_agent.types') as mock_types:
                    # Mock all the required components
                    mock_client = MagicMock()
                    mock_get_client.return_value = mock_client
                    mock_agent_config = MagicMock()
                    mock_create_config.return_value = mock_agent_config
                    
                    # Mock the types
                    mock_types.Tool.return_value = MagicMock()
                    mock_types.GoogleSearch.return_value = MagicMock()
                    mock_types.GoogleSearchRetrieval.return_value = MagicMock()
                    mock_types.DynamicRetrievalConfig.return_value = MagicMock()
                    mock_types.DynamicRetrievalConfigMode.MODE_DYNAMIC = "MODE_DYNAMIC"
                    
                    with patch('agent.search.SearchManager'):
                        with patch('agent.citation.GroundingProcessor'):
                            with patch('agent.citation.CitationFormatter'):
                                agent = WebSearchAgent(test_configuration)
                                
                                assert agent.config == test_configuration
                                assert agent.agent_config == mock_agent_config
                                assert agent.client == mock_client
    
    def test_run_successful_gemini_grounding(self, mock_environment, test_configuration):
        """Test successful web search using Gemini grounding."""
        with patch('agent.agents.web_search_agent.get_genai_client') as mock_get_client:
            with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
                with patch('agent.agents.web_search_agent.types') as mock_types:
                    with patch('agent.search.SearchManager') as mock_search_manager:
                        with patch('agent.citation.GroundingProcessor') as mock_grounding_processor:
                            with patch('agent.citation.CitationFormatter') as mock_citation_formatter:
                                # Setup mocks
                                mock_client = MagicMock()
                                mock_get_client.return_value = mock_client
                                mock_agent_config = MagicMock()
                                mock_create_config.return_value = mock_agent_config
                                
                                # Mock types
                                mock_types.Tool.return_value = MagicMock()
                                mock_types.GoogleSearch.return_value = MagicMock()
                                mock_types.GoogleSearchRetrieval.return_value = MagicMock()
                                mock_types.DynamicRetrievalConfig.return_value = MagicMock()
                                mock_types.DynamicRetrievalConfigMode.MODE_DYNAMIC = "MODE_DYNAMIC"
                                
                                
                                # Mock grounding response
                                mock_response = MagicMock()
                                mock_response.text = "Test response text"
                                
                                # Create agent first
                                agent = WebSearchAgent(test_configuration)
                                
                                # Mock the actual instances created during initialization
                                agent.grounding_processor.extract_sources_from_grounding = MagicMock(return_value=[
                                    Source(title="Test Source", url="http://test.com", short_url="test", label="Test")
                                ])
                                agent.grounding_processor.create_citations_from_grounding = MagicMock(return_value=[])
                                agent.citation_formatter.add_inline_citations = MagicMock(return_value="Test response with citations")
                                
                                # Mock the grounding search
                                with patch.object(agent, '_search_with_gemini_grounding') as mock_grounding_search:
                                    mock_grounding_search.return_value = {
                                        'status': 'success',
                                        'response': mock_response,
                                        'grounding_used': True,
                                        'source': 'gemini_grounding'
                                    }
                                    
                                    # Mock asyncio.run to avoid actual async execution
                                    with patch('asyncio.run', return_value=mock_grounding_search.return_value):
                                        input_data = WebSearchInput(
                                            search_query="test query",
                                            query_id=1,
                                            current_date="January 15, 2024"
                                        )
                                        
                                        result = agent.run(input_data)
                                        
                                        assert isinstance(result, WebSearchOutput)
                                        assert "Test response with citations" in result.content
                                        assert len(result.sources) == 1
                                        assert result.sources[0].title == "Test Source"
    
    def test_run_with_grounding_failure_fallback(self, mock_environment, test_configuration):
        """Test fallback search when Gemini grounding fails."""
        with patch('agent.agents.web_search_agent.get_genai_client') as mock_get_client:
            with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
                with patch('agent.agents.web_search_agent.types') as mock_types:
                    with patch('agent.search.SearchManager') as mock_search_manager:
                        with patch('agent.citation.GroundingProcessor'):
                            with patch('agent.citation.CitationFormatter'):
                                # Setup mocks
                                mock_client = MagicMock()
                                mock_get_client.return_value = mock_client
                                mock_agent_config = MagicMock()
                                mock_create_config.return_value = mock_agent_config
                                
                                # Mock types
                                mock_types.Tool.return_value = MagicMock()
                                mock_types.GoogleSearch.return_value = MagicMock()
                                mock_types.GoogleSearchRetrieval.return_value = MagicMock()
                                mock_types.DynamicRetrievalConfig.return_value = MagicMock()
                                mock_types.DynamicRetrievalConfigMode.MODE_DYNAMIC = "MODE_DYNAMIC"
                                mock_types.GenerateContentConfig.return_value = MagicMock()
                                
                                # Create agent first
                                agent = WebSearchAgent(test_configuration)
                                
                                # Mock the search manager instance
                                agent.search_manager.search_web = MagicMock(return_value=[
                                    {"title": "Test Result", "url": "http://test.com", "snippet": "Test snippet"}
                                ])
                                
                                # Mock client response for fallback
                                mock_fallback_response = MagicMock()
                                mock_fallback_response.text = "Fallback response"
                                mock_client.models.generate_content.return_value = mock_fallback_response
                                
                                # Mock the grounding search to fail
                                with patch.object(agent, '_search_with_gemini_grounding') as mock_grounding_search:
                                    mock_grounding_search.return_value = {
                                        'status': 'error',
                                        'error': 'Grounding failed'
                                    }
                                    
                                    with patch('asyncio.run', return_value=mock_grounding_search.return_value):
                                        with patch('builtins.print'):  # Suppress prints
                                            input_data = WebSearchInput(
                                                search_query="test query",
                                                query_id=1,
                                                current_date="January 15, 2024"
                                            )
                                            
                                            result = agent.run(input_data)
                                            
                                            assert isinstance(result, WebSearchOutput)
                                            assert result.content is not None
                                            # Should use the search manager fallback
                                            agent.search_manager.search_web.assert_called_once()
    
    def test_run_with_complete_failure(self, mock_environment, test_configuration):
        """Test complete failure scenario."""
        with patch('agent.agents.web_search_agent.get_genai_client') as mock_get_client:
            with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
                with patch('agent.agents.web_search_agent.types') as mock_types:
                    with patch('agent.search.SearchManager'):
                        with patch('agent.citation.GroundingProcessor'):
                            with patch('agent.citation.CitationFormatter'):
                                # Setup mocks
                                mock_client = MagicMock()
                                mock_get_client.return_value = mock_client
                                mock_agent_config = MagicMock()
                                mock_create_config.return_value = mock_agent_config
                                
                                # Mock types
                                mock_types.Tool.return_value = MagicMock()
                                mock_types.GoogleSearch.return_value = MagicMock()
                                mock_types.GoogleSearchRetrieval.return_value = MagicMock()
                                mock_types.DynamicRetrievalConfig.return_value = MagicMock()
                                mock_types.DynamicRetrievalConfigMode.MODE_DYNAMIC = "MODE_DYNAMIC"
                                
                                agent = WebSearchAgent(test_configuration)
                                
                                # Mock everything to fail
                                with patch('asyncio.run', side_effect=Exception("Complete failure")):
                                    with patch('builtins.print'):  # Suppress prints
                                        input_data = WebSearchInput(
                                            search_query="test query",
                                            query_id=1,
                                            current_date="January 15, 2024"
                                        )
                                        
                                        result = agent.run(input_data)
                                        
                                        assert isinstance(result, WebSearchOutput)
                                        assert "Unable to perform web search" in result.content
    
    def test_validate_input(self, mock_environment, test_configuration):
        """Test input validation."""
        with patch('agent.agents.web_search_agent.get_genai_client'):
            with patch('agent.configuration.Configuration.create_agent_config'):
                with patch('agent.agents.web_search_agent.types') as mock_types:
                    with patch('agent.search.SearchManager'):
                        with patch('agent.citation.GroundingProcessor'):
                            with patch('agent.citation.CitationFormatter'):
                                # Mock types
                                mock_types.Tool.return_value = MagicMock()
                                mock_types.GoogleSearch.return_value = MagicMock()
                                mock_types.GoogleSearchRetrieval.return_value = MagicMock()
                                mock_types.DynamicRetrievalConfig.return_value = MagicMock()
                                mock_types.DynamicRetrievalConfigMode.MODE_DYNAMIC = "MODE_DYNAMIC"
                                
                                agent = WebSearchAgent(test_configuration)
                                
                                # Valid input
                                valid_input = WebSearchInput(
                                    search_query="test",
                                    query_id=1,
                                    current_date="2024"
                                )
                                assert agent._validate_input(valid_input) is True
                                
                                # Invalid input (None)
                                assert agent._validate_input(None) is False