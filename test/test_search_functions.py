"""
Tests for search functions in agents.py.
Tests search_with_gemini_grounding, search_web, and run_async_search.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import sys
from pathlib import Path
import httpx

# Add backend src to path
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from agent.agents import (
    search_with_gemini_grounding,
    search_web,
    run_async_search
)


class TestSearchWithGeminiGrounding:
    """Test the search_with_gemini_grounding function."""
    
    @pytest.mark.asyncio
    async def test_successful_grounding_search(self, mock_environment, mock_genai_client):
        """Test successful Gemini grounding search."""
        with patch('agent.agents.get_genai_client', return_value=mock_genai_client):
            with patch('agent.agents.types.Tool') as mock_tool:
                with patch('agent.agents.types.GoogleSearch', create=True) as mock_google_search:
                    result = await search_with_gemini_grounding("quantum computing")
                    
                    assert result['status'] == 'success'
                    assert result['source'] == 'gemini_grounding'
                    assert 'response' in result
                    assert 'grounding_used' in result
                    
                    # Verify the client was called correctly
                    mock_genai_client.models.generate_content.assert_called_once()
                    call_args = mock_genai_client.models.generate_content.call_args
                    assert call_args[1]['model'] == "gemini-2.5-flash"
                    assert "quantum computing" in call_args[1]['contents']
    
    @pytest.mark.asyncio
    async def test_grounding_with_metadata(self, mock_environment, mock_grounding_response):
        """Test grounding search that returns metadata."""
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_grounding_response
        
        with patch('agent.agents.get_genai_client', return_value=mock_client):
            with patch('agent.agents.types.Tool') as mock_tool:
                with patch('agent.agents.types.GoogleSearch', create=True) as mock_google_search:
                    result = await search_with_gemini_grounding("quantum computing")
                    
                    assert result['status'] == 'success'
                    assert bool(result['grounding_used']) is True
    
    @pytest.mark.asyncio
    async def test_grounding_without_metadata(self, mock_environment):
        """Test grounding search without metadata (knowledge-based)."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Knowledge-based response"
        mock_response.candidates = []  # No grounding metadata
        mock_client.models.generate_content.return_value = mock_response
        
        with patch('agent.agents.get_genai_client', return_value=mock_client):
            with patch('agent.agents.types.Tool') as mock_tool:
                with patch('agent.agents.types.GoogleSearch', create=True) as mock_google_search:
                    result = await search_with_gemini_grounding("quantum computing")
                    
                    assert result['status'] == 'success'
                    assert bool(result['grounding_used']) is False
    
    @pytest.mark.asyncio
    async def test_grounding_api_error(self, mock_environment):
        """Test handling of API errors."""
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("API Error")
        
        with patch('agent.agents.get_genai_client', return_value=mock_client):
            with patch('agent.agents.types.Tool') as mock_tool:
                with patch('agent.agents.types.GoogleSearch', create=True) as mock_google_search:
                    result = await search_with_gemini_grounding("quantum computing")
                    
                    assert result['status'] == 'error'
                    assert result['source'] == 'gemini_grounding'
                    assert 'API Error' in result['error']
    
    @pytest.mark.asyncio
    async def test_grounding_client_creation_error(self, mock_environment):
        """Test handling of client creation errors."""
        with patch('agent.agents.get_genai_client', side_effect=ValueError("No API key")):
            result = await search_with_gemini_grounding("quantum computing")
            
            assert result['status'] == 'error'
            assert 'No API key' in result['error']


class TestSearchWeb:
    """Test the search_web function."""
    
    @pytest.mark.asyncio
    async def test_successful_gemini_grounding(self, mock_environment, mock_grounding_response):
        """Test successful search using Gemini grounding."""
        with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
            mock_grounding.return_value = {
                'status': 'success',
                'response': mock_grounding_response,
                'grounding_used': True,
                'source': 'gemini_grounding'
            }
            
            with patch('agent.agents.extract_sources_from_grounding') as mock_extract:
                mock_extract.return_value = [
                    MagicMock(title="Test Source", url="https://test.com")
                ]
                
                results = await search_web("quantum computing")
                
                assert len(results) > 0
                assert results[0]['source'] == 'gemini_grounding'
                assert results[0]['title'] == "Test Source"
                assert results[0]['url'] == "https://test.com"
    
    @pytest.mark.asyncio
    async def test_gemini_knowledge_response(self, mock_environment):
        """Test Gemini knowledge-based response (no grounding)."""
        with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
            mock_response = MagicMock()
            mock_response.text = "Knowledge-based answer about quantum computing"
            
            mock_grounding.return_value = {
                'status': 'success',
                'response': mock_response,
                'grounding_used': False,
                'source': 'gemini_grounding'
            }
            
            results = await search_web("quantum computing")
            
            assert len(results) == 1
            assert results[0]['source'] == 'gemini_knowledge'
            assert "Knowledge-based answer" in results[0]['title']
            assert "quantum+computing" in results[0]['url']
    
    @pytest.mark.asyncio 
    async def test_fallback_to_google_custom_search(self, mock_environment):
        """Test fallback to Google Custom Search API."""
        # Mock Gemini grounding failure
        with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
            mock_grounding.return_value = {
                'status': 'error',
                'error': 'Gemini failed',
                'source': 'gemini_grounding'
            }
            
            # Mock successful Google Custom Search
            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json = MagicMock(return_value={
                    "items": [
                        {
                            "title": "Quantum Computing Research",
                            "link": "https://quantum-research.com",
                            "snippet": "Latest quantum computing developments..."
                        }
                    ]
                })
                mock_response.raise_for_status = MagicMock()
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value.__aenter__.return_value = mock_client
                
                results = await search_web("quantum computing")
                
                assert len(results) == 1
                assert results[0]['source'] == 'google_custom'
                assert results[0]['title'] == "Quantum Computing Research"
    
    @pytest.mark.asyncio
    async def test_fallback_to_searchapi(self, mock_environment):
        """Test fallback to SearchAPI.io."""
        # Mock Gemini grounding failure to force fallback
        with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
            mock_grounding.return_value = {'status': 'error', 'error': 'Failed'}
            
            # Force Google Custom Search to fail by making API call raise exception
            with patch('httpx.AsyncClient') as mock_client_class:
                # Create a mock client that fails for Google Custom Search but succeeds for SearchAPI
                mock_client = AsyncMock()
                
                def mock_get_side_effect(url, **kwargs):
                    mock_response = MagicMock()
                    if 'googleapis.com' in url:
                        # Google Custom Search fails
                        raise Exception("Google Custom Search failed")
                    else:
                        # SearchAPI succeeds
                        mock_response.status_code = 200
                        mock_response.json = MagicMock(return_value={
                            "organic_results": [
                                {
                                    "title": "SearchAPI Result",
                                    "link": "https://searchapi-result.com",
                                    "snippet": "SearchAPI quantum computing info..."
                                }
                            ]
                        })
                    return mock_response
                    
                mock_client.get = AsyncMock(side_effect=mock_get_side_effect)
                mock_client_class.return_value.__aenter__.return_value = mock_client
                
                results = await search_web("quantum computing")
                
                assert len(results) == 1
                assert results[0]['source'] == 'searchapi'
                assert results[0]['title'] == "SearchAPI Result"
    
    @pytest.mark.asyncio
    async def test_fallback_to_duckduckgo(self, mock_environment):
        """Test fallback to DuckDuckGo search."""
        # Mock failures for previous search methods
        with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
            mock_grounding.return_value = {'status': 'error', 'error': 'Failed'}
            
            # Clear SearchAPI key to force DuckDuckGo fallback  
            with patch.dict('os.environ', {'SEARCHAPI_API_KEY': ''}):
                with patch('httpx.AsyncClient') as mock_client_class:
                    mock_client = AsyncMock()
                    
                    def mock_get_side_effect(url, **kwargs):
                        mock_response = MagicMock()
                        if 'googleapis.com' in url:
                            # Google Custom Search fails
                            raise Exception("Google Custom Search failed")
                        elif 'searchapi.io' in url:
                            # SearchAPI would fail (but shouldn't be called due to missing key)
                            raise Exception("SearchAPI failed")
                        else:
                            # DuckDuckGo succeeds
                            mock_response.status_code = 200
                            mock_response.json = MagicMock(return_value={
                                "AbstractText": "Quantum computing is a type of computation...",
                                "Heading": "Quantum Computing", 
                                "AbstractURL": "https://en.wikipedia.org/wiki/Quantum_computing",
                                "RelatedTopics": [
                                    {
                                        "Text": "Quantum algorithms description",
                                        "FirstURL": "https://example.com/quantum-algorithms"
                                    }
                                ]
                            })
                        return mock_response
                        
                    mock_client.get = AsyncMock(side_effect=mock_get_side_effect)
                    mock_client_class.return_value.__aenter__.return_value = mock_client
                    
                    results = await search_web("quantum computing")
                    
                    assert len(results) >= 1
                    assert results[0]['source'] == 'duckduckgo'
                    assert results[0]['title'] == "Quantum Computing"
    
    @pytest.mark.asyncio
    async def test_knowledge_base_fallback_france(self, mock_environment):
        """Test knowledge base fallback for France capital query."""
        # Mock all API failures
        with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
            mock_grounding.return_value = {'status': 'error', 'error': 'Failed'}
            
            with patch.dict('os.environ', {'GOOGLE_API_KEY': '', 'SEARCHAPI_API_KEY': ''}):
                with patch('httpx.AsyncClient') as mock_client_class:
                    mock_client = AsyncMock()
                    mock_client.side_effect = Exception("Network error")
                    mock_client_class.return_value.__aenter__.return_value = mock_client
                    
                    results = await search_web("capital of france")
                    
                    assert len(results) == 1
                    assert results[0]['source'] == 'knowledge_base'
                    assert "Paris" in results[0]['title']
    
    @pytest.mark.asyncio
    async def test_knowledge_base_fallback_python(self, mock_environment):
        """Test knowledge base fallback for Python query."""
        with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
            mock_grounding.return_value = {'status': 'error', 'error': 'Failed'}
            
            with patch.dict('os.environ', {'GOOGLE_API_KEY': '', 'SEARCHAPI_API_KEY': ''}):
                with patch('httpx.AsyncClient') as mock_client_class:
                    mock_client = AsyncMock()
                    mock_client.side_effect = Exception("Network error")
                    mock_client_class.return_value.__aenter__.return_value = mock_client
                    
                    results = await search_web("python programming")
                    
                    assert len(results) == 1
                    assert results[0]['source'] == 'knowledge_base'
                    assert "Python" in results[0]['title']
    
    @pytest.mark.asyncio
    async def test_knowledge_base_fallback_generic(self, mock_environment):
        """Test generic knowledge base fallback."""
        with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
            mock_grounding.return_value = {'status': 'error', 'error': 'Failed'}
            
            with patch.dict('os.environ', {'GOOGLE_API_KEY': '', 'SEARCHAPI_API_KEY': ''}):
                with patch('httpx.AsyncClient') as mock_client_class:
                    mock_client = AsyncMock()
                    mock_client.side_effect = Exception("Network error")
                    mock_client_class.return_value.__aenter__.return_value = mock_client
                    
                    results = await search_web("obscure topic")
                    
                    assert len(results) == 1
                    assert results[0]['source'] == 'knowledge_base'
                    assert "Information about: obscure topic" in results[0]['title']
    
    @pytest.mark.asyncio
    async def test_google_custom_search_http_error(self, mock_environment):
        """Test Google Custom Search API HTTP error handling."""
        with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
            mock_grounding.return_value = {'status': 'error', 'error': 'Failed'}
            
            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_response = MagicMock()
                mock_response.raise_for_status = MagicMock(side_effect=httpx.HTTPStatusError("404 Not Found", request=MagicMock(), response=MagicMock()))
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value.__aenter__.return_value = mock_client
                
                with patch.dict('os.environ', {'SEARCHAPI_API_KEY': ''}):
                    results = await search_web("quantum computing")
                    
                    # Should fallback to knowledge base
                    assert results[0]['source'] == 'knowledge_base'
    
    @pytest.mark.asyncio
    async def test_searchapi_non_200_status(self, mock_environment):
        """Test SearchAPI.io non-200 status code handling."""
        with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
            mock_grounding.return_value = {'status': 'error', 'error': 'Failed'}
            
            with patch('httpx.AsyncClient') as mock_client_class:
                mock_client = AsyncMock()
                
                def mock_get_side_effect(url, **kwargs):
                    mock_response = MagicMock()
                    if 'googleapis.com' in url:
                        # Google Custom Search fails
                        raise Exception("Google Custom Search failed")
                    elif 'searchapi.io' in url:
                        # SearchAPI returns 404
                        mock_response.status_code = 404
                    else:
                        # DuckDuckGo succeeds
                        mock_response.status_code = 200
                        mock_response.json = MagicMock(return_value={
                            "AbstractText": "Quantum computing fallback...",
                            "Heading": "Quantum Computing",
                            "AbstractURL": "https://en.wikipedia.org/wiki/Quantum_computing"
                        })
                    return mock_response
                    
                mock_client.get = AsyncMock(side_effect=mock_get_side_effect)
                mock_client_class.return_value.__aenter__.return_value = mock_client
                
                results = await search_web("quantum computing")
                
                # Should fallback to DuckDuckGo or knowledge base
                assert len(results) >= 1
                assert results[0]['source'] in ['duckduckgo', 'knowledge_base']
    
    @pytest.mark.asyncio
    async def test_duckduckgo_timeout(self, mock_environment):
        """Test DuckDuckGo timeout handling."""
        with patch('agent.agents.search_with_gemini_grounding') as mock_grounding:
            mock_grounding.return_value = {'status': 'error', 'error': 'Failed'}
            
            with patch.dict('os.environ', {'GOOGLE_API_KEY': '', 'SEARCHAPI_API_KEY': ''}):
                with patch('httpx.AsyncClient') as mock_client_class:
                    mock_client = AsyncMock()
                    mock_client.get = AsyncMock(side_effect=asyncio.TimeoutError("Timeout"))
                    mock_client_class.return_value.__aenter__.return_value = mock_client
                    
                    results = await search_web("quantum computing")
                    
                    # Should fallback to knowledge base
                    assert results[0]['source'] == 'knowledge_base'


class TestRunAsyncSearch:
    """Test the run_async_search function."""
    
    def test_run_async_search_new_loop(self):
        """Test running async search with new event loop."""
        with patch('agent.agents.search_web') as mock_search_web:
            mock_search_web.return_value = [{"title": "Test", "url": "test.com"}]
            
            with patch('asyncio.get_event_loop') as mock_get_loop:
                mock_get_loop.side_effect = RuntimeError("No current event loop")
                
                with patch('asyncio.run') as mock_run:
                    mock_run.return_value = [{"title": "Test", "url": "test.com"}]
                    
                    results = run_async_search("test query")
                    
                    mock_run.assert_called_once()
                    assert results == [{"title": "Test", "url": "test.com"}]
    
    def test_run_async_search_existing_loop_not_running(self):
        """Test with existing event loop that's not running."""
        with patch('agent.agents.search_web') as mock_search_web:
            mock_search_web.return_value = [{"title": "Test", "url": "test.com"}]
            
            mock_loop = MagicMock()
            mock_loop.is_running.return_value = False
            
            with patch('asyncio.get_event_loop', return_value=mock_loop):
                with patch('asyncio.run') as mock_run:
                    mock_run.return_value = [{"title": "Test", "url": "test.com"}]
                    
                    results = run_async_search("test query")
                    
                    mock_run.assert_called_once()
                    assert results == [{"title": "Test", "url": "test.com"}]
    
    def test_run_async_search_running_loop(self):
        """Test with running event loop using thread executor."""
        with patch('agent.agents.search_web') as mock_search_web:
            mock_search_web.return_value = [{"title": "Test", "url": "test.com"}]
            
            mock_loop = MagicMock()
            mock_loop.is_running.return_value = True
            
            with patch('asyncio.get_event_loop', return_value=mock_loop):
                with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
                    mock_future = MagicMock()
                    mock_future.result.return_value = [{"title": "Test", "url": "test.com"}]
                    
                    mock_executor_instance = MagicMock()
                    mock_executor_instance.__enter__.return_value = mock_executor_instance
                    mock_executor_instance.submit.return_value = mock_future
                    mock_executor.return_value = mock_executor_instance
                    
                    results = run_async_search("test query")
                    
                    mock_executor_instance.submit.assert_called_once()
                    assert results == [{"title": "Test", "url": "test.com"}]
    
    def test_run_async_search_exception_fallback(self):
        """Test exception handling and fallback to asyncio.run."""
        with patch('agent.agents.search_web') as mock_search_web:
            mock_search_web.return_value = [{"title": "Test", "url": "test.com"}]
            
            with patch('asyncio.get_event_loop', side_effect=Exception("Error")):
                with patch('asyncio.run') as mock_run:
                    mock_run.return_value = [{"title": "Test", "url": "test.com"}]
                    
                    results = run_async_search("test query")
                    
                    mock_run.assert_called_once()
                    assert results == [{"title": "Test", "url": "test.com"}]
    
    def test_run_async_search_with_num_results(self):
        """Test run_async_search with custom num_results parameter."""
        with patch('agent.agents.search_web') as mock_search_web:
            mock_search_web.return_value = [{"title": f"Test {i}", "url": f"test{i}.com"} for i in range(10)]
            
            with patch('asyncio.run') as mock_run:
                mock_run.return_value = [{"title": f"Test {i}", "url": f"test{i}.com"} for i in range(10)]
                
                results = run_async_search("test query", num_results=10)
                
                # Verify search_web was called with correct parameters
                expected_call = mock_search_web.return_value
                assert len(results) == 10