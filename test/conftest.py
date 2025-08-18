"""
Test configuration and fixtures for agents.py testing.
Provides mocks, fixtures, and test utilities.
"""

import pytest
import os
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Dict, Any, List
import sys
from pathlib import Path

# Add the backend src directory to the Python path
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

# Create a mock BaseAgent metaclass that works with subscripts
class MockBaseAgentMeta(type):
    def __getitem__(cls, item):
        return cls  # Allow BaseAgent[Type1, Type2] syntax
        
class MockBaseAgentClass(metaclass=MockBaseAgentMeta):
    def __init__(self, *args, **kwargs):
        self.config = kwargs.get('config')
        
    def run(self, *args, **kwargs):
        """Mock run method for BaseAgent"""
        return MagicMock()

# Mock BaseAgentConfig as well
class MockBaseAgentConfig:
    def __init__(self, *args, **kwargs):
        self.client = kwargs.get('client')
        self.temperature = kwargs.get('temperature', 1.0)
        self.max_retries = kwargs.get('max_retries', 2)

# Mock the module-level API key check and BaseAgent before importing modules
with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
    with patch('atomic_agents.agents.base_agent.BaseAgent', MockBaseAgentClass):
        with patch('atomic_agents.agents.base_agent.BaseAgentConfig', MockBaseAgentConfig):
            # Import the actual modules we're testing
            from agent.state import (
                QueryGenerationInput,
                QueryGenerationOutput,
                WebSearchInput,
                WebSearchOutput,
                ReflectionInput,
                ReflectionOutput,
                FinalizationInput,
                FinalizationOutput,
                Source,
                Citation
            )
            from agent.configuration import Configuration


@pytest.fixture
def mock_environment():
    """Mock environment variables for all tests."""
    env_vars = {
        "GEMINI_API_KEY": "test-gemini-key-12345",
        "GOOGLE_API_KEY": "test-google-key-12345", 
        "GOOGLE_SEARCH_ENGINE_ID": "test-engine-id-12345",
        "SEARCHAPI_API_KEY": "test-searchapi-key-12345"
    }
    
    with patch.dict(os.environ, env_vars, clear=False):
        # Also patch the os.getenv calls in the modules that use them
        with patch('os.getenv') as mock_getenv:
            def mock_getenv_func(key, default=None):
                return env_vars.get(key, default)
            mock_getenv.side_effect = mock_getenv_func
            yield env_vars


@pytest.fixture
def mock_genai_client():
    """Mock Google GenAI client."""
    mock_client = MagicMock()
    
    # Mock response with grounding metadata
    mock_response = MagicMock()
    mock_response.text = "This is a test response about quantum computing."
    
    # Mock grounding metadata structure
    mock_candidate = MagicMock()
    mock_grounding_metadata = MagicMock()
    
    # Mock chunks
    mock_chunk = MagicMock()
    mock_chunk.web.uri = "https://example.com/quantum"
    mock_chunk.web.title = "Quantum Computing Research"
    mock_grounding_metadata.grounding_chunks = [mock_chunk]
    
    # Mock supports
    mock_support = MagicMock()
    mock_support.segment.start_index = 0
    mock_support.segment.end_index = 10
    mock_support.grounding_chunk_indices = [0]
    mock_grounding_metadata.grounding_supports = [mock_support]
    
    mock_candidate.grounding_metadata = mock_grounding_metadata
    mock_response.candidates = [mock_candidate]
    
    mock_client.models.generate_content.return_value = mock_response
    
    return mock_client


@pytest.fixture
def mock_instructor_client():
    """Mock instructor client for structured outputs."""
    mock_client = MagicMock()
    
    # Mock chat completions create method
    mock_completions = MagicMock()
    mock_client.chat.completions = mock_completions
    
    return mock_client


@pytest.fixture
def sample_query_generation_input():
    """Sample input for query generation testing."""
    return QueryGenerationInput(
        research_topic="What are the latest developments in quantum computing?",
        number_of_queries=3,
        current_date="January 15, 2024"
    )


@pytest.fixture
def sample_query_generation_output():
    """Sample output for query generation testing."""
    return QueryGenerationOutput(
        queries=[
            "quantum computing breakthroughs 2024",
            "quantum algorithms research latest",
            "quantum hardware developments 2024"
        ],
        rationale="These queries cover different aspects of quantum computing developments"
    )


@pytest.fixture
def sample_web_search_input():
    """Sample input for web search testing."""
    return WebSearchInput(
        search_query="quantum computing breakthroughs 2024",
        query_id=1,
        current_date="January 15, 2024"
    )


@pytest.fixture
def sample_sources():
    """Sample source objects."""
    return [
        Source(
            title="Quantum Computing Research 2024",
            url="https://example.com/quantum-research",
            short_url="quantum-source-1",
            label="Source 1"
        ),
        Source(
            title="Latest Quantum Developments",
            url="https://example.com/quantum-dev",
            short_url="quantum-source-2", 
            label="Source 2"
        )
    ]


@pytest.fixture
def sample_citations():
    """Sample citation objects."""
    return [
        Citation(
            start_index=0,
            end_index=50,
            segments=[
                Source(
                    title="Quantum Research",
                    url="https://example.com/quantum",
                    short_url="cite-1",
                    label="Citation 1"
                )
            ]
        )
    ]


@pytest.fixture
def sample_web_search_output(sample_sources, sample_citations):
    """Sample output for web search testing."""
    return WebSearchOutput(
        content="Quantum computing has made significant advances in 2024 with new algorithms and hardware improvements.",
        sources=sample_sources,
        citations=sample_citations
    )


@pytest.fixture
def sample_reflection_input():
    """Sample input for reflection testing."""
    return ReflectionInput(
        research_topic="quantum computing developments",
        summaries=[
            "Quantum computing has improved significantly",
            "New algorithms have been developed"
        ],
        current_loop=1
    )


@pytest.fixture
def sample_reflection_output():
    """Sample output for reflection testing."""
    return ReflectionOutput(
        is_sufficient=False,
        knowledge_gap="Need more specific performance benchmarks",
        follow_up_queries=["quantum computing performance benchmarks 2024"]
    )


@pytest.fixture
def sample_finalization_input(sample_sources):
    """Sample input for finalization testing."""
    return FinalizationInput(
        research_topic="quantum computing developments",
        summaries=[
            "Quantum computing has advanced with new hardware",
            "Performance improvements are significant"
        ],
        sources=sample_sources,
        current_date="January 15, 2024"
    )


@pytest.fixture
def sample_finalization_output(sample_sources):
    """Sample output for finalization testing."""
    return FinalizationOutput(
        final_answer="Based on the research, quantum computing has made remarkable progress in 2024 with significant hardware and software improvements.",
        used_sources=sample_sources[:2]
    )


@pytest.fixture
def mock_httpx_response():
    """Mock httpx response for API calls."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {
                "title": "Quantum Computing Advances",
                "link": "https://example.com/quantum",
                "snippet": "Recent advances in quantum computing..."
            }
        ]
    }
    return mock_response


@pytest.fixture
def mock_search_api_response():
    """Mock SearchAPI.io response."""
    return {
        "organic_results": [
            {
                "title": "Quantum Computing News",
                "link": "https://quantum-news.com",
                "snippet": "Latest quantum computing developments..."
            }
        ]
    }


@pytest.fixture
def mock_duckduckgo_response():
    """Mock DuckDuckGo API response."""
    return {
        "AbstractText": "Quantum computing is a type of computation...",
        "Heading": "Quantum Computing",
        "AbstractURL": "https://en.wikipedia.org/wiki/Quantum_computing",
        "RelatedTopics": [
            {
                "Text": "Quantum algorithms are running on quantum computers",
                "FirstURL": "https://example.com/quantum-algorithms"
            }
        ]
    }


@pytest.fixture
def test_configuration():
    """Test configuration object."""
    config = Configuration(
        query_generator_model="gemini-2.5-flash",
        reflection_model="gemini-2.5-flash", 
        answer_model="gemini-2.5-flash",
        number_of_initial_queries=3,
        max_research_loops=2
    )
    return config


@pytest.fixture
def mock_grounding_response():
    """Mock response from Gemini with grounding metadata."""
    mock_response = MagicMock()
    mock_response.text = "Quantum computing has achieved significant milestones in 2024. These developments include improved error correction and new quantum algorithms."
    
    # Create mock grounding metadata
    mock_candidate = MagicMock()
    mock_metadata = MagicMock()
    
    # Mock chunks
    chunk1 = MagicMock()
    chunk1.web.uri = "https://quantum-research.com/2024"
    chunk1.web.title = "Quantum Research 2024"
    
    chunk2 = MagicMock()
    chunk2.web.uri = "https://quantum-algorithms.org" 
    chunk2.web.title = "Quantum Algorithms Research"
    
    mock_metadata.grounding_chunks = [chunk1, chunk2]
    
    # Mock supports
    support1 = MagicMock()
    support1.segment.start_index = 0
    support1.segment.end_index = 65
    support1.grounding_chunk_indices = [0]
    
    support2 = MagicMock() 
    support2.segment.start_index = 66
    support2.segment.end_index = 143  # Set to text length to ensure it's within bounds
    support2.grounding_chunk_indices = [1]
    
    mock_metadata.grounding_supports = [support1, support2]
    
    mock_candidate.grounding_metadata = mock_metadata
    mock_response.candidates = [mock_candidate]
    
    return mock_response


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


class MockAgent:
    """Mock agent class for testing."""
    
    def __init__(self, config):
        self.config = config
        self.agent_config = config
        
    def run(self, input_data):
        """Mock run method."""
        return MagicMock()


class MockAgentConfig:
    """Mock AgentConfig class since it's missing from imports."""
    
    def __init__(self, client=None, temperature=1.0, max_retries=2):
        self.client = client
        self.temperature = temperature
        self.max_retries = max_retries


@pytest.fixture
def mock_agent_config(mock_instructor_client):
    """Mock agent configuration."""
    return MockAgentConfig(client=mock_instructor_client)


# Helper functions for testing
class TestHelpers:
    """Helper functions for testing."""
    
    @staticmethod
    def create_mock_response(text="Test response", has_grounding=True):
        """Create a mock response object."""
        mock_response = MagicMock()
        mock_response.text = text
        
        if has_grounding:
            mock_candidate = MagicMock()
            mock_metadata = MagicMock()
            
            # Create minimal grounding structure
            mock_chunk = MagicMock()
            mock_chunk.web.uri = "https://test.com"
            mock_chunk.web.title = "Test Source"
            mock_metadata.grounding_chunks = [mock_chunk]
            
            mock_support = MagicMock()
            mock_support.segment.start_index = 0
            mock_support.segment.end_index = len(text)
            mock_support.grounding_chunk_indices = [0]
            mock_metadata.grounding_supports = [mock_support]
            
            mock_candidate.grounding_metadata = mock_metadata
            mock_response.candidates = [mock_candidate]
        else:
            mock_response.candidates = []
            
        return mock_response
    
    @staticmethod
    def create_mock_search_results(count=3):
        """Create mock search results."""
        return [
            {
                "title": f"Test Result {i+1}",
                "url": f"https://test{i+1}.com",
                "snippet": f"This is test snippet {i+1}",
                "source": "test_source"
            }
            for i in range(count)
        ]
    
    @staticmethod
    def validate_source_structure(source):
        """Validate source object structure."""
        required_fields = ["title", "url", "short_url", "label"]
        return all(hasattr(source, field) for field in required_fields)
    
    @staticmethod
    def validate_citation_structure(citation):
        """Validate citation object structure.""" 
        return (hasattr(citation, 'start_index') and 
                hasattr(citation, 'end_index') and
                hasattr(citation, 'segments'))


@pytest.fixture
def test_helpers():
    """Provide test helper functions."""
    return TestHelpers()


@pytest.fixture
def mock_agent_config_import():
    """Mock the AgentConfig import since tests expect it in agent.configuration."""
    with patch('agent.configuration.AgentConfig', MockAgentConfig):
        with patch('atomic_agents.agents.base_agent.BaseAgentConfig', MockBaseAgentConfig):
            yield MockAgentConfig


@pytest.fixture  
def mock_agent_dependencies():
    """Mock all agent dependencies in one place for cleaner tests."""
    # Use our MockBaseAgentClass that supports subscripting
    mock_base_agent_class = MockBaseAgentClass
    mock_base_agent_instance = MagicMock()
    
    with patch('atomic_agents.agents.base_agent.BaseAgent', mock_base_agent_class):
        with patch('atomic_agents.agents.base_agent.BaseAgentConfig', MockBaseAgentConfig):
            with patch('agent.configuration.genai.configure'):
                with patch('agent.configuration.instructor.from_gemini') as mock_from_gemini:
                    with patch('agent.configuration.genai.GenerativeModel') as mock_model:
                        with patch('google.generativeai.types.GoogleSearch', create=True) as mock_google_search:
                            with patch('google.generativeai.types.GoogleSearchRetrieval', create=True) as mock_google_search_retrieval:
                                with patch('google.generativeai.types.DynamicRetrievalConfig', create=True) as mock_dynamic_config:
                                    with patch('google.generativeai.types.DynamicRetrievalConfigMode', create=True) as mock_mode:
                                        with patch('google.generativeai.types.Tool', create=True) as mock_tool:
                                            mock_client = MagicMock()
                                            mock_from_gemini.return_value = mock_client
                                            mock_model.return_value = MagicMock()
                                            mock_tool.return_value = MagicMock()
                                            mock_mode.MODE_DYNAMIC = "MODE_DYNAMIC"
                                            
                                            yield {
                                                'base_agent': mock_base_agent_class,
                                                'base_agent_instance': mock_base_agent_instance,
                                                'client': mock_client,
                                                'from_gemini': mock_from_gemini,
                                                'model': mock_model,
                                                'google_search': mock_google_search,
                                                'google_search_retrieval': mock_google_search_retrieval,
                                                'tool': mock_tool
                                            }