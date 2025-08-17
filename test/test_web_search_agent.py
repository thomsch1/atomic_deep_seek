"""
Tests for WebSearchAgent class in agents.py.
Tests web search functionality, grounding integration, and fallback mechanisms.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import sys
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from agent.agents import WebSearchAgent
from agent.state import WebSearchInput, WebSearchOutput, Source, Citation
from agent.configuration import Configuration

# Define a helper context manager for consistent mocking
class MockGeminiTypes:
    def __enter__(self):
        self.patches = [
            patch('agent.agents.types.Tool', create=True),
            patch('agent.agents.types.GoogleSearch', create=True),
            patch('agent.agents.types.GoogleSearchRetrieval', create=True),
            patch('agent.agents.types.DynamicRetrievalConfig', create=True),
            patch('agent.agents.types.DynamicRetrievalConfigMode', create=True),
            patch('agent.agents.types.GenerateContentConfig', create=True)
        ]
        
        mocks = [p.__enter__() for p in self.patches]
        for mock in mocks:
            mock.return_value = MagicMock()
            
        return mocks
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for patch_obj in reversed(self.patches):
            patch_obj.__exit__(exc_type, exc_val, exc_tb)


class TestWebSearchAgent:
    """Test the WebSearchAgent class."""
    
    def test_agent_initialization(self, mock_environment, test_configuration, mock_genai_client, mock_agent_dependencies):
        """Test agent initialization with valid configuration."""
        with patch.object(Configuration, 'create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                with MockGeminiTypes():
                    agent = WebSearchAgent(test_configuration)
                    
                    assert agent.config == test_configuration
                    assert agent.agent_config is not None
                    assert agent.client == mock_genai_client
                    assert agent.grounding_tool is not None
                    assert agent.legacy_tool is not None
    
    def test_run_successful_grounding(self, mock_environment, test_configuration, sample_web_search_input, mock_grounding_response):
        """Test successful web search using Gemini grounding."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            mock_genai_client = MagicMock()
            
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                with MockGeminiTypes():
                    with patch('asyncio.run') as mock_run:
                        # Mock the async function result
                        mock_run.return_value = {
                            'status': 'success',
                            'response': mock_grounding_response,
                            'grounding_used': True,
                            'source': 'gemini_grounding'
                        }
                        
                        with patch('agent.agents.extract_sources_from_grounding') as mock_extract:
                            with patch('agent.agents.add_inline_citations') as mock_citations:
                                with patch('agent.agents.create_citations_from_grounding') as mock_create_citations:
                                    # Setup return values
                                    mock_sources = [
                                        Source(title="Test Source", url="https://test.com", short_url="test-1", label="Source 1")
                                    ]
                                    mock_extract.return_value = mock_sources
                                    mock_citations.return_value = "Content with citations"
                                    mock_create_citations.return_value = [
                                        Citation(start_index=0, end_index=10, segments=mock_sources)
                                    ]
                                    
                                    agent = WebSearchAgent(test_configuration)
                                    result = agent.run(sample_web_search_input)
                                    
                                    assert isinstance(result, WebSearchOutput)
                                    assert result.content == "Content with citations"
                                    assert len(result.sources) == 1
                                    assert len(result.citations) == 1
                                    assert result.sources[0].title == "Test Source"
    
    def test_run_grounding_without_search(self, mock_environment, test_configuration, sample_web_search_input):
        """Test Gemini response without grounding (knowledge-based)."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            mock_genai_client = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Knowledge-based response about quantum computing"
            
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                with MockGeminiTypes():
                    with patch('asyncio.run') as mock_run:
                        mock_run.return_value = {
                            'status': 'success',
                            'response': mock_response,
                            'grounding_used': False,
                            'source': 'gemini_grounding'
                        }
                        
                        agent = WebSearchAgent(test_configuration)
                        result = agent.run(sample_web_search_input)
                        
                        assert isinstance(result, WebSearchOutput)
                        assert result.content == "Knowledge-based response about quantum computing"
                        assert len(result.sources) == 0
                        assert len(result.citations) == 0
    
    def test_run_grounding_failure_fallback(self, mock_environment, test_configuration, sample_web_search_input):
        """Test fallback to traditional search when grounding fails."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            mock_genai_client = MagicMock()
            
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                with MockGeminiTypes():
                    with patch('asyncio.run') as mock_run:
                        mock_run.return_value = {
                            'status': 'error',
                            'error': 'Grounding failed',
                            'source': 'gemini_grounding'
                        }
                        
                        with patch('agent.agents.run_async_search') as mock_search:
                            mock_search.return_value = [
                                {
                                    'title': 'Fallback Result',
                                    'url': 'https://fallback.com',
                                    'snippet': 'Fallback content'
                                }
                            ]
                            
                            mock_genai_client.models.generate_content.return_value.text = "Synthesized response"
                            
                            with patch('agent.prompts.web_searcher_instructions', "Test prompt: {current_date} {research_topic}"):
                                agent = WebSearchAgent(test_configuration)
                                result = agent.run(sample_web_search_input)
                                
                                assert isinstance(result, WebSearchOutput)
                                assert "Sources:" in result.content  # Citations added
                                assert len(result.sources) == 1
                                assert result.sources[0].title == "Fallback Result"
    
    def test_run_citation_insertion_error(self, mock_environment, test_configuration, sample_web_search_input, mock_grounding_response):
        """Test handling of citation insertion errors."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            mock_genai_client = MagicMock()
            
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                with MockGeminiTypes():
                    with patch('asyncio.run') as mock_run:
                        mock_run.return_value = {
                            'status': 'success',
                            'response': mock_grounding_response,
                            'grounding_used': True,
                            'source': 'gemini_grounding'
                        }
                        
                        with patch('agent.agents.extract_sources_from_grounding') as mock_extract:
                            with patch('agent.agents.add_inline_citations', side_effect=Exception("Citation error")):
                                with patch('agent.agents.create_citations_from_grounding') as mock_create_citations:
                                    with patch('builtins.print') as mock_print:
                                        mock_sources = [Source(title="Test", url="https://test.com", short_url="test-1", label="Source 1")]
                                        mock_extract.return_value = mock_sources
                                        mock_create_citations.return_value = []
                                        
                                        agent = WebSearchAgent(test_configuration)
                                        result = agent.run(sample_web_search_input)
                                        
                                        # Should use original text when citation insertion fails
                                        assert isinstance(result, WebSearchOutput)
                                        assert result.content == mock_grounding_response.text
                                        
                                        # Verify error was logged
                                        assert any("Citation insertion failed" in str(call) for call in mock_print.call_args_list)
    
    def test_run_citation_creation_error(self, mock_environment, test_configuration, sample_web_search_input, mock_grounding_response):
        """Test handling of citation creation errors."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            mock_genai_client = MagicMock()
            
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                with MockGeminiTypes():
                    with patch('asyncio.run') as mock_run:
                        mock_run.return_value = {
                            'status': 'success',
                            'response': mock_grounding_response,
                            'grounding_used': True,
                            'source': 'gemini_grounding'
                        }
                        
                        with patch('agent.agents.extract_sources_from_grounding') as mock_extract:
                            with patch('agent.agents.add_inline_citations') as mock_citations:
                                with patch('agent.agents.create_citations_from_grounding', side_effect=Exception("Citation creation error")):
                                    with patch('builtins.print') as mock_print:
                                        mock_sources = [Source(title="Test", url="https://test.com", short_url="test-1", label="Source 1")]
                                        mock_extract.return_value = mock_sources
                                        mock_citations.return_value = "Content with citations"
                                        
                                        agent = WebSearchAgent(test_configuration)
                                        result = agent.run(sample_web_search_input)
                                        
                                        assert isinstance(result, WebSearchOutput)
                                        assert result.content == "Content with citations"
                                        assert len(result.citations) == 0  # Should be empty due to error
                                        
                                        # Verify error was logged
                                        assert any("Citation creation failed" in str(call) for call in mock_print.call_args_list)
    
    def test_run_general_exception(self, mock_environment, test_configuration, sample_web_search_input):
        """Test handling of general exceptions in run method."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            mock_genai_client = MagicMock()
            
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                with MockGeminiTypes():
                    with patch('asyncio.run', side_effect=Exception("General error")):
                        with patch.object(WebSearchAgent, '_fallback_search') as mock_fallback:
                            mock_fallback.return_value = WebSearchOutput(
                                content="Fallback content",
                                sources=[],
                                citations=[]
                            )
                            
                            with patch('builtins.print') as mock_print:
                                agent = WebSearchAgent(test_configuration)
                                result = agent.run(sample_web_search_input)
                                
                                assert isinstance(result, WebSearchOutput)
                                assert result.content == "Fallback content"
                                
                                # Verify error was logged and fallback was called
                                assert any("WebSearch Agent error" in str(call) for call in mock_print.call_args_list)
                                mock_fallback.assert_called_once_with(sample_web_search_input)
    
    def test_fallback_search_successful(self, mock_environment, test_configuration, sample_web_search_input):
        """Test successful fallback search method."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            mock_genai_client = MagicMock()
            mock_genai_client.models.generate_content.return_value.text = "Synthesized response"
            
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                with MockGeminiTypes():
                    with patch('agent.agents.run_async_search') as mock_search:
                        mock_search.return_value = [
                            {
                                'title': 'Search Result 1',
                                'url': 'https://result1.com',
                                'snippet': 'First result snippet'
                            },
                            {
                                'title': 'Search Result 2',
                                'url': 'https://result2.com',
                                'snippet': 'Second result snippet'
                            }
                        ]
                        
                        with patch('agent.prompts.web_searcher_instructions', "Test prompt: {current_date} {research_topic}"):
                            agent = WebSearchAgent(test_configuration)
                            result = agent._fallback_search(sample_web_search_input)
                            
                            assert isinstance(result, WebSearchOutput)
                            assert "Sources:" in result.content
                            assert len(result.sources) == 2
                            assert result.sources[0].title == "Search Result 1"
                            assert result.sources[1].title == "Search Result 2"
                            assert len(result.citations) == 2  # One per source
    
    def test_fallback_search_no_results(self, mock_environment, test_configuration, sample_web_search_input):
        """Test fallback search when no results are found."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            mock_genai_client = MagicMock()
            
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                with MockGeminiTypes():
                    with patch('agent.agents.run_async_search') as mock_search:
                        mock_search.return_value = []  # No results
                        
                        agent = WebSearchAgent(test_configuration)
                        result = agent._fallback_search(sample_web_search_input)
                        
                        assert isinstance(result, WebSearchOutput)
                        assert "No search results found" in result.content
                        assert len(result.sources) == 0
                        assert len(result.citations) == 0
    
    def test_fallback_search_exception(self, mock_environment, test_configuration, sample_web_search_input):
        """Test fallback search exception handling."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            mock_genai_client = MagicMock()
            
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                with MockGeminiTypes():
                    with patch('agent.agents.run_async_search', side_effect=Exception("Search failed")):
                        with patch('builtins.print') as mock_print:
                            agent = WebSearchAgent(test_configuration)
                            result = agent._fallback_search(sample_web_search_input)
                            
                            assert isinstance(result, WebSearchOutput)
                            assert "Error performing search" in result.content
                            assert "Search failed" in result.content
                            assert len(result.sources) == 0
                            assert len(result.citations) == 0
                            
                            # Verify error was logged
                            assert any("Fallback search also failed" in str(call) for call in mock_print.call_args_list)
    
    def test_add_citations_to_content(self, mock_environment, test_configuration):
        """Test the _add_citations_to_content method."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            with patch('agent.agents.get_genai_client') as mock_get_client:
                mock_genai_client = MagicMock()
                mock_get_client.return_value = mock_genai_client
                
                with MockGeminiTypes():
                    agent = WebSearchAgent(test_configuration)
                    
                    content = "This is test content."
                    sources = [
                        Source(title="Source 1", url="https://source1.com", short_url="s1", label="Source 1"),
                        Source(title="Source 2", url="https://source2.com", short_url="s2", label="Source 2")
                    ]
                    
                    result = agent._add_citations_to_content(content, sources)
                    
                    assert "This is test content." in result
                    assert "Sources:" in result
                    assert "[1] [Source 1](https://source1.com)" in result
                    assert "[2] [Source 2](https://source2.com)" in result
    
    def test_add_citations_to_content_empty_sources(self, mock_environment, test_configuration):
        """Test _add_citations_to_content with empty sources."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            with patch('agent.agents.get_genai_client') as mock_get_client:
                mock_genai_client = MagicMock()
                mock_get_client.return_value = mock_genai_client
                
                with MockGeminiTypes():
                    agent = WebSearchAgent(test_configuration)
                    
                    content = "This is test content."
                    sources = []
                    
                    result = agent._add_citations_to_content(content, sources)
                    
                    assert result == content  # Should return unchanged
    
    def test_create_citation_objects(self, mock_environment, test_configuration):
        """Test the _create_citation_objects method."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            with patch('agent.agents.get_genai_client') as mock_get_client:
                mock_genai_client = MagicMock()
                mock_get_client.return_value = mock_genai_client
                
                with MockGeminiTypes():
                    agent = WebSearchAgent(test_configuration)
                    
                    sources = [
                        Source(title="Source 1", url="https://source1.com", short_url="s1", label="Source 1"),
                        Source(title="Source 2", url="https://source2.com", short_url="s2", label="Source 2")
                    ]
                    
                    citations = agent._create_citation_objects(sources)
                    
                    assert len(citations) == 2
                    assert all(isinstance(citation, Citation) for citation in citations)
                    assert citations[0].start_index == 0
                    assert citations[0].end_index == 0
                    assert len(citations[0].segments) == 1
                    assert citations[0].segments[0] == sources[0]
    
    def test_fallback_search_context_creation(self, mock_environment, test_configuration, sample_web_search_input):
        """Test that fallback search creates proper context from search results."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            mock_genai_client = MagicMock()
            
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                with MockGeminiTypes():
                    with patch('agent.agents.run_async_search') as mock_search:
                        mock_search.return_value = [
                            {
                                'title': 'Test Result',
                                'url': 'https://test.com',
                                'snippet': 'Test snippet'
                            }
                        ]
                        
                        # Capture the prompt that gets sent to the client
                        def capture_prompt(*args, **kwargs):
                            capture_prompt.captured_prompt = kwargs.get('contents', '')
                            mock_response = MagicMock()
                            mock_response.text = "Generated response"
                            return mock_response
                        
                        mock_genai_client.models.generate_content.side_effect = capture_prompt
                        
                        with patch('agent.prompts.web_searcher_instructions', "Test prompt: {current_date} {research_topic}"):
                            agent = WebSearchAgent(test_configuration)
                            agent._fallback_search(sample_web_search_input)
                            
                            # Verify the context contains search results
                            prompt = capture_prompt.captured_prompt
                            assert "Search Query:" in prompt
                            assert sample_web_search_input.search_query in prompt
                            assert "Test Result" in prompt
                            assert "https://test.com" in prompt
                            assert "Test snippet" in prompt
    
    def test_fallback_search_filters_empty_urls(self, mock_environment, test_configuration, sample_web_search_input):
        """Test that fallback search filters out results with empty URLs."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            mock_genai_client = MagicMock()
            mock_genai_client.models.generate_content.return_value.text = "Response"
            
            with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
                with MockGeminiTypes():
                    with patch('agent.agents.run_async_search') as mock_search:
                        mock_search.return_value = [
                            {
                                'title': 'Valid Result',
                                'url': 'https://valid.com',
                                'snippet': 'Valid snippet'
                            },
                            {
                                'title': 'Invalid Result',
                                'url': '',  # Empty URL
                                'snippet': 'Invalid snippet'
                            }
                        ]
                        
                        with patch('agent.prompts.web_searcher_instructions', "Test prompt: {current_date} {research_topic}"):
                            agent = WebSearchAgent(test_configuration)
                            result = agent._fallback_search(sample_web_search_input)
                            
                            # Should only include the valid result
                            assert len(result.sources) == 1
                            assert result.sources[0].title == "Valid Result"
                            assert result.sources[0].url == "https://valid.com"