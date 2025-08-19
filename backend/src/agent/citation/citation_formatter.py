"""
Citation formatter for adding inline citations and formatting text with citation markers.
"""

from typing import List, Dict, Any, Optional
from ..state import Citation, Source
from ..logging_config import AgentLogger


class CitationFormatter:
    """Handles formatting of text with inline citations."""
    
    def __init__(self):
        self.logger = AgentLogger("citation.formatter")
    
    def add_inline_citations(self, response: Any) -> str:
        """
        Add inline citations based on grounding metadata.
        
        Args:
            response: Gemini response object with grounding metadata
            
        Returns:
            Text with inline citations added
        """
        try:
            text = self._extract_text_from_response(response)
            
            if not self._has_grounding_metadata(response):
                self.logger.info("No grounding metadata found, returning original text")
                return text
            
            metadata = response.candidates[0].grounding_metadata
            supports = getattr(metadata, 'grounding_supports', [])
            chunks = getattr(metadata, 'grounding_chunks', [])
            
            if not supports or not chunks:
                self.logger.info("No grounding supports or chunks found")
                return text
            
            # Sort by end_index descending to avoid shifting issues when inserting
            sorted_supports = self._sort_supports_by_end_index(supports)
            
            modified_text = text
            citation_count = 0
            
            for support in sorted_supports:
                try:
                    modified_text = self._insert_citation_for_support(
                        modified_text, support, chunks
                    )
                    citation_count += 1
                    
                except Exception as e:
                    self.logger.warning_skip(f"Error inserting citation: {e}")
                    continue
            
            if citation_count > 0:
                self.logger.info_success(f"Added {citation_count} inline citations")
            else:
                self.logger.info("No citations were successfully added")
            
            return modified_text
            
        except Exception as e:
            self.logger.error(f"Error adding inline citations: {e}")
            return self._extract_text_from_response(response)
    
    def insert_citation_markers(
        self, 
        text: str, 
        citations_list: List[Dict[str, Any]]
    ) -> str:
        """
        Insert citation markers into text based on start and end indices.
        
        Args:
            text: Original text string
            citations_list: List of citation dictionaries with indices and segments
            
        Returns:
            Text with citation markers inserted
        """
        try:
            if not citations_list:
                return text
            
            # Sort citations by end_index in descending order to avoid index shifting
            sorted_citations = sorted(
                citations_list, 
                key=lambda c: (c.get("end_index", 0), c.get("start_index", 0)), 
                reverse=True
            )
            
            modified_text = text
            inserted_count = 0
            
            for citation_info in sorted_citations:
                try:
                    end_idx = citation_info.get("end_index")
                    segments = citation_info.get("segments", [])
                    
                    if end_idx is None or not segments:
                        continue
                    
                    # Validate end index
                    if not isinstance(end_idx, int) or end_idx < 0 or end_idx > len(modified_text):
                        self.logger.warning_skip(f"Invalid end index: {end_idx}")
                        continue
                    
                    # Build citation marker
                    marker_parts = []
                    for segment in segments:
                        label = segment.get('label', 'Source')
                        # Use the actual URL instead of short_url placeholder
                        url = segment.get('url', segment.get('short_url', '#'))
                        marker_parts.append(f" [{label}]({url})")
                    
                    if marker_parts:
                        citation_marker = "".join(marker_parts)
                        
                        # Insert citation marker at end index
                        modified_text = (
                            modified_text[:end_idx] + 
                            citation_marker + 
                            modified_text[end_idx:]
                        )
                        inserted_count += 1
                        
                except Exception as e:
                    self.logger.warning_skip(f"Error inserting citation marker: {e}")
                    continue
            
            if inserted_count > 0:
                self.logger.info_success(f"Inserted {inserted_count} citation markers")
            
            return modified_text
            
        except Exception as e:
            self.logger.error(f"Error inserting citation markers: {e}")
            return text
    
    def format_citations_as_references(self, citations: List[Citation]) -> str:
        """
        Format citations as a references section.
        
        Args:
            citations: List of Citation objects
            
        Returns:
            Formatted references string
        """
        if not citations:
            return ""
        
        try:
            references = []
            seen_urls = set()
            ref_number = 1
            
            for citation in citations:
                for segment in citation.segments:
                    if isinstance(segment, Source) and segment.url not in seen_urls:
                        reference = f"{ref_number}. [{segment.title}]({segment.url})"
                        references.append(reference)
                        seen_urls.add(segment.url)
                        ref_number += 1
            
            if references:
                references_text = "\n\n## References\n\n" + "\n".join(references)
                self.logger.info_success(f"Generated {len(references)} references")
                return references_text
            
        except Exception as e:
            self.logger.error(f"Error formatting references: {e}")
        
        return ""
    
    def _extract_text_from_response(self, response: Any) -> str:
        """
        Extract text content from a response object.
        
        Args:
            response: Response object
            
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
            
            self.logger.warning_skip("Could not extract text from response")
            return ""
            
        except Exception as e:
            self.logger.error(f"Error extracting text from response: {e}")
            return ""
    
    def _has_grounding_metadata(self, response: Any) -> bool:
        """
        Check if response contains grounding metadata.
        
        Args:
            response: Response object to check
            
        Returns:
            True if grounding metadata is present
        """
        return (hasattr(response, 'candidates') and 
                response.candidates and 
                hasattr(response.candidates[0], 'grounding_metadata') and
                response.candidates[0].grounding_metadata)
    
    def _sort_supports_by_end_index(self, supports: List[Any]) -> List[Any]:
        """
        Sort grounding supports by end index in descending order.
        
        Args:
            supports: List of grounding support objects
            
        Returns:
            Sorted list of supports
        """
        try:
            return sorted(
                supports,
                key=lambda s: getattr(s.segment, 'end_index', 0) if hasattr(s, 'segment') else 0,
                reverse=True
            )
        except Exception as e:
            self.logger.warning_skip(f"Error sorting supports: {e}")
            return supports
    
    def _insert_citation_for_support(
        self, 
        text: str, 
        support: Any, 
        chunks: List[Any]
    ) -> str:
        """
        Insert citation for a single grounding support.
        
        Args:
            text: Current text
            support: Grounding support object
            chunks: List of grounding chunks
            
        Returns:
            Text with citation inserted
        """
        if not hasattr(support, 'segment') or not hasattr(support.segment, 'end_index'):
            return text
        
        end_index = support.segment.end_index
        
        # Validate end_index
        if (end_index is None or 
            not isinstance(end_index, int) or 
            end_index < 0 or 
            end_index > len(text)):
            return text
        
        if not (hasattr(support, 'grounding_chunk_indices') and 
                support.grounding_chunk_indices):
            return text
        
        # Create citation links
        citation_links = []
        for chunk_idx in support.grounding_chunk_indices:
            try:
                if (chunk_idx < len(chunks) and 
                    hasattr(chunks[chunk_idx], 'web') and 
                    hasattr(chunks[chunk_idx].web, 'uri')):
                    
                    uri = chunks[chunk_idx].web.uri
                    if uri:
                        citation_links.append(f"[{chunk_idx + 1}]({uri})")
                        
            except Exception as e:
                self.logger.warning_skip(f"Error processing chunk {chunk_idx}: {e}")
                continue
        
        if citation_links:
            # Format with space before and proper spacing between citations
            citation_string = " " + ", ".join(citation_links)
            # Insert citation at the validated end_index
            text = text[:end_index] + citation_string + text[end_index:]
        
        return text
    
    def validate_citation_indices(self, text: str, citations: List[Citation]) -> List[Citation]:
        """
        Validate and filter citations with valid text indices.
        
        Args:
            text: Text to validate indices against
            citations: List of citations to validate
            
        Returns:
            List of citations with valid indices
        """
        valid_citations = []
        text_length = len(text)
        
        for citation in citations:
            try:
                start_idx = citation.start_index
                end_idx = citation.end_index
                
                # Validate indices
                if (isinstance(start_idx, int) and isinstance(end_idx, int) and
                    0 <= start_idx <= text_length and
                    0 <= end_idx <= text_length and
                    start_idx <= end_idx):
                    
                    valid_citations.append(citation)
                else:
                    self.logger.warning_skip(
                        f"Invalid citation indices: {start_idx}-{end_idx} for text length {text_length}"
                    )
                    
            except Exception as e:
                self.logger.warning_skip(f"Error validating citation: {e}")
                continue
        
        return valid_citations