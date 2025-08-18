"""
Google Custom Search API provider.
"""

import os
from typing import List
import httpx

from .base_provider import BaseSearchProvider, SearchResponse, SearchResult, SearchStatus
from ..http_client import get_http_client


class GoogleCustomSearchProvider(BaseSearchProvider):
    """Search provider using Google Custom Search API."""
    
    def __init__(self):
        super().__init__("google_custom")
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def is_available(self) -> bool:
        """Check if Google Custom Search is available."""
        return bool(self.api_key and self.search_engine_id)
    
    async def search(self, query: str, num_results: int = 5) -> SearchResponse:
        """
        Search using Google Custom Search API.
        
        Args:
            query: The search query string
            num_results: Maximum number of results (limited to 10 by Google)
            
        Returns:
            SearchResponse with results or error information
        """
        if not self.is_available():
            return self._create_error_response(
                query,
                "Google Custom Search not configured - missing API key or search engine ID"
            )
        
        self._log_search_attempt(query, num_results)
        
        try:
            # Google limits to 10 results per request
            limited_results = min(num_results, 10)
            
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": limited_results
            }
            
            client = await get_http_client()
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = self._parse_search_results(data)
            
            if results:
                self._log_search_success(len(results))
            else:
                self.logger.info("No results found for query")
            
            return self._create_success_response(
                query=query,
                results=results,
                metadata={
                    'total_results': data.get('searchInformation', {}).get('totalResults', '0'),
                    'search_time': data.get('searchInformation', {}).get('searchTime', '0')
                }
            )
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            self._log_search_error(error_msg, "Falling back to next provider")
            return self._create_error_response(query, error_msg)
            
        except httpx.RequestError as e:
            error_msg = f"Request failed: {str(e)}"
            self._log_search_error(error_msg, "Falling back to next provider")
            return self._create_error_response(query, error_msg)
            
        except Exception as e:
            error_msg = f"Google Custom Search failed: {str(e)}"
            self._log_search_error(error_msg, "Falling back to next provider")
            return self._create_error_response(query, error_msg)
    
    def _parse_search_results(self, data: dict) -> List[SearchResult]:
        """
        Parse Google Custom Search API response into SearchResult objects.
        
        Args:
            data: Raw JSON response from Google API
            
        Returns:
            List of SearchResult objects
        """
        results = []
        
        if "items" not in data:
            return results
        
        for item in data["items"]:
            try:
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source="google_custom",
                    metadata={
                        'display_link': item.get('displayLink', ''),
                        'formatted_url': item.get('formattedUrl', ''),
                        'cache_id': item.get('cacheId', ''),
                        'page_map': item.get('pagemap', {})
                    }
                )
                results.append(result)
                
            except Exception as e:
                self.logger.warning_skip(f"Error parsing search result item: {e}")
                continue
        
        return results
    
    def get_quota_info(self) -> dict:
        """
        Get information about API quota usage (if available).
        Note: This would require additional API calls to check quota.
        """
        return {
            'daily_limit': 100,  # Default free tier limit
            'queries_per_second': 10,  # Rate limit
            'note': 'Quota info requires separate API call'
        }