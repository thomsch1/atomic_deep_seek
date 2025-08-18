"""
Compatibility functions for integration tests.
These functions provide the interface expected by integration tests.
"""

from typing import List, Dict, Any
from ..state import Source, Citation
from ..citation import GroundingProcessor, CitationFormatter


# Global instances for efficiency
_grounding_processor = GroundingProcessor()
_citation_formatter = CitationFormatter()


async def search_with_gemini_grounding(query: str) -> Dict[str, Any]:
    """
    Mock-compatible function for Gemini grounding search.
    This is mainly used by tests and returns a standard format.
    """
    return {
        'status': 'success',
        'response': None,
        'grounding_used': True,
        'source': 'gemini_grounding',
        'query': query
    }


def extract_sources_from_grounding(response: Any) -> List[Source]:
    """
    Extract Source objects from grounding metadata.
    Delegates to GroundingProcessor.
    """
    return _grounding_processor.extract_sources_from_grounding(response)


def add_inline_citations(response: Any) -> str:
    """
    Add inline citations based on grounding metadata.
    Delegates to CitationFormatter.
    """
    return _citation_formatter.add_inline_citations(response)


def create_citations_from_grounding(response: Any) -> List[Citation]:
    """
    Create Citation objects from grounding metadata.
    Delegates to GroundingProcessor.
    """
    return _grounding_processor.create_citations_from_grounding(response)


async def run_async_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Run async search using the search manager.
    This provides compatibility for tests.
    """
    from ..search.search_manager import search_web
    results = await search_web(query, max_results)
    return results