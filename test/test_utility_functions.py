"""
Tests for utility functions in agents.py.
Tests get_genai_client, add_inline_citations, extract_sources_from_grounding, and create_citations_from_grounding.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent.parent / "backend" / "src" 
sys.path.insert(0, str(backend_src))

from agent.agents import (
    get_genai_client,
    add_inline_citations, 
    extract_sources_from_grounding,
    create_citations_from_grounding
)
from agent.state import Source, Citation


class TestGetGenaiClient:
    """Test the get_genai_client function."""
    
    def test_get_client_with_gemini_api_key(self, mock_environment):
        """Test client creation with GEMINI_API_KEY."""
        with patch('agent.agents.genai') as mock_genai:
            mock_client = MagicMock()
            mock_genai.Client.return_value = mock_client
            
            client = get_genai_client()
            
            mock_genai.Client.assert_called_once_with(api_key="test-gemini-key-12345")
            assert client == mock_client
    
    def test_get_client_with_google_api_key(self):
        """Test client creation with GOOGLE_API_KEY as fallback."""
        # Clear all environment variables and only set GOOGLE_API_KEY
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-google-key-12345"}, clear=True):
            with patch('agent.agents.genai') as mock_genai:
                mock_client = MagicMock()
                mock_genai.Client.return_value = mock_client
                
                client = get_genai_client()
                
                mock_genai.Client.assert_called_once_with(api_key="test-google-key-12345")
                assert client == mock_client
    
    def test_get_client_no_api_key(self):
        """Test error when no API key is available."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY or GOOGLE_API_KEY must be set"):
                get_genai_client()
    
    def test_get_client_empty_api_keys(self):
        """Test error when API keys are empty strings."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}):
            with pytest.raises(ValueError, match="GEMINI_API_KEY or GOOGLE_API_KEY must be set"):
                get_genai_client()


class TestAddInlineCitations:
    """Test the add_inline_citations function."""
    
    def test_add_citations_with_valid_metadata(self, mock_grounding_response):
        """Test adding citations with valid grounding metadata."""
        result = add_inline_citations(mock_grounding_response)
        
        # Should contain the original text with citations inserted
        assert "Quantum computing has achieved significant milestones in 2024" in result
        assert "[1](https://quantum-research.com/2024)" in result
        assert "[2](https://quantum-algorithms.org)" in result
        
        # Note: Citations are inserted in reverse order of end_index to avoid text shifting issues
        # So citation 2 (end_index=143) is inserted first, then citation 1 (end_index=65)
    
    def test_add_citations_no_candidates(self):
        """Test with response that has no candidates."""
        mock_response = MagicMock()
        mock_response.text = "Test text"
        mock_response.candidates = []
        
        result = add_inline_citations(mock_response)
        assert result == "Test text"
    
    def test_add_citations_no_grounding_metadata(self):
        """Test with response that has no grounding metadata."""
        mock_response = MagicMock()
        mock_response.text = "Test text"
        mock_candidate = MagicMock()
        mock_candidate.grounding_metadata = None
        mock_response.candidates = [mock_candidate]
        
        result = add_inline_citations(mock_response)
        assert result == "Test text"
    
    def test_add_citations_no_supports(self):
        """Test with response that has empty grounding supports."""
        mock_response = MagicMock()
        mock_response.text = "Test text"
        mock_candidate = MagicMock()
        mock_metadata = MagicMock()
        mock_metadata.grounding_supports = []
        mock_metadata.grounding_chunks = []
        mock_candidate.grounding_metadata = mock_metadata
        mock_response.candidates = [mock_candidate]
        
        result = add_inline_citations(mock_response)
        assert result == "Test text"
    
    def test_add_citations_invalid_end_index(self, test_helpers):
        """Test with invalid end_index values."""
        mock_response = test_helpers.create_mock_response("Short text")
        
        # Modify the support to have invalid end_index
        mock_response.candidates[0].grounding_metadata.grounding_supports[0].segment.end_index = None
        
        result = add_inline_citations(mock_response)
        assert result == "Short text"  # Should return original text unchanged
    
    def test_add_citations_end_index_exceeds_length(self, test_helpers):
        """Test with end_index that exceeds text length."""
        mock_response = test_helpers.create_mock_response("Short")
        
        # Set end_index beyond text length
        mock_response.candidates[0].grounding_metadata.grounding_supports[0].segment.end_index = 100
        
        result = add_inline_citations(mock_response)
        assert result == "Short"  # Should return original text unchanged
    
    def test_add_citations_negative_end_index(self, test_helpers):
        """Test with negative end_index."""
        mock_response = test_helpers.create_mock_response("Test text")
        
        # Set negative end_index
        mock_response.candidates[0].grounding_metadata.grounding_supports[0].segment.end_index = -1
        
        result = add_inline_citations(mock_response)
        assert result == "Test text"  # Should return original text unchanged
    
    def test_add_citations_multiple_supports_sorted(self):
        """Test that citations are inserted in correct order (descending by end_index)."""
        mock_response = MagicMock()
        mock_response.text = "This is a test sentence with multiple citations."
        
        mock_candidate = MagicMock()
        mock_metadata = MagicMock()
        
        # Create mock chunks
        chunk1 = MagicMock()
        chunk1.web.uri = "https://first.com"
        chunk1.web.title = "First Source"
        
        chunk2 = MagicMock()
        chunk2.web.uri = "https://second.com" 
        chunk2.web.title = "Second Source"
        
        mock_metadata.grounding_chunks = [chunk1, chunk2]
        
        # Create supports with different end indices
        support1 = MagicMock()
        support1.segment.end_index = 20  # Earlier in text
        support1.grounding_chunk_indices = [0]
        
        support2 = MagicMock()
        support2.segment.end_index = 40  # Later in text
        support2.grounding_chunk_indices = [1]
        
        mock_metadata.grounding_supports = [support1, support2]
        mock_candidate.grounding_metadata = mock_metadata
        mock_response.candidates = [mock_candidate]
        
        result = add_inline_citations(mock_response)
        
        # Should process supports in descending order by end_index
        assert "[2](https://second.com)" in result
        assert "[1](https://first.com)" in result


class TestExtractSourcesFromGrounding:
    """Test the extract_sources_from_grounding function."""
    
    def test_extract_sources_valid_metadata(self, mock_grounding_response):
        """Test extracting sources from valid grounding metadata."""
        sources = extract_sources_from_grounding(mock_grounding_response)
        
        assert len(sources) == 2
        assert sources[0].title == "Quantum Research 2024"
        assert sources[0].url == "https://quantum-research.com/2024"
        assert sources[0].short_url == "grounding-source-1"
        assert sources[0].label == "Source 1"
        
        assert sources[1].title == "Quantum Algorithms Research"
        assert sources[1].url == "https://quantum-algorithms.org"
    
    def test_extract_sources_no_candidates(self):
        """Test with response that has no candidates."""
        mock_response = MagicMock()
        mock_response.candidates = []
        
        sources = extract_sources_from_grounding(mock_response)
        assert sources == []
    
    def test_extract_sources_no_grounding_metadata(self):
        """Test with response that has no grounding metadata."""
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_candidate.grounding_metadata = None
        mock_response.candidates = [mock_candidate]
        
        sources = extract_sources_from_grounding(mock_response)
        assert sources == []
    
    def test_extract_sources_no_chunks(self):
        """Test with response that has empty chunks."""
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_metadata = MagicMock()
        mock_metadata.grounding_chunks = []
        mock_candidate.grounding_metadata = mock_metadata
        mock_response.candidates = [mock_candidate]
        
        sources = extract_sources_from_grounding(mock_response)
        assert sources == []
    
    def test_extract_sources_chunk_without_web(self):
        """Test with chunks that don't have web attribute."""
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_metadata = MagicMock()
        
        mock_chunk = MagicMock()
        delattr(mock_chunk, 'web')  # Remove web attribute
        mock_metadata.grounding_chunks = [mock_chunk]
        
        mock_candidate.grounding_metadata = mock_metadata
        mock_response.candidates = [mock_candidate]
        
        sources = extract_sources_from_grounding(mock_response)
        assert sources == []
    
    def test_extract_sources_default_title(self):
        """Test that default title is used when title is missing."""
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_metadata = MagicMock()
        
        mock_chunk = MagicMock()
        mock_chunk.web.uri = "https://test.com"
        # Don't set title attribute to test default
        del mock_chunk.web.title
        
        mock_metadata.grounding_chunks = [mock_chunk]
        mock_candidate.grounding_metadata = mock_metadata
        mock_response.candidates = [mock_candidate]
        
        sources = extract_sources_from_grounding(mock_response)
        
        assert len(sources) == 1
        assert sources[0].title == "Source 1"  # Default title


class TestCreateCitationsFromGrounding:
    """Test the create_citations_from_grounding function."""
    
    def test_create_citations_valid_metadata(self, mock_grounding_response):
        """Test creating citations from valid grounding metadata."""
        citations = create_citations_from_grounding(mock_grounding_response)
        
        assert len(citations) == 2
        
        # Check first citation
        citation1 = citations[0]
        assert citation1.start_index == 0
        assert citation1.end_index == 65
        assert len(citation1.segments) == 1
        assert citation1.segments[0].title == "Quantum Research 2024"
        assert citation1.segments[0].url == "https://quantum-research.com/2024"
        
        # Check second citation  
        citation2 = citations[1]
        assert citation2.start_index == 66
        assert citation2.end_index == 143  # Updated to match the fixture value
        assert len(citation2.segments) == 1
        assert citation2.segments[0].title == "Quantum Algorithms Research"
    
    def test_create_citations_no_candidates(self):
        """Test with response that has no candidates."""
        mock_response = MagicMock()
        mock_response.candidates = []
        
        citations = create_citations_from_grounding(mock_response)
        assert citations == []
    
    def test_create_citations_no_grounding_metadata(self):
        """Test with response that has no grounding metadata."""
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_candidate.grounding_metadata = None
        mock_response.candidates = [mock_candidate]
        
        citations = create_citations_from_grounding(mock_response)
        assert citations == []
    
    def test_create_citations_missing_segment_attributes(self):
        """Test with supports missing required segment attributes."""
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_metadata = MagicMock()
        
        # Create support without proper segment attributes
        mock_support = MagicMock()
        delattr(mock_support, 'segment')
        
        mock_metadata.grounding_supports = [mock_support]
        mock_metadata.grounding_chunks = []
        mock_candidate.grounding_metadata = mock_metadata
        mock_response.candidates = [mock_candidate]
        
        citations = create_citations_from_grounding(mock_response)
        assert citations == []
    
    def test_create_citations_none_indices(self):
        """Test with None start/end indices."""
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_metadata = MagicMock()
        
        mock_support = MagicMock()
        mock_support.segment.start_index = None
        mock_support.segment.end_index = None
        mock_support.grounding_chunk_indices = [0]
        
        mock_metadata.grounding_supports = [mock_support]
        mock_metadata.grounding_chunks = []
        mock_candidate.grounding_metadata = mock_metadata
        mock_response.candidates = [mock_candidate]
        
        citations = create_citations_from_grounding(mock_response)
        assert citations == []
    
    def test_create_citations_invalid_chunk_indices(self):
        """Test with invalid chunk indices."""
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_metadata = MagicMock()
        
        mock_support = MagicMock()
        mock_support.segment.start_index = 0
        mock_support.segment.end_index = 10
        mock_support.grounding_chunk_indices = [999]  # Invalid index
        
        mock_metadata.grounding_supports = [mock_support]
        mock_metadata.grounding_chunks = []  # Empty chunks
        mock_candidate.grounding_metadata = mock_metadata
        mock_response.candidates = [mock_candidate]
        
        citations = create_citations_from_grounding(mock_response)
        assert citations == []  # Should be empty due to no valid segments
    
    def test_create_citations_index_validation(self):
        """Test index validation and correction logic."""
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_metadata = MagicMock()
        
        # Create chunk
        mock_chunk = MagicMock()
        mock_chunk.web.uri = "https://test.com"
        mock_chunk.web.title = "Test Source"
        mock_metadata.grounding_chunks = [mock_chunk]
        
        # Create support with invalid indices that should be corrected
        mock_support = MagicMock()
        mock_support.segment.start_index = -5  # Should be corrected to 0
        mock_support.segment.end_index = -1   # Should be corrected to 0
        mock_support.grounding_chunk_indices = [0]
        
        mock_metadata.grounding_supports = [mock_support]
        mock_candidate.grounding_metadata = mock_metadata
        mock_response.candidates = [mock_candidate]
        
        citations = create_citations_from_grounding(mock_response)
        
        assert len(citations) == 1
        citation = citations[0]
        assert citation.start_index == 0  # Corrected from -5
        assert citation.end_index == 0    # Corrected from -1
    
    def test_create_citations_end_before_start(self):
        """Test correction when end_index is before start_index."""
        mock_response = MagicMock()
        mock_candidate = MagicMock()
        mock_metadata = MagicMock()
        
        # Create chunk
        mock_chunk = MagicMock()
        mock_chunk.web.uri = "https://test.com"
        mock_chunk.web.title = "Test Source"
        mock_metadata.grounding_chunks = [mock_chunk]
        
        # Create support with end_index before start_index
        mock_support = MagicMock()
        mock_support.segment.start_index = 10
        mock_support.segment.end_index = 5   # Before start_index
        mock_support.grounding_chunk_indices = [0]
        
        mock_metadata.grounding_supports = [mock_support]
        mock_candidate.grounding_metadata = mock_metadata
        mock_response.candidates = [mock_candidate]
        
        citations = create_citations_from_grounding(mock_response)
        
        assert len(citations) == 1
        citation = citations[0]
        assert citation.start_index == 10
        assert citation.end_index == 10  # Should be corrected to equal start_index