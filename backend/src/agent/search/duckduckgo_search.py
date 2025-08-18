"""
DuckDuckGo search provider using their Instant Answer API.
"""

from typing import List, Dict, Any
import httpx

from .base_provider import BaseSearchProvider, SearchResponse, SearchResult, SearchStatus
from ..http_client import get_http_client


class DuckDuckGoProvider(BaseSearchProvider):
    """Search provider using DuckDuckGo Instant Answer API."""
    
    def __init__(self):
        super().__init__("duckduckgo")
        self.base_url = "https://api.duckduckgo.com/"
        self.timeout = 10.0
    
    def is_available(self) -> bool:
        """DuckDuckGo is always available (no API key required)."""
        return True
    
    async def search(self, query: str, num_results: int = 5) -> SearchResponse:
        """
        Search using DuckDuckGo Instant Answer API.
        
        Args:
            query: The search query string
            num_results: Maximum number of results to return
            
        Returns:
            SearchResponse with results or error information
        """
        self._log_search_attempt(query, num_results)
        
        try:
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            client = await get_http_client()
            response = await client.get(
                self.base_url, 
                params=params, 
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                error_msg = f"DuckDuckGo returned status {response.status_code}"
                self._log_search_error(error_msg, "Using knowledge-based fallback")
                return self._create_error_response(query, error_msg)
            
            data = response.json()
            results = self._parse_search_results(data, query, num_results)
            
            if results:
                self._log_search_success(len(results))
            else:
                self.logger.info("No instant answers or related topics found")
            
            return self._create_success_response(
                query=query,
                results=results,
                metadata={
                    'answer_type': data.get('AnswerType', ''),
                    'definition': data.get('Definition', ''),
                    'entity': data.get('Entity', ''),
                    'infobox': data.get('Infobox', {})
                }
            )
            
        except httpx.TimeoutException:
            error_msg = "DuckDuckGo request timed out"
            self._log_search_error(error_msg, "Using knowledge-based fallback")
            return self._create_error_response(query, error_msg)
            
        except httpx.RequestError as e:
            error_msg = f"Request failed: {str(e)}"
            self._log_search_error(error_msg, "Using knowledge-based fallback")
            return self._create_error_response(query, error_msg)
            
        except Exception as e:
            error_msg = f"DuckDuckGo search failed: {str(e)}"
            self._log_search_error(error_msg, "Using knowledge-based fallback")
            return self._create_error_response(query, error_msg)
    
    def _parse_search_results(self, data: Dict[str, Any], query: str, num_results: int) -> List[SearchResult]:
        """
        Parse DuckDuckGo API response into SearchResult objects.
        
        Args:
            data: Raw JSON response from DuckDuckGo API
            query: Original search query
            num_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
        """
        results = []
        
        # Try to get instant answer first
        if data.get("AbstractText"):
            result = SearchResult(
                title=data.get("Heading", query),
                url=data.get("AbstractURL", "https://duckduckgo.com/"),
                snippet=data.get("AbstractText", ""),
                source="duckduckgo",
                metadata={
                    'type': 'abstract',
                    'source_info': data.get('AbstractSource', ''),
                    'image': data.get('Image', ''),
                    'definition': data.get('Definition', ''),
                    'answer': data.get('Answer', '')
                }
            )
            results.append(result)
        
        # Add answer if available and different from abstract
        if data.get("Answer") and data.get("Answer") != data.get("AbstractText"):
            answer_result = SearchResult(
                title=f"Answer: {query}",
                url=data.get("AbstractURL", "https://duckduckgo.com/"),
                snippet=data.get("Answer", ""),
                source="duckduckgo",
                metadata={
                    'type': 'answer',
                    'answer_type': data.get('AnswerType', '')
                }
            )
            results.append(answer_result)
        
        # Add related topics
        remaining_slots = num_results - len(results)
        if remaining_slots > 0:
            related_topics = data.get("RelatedTopics", [])
            
            for topic in related_topics[:remaining_slots]:
                try:
                    if isinstance(topic, dict) and topic.get("Text"):
                        # Extract title from URL or use first few words of text
                        title = self._extract_title_from_topic(topic)
                        
                        topic_result = SearchResult(
                            title=title,
                            url=topic.get("FirstURL", ""),
                            snippet=topic.get("Text", ""),
                            source="duckduckgo",
                            metadata={
                                'type': 'related_topic',
                                'icon': topic.get('Icon', {}),
                                'result': topic.get('Result', '')
                            }
                        )
                        results.append(topic_result)
                        
                except Exception as e:
                    self.logger.warning_skip(f"Error parsing related topic: {e}")
                    continue
        
        return results
    
    def _extract_title_from_topic(self, topic: Dict[str, Any]) -> str:
        """
        Extract a meaningful title from a related topic.
        
        Args:
            topic: Related topic dictionary
            
        Returns:
            Extracted title string
        """
        try:
            # Try to get title from URL
            first_url = topic.get("FirstURL", "")
            if first_url:
                # Extract from Wikipedia-style URLs
                if "wikipedia.org" in first_url:
                    title_part = first_url.split("/")[-1]
                    return title_part.replace("_", " ").replace("%20", " ")
                
                # Extract from other URLs
                url_parts = first_url.split("/")
                if url_parts:
                    title_part = url_parts[-1]
                    if title_part:
                        return title_part.replace("_", " ").replace("-", " ")
            
            # Fallback to first few words of text
            text = topic.get("Text", "")
            if text:
                words = text.split()[:5]  # Take first 5 words
                return " ".join(words) + ("..." if len(text.split()) > 5 else "")
            
            return "Related Topic"
            
        except Exception:
            return "Related Topic"
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get information about the DuckDuckGo API."""
        return {
            'name': 'DuckDuckGo Instant Answer API',
            'requires_api_key': False,
            'rate_limits': 'Reasonable use policy',
            'documentation': 'https://duckduckgo.com/api',
            'features': [
                'Instant answers',
                'Abstract information',
                'Related topics',
                'Definitions',
                'Calculations'
            ],
            'limitations': [
                'Limited to instant answers and topics',
                'No traditional web search results',
                'May not return results for all queries'
            ]
        }