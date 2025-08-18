"""
Search module for the agent package.
Provides search providers and orchestration.
"""

from .base_provider import (
    BaseSearchProvider, 
    GroundingProvider, 
    FallbackProvider,
    SearchResult,
    SearchResponse,
    SearchStatus
)
from .search_manager import SearchManager, SearchStrategy, search_web
from .gemini_search import GeminiSearchProvider
from .google_custom_search import GoogleCustomSearchProvider
from .searchapi_provider import SearchAPIProvider
from .duckduckgo_search import DuckDuckGoProvider
from .fallback_provider import KnowledgeFallbackProvider

__all__ = [
    'BaseSearchProvider',
    'GroundingProvider', 
    'FallbackProvider',
    'SearchResult',
    'SearchResponse', 
    'SearchStatus',
    'SearchManager',
    'SearchStrategy',
    'search_web',
    'GeminiSearchProvider',
    'GoogleCustomSearchProvider',
    'SearchAPIProvider', 
    'DuckDuckGoProvider',
    'KnowledgeFallbackProvider'
]