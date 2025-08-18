"""
Search manager that orchestrates multiple search providers with fallback logic.
"""

import asyncio
from typing import List, Dict, Any, Optional, Type
from enum import Enum

from .base_provider import BaseSearchProvider, SearchResponse, SearchResult, SearchStatus
from .gemini_search import GeminiSearchProvider
from .google_custom_search import GoogleCustomSearchProvider
from .searchapi_provider import SearchAPIProvider
from .duckduckgo_search import DuckDuckGoProvider
from .fallback_provider import KnowledgeFallbackProvider
from ..logging_config import AgentLogger


class SearchStrategy(Enum):
    """Search strategy enum."""
    SEQUENTIAL = "sequential"  # Try providers one by one until success
    PARALLEL = "parallel"      # Try multiple providers in parallel
    BEST_EFFORT = "best_effort"  # Try all and return best result


class SearchManager:
    """Manages multiple search providers with fallback and retry logic."""
    
    def __init__(self, strategy: SearchStrategy = SearchStrategy.SEQUENTIAL):
        self.logger = AgentLogger("search.manager")
        self.strategy = strategy
        self._providers = []
        self._fallback_provider = None
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize search providers in priority order."""
        # Primary providers (external APIs)
        provider_classes = [
            GeminiSearchProvider,
            GoogleCustomSearchProvider, 
            SearchAPIProvider,
            DuckDuckGoProvider
        ]
        
        for provider_class in provider_classes:
            try:
                provider = provider_class()
                if provider.is_available():
                    self._providers.append(provider)
                    self.logger.info(f"Initialized {provider.get_name()} provider")
                else:
                    self.logger.warning(f"{provider.get_name()} provider not available")
            except Exception as e:
                self.logger.warning_skip(f"Failed to initialize {provider_class.__name__}: {e}")
        
        # Always initialize fallback provider
        try:
            self._fallback_provider = KnowledgeFallbackProvider()
            self.logger.info("Initialized knowledge fallback provider")
        except Exception as e:
            self.logger.error(f"Failed to initialize fallback provider: {e}")
        
        self.logger.info(f"Search manager initialized with {len(self._providers)} providers")
    
    async def search(
        self, 
        query: str, 
        num_results: int = 5, 
        strategy: Optional[SearchStrategy] = None
    ) -> SearchResponse:
        """
        Execute search using configured strategy.
        
        Args:
            query: The search query
            num_results: Maximum number of results to return
            strategy: Override default search strategy
            
        Returns:
            SearchResponse with results from best available provider
        """
        if not query.strip():
            return self._create_error_response("Empty query provided")
        
        search_strategy = strategy or self.strategy
        self.logger.info(f"Executing search with {search_strategy.value} strategy: '{query}'")
        
        if search_strategy == SearchStrategy.SEQUENTIAL:
            return await self._search_sequential(query, num_results)
        elif search_strategy == SearchStrategy.PARALLEL:
            return await self._search_parallel(query, num_results)
        elif search_strategy == SearchStrategy.BEST_EFFORT:
            return await self._search_best_effort(query, num_results)
        else:
            return self._create_error_response(f"Unknown search strategy: {search_strategy}")
    
    async def _search_sequential(self, query: str, num_results: int) -> SearchResponse:
        """Search providers sequentially until one succeeds."""
        for provider in self._providers:
            try:
                self.logger.info(f"Trying {provider.get_name()} provider")
                response = await provider.search(query, num_results)
                
                if response.status == SearchStatus.SUCCESS and response.has_results():
                    self.logger.info_success(f"{provider.get_name()} provided {response.result_count()} results")
                    return response
                elif response.status == SearchStatus.SUCCESS:
                    self.logger.info(f"{provider.get_name()} succeeded but returned no results")
                    continue
                else:
                    self.logger.info_fallback(f"{provider.get_name()} failed, trying next provider")
                    continue
                    
            except Exception as e:
                self.logger.warning_skip(f"{provider.get_name()} raised exception: {e}")
                continue
        
        # All providers failed, use fallback
        return await self._use_fallback(query, num_results)
    
    async def _search_parallel(self, query: str, num_results: int) -> SearchResponse:
        """Search providers in parallel and return first successful result."""
        if not self._providers:
            return await self._use_fallback(query, num_results)
        
        # Create tasks for all available providers
        tasks = []
        for provider in self._providers:
            task = asyncio.create_task(
                self._safe_provider_search(provider, query, num_results)
            )
            tasks.append((provider.get_name(), task))
        
        try:
            # Wait for first successful result
            while tasks:
                done, pending = await asyncio.wait(
                    [task for _, task in tasks], 
                    return_when=asyncio.FIRST_COMPLETED,
                    timeout=30.0  # Overall timeout
                )
                
                for task in done:
                    try:
                        response = await task
                        if response and response.status == SearchStatus.SUCCESS and response.has_results():
                            # Cancel remaining tasks
                            for _, pending_task in tasks:
                                if pending_task in pending:
                                    pending_task.cancel()
                            
                            self.logger.info_success(f"Parallel search succeeded with {response.result_count()} results")
                            return response
                    except Exception as e:
                        self.logger.warning_skip(f"Parallel task failed: {e}")
                
                # Remove completed tasks
                tasks = [(name, task) for name, task in tasks if task in pending]
            
        except asyncio.TimeoutError:
            self.logger.warning_skip("Parallel search timed out")
        
        # Cancel any remaining tasks and use fallback
        for _, task in tasks:
            task.cancel()
        
        return await self._use_fallback(query, num_results)
    
    async def _search_best_effort(self, query: str, num_results: int) -> SearchResponse:
        """Try all providers and return the best result."""
        results = []
        
        # Try all providers
        for provider in self._providers:
            try:
                response = await self._safe_provider_search(provider, query, num_results)
                if response and response.status == SearchStatus.SUCCESS:
                    results.append(response)
            except Exception as e:
                self.logger.warning_skip(f"{provider.get_name()} failed in best-effort search: {e}")
        
        if results:
            # Choose best result based on criteria
            best_response = self._choose_best_response(results)
            self.logger.info_success(f"Best effort search returned {best_response.result_count()} results")
            return best_response
        
        return await self._use_fallback(query, num_results)
    
    async def _safe_provider_search(
        self, 
        provider: BaseSearchProvider, 
        query: str, 
        num_results: int
    ) -> Optional[SearchResponse]:
        """Safely execute provider search with error handling."""
        try:
            return await provider.search(query, num_results)
        except Exception as e:
            self.logger.warning_skip(f"{provider.get_name()} search failed: {e}")
            return None
    
    def _choose_best_response(self, responses: List[SearchResponse]) -> SearchResponse:
        """Choose the best response from multiple results."""
        if not responses:
            raise ValueError("No responses to choose from")
        
        # Prioritize responses with more results
        responses_with_results = [r for r in responses if r.has_results()]
        if responses_with_results:
            # Sort by result count descending, then by grounding usage
            return max(responses_with_results, key=lambda r: (
                r.result_count(),
                r.grounding_used
            ))
        
        # If no responses have results, return the first one
        return responses[0]
    
    async def _use_fallback(self, query: str, num_results: int) -> SearchResponse:
        """Use the fallback provider when all others fail."""
        if not self._fallback_provider:
            return self._create_error_response("No fallback provider available")
        
        self.logger.info_fallback("Using knowledge-based fallback results")
        
        try:
            return await self._fallback_provider.search(query, num_results)
        except Exception as e:
            self.logger.error(f"Fallback provider failed: {e}")
            return self._create_error_response(f"All search providers failed, including fallback: {e}")
    
    def _create_error_response(self, error: str) -> SearchResponse:
        """Create a standard error response."""
        return SearchResponse(
            status=SearchStatus.ERROR,
            results=[],
            query="",
            provider="search_manager",
            error=error
        )
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all search providers."""
        status = {
            'active_providers': [],
            'unavailable_providers': [],
            'fallback_available': self._fallback_provider is not None,
            'strategy': self.strategy.value
        }
        
        all_provider_classes = [
            GeminiSearchProvider,
            GoogleCustomSearchProvider,
            SearchAPIProvider, 
            DuckDuckGoProvider
        ]
        
        available_names = {p.get_name() for p in self._providers}
        
        for provider_class in all_provider_classes:
            try:
                provider = provider_class()
                if provider.is_available():
                    status['active_providers'].append({
                        'name': provider.get_name(),
                        'available': True
                    })
                else:
                    status['unavailable_providers'].append({
                        'name': provider.get_name(),
                        'available': False,
                        'reason': 'Configuration missing'
                    })
            except Exception as e:
                status['unavailable_providers'].append({
                    'name': provider_class.__name__,
                    'available': False,
                    'reason': str(e)
                })
        
        return status
    
    def add_provider(self, provider: BaseSearchProvider) -> None:
        """Add a custom search provider."""
        if provider.is_available():
            self._providers.append(provider)
            self.logger.info(f"Added custom provider: {provider.get_name()}")
        else:
            self.logger.warning(f"Custom provider not available: {provider.get_name()}")
    
    def remove_provider(self, provider_name: str) -> bool:
        """Remove a provider by name."""
        for i, provider in enumerate(self._providers):
            if provider.get_name() == provider_name:
                del self._providers[i]
                self.logger.info(f"Removed provider: {provider_name}")
                return True
        
        self.logger.warning(f"Provider not found: {provider_name}")
        return False
    
    def set_strategy(self, strategy: SearchStrategy) -> None:
        """Change the search strategy."""
        self.strategy = strategy
        self.logger.info(f"Changed search strategy to: {strategy.value}")


# Convenience function for backward compatibility
async def search_web(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Legacy function for backward compatibility.
    Converts new SearchResponse format to old dictionary format.
    """
    manager = SearchManager()
    response = await manager.search(query, num_results)
    
    # Convert to old format for compatibility
    results = []
    for result in response.results:
        results.append({
            'title': result.title,
            'url': result.url,
            'snippet': result.snippet,
            'source': result.source
        })
    
    return results