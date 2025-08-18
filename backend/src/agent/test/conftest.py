"""
Test configuration and fixtures for the refactored agent tests.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Add backend src to path
backend_src = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_src))

from agent.configuration import Configuration
from agent.state import *


@pytest.fixture
def mock_environment():
    """Mock environment variables for testing."""
    env_vars = {
        'GEMINI_API_KEY': 'test_gemini_key',
        'GOOGLE_API_KEY': 'test_google_key',
        'GOOGLE_SEARCH_ENGINE_ID': 'test_search_engine_id',
        'SEARCHAPI_API_KEY': 'test_searchapi_key'
    }
    
    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def test_configuration():
    """Create a test configuration object."""
    return Configuration(
        query_generator_model="gemini-2.5-flash",
        web_searcher_model="gemini-2.5-flash", 
        reflection_model="gemini-2.5-flash",
        answer_model="gemini-2.5-flash"
    )


@pytest.fixture
def mock_genai_client():
    """Mock GenAI client for testing."""
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MagicMock()
    return mock_client


@pytest.fixture
def mock_agent_config():
    """Mock agent configuration."""
    mock_config = MagicMock()
    mock_config.client = MagicMock()
    mock_config.client.chat.completions = MagicMock()
    return mock_config


@pytest.fixture
def sample_query_generation_input():
    """Sample input for QueryGenerationAgent."""
    return QueryGenerationInput(
        research_topic="quantum computing",
        number_of_queries=3,
        current_date="January 15, 2024"
    )


@pytest.fixture
def sample_query_generation_output():
    """Sample output for QueryGenerationAgent."""
    return QueryGenerationOutput(
        queries=[
            "What is quantum computing and how does it work?",
            "What are the current applications of quantum computing?",
            "What are the challenges facing quantum computing development?"
        ],
        rationale="Generated diverse queries to explore different aspects of quantum computing"
    )


@pytest.fixture
def sample_web_search_input():
    """Sample input for WebSearchAgent."""
    return WebSearchInput(
        search_query="What is quantum computing?",
        query_id=1,
        current_date="January 15, 2024"
    )


@pytest.fixture
def sample_web_search_output():
    """Sample output for WebSearchAgent."""
    return WebSearchOutput(
        content="Quantum computing is a type of computation that harnesses quantum mechanics...",
        sources=[
            Source(
                title="Introduction to Quantum Computing",
                url="https://example.com/quantum-intro",
                short_url="quantum-intro",
                label="Source 1"
            )
        ],
        citations=[
            Citation(
                start_index=0,
                end_index=50,
                segments=[
                    Source(
                        title="Introduction to Quantum Computing",
                        url="https://example.com/quantum-intro", 
                        short_url="quantum-intro",
                        label="Source 1"
                    )
                ]
            )
        ]
    )


@pytest.fixture
def sample_reflection_input():
    """Sample input for ReflectionAgent."""
    return ReflectionInput(
        research_topic="quantum computing",
        summaries=["Basic overview of quantum computing principles"],
        current_loop=1
    )


@pytest.fixture
def sample_reflection_output():
    """Sample output for ReflectionAgent."""
    return ReflectionOutput(
        is_sufficient=False,
        knowledge_gap="Need more information about practical applications and current limitations",
        follow_up_queries=[
            "What are the practical applications of quantum computing today?",
            "What are the main challenges preventing widespread quantum computing adoption?"
        ]
    )


@pytest.fixture
def sample_finalization_input():
    """Sample input for FinalizationAgent."""
    return FinalizationInput(
        research_topic="quantum computing",
        summaries=[
            "Quantum computing uses quantum mechanics principles for computation",
            "Current applications include cryptography and optimization problems"
        ],
        sources=[
            Source(
                title="Quantum Computing Overview",
                url="https://example.com/quantum-overview",
                short_url="quantum-overview", 
                label="Source 1"
            )
        ],
        current_date="January 15, 2024"
    )


@pytest.fixture
def sample_finalization_output():
    """Sample output for FinalizationAgent."""
    return FinalizationOutput(
        final_answer="Quantum computing is a revolutionary approach to computation that leverages quantum mechanics principles...",
        used_sources=[
            Source(
                title="Quantum Computing Overview",
                url="https://example.com/quantum-overview",
                short_url="quantum-overview",
                label="Source 1"
            )
        ]
    )


@pytest.fixture
def mock_grounding_response():
    """Mock Gemini grounding response."""
    mock_response = MagicMock()
    mock_response.text = "Test response text with grounding information"
    mock_response.candidates = [MagicMock()]
    mock_response.candidates[0].grounding_metadata = MagicMock()
    
    # Mock grounding chunks
    mock_chunk = MagicMock()
    mock_chunk.web.uri = "https://example.com/test"
    mock_chunk.web.title = "Test Source"
    mock_response.candidates[0].grounding_metadata.grounding_chunks = [mock_chunk]
    
    # Mock grounding supports
    mock_support = MagicMock()
    mock_support.segment.start_index = 0
    mock_support.segment.end_index = 50
    mock_support.grounding_chunk_indices = [0]
    mock_response.candidates[0].grounding_metadata.grounding_supports = [mock_support]
    
    return mock_response


@pytest.fixture
def mock_search_results():
    """Mock search results for testing."""
    return [
        {
            "title": "Quantum Computing Basics",
            "url": "https://example.com/quantum-basics",
            "snippet": "Introduction to quantum computing principles and applications",
            "source": "test_source"
        },
        {
            "title": "Advanced Quantum Algorithms", 
            "url": "https://example.com/quantum-algorithms",
            "snippet": "Overview of quantum algorithms and their implementations",
            "source": "test_source"
        }
    ]


# Additional fixtures for HTTP client mocking
@pytest.fixture
def mock_httpx_response():
    """Mock httpx response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {
                "title": "Test Result",
                "link": "https://example.com/test",
                "snippet": "Test snippet"
            }
        ]
    }
    return mock_response


@pytest.fixture
def mock_citation_data():
    """Mock citation data for testing."""
    return {
        "sources": [
            Source(
                title="Test Source 1",
                url="https://example.com/source1",
                short_url="source1",
                label="Source 1"
            ),
            Source(
                title="Test Source 2", 
                url="https://example.com/source2",
                short_url="source2",
                label="Source 2"
            )
        ],
        "citations": [
            Citation(
                start_index=0,
                end_index=25,
                segments=[
                    Source(
                        title="Test Source 1",
                        url="https://example.com/source1",
                        short_url="source1", 
                        label="Source 1"
                    )
                ]
            )
        ]
    }