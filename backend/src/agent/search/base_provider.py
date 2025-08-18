"""
Base search provider interface for all search implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from ..logging_config import AgentLogger


class SearchStatus(Enum):
    """Status enum for search operations."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    NO_RESULTS = "no_results"


@dataclass
class SearchResult:
    """Standard search result format."""
    title: str
    url: str
    snippet: str
    source: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass 
class SearchResponse:
    """Standard search response format."""
    status: SearchStatus
    results: List[SearchResult]
    query: str
    provider: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    grounding_used: bool = False
    
    def has_results(self) -> bool:
        """Check if the response contains results."""
        return bool(self.results)
    
    def result_count(self) -> int:
        """Get number of results."""
        return len(self.results)


class BaseSearchProvider(ABC):
    """Abstract base class for all search providers."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = AgentLogger(f"search.{name}")
    
    @abstractmethod
    async def search(self, query: str, num_results: int = 5) -> SearchResponse:
        """
        Execute a search query and return results.
        
        Args:
            query: The search query string
            num_results: Maximum number of results to return
            
        Returns:
            SearchResponse with results or error information
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the search provider is available and configured.
        
        Returns:
            True if provider can be used, False otherwise
        """
        pass
    
    def get_name(self) -> str:
        """Get the provider name."""
        return self.name
    
    def _create_error_response(
        self, 
        query: str, 
        error: str,
        status: SearchStatus = SearchStatus.ERROR
    ) -> SearchResponse:
        """Create a standardized error response."""
        return SearchResponse(
            status=status,
            results=[],
            query=query,
            provider=self.name,
            error=error
        )
    
    def _create_success_response(
        self,
        query: str,
        results: List[SearchResult],
        metadata: Optional[Dict[str, Any]] = None,
        grounding_used: bool = False
    ) -> SearchResponse:
        """Create a standardized success response."""
        status = SearchStatus.SUCCESS if results else SearchStatus.NO_RESULTS
        
        return SearchResponse(
            status=status,
            results=results,
            query=query,
            provider=self.name,
            metadata=metadata,
            grounding_used=grounding_used
        )
    
    def _log_search_attempt(self, query: str, num_results: int) -> None:
        """Log search attempt."""
        self.logger.info(f"Attempting search: '{query}' (max {num_results} results)")
    
    def _log_search_success(self, result_count: int) -> None:
        """Log successful search."""
        self.logger.info_success(f"Search returned {result_count} results")
    
    def _log_search_error(self, error: str, fallback_msg: Optional[str] = None) -> None:
        """Log search error with optional fallback message."""
        self.logger.error_with_fallback(f"Search failed: {error}", fallback_msg)
    
    def _log_search_warning(self, message: str) -> None:
        """Log search warning."""
        self.logger.warning_skip(message)


class GroundingProvider(BaseSearchProvider):
    """Base class for providers that support grounding/citations."""
    
    @abstractmethod
    async def search_with_grounding(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Execute search with grounding metadata for citations.
        
        Args:
            query: The search query string
            num_results: Maximum number of results to return
            
        Returns:
            Dictionary with grounding metadata and results
        """
        pass
    
    def extract_grounding_sources(self, grounding_data: Any) -> List[Dict[str, Any]]:
        """Extract source information from grounding metadata."""
        # Default implementation - subclasses should override
        return []


class FallbackProvider(BaseSearchProvider):
    """Base class for fallback/knowledge-based providers."""
    
    @abstractmethod
    def get_fallback_results(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """
        Get fallback results when other providers fail.
        
        Args:
            query: The search query string
            num_results: Maximum number of results to return
            
        Returns:
            List of fallback search results
        """
        pass