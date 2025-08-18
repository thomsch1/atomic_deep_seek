import warnings
from typing import Any, Dict, List
from agent.state import Message


def get_research_topic(messages: List[Message]) -> str:
    """
    Get the research topic from the messages.
    """
    # check if request has a history and combine the messages into a single string
    if len(messages) == 1:
        research_topic = messages[-1].content
    else:
        research_topic = ""
        for message in messages:
            if message.role == "user":
                research_topic += f"User: {message.content}\n"
            elif message.role == "assistant":
                research_topic += f"Assistant: {message.content}\n"
    return research_topic


def resolve_urls(urls_to_resolve: List[Any], id: int) -> Dict[str, str]:
    """
    Create a map of the vertex ai search urls (very long) to a short url with a unique id for each url.
    Ensures each original URL gets a consistent shortened form while maintaining uniqueness.
    """
    prefix = f"https://vertexaisearch.cloud.google.com/id/"
    urls = [site.web.uri for site in urls_to_resolve]

    # Create a dictionary that maps each unique URL to its first occurrence index
    resolved_map = {}
    for idx, url in enumerate(urls):
        if url not in resolved_map:
            resolved_map[url] = f"{prefix}{id}-{idx}"

    return resolved_map


def insert_citation_markers(text, citations_list):
    """
    DEPRECATED: Use agent.citation.CitationFormatter.insert_citation_markers instead.
    
    This function will be removed in a future version.
    """
    warnings.warn(
        "insert_citation_markers is deprecated and will be removed in a future version. "
        "Use agent.citation.CitationFormatter.insert_citation_markers instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Import here to avoid circular imports
    from .citation import CitationFormatter
    
    formatter = CitationFormatter()
    return formatter.insert_citation_markers(text, citations_list)


def get_citations(response, resolved_urls_map):
    """
    DEPRECATED: Use agent.citation.GroundingProcessor.create_citations_from_grounding instead.
    
    This function will be removed in a future version.
    """
    warnings.warn(
        "get_citations is deprecated and will be removed in a future version. "
        "Use agent.citation.GroundingProcessor.create_citations_from_grounding instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Import here to avoid circular imports
    from .citation import GroundingProcessor
    
    processor = GroundingProcessor()
    citations = processor.create_citations_from_grounding(response)
    
    # Convert to legacy format for backward compatibility
    legacy_citations = []
    for citation in citations:
        legacy_citation = {
            "start_index": citation.start_index,
            "end_index": citation.end_index,
            "segments": []
        }
        
        for segment in citation.segments:
            # Try to find resolved URL, fallback to original URL
            resolved_url = resolved_urls_map.get(segment.url, segment.url)
            legacy_citation["segments"].append({
                "label": segment.label,
                "short_url": resolved_url,
                "value": segment.url
            })
        
        legacy_citations.append(legacy_citation)
    
    return legacy_citations
