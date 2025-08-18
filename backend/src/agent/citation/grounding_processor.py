"""
Grounding processor for extracting citation information from Gemini grounding metadata.
"""

from typing import List, Any, Optional
from ..state import Source, Citation
from ..logging_config import AgentLogger


class GroundingProcessor:
    """Processes grounding metadata to extract sources and citations."""
    
    def __init__(self):
        self.logger = AgentLogger("citation.grounding_processor")
    
    def extract_sources_from_grounding(self, response: Any) -> List[Source]:
        """
        Extract Source objects from grounding metadata.
        
        Args:
            response: Gemini response object with grounding metadata
            
        Returns:
            List of Source objects extracted from grounding metadata
        """
        sources = []
        
        try:
            if not self._has_grounding_metadata(response):
                self.logger.info("No grounding metadata found in response")
                return sources
            
            metadata = response.candidates[0].grounding_metadata
            chunks = getattr(metadata, 'grounding_chunks', [])
            
            for i, chunk in enumerate(chunks):
                try:
                    if hasattr(chunk, 'web') and hasattr(chunk.web, 'uri'):
                        title = getattr(chunk.web, 'title', f"Source {i + 1}")
                        uri = chunk.web.uri
                        
                        # Validate URI is not empty
                        if not uri:
                            self.logger.warning_skip(f"Empty URI for chunk {i}")
                            continue
                        
                        source = Source(
                            title=title,
                            url=uri,
                            short_url=f"grounding-source-{i+1}",
                            label=f"Source {i + 1}"
                        )
                        sources.append(source)
                        
                except Exception as e:
                    self.logger.warning_skip(f"Error processing chunk {i}: {e}")
                    continue
            
            self.logger.info_success(f"Extracted {len(sources)} sources from grounding metadata")
            
        except Exception as e:
            self.logger.error(f"Error extracting sources from grounding: {e}")
        
        return sources
    
    def create_citations_from_grounding(self, response: Any) -> List[Citation]:
        """
        Create Citation objects from grounding metadata.
        
        Args:
            response: Gemini response object with grounding metadata
            
        Returns:
            List of Citation objects with segments and indices
        """
        citations = []
        
        try:
            if not self._has_grounding_metadata(response):
                self.logger.info("No grounding metadata found for citation creation")
                return citations
            
            metadata = response.candidates[0].grounding_metadata
            supports = getattr(metadata, 'grounding_supports', [])
            chunks = getattr(metadata, 'grounding_chunks', [])
            
            for support_idx, support in enumerate(supports):
                try:
                    citation = self._process_grounding_support(support, chunks, support_idx)
                    if citation:
                        citations.append(citation)
                        
                except Exception as e:
                    self.logger.warning_skip(f"Error processing support {support_idx}: {e}")
                    continue
            
            self.logger.info_success(f"Created {len(citations)} citations from grounding metadata")
            
        except Exception as e:
            self.logger.error(f"Error creating citations from grounding: {e}")
        
        return citations
    
    def _has_grounding_metadata(self, response: Any) -> bool:
        """
        Check if response contains grounding metadata.
        
        Args:
            response: Response object to check
            
        Returns:
            True if grounding metadata is present, False otherwise
        """
        return (hasattr(response, 'candidates') and 
                response.candidates and 
                hasattr(response.candidates[0], 'grounding_metadata') and
                response.candidates[0].grounding_metadata)
    
    def _process_grounding_support(
        self, 
        support: Any, 
        chunks: List[Any], 
        support_idx: int
    ) -> Optional[Citation]:
        """
        Process a single grounding support to create a Citation.
        
        Args:
            support: Grounding support object
            chunks: List of grounding chunks
            support_idx: Index of the support for logging
            
        Returns:
            Citation object if processing succeeds, None otherwise
        """
        # Validate support has required attributes
        if not self._validate_support_structure(support):
            self.logger.warning_skip(f"Support {support_idx} has invalid structure")
            return None
        
        # Extract and validate indices
        start_idx_raw = getattr(support.segment, 'start_index', None)
        end_idx_raw = getattr(support.segment, 'end_index', None)
        chunk_indices = getattr(support, 'grounding_chunk_indices', None)
        
        # Skip if any critical attribute is None or invalid
        if (start_idx_raw is None or end_idx_raw is None or 
            chunk_indices is None or not chunk_indices):
            self.logger.warning_skip(f"Support {support_idx} has missing critical attributes")
            return None
        
        # Normalize and validate indices
        start_idx, end_idx = self._normalize_indices(start_idx_raw, end_idx_raw)
        
        # Create source segments for this citation
        segments = self._create_source_segments(chunk_indices, chunks)
        
        if not segments:
            self.logger.warning_skip(f"Support {support_idx} has no valid segments")
            return None
        
        return Citation(
            start_index=start_idx,
            end_index=end_idx,
            segments=segments
        )
    
    def _validate_support_structure(self, support: Any) -> bool:
        """
        Validate that a grounding support has the required structure.
        
        Args:
            support: Grounding support object to validate
            
        Returns:
            True if structure is valid, False otherwise
        """
        return (hasattr(support, 'segment') and 
                hasattr(support.segment, 'start_index') and
                hasattr(support.segment, 'end_index') and
                hasattr(support, 'grounding_chunk_indices'))
    
    def _normalize_indices(self, start_idx_raw: Any, end_idx_raw: Any) -> tuple[int, int]:
        """
        Normalize and validate start and end indices.
        
        Args:
            start_idx_raw: Raw start index value
            end_idx_raw: Raw end index value
            
        Returns:
            Tuple of (normalized_start, normalized_end)
        """
        # Convert to integers, defaulting to 0 for invalid values
        start_idx = start_idx_raw if isinstance(start_idx_raw, int) else 0
        end_idx = end_idx_raw if isinstance(end_idx_raw, int) else 0
        
        # Ensure non-negative values
        start_idx = max(0, start_idx)
        end_idx = max(0, end_idx)
        
        # Ensure end_index >= start_index
        if end_idx < start_idx:
            self.logger.warning_skip(f"End index {end_idx} < start index {start_idx}, adjusting")
            end_idx = start_idx
        
        return start_idx, end_idx
    
    def _create_source_segments(self, chunk_indices: List[int], chunks: List[Any]) -> List[Source]:
        """
        Create Source objects from chunk indices.
        
        Args:
            chunk_indices: List of chunk indices to process
            chunks: List of available chunks
            
        Returns:
            List of Source objects
        """
        segments = []
        
        for chunk_idx in chunk_indices:
            try:
                if (chunk_idx < len(chunks) and 
                    hasattr(chunks[chunk_idx], 'web') and 
                    hasattr(chunks[chunk_idx].web, 'uri')):
                    
                    chunk = chunks[chunk_idx]
                    title = getattr(chunk.web, 'title', f"Source {chunk_idx + 1}")
                    uri = chunk.web.uri
                    
                    if not uri:
                        self.logger.warning_skip(f"Empty URI for chunk {chunk_idx}")
                        continue
                    
                    source = Source(
                        title=title,
                        url=uri,
                        short_url=f"grounding-source-{chunk_idx+1}",
                        label=f"Source {chunk_idx + 1}"
                    )
                    segments.append(source)
                    
            except Exception as e:
                self.logger.warning_skip(f"Error processing chunk {chunk_idx}: {e}")
                continue
        
        return segments
    
    def get_grounding_statistics(self, response: Any) -> dict:
        """
        Get statistics about grounding metadata in a response.
        
        Args:
            response: Response object to analyze
            
        Returns:
            Dictionary with grounding statistics
        """
        stats = {
            'has_grounding': False,
            'chunk_count': 0,
            'support_count': 0,
            'valid_citations': 0,
            'sources_extracted': 0
        }
        
        try:
            if self._has_grounding_metadata(response):
                stats['has_grounding'] = True
                
                metadata = response.candidates[0].grounding_metadata
                chunks = getattr(metadata, 'grounding_chunks', [])
                supports = getattr(metadata, 'grounding_supports', [])
                
                stats['chunk_count'] = len(chunks)
                stats['support_count'] = len(supports)
                
                # Count valid citations
                citations = self.create_citations_from_grounding(response)
                stats['valid_citations'] = len(citations)
                
                # Count extracted sources
                sources = self.extract_sources_from_grounding(response)
                stats['sources_extracted'] = len(sources)
                
        except Exception as e:
            self.logger.warning_skip(f"Error calculating grounding statistics: {e}")
        
        return stats