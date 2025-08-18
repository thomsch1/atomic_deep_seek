"""
Gemini grounding search provider using Google's Gemini API with search integration.
"""

import os
from typing import Dict, List, Any, Optional
from google import genai
from google.genai import types

from .base_provider import GroundingProvider, SearchResponse, SearchResult, SearchStatus
from ..logging_config import AgentLogger


class GeminiSearchProvider(GroundingProvider):
    """Search provider using Gemini's grounding capabilities."""
    
    def __init__(self):
        super().__init__("gemini_grounding")
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Gemini client."""
        try:
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                self.logger.error("No API key found for Gemini client")
                return
            
            self.client = genai.Client(api_key=api_key)
            self.logger.info("Gemini client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Gemini search is available."""
        return self.client is not None
    
    async def search(self, query: str, num_results: int = 5) -> SearchResponse:
        """
        Search using Gemini with grounding, then convert to standard format.
        """
        if not self.is_available():
            return self._create_error_response(
                query, 
                "Gemini client not available or API key missing"
            )
        
        try:
            self._log_search_attempt(query, num_results)
            
            # Use grounding search
            grounding_result = await self.search_with_grounding(query, num_results)
            
            if grounding_result['status'] == 'error':
                return self._create_error_response(query, grounding_result['error'])
            
            # Convert grounding result to standard format
            results = []
            if grounding_result.get('grounding_used') and 'response' in grounding_result:
                sources = self.extract_grounding_sources(grounding_result['response'])
                
                for source in sources[:num_results]:
                    results.append(SearchResult(
                        title=source.get('title', 'No title'),
                        url=source.get('uri', ''),
                        snippet=source.get('snippet', ''),
                        source='gemini_grounding',
                        metadata={'grounding_chunk': source}
                    ))
            
            if results:
                self._log_search_success(len(results))
            else:
                self.logger.info_knowledge("Model answered from knowledge, no search performed")
            
            return self._create_success_response(
                query=query,
                results=results,
                grounding_used=grounding_result.get('grounding_used', False),
                metadata={'raw_response': grounding_result}
            )
            
        except Exception as e:
            self._log_search_error(str(e), "Falling back to next provider")
            return self._create_error_response(query, str(e))
    
    async def search_with_grounding(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Execute search using Gemini grounding with proper error handling.
        """
        if not self.client:
            return {
                'status': 'error',
                'error': 'Gemini client not initialized',
                'grounding_used': False
            }
        
        try:
            # Define grounding tool (for Gemini 2.0+) with error handling
            try:
                grounding_tool = types.Tool(
                    google_search=types.GoogleSearch()
                )
            except AttributeError:
                # Fallback if GoogleSearch is not available
                return {
                    'status': 'error',
                    'error': 'GoogleSearch tool not available in current SDK version',
                    'grounding_used': False
                }
            
            # Configure generation settings
            try:
                config = types.GenerateContentConfig(
                    tools=[grounding_tool]
                )
            except AttributeError:
                # Fallback if GenerateContentConfig is not available
                config = None
            
            # Make the request
            if config:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"Provide comprehensive information about: {query}",
                    config=config
                )
            else:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"Provide comprehensive information about: {query}"
                )
            
            # Check if grounding was used
            grounding_used = (
                hasattr(response, 'candidates') and 
                response.candidates and 
                hasattr(response.candidates[0], 'grounding_metadata') and
                response.candidates[0].grounding_metadata
            )
            
            if not grounding_used:
                self.logger.info_knowledge("Model answered from knowledge, no search performed")
                
            return {
                'status': 'success',
                'response': response,
                'grounding_used': grounding_used,
                'source': 'gemini_grounding'
            }
            
        except Exception as e:
            self.logger.error_with_fallback(f"Gemini grounding failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'source': 'gemini_grounding'
            }
    
    def extract_grounding_sources(self, response: Any) -> List[Dict[str, Any]]:
        """
        Extract source information from Gemini grounding metadata.
        
        Args:
            response: Gemini response with grounding metadata
            
        Returns:
            List of source dictionaries with title, uri, snippet
        """
        sources = []
        
        try:
            if not (hasattr(response, 'candidates') and response.candidates):
                return sources
                
            candidate = response.candidates[0]
            if not hasattr(candidate, 'grounding_metadata'):
                return sources
                
            grounding_metadata = candidate.grounding_metadata
            if not hasattr(grounding_metadata, 'grounding_chunks'):
                return sources
            
            for chunk in grounding_metadata.grounding_chunks:
                if hasattr(chunk, 'web'):
                    web_chunk = chunk.web
                    source_info = {
                        'title': getattr(web_chunk, 'title', 'No title'),
                        'uri': getattr(web_chunk, 'uri', ''),
                        'snippet': getattr(web_chunk, 'snippet', ''),
                        'grounding_support': getattr(chunk, 'grounding_support', None)
                    }
                    sources.append(source_info)
                    
        except Exception as e:
            self.logger.warning_skip(f"Error extracting grounding sources: {e}")
        
        return sources
    
    def get_model_response_text(self, response: Any) -> str:
        """
        Extract text from Gemini response.
        
        Args:
            response: Gemini response object
            
        Returns:
            Extracted text content
        """
        try:
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    parts = candidate.content.parts
                    if parts and hasattr(parts[0], 'text'):
                        return parts[0].text
            return ""
        except Exception as e:
            self.logger.warning_skip(f"Error extracting response text: {e}")
            return ""