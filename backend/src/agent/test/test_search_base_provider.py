"""
Tests for search base provider functionality.
"""

import pytest
from unittest.mock import MagicMock
from agent.search.base_provider import (
    BaseSearchProvider,
    GroundingProvider, 
    FallbackProvider,
    SearchResult,
    SearchResponse,
    SearchStatus
)


class TestSearchResult:
    """Test SearchResult dataclass."""
    
    def test_search_result_creation(self):
        """Test SearchResult creation."""
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            snippet="Test snippet",
            source="test_provider",
            metadata={"key": "value"}
        )
        
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.snippet == "Test snippet" 
        assert result.source == "test_provider"
        assert result.metadata == {"key": "value"}


class TestSearchResponse:
    """Test SearchResponse dataclass."""
    
    def test_search_response_creation(self):
        """Test SearchResponse creation."""
        result = SearchResult(
            title="Test",
            url="https://example.com", 
            snippet="snippet",
            source="test"
        )
        
        response = SearchResponse(
            status=SearchStatus.SUCCESS,
            results=[result],
            query="test query",
            provider="test_provider"
        )
        
        assert response.status == SearchStatus.SUCCESS
        assert len(response.results) == 1
        assert response.query == "test query"
        assert response.provider == "test_provider"
    
    def test_has_results(self):
        """Test has_results method."""
        response_with_results = SearchResponse(
            status=SearchStatus.SUCCESS,
            results=[MagicMock()],
            query="test",
            provider="test"
        )
        
        response_without_results = SearchResponse(
            status=SearchStatus.NO_RESULTS,
            results=[],
            query="test", 
            provider="test"
        )
        
        assert response_with_results.has_results() is True
        assert response_without_results.has_results() is False
    
    def test_result_count(self):
        """Test result_count method."""
        response = SearchResponse(
            status=SearchStatus.SUCCESS,
            results=[MagicMock(), MagicMock(), MagicMock()],
            query="test",
            provider="test"
        )
        
        assert response.result_count() == 3


class ConcreteSearchProvider(BaseSearchProvider):
    """Concrete implementation for testing."""
    
    async def search(self, query: str, num_results: int = 5) -> SearchResponse:
        return self._create_success_response(query, [])
    
    def is_available(self) -> bool:
        return True


class TestBaseSearchProvider:
    """Test BaseSearchProvider abstract class."""
    
    def test_provider_initialization(self):
        """Test provider initialization."""
        provider = ConcreteSearchProvider("test_provider")
        
        assert provider.name == "test_provider"
        assert provider.get_name() == "test_provider"
        assert provider.logger is not None
    
    def test_is_available(self):
        """Test is_available method.""" 
        provider = ConcreteSearchProvider("test")
        assert provider.is_available() is True
    
    def test_create_error_response(self):
        """Test error response creation."""
        provider = ConcreteSearchProvider("test")
        
        response = provider._create_error_response("test query", "test error")
        
        assert response.status == SearchStatus.ERROR
        assert response.query == "test query"
        assert response.error == "test error"
        assert response.provider == "test"
        assert not response.has_results()
    
    def test_create_success_response(self):
        """Test success response creation."""
        provider = ConcreteSearchProvider("test")
        
        results = [SearchResult("title", "url", "snippet", "test")]
        response = provider._create_success_response("query", results)
        
        assert response.status == SearchStatus.SUCCESS
        assert response.query == "query"
        assert response.provider == "test"
        assert response.has_results()
        assert response.result_count() == 1
    
    def test_create_success_response_no_results(self):
        """Test success response with no results."""
        provider = ConcreteSearchProvider("test")
        
        response = provider._create_success_response("query", [])
        
        assert response.status == SearchStatus.NO_RESULTS
        assert not response.has_results()
    
    @pytest.mark.asyncio
    async def test_search_method(self):
        """Test concrete search implementation."""
        provider = ConcreteSearchProvider("test")
        
        response = await provider.search("test query")
        
        assert isinstance(response, SearchResponse)
        assert response.status == SearchStatus.NO_RESULTS


class ConcreteGroundingProvider(GroundingProvider):
    """Concrete grounding provider for testing."""
    
    async def search(self, query: str, num_results: int = 5) -> SearchResponse:
        return self._create_success_response(query, [])
    
    def is_available(self) -> bool:
        return True
    
    async def search_with_grounding(self, query: str, num_results: int = 5) -> dict:
        return {"status": "success", "grounding_used": True}


class TestGroundingProvider:
    """Test GroundingProvider class."""
    
    @pytest.mark.asyncio
    async def test_search_with_grounding(self):
        """Test search with grounding method."""
        provider = ConcreteGroundingProvider("grounding_test")
        
        result = await provider.search_with_grounding("test query")
        
        assert result["status"] == "success"
        assert result["grounding_used"] is True
    
    def test_extract_grounding_sources(self):
        """Test extract grounding sources method."""
        provider = ConcreteGroundingProvider("grounding_test")
        
        sources = provider.extract_grounding_sources(None)
        
        assert isinstance(sources, list)
        assert len(sources) == 0  # Default implementation


class ConcreteFallbackProvider(FallbackProvider):
    """Concrete fallback provider for testing."""
    
    async def search(self, query: str, num_results: int = 5) -> SearchResponse:
        results = self.get_fallback_results(query, num_results)
        return self._create_success_response(query, results)
    
    def is_available(self) -> bool:
        return True
    
    def get_fallback_results(self, query: str, num_results: int = 5) -> list:
        return [SearchResult("Fallback", "http://fallback.com", "fallback snippet", "fallback")]


class TestFallbackProvider:
    """Test FallbackProvider class."""
    
    def test_get_fallback_results(self):
        """Test get fallback results method."""
        provider = ConcreteFallbackProvider("fallback_test")
        
        results = provider.get_fallback_results("test query")
        
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0].title == "Fallback"
    
    @pytest.mark.asyncio
    async def test_search_with_fallback(self):
        """Test search using fallback."""
        provider = ConcreteFallbackProvider("fallback_test") 
        
        response = await provider.search("test query")
        
        assert response.status == SearchStatus.SUCCESS
        assert response.has_results()
        assert response.result_count() == 1