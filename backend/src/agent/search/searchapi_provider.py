"""
SearchAPI.io provider for web search.
"""

import os
from typing import List
import httpx

from .base_provider import BaseSearchProvider, SearchResponse, SearchResult, SearchStatus
from ..http_client import get_http_client


class SearchAPIProvider(BaseSearchProvider):
    """Search provider using SearchAPI.io service."""
    
    def __init__(self):
        super().__init__("searchapi")
        self.api_key = os.getenv("SEARCHAPI_API_KEY")
        self.base_url = "https://www.searchapi.io/api/v1/search"
    
    def is_available(self) -> bool:
        """Check if SearchAPI is available."""
        return bool(self.api_key)
    
    async def search(self, query: str, num_results: int = 5) -> SearchResponse:
        """
        Search using SearchAPI.io service.
        
        Args:
            query: The search query string
            num_results: Maximum number of results to return
            
        Returns:
            SearchResponse with results or error information
        """
        if not self.is_available():
            return self._create_error_response(
                query,
                "SearchAPI not configured - missing API key"
            )
        
        self._log_search_attempt(query, num_results)
        
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.api_key
            }
            
            client = await get_http_client()
            response = await client.get(self.base_url, params=params)
            
            if response.status_code != 200:
                error_msg = f"SearchAPI returned status {response.status_code}: {response.text}"
                self._log_search_error(error_msg, "Falling back to next provider")
                return self._create_error_response(query, error_msg)
            
            data = response.json()
            results = self._parse_search_results(data, num_results)
            
            if results:
                self._log_search_success(len(results))
            else:
                self.logger.info("No organic results found")
            
            return self._create_success_response(
                query=query,
                results=results,
                metadata={
                    'search_metadata': data.get('search_metadata', {}),
                    'total_results': len(data.get("organic_results", []))
                }
            )
            
        except httpx.RequestError as e:
            error_msg = f"Request failed: {str(e)}"
            self._log_search_error(error_msg, "Falling back to next provider")
            return self._create_error_response(query, error_msg)
            
        except Exception as e:
            error_msg = f"SearchAPI failed: {str(e)}"
            self._log_search_error(error_msg, "Falling back to next provider")
            return self._create_error_response(query, error_msg)
    
    def _parse_search_results(self, data: dict, num_results: int) -> List[SearchResult]:
        """
        Parse SearchAPI.io response into SearchResult objects.
        
        Args:
            data: Raw JSON response from SearchAPI
            num_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
        """
        results = []
        organic_results = data.get("organic_results", [])
        
        for item in organic_results[:num_results]:
            try:
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source="searchapi",
                    metadata={
                        'position': item.get('position', 0),
                        'displayed_link': item.get('displayed_link', ''),
                        'favicon': item.get('favicon', ''),
                        'date': item.get('date', ''),
                        'rich_snippet': item.get('rich_snippet', {})
                    }
                )
                results.append(result)
                
            except Exception as e:
                self.logger.warning_skip(f"Error parsing search result item: {e}")
                continue
        
        return results
    
    def get_supported_engines(self) -> List[str]:
        """Get list of supported search engines."""
        return [
            "google",
            "bing", 
            "yahoo",
            "duckduckgo",
            "yandex",
            "baidu"
        ]
    
    async def search_with_engine(
        self, 
        query: str, 
        engine: str = "google", 
        num_results: int = 5
    ) -> SearchResponse:
        """
        Search using a specific search engine.
        
        Args:
            query: The search query string
            engine: Search engine to use (google, bing, etc.)
            num_results: Maximum number of results to return
            
        Returns:
            SearchResponse with results or error information
        """
        if not self.is_available():
            return self._create_error_response(
                query,
                "SearchAPI not configured - missing API key"
            )
        
        if engine not in self.get_supported_engines():
            return self._create_error_response(
                query,
                f"Unsupported engine: {engine}"
            )
        
        self.logger.info(f"Searching with {engine} engine")
        
        try:
            params = {
                "engine": engine,
                "q": query,
                "api_key": self.api_key
            }
            
            client = await get_http_client()
            response = await client.get(self.base_url, params=params)
            
            if response.status_code != 200:
                error_msg = f"SearchAPI ({engine}) returned status {response.status_code}"
                return self._create_error_response(query, error_msg)
            
            data = response.json()
            results = self._parse_search_results(data, num_results)
            
            return self._create_success_response(
                query=query,
                results=results,
                metadata={
                    'engine': engine,
                    'search_metadata': data.get('search_metadata', {})
                }
            )
            
        except Exception as e:
            error_msg = f"SearchAPI ({engine}) failed: {str(e)}"
            return self._create_error_response(query, error_msg)