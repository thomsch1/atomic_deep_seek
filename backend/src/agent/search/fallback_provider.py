"""
Knowledge-based fallback search provider.
"""

from typing import List, Dict, Any
import re

from .base_provider import FallbackProvider, SearchResponse, SearchResult, SearchStatus


class KnowledgeFallbackProvider(FallbackProvider):
    """Fallback search provider that returns knowledge-based results."""
    
    def __init__(self):
        super().__init__("knowledge_fallback")
        self._knowledge_base = self._initialize_knowledge_base()
    
    def is_available(self) -> bool:
        """Knowledge fallback is always available."""
        return True
    
    def _initialize_knowledge_base(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the knowledge base with common query patterns and responses."""
        return {
            'paris_capital_france': {
                'patterns': [r'capital.*france', r'france.*capital', r'paris.*france'],
                'results': [{
                    'title': 'Paris - Capital of France',
                    'url': 'https://en.wikipedia.org/wiki/Paris',
                    'snippet': 'Paris is the capital and most populous city of France. With an estimated population of 2,165,423 residents in 2019, it is the fourth-largest city in the European Union.',
                    'metadata': {'confidence': 0.95, 'category': 'geography'}
                }]
            },
            'python_programming': {
                'patterns': [r'python.*program', r'python.*language', r'^python$'],
                'results': [{
                    'title': 'Python Programming Language',
                    'url': 'https://www.python.org/',
                    'snippet': 'Python is a high-level, interpreted programming language with dynamic semantics. Its high-level built in data structures make it attractive for Rapid Application Development.',
                    'metadata': {'confidence': 0.90, 'category': 'programming'}
                }]
            },
            'artificial_intelligence': {
                'patterns': [r'artificial intelligence', r'\bai\b', r'machine learning'],
                'results': [{
                    'title': 'Artificial Intelligence',
                    'url': 'https://en.wikipedia.org/wiki/Artificial_intelligence',
                    'snippet': 'Artificial Intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by humans and animals.',
                    'metadata': {'confidence': 0.85, 'category': 'technology'}
                }]
            },
            'climate_change': {
                'patterns': [r'climate change', r'global warming', r'greenhouse effect'],
                'results': [{
                    'title': 'Climate Change',
                    'url': 'https://en.wikipedia.org/wiki/Climate_change',
                    'snippet': 'Climate change refers to long-term shifts in global or regional climate patterns, attributed largely to increased levels of atmospheric carbon dioxide.',
                    'metadata': {'confidence': 0.85, 'category': 'environment'}
                }]
            },
            'internet': {
                'patterns': [r'\binternet\b', r'world wide web', r'\bwww\b'],
                'results': [{
                    'title': 'Internet - Global Network',
                    'url': 'https://en.wikipedia.org/wiki/Internet',
                    'snippet': 'The Internet is a global system of interconnected computer networks that uses the Internet protocol suite to communicate between networks and devices.',
                    'metadata': {'confidence': 0.80, 'category': 'technology'}
                }]
            }
        }
    
    async def search(self, query: str, num_results: int = 5) -> SearchResponse:
        """
        Search using knowledge-based fallback results.
        
        Args:
            query: The search query string
            num_results: Maximum number of results to return
            
        Returns:
            SearchResponse with fallback results
        """
        self.logger.info(f"Using knowledge-based fallback for query: {query}")
        
        results = self.get_fallback_results(query, num_results)
        
        if results:
            self.logger.info_success(f"Provided {len(results)} fallback results")
        else:
            self.logger.info("Generated generic fallback result")
        
        return self._create_success_response(
            query=query,
            results=results,
            metadata={'fallback_type': 'knowledge_base', 'pattern_matched': bool(results)}
        )
    
    def get_fallback_results(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """
        Get fallback results based on query patterns.
        
        Args:
            query: The search query string
            num_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
        """
        query_lower = query.lower()
        
        # Check knowledge base patterns
        for knowledge_item, data in self._knowledge_base.items():
            for pattern in data['patterns']:
                if re.search(pattern, query_lower):
                    results = []
                    for result_data in data['results'][:num_results]:
                        result = SearchResult(
                            title=result_data['title'],
                            url=result_data['url'],
                            snippet=result_data['snippet'],
                            source='knowledge_base',
                            metadata=result_data.get('metadata', {})
                        )
                        results.append(result)
                    return results
        
        # Generic fallback if no patterns match
        generic_result = SearchResult(
            title=f"Information about: {query}",
            url="https://example.com/search",
            snippet=f"Search results for '{query}' are currently limited. This is a placeholder result from the knowledge base fallback system.",
            source="knowledge_base",
            metadata={'confidence': 0.1, 'category': 'generic', 'fallback': True}
        )
        
        return [generic_result]
    
    def add_knowledge_item(
        self, 
        key: str, 
        patterns: List[str], 
        results: List[Dict[str, Any]]
    ) -> None:
        """
        Add a new knowledge item to the fallback provider.
        
        Args:
            key: Unique identifier for the knowledge item
            patterns: List of regex patterns to match queries
            results: List of result dictionaries
        """
        self._knowledge_base[key] = {
            'patterns': patterns,
            'results': results
        }
        self.logger.info(f"Added knowledge item: {key}")
    
    def get_knowledge_categories(self) -> List[str]:
        """Get list of available knowledge categories."""
        categories = set()
        for data in self._knowledge_base.values():
            for result in data['results']:
                category = result.get('metadata', {}).get('category')
                if category:
                    categories.add(category)
        return sorted(list(categories))
    
    def search_by_category(self, category: str, num_results: int = 5) -> List[SearchResult]:
        """
        Get results filtered by category.
        
        Args:
            category: Category to filter by
            num_results: Maximum number of results
            
        Returns:
            List of SearchResult objects from the category
        """
        results = []
        
        for data in self._knowledge_base.values():
            for result_data in data['results']:
                if result_data.get('metadata', {}).get('category') == category:
                    if len(results) >= num_results:
                        break
                    
                    result = SearchResult(
                        title=result_data['title'],
                        url=result_data['url'],
                        snippet=result_data['snippet'],
                        source='knowledge_base',
                        metadata=result_data.get('metadata', {})
                    )
                    results.append(result)
            
            if len(results) >= num_results:
                break
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        total_items = len(self._knowledge_base)
        total_results = sum(len(data['results']) for data in self._knowledge_base.values())
        total_patterns = sum(len(data['patterns']) for data in self._knowledge_base.values())
        categories = self.get_knowledge_categories()
        
        return {
            'knowledge_items': total_items,
            'total_results': total_results,
            'total_patterns': total_patterns,
            'categories': categories,
            'category_count': len(categories)
        }