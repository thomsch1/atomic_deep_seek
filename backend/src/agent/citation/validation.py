"""
Citation validation utilities for ensuring citation data integrity.
"""

from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse
from ..state import Citation, Source
from ..logging_config import AgentLogger


class CitationValidator:
    """Validates citation data for consistency and correctness."""
    
    def __init__(self):
        self.logger = AgentLogger("citation.validator")
    
    def validate_citation(self, citation: Citation, text_length: Optional[int] = None) -> Dict[str, Any]:
        """
        Validate a single citation object.
        
        Args:
            citation: Citation object to validate
            text_length: Length of text for index validation (optional)
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'citation_data': {
                'start_index': citation.start_index,
                'end_index': citation.end_index,
                'segment_count': len(citation.segments)
            }
        }
        
        try:
            # Validate indices
            self._validate_indices(citation, text_length, validation_result)
            
            # Validate segments
            self._validate_segments(citation.segments, validation_result)
            
            # Overall validation
            if validation_result['errors']:
                validation_result['is_valid'] = False
                
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Validation error: {str(e)}")
            self.logger.error(f"Citation validation error: {e}")
        
        return validation_result
    
    def validate_citations_list(
        self, 
        citations: List[Citation], 
        text_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validate a list of citations.
        
        Args:
            citations: List of Citation objects to validate
            text_length: Length of text for index validation (optional)
            
        Returns:
            Dictionary with validation results for all citations
        """
        results = {
            'total_citations': len(citations),
            'valid_citations': 0,
            'invalid_citations': 0,
            'total_errors': 0,
            'total_warnings': 0,
            'citation_results': [],
            'overlapping_citations': []
        }
        
        try:
            # Validate each citation individually
            for i, citation in enumerate(citations):
                result = self.validate_citation(citation, text_length)
                result['citation_index'] = i
                results['citation_results'].append(result)
                
                if result['is_valid']:
                    results['valid_citations'] += 1
                else:
                    results['invalid_citations'] += 1
                
                results['total_errors'] += len(result['errors'])
                results['total_warnings'] += len(result['warnings'])
            
            # Check for overlapping citations
            overlaps = self._find_overlapping_citations(citations)
            results['overlapping_citations'] = overlaps
            
            if overlaps:
                results['total_warnings'] += len(overlaps)
                
        except Exception as e:
            self.logger.error(f"Error validating citations list: {e}")
            results['validation_error'] = str(e)
        
        return results
    
    def validate_source(self, source: Source) -> Dict[str, Any]:
        """
        Validate a single source object.
        
        Args:
            source: Source object to validate
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'source_data': {
                'title': source.title,
                'url': source.url,
                'short_url': source.short_url,
                'label': source.label
            }
        }
        
        try:
            # Validate required fields
            if not source.title or not source.title.strip():
                validation_result['errors'].append("Source title is empty or missing")
            
            if not source.url or not source.url.strip():
                validation_result['errors'].append("Source URL is empty or missing")
            else:
                # Validate URL format
                url_validation = self._validate_url(source.url)
                if not url_validation['is_valid']:
                    validation_result['errors'].extend(url_validation['errors'])
                validation_result['warnings'].extend(url_validation['warnings'])
            
            if not source.label or not source.label.strip():
                validation_result['warnings'].append("Source label is empty")
            
            # Check short_url if provided
            if source.short_url:
                if not source.short_url.strip():
                    validation_result['warnings'].append("Short URL is empty string")
            
            # Set overall validity
            if validation_result['errors']:
                validation_result['is_valid'] = False
                
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Source validation error: {str(e)}")
            self.logger.error(f"Source validation error: {e}")
        
        return validation_result
    
    def sanitize_citation_text(self, text: str, max_length: int = 1000) -> str:
        """
        Sanitize citation text by removing problematic characters and limiting length.
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        try:
            if not text:
                return ""
            
            # Remove null characters and control characters
            sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
            
            # Trim excessive whitespace
            sanitized = ' '.join(sanitized.split())
            
            # Limit length
            if len(sanitized) > max_length:
                sanitized = sanitized[:max_length].rsplit(' ', 1)[0] + "..."
            
            return sanitized
            
        except Exception as e:
            self.logger.warning_skip(f"Error sanitizing text: {e}")
            return str(text)[:max_length] if text else ""
    
    def _validate_indices(
        self, 
        citation: Citation, 
        text_length: Optional[int], 
        result: Dict[str, Any]
    ) -> None:
        """
        Validate citation indices.
        
        Args:
            citation: Citation to validate
            text_length: Length of text for validation
            result: Result dictionary to update
        """
        start_idx = citation.start_index
        end_idx = citation.end_index
        
        # Check if indices are integers
        if not isinstance(start_idx, int):
            result['errors'].append(f"Start index is not an integer: {type(start_idx)}")
        
        if not isinstance(end_idx, int):
            result['errors'].append(f"End index is not an integer: {type(end_idx)}")
        
        # If both are integers, do further validation
        if isinstance(start_idx, int) and isinstance(end_idx, int):
            # Check non-negative
            if start_idx < 0:
                result['errors'].append(f"Start index is negative: {start_idx}")
            
            if end_idx < 0:
                result['errors'].append(f"End index is negative: {end_idx}")
            
            # Check logical order
            if start_idx > end_idx:
                result['errors'].append(
                    f"Start index ({start_idx}) > end index ({end_idx})"
                )
            
            # Check against text length if provided
            if text_length is not None:
                if start_idx > text_length:
                    result['errors'].append(
                        f"Start index ({start_idx}) > text length ({text_length})"
                    )
                
                if end_idx > text_length:
                    result['errors'].append(
                        f"End index ({end_idx}) > text length ({text_length})"
                    )
    
    def _validate_segments(self, segments: List[Source], result: Dict[str, Any]) -> None:
        """
        Validate citation segments.
        
        Args:
            segments: List of Source objects to validate
            result: Result dictionary to update
        """
        if not segments:
            result['warnings'].append("Citation has no segments")
            return
        
        seen_urls = set()
        
        for i, segment in enumerate(segments):
            # Validate segment type
            if not isinstance(segment, Source):
                result['errors'].append(f"Segment {i} is not a Source object")
                continue
            
            # Validate individual source
            source_result = self.validate_source(segment)
            
            # Add segment-specific prefixes to errors/warnings
            for error in source_result['errors']:
                result['errors'].append(f"Segment {i}: {error}")
            
            for warning in source_result['warnings']:
                result['warnings'].append(f"Segment {i}: {warning}")
            
            # Check for duplicate URLs in segments
            if segment.url in seen_urls:
                result['warnings'].append(f"Duplicate URL in segment {i}: {segment.url}")
            else:
                seen_urls.add(segment.url)
    
    def _validate_url(self, url: str) -> Dict[str, Any]:
        """
        Validate URL format and structure.
        
        Args:
            url: URL to validate
            
        Returns:
            Dictionary with validation results
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            parsed = urlparse(url)
            
            # Check for scheme
            if not parsed.scheme:
                result['errors'].append("URL missing scheme (http/https)")
            elif parsed.scheme not in ['http', 'https']:
                result['warnings'].append(f"Unusual URL scheme: {parsed.scheme}")
            
            # Check for netloc (domain)
            if not parsed.netloc:
                result['errors'].append("URL missing domain")
            
            # Check for suspicious patterns
            if 'localhost' in parsed.netloc:
                result['warnings'].append("URL points to localhost")
            
            if parsed.netloc.startswith('.'):
                result['errors'].append("Invalid domain format")
            
            # Set overall validity
            if result['errors']:
                result['is_valid'] = False
                
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f"URL parsing error: {str(e)}")
        
        return result
    
    def _find_overlapping_citations(self, citations: List[Citation]) -> List[Dict[str, Any]]:
        """
        Find citations with overlapping text ranges.
        
        Args:
            citations: List of citations to check
            
        Returns:
            List of overlap information dictionaries
        """
        overlaps = []
        
        for i, citation1 in enumerate(citations):
            for j, citation2 in enumerate(citations[i+1:], i+1):
                try:
                    # Check if citations overlap
                    if self._citations_overlap(citation1, citation2):
                        overlap_info = {
                            'citation1_index': i,
                            'citation2_index': j,
                            'citation1_range': (citation1.start_index, citation1.end_index),
                            'citation2_range': (citation2.start_index, citation2.end_index),
                            'overlap_type': self._get_overlap_type(citation1, citation2)
                        }
                        overlaps.append(overlap_info)
                        
                except Exception as e:
                    self.logger.warning_skip(f"Error checking overlap between citations {i} and {j}: {e}")
                    continue
        
        return overlaps
    
    def _citations_overlap(self, citation1: Citation, citation2: Citation) -> bool:
        """
        Check if two citations have overlapping ranges.
        
        Args:
            citation1: First citation
            citation2: Second citation
            
        Returns:
            True if citations overlap
        """
        start1, end1 = citation1.start_index, citation1.end_index
        start2, end2 = citation2.start_index, citation2.end_index
        
        # Check for overlap: not (end1 <= start2 or end2 <= start1)
        return not (end1 <= start2 or end2 <= start1)
    
    def _get_overlap_type(self, citation1: Citation, citation2: Citation) -> str:
        """
        Determine the type of overlap between two citations.
        
        Args:
            citation1: First citation
            citation2: Second citation
            
        Returns:
            String describing overlap type
        """
        start1, end1 = citation1.start_index, citation1.end_index
        start2, end2 = citation2.start_index, citation2.end_index
        
        if start1 == start2 and end1 == end2:
            return "identical"
        elif start1 <= start2 and end1 >= end2:
            return "citation1_contains_citation2"
        elif start2 <= start1 and end2 >= end1:
            return "citation2_contains_citation1"
        else:
            return "partial_overlap"