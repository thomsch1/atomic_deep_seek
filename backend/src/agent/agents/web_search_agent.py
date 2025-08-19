"""
Agent for performing web searches and research using Gemini grounding.
"""

import asyncio
from typing import List
from google import genai
from google.genai import types

from agent.base import BaseResearchAgent, handle_agent_errors, handle_async_agent_errors
from agent.state import WebSearchInput, WebSearchOutput, Source, Citation
from agent.configuration import Configuration
from agent.prompts import web_searcher_instructions
from agent.search import SearchManager
from agent.citation import GroundingProcessor, CitationFormatter


def get_genai_client():
    """Create and return GenAI client."""
    import os
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY must be set")
    return genai.Client(api_key=api_key)


class WebSearchAgent(BaseResearchAgent[WebSearchInput, WebSearchOutput]):
    """Updated agent using proper Gemini grounding and search providers."""
    
    def _initialize_agent_config(self) -> None:
        """Initialize the agent configuration."""
        self.agent_config = self.config.create_agent_config()
        self.client = get_genai_client()  # Create the genai client
        self.search_manager = SearchManager()
        self.grounding_processor = GroundingProcessor()
        self.citation_formatter = CitationFormatter()
        
        # Define grounding tools
        self.grounding_tool = types.Tool(google_search=types.GoogleSearch())
        
        # For legacy Gemini 1.5 models if needed
        self.legacy_tool = types.Tool(
            google_search_retrieval=types.GoogleSearchRetrieval(
                dynamic_retrieval_config=types.DynamicRetrievalConfig(
                    mode=types.DynamicRetrievalConfigMode.MODE_DYNAMIC,
                    dynamic_threshold=0.7
                )
            )
        )
    
    @handle_agent_errors(context="web search")
    def run(self, input_data: WebSearchInput) -> WebSearchOutput:
        """Perform web research using official Gemini grounding."""
        
        if not self._validate_input(input_data):
            return self._create_fallback_response(input_data, "invalid input")
        
        try:
            # Step 1: Try Gemini grounding first
            grounding_result = asyncio.run(self._search_with_gemini_grounding(input_data.search_query))
            
            if grounding_result['status'] == 'success':
                response = grounding_result['response']
                
                if grounding_result['grounding_used']:
                    # Extract sources from grounding metadata
                    sources = self.grounding_processor.extract_sources_from_grounding(response)
                    
                    # Add inline citations to the response with error handling
                    try:
                        content_with_citations = self.citation_formatter.add_inline_citations(response)
                    except Exception as e:
                        self._handle_error(e, "citation insertion")
                        content_with_citations = response.text
                    
                    # Create citation objects with error handling
                    try:
                        citations = self.grounding_processor.create_citations_from_grounding(response)
                    except Exception as e:
                        self._handle_error(e, "citation creation")
                        citations = []
                    
                    print(f"✅ Gemini grounding provided {len(sources)} sources with {len(citations)} citations")
                    
                    return WebSearchOutput(
                        content=content_with_citations,
                        sources=sources,
                        citations=citations
                    )
                else:
                    # Model used its knowledge without grounding
                    print("ℹ️ Gemini answered from knowledge (no grounding used)")
                    return WebSearchOutput(
                        content=response.text,
                        sources=[],
                        citations=[]
                    )
            else:
                # Gemini grounding failed, fall back to traditional search
                print(f"❌ Gemini grounding failed: {grounding_result.get('error', 'Unknown error')}")
                print("🔄 Falling back to traditional search method")
                return self._fallback_search(input_data)
                
        except Exception as e:
            self._handle_error(e, "web search")
            return self._fallback_search(input_data)
    
    @handle_async_agent_errors(context="gemini grounding")
    async def _search_with_gemini_grounding(self, query: str) -> dict:
        """Primary search using Gemini grounding with proper error handling."""
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
            grounding_used = (hasattr(response, 'candidates') and 
                             response.candidates and 
                             hasattr(response.candidates[0], 'grounding_metadata') and
                             response.candidates[0].grounding_metadata)
            
            if not grounding_used:
                print("ℹ️ Model answered from knowledge, no search performed")
                
            return {
                'status': 'success',
                'response': response,
                'grounding_used': grounding_used,
                'source': 'gemini_grounding'
            }
            
        except Exception as e:
            print(f"❌ Gemini grounding failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'source': 'gemini_grounding'
            }
    
    @handle_agent_errors(context="fallback search")
    def _fallback_search(self, input_data: WebSearchInput) -> WebSearchOutput:
        """Fallback to traditional search method."""
        try:
            # Step 1: Perform web search to get real results
            search_results = self.search_manager.search_web(input_data.search_query, num_results=5)
            
            if not search_results:
                # Fallback if no search results
                return WebSearchOutput(
                    content=f"No search results found for: {input_data.search_query}",
                    sources=[],
                    citations=[]
                )
            
            # Step 2: Create context from search results
            search_context = f"Search Query: {input_data.search_query}\n\nSearch Results:\n"
            sources = []
            
            for i, result in enumerate(search_results):
                search_context += f"\n[{i+1}] Title: {result['title']}\n"
                search_context += f"URL: {result['url']}\n"
                search_context += f"Snippet: {result['snippet']}\n"
                
                # Create source objects
                if result['url']:  # Only add sources with valid URLs
                    source = Source(
                        title=result['title'],
                        url=result['url'],
                        short_url=f"source-{input_data.query_id}-{i+1}",
                        label=f"Source {i+1}"
                    )
                    sources.append(source)
            
            # Step 3: Format the prompt for the AI to synthesize information
            formatted_prompt = web_searcher_instructions.format(
                current_date=input_data.current_date,
                research_topic=input_data.search_query,
            )
            
            full_prompt = f"{formatted_prompt}\n\n{search_context}\n\nPlease provide a comprehensive answer based on the search results above. Include relevant information from multiple sources and synthesize the findings."
            
            # Step 4: Generate AI response based on search results (fallback to old method)
            config = types.GenerateContentConfig()
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=config
            )
            
            # Step 5: Add citations to the response using citation formatter
            content_with_citations = self._add_citations_to_content(response.text, sources)
            
            return WebSearchOutput(
                content=content_with_citations,
                sources=sources,
                citations=self._create_citation_objects(sources)
            )
            
        except Exception as e:
            self._handle_error(e, "fallback search")
            return self._create_fallback_response(input_data, "fallback search failed")
    
    def _add_citations_to_content(self, content: str, sources: List[Source]) -> str:
        """Add citation markers to the content."""
        if not sources:
            return content
        
        # Add inline citation at the end of the content and references section
        inline_citations = []
        references_text = "\n\n## References\n"
        
        for i, source in enumerate(sources):
            inline_citations.append(f"[{i+1}]({source.url})")
            references_text += f"{i+1}. [{source.title}]({source.url})\n"
        
        # Add inline citations at the end of the main content
        if inline_citations:
            citation_string = " " + ", ".join(inline_citations)
            content_with_inline = content.rstrip() + citation_string
        else:
            content_with_inline = content
        
        return content_with_inline + references_text
    
    def _create_citation_objects(self, sources: List[Source]) -> List[Citation]:
        """Create citation objects from sources."""
        citations = []
        for i, source in enumerate(sources):
            citation = Citation(
                start_index=0,  # For simplicity, citing the whole content
                end_index=0,
                segments=[source]
            )
            citations.append(citation)
        
        return citations
    
    def _create_fallback_response(self, input_data: WebSearchInput, error_context: str) -> WebSearchOutput:
        """Create a fallback response when web search fails."""
        # Handle None input_data safely
        search_query = "unknown query"
        
        if input_data is not None:
            search_query = getattr(input_data, 'search_query', None) or "unknown query"
        
        print(f"🔄 Using fallback web search response for: {search_query}")
        
        fallback_content = f"Unable to perform web search for: {search_query}. "
        fallback_content += f"Error context: {error_context}. "
        fallback_content += "Please try again later or refine your search query."
        
        return WebSearchOutput(
            content=fallback_content,
            sources=[],
            citations=[]
        )