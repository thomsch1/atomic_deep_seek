# Testing Implementation Guide

This comprehensive guide provides complete testing patterns, strategies, and implementation templates for the AI-powered web research application. It covers unit tests, integration tests, end-to-end tests, and performance testing for both backend and frontend components.

## 🧪 Testing Strategy Overview

### Testing Pyramid

```
                /\
               /  \
              /E2E \     ← End-to-End Tests (Few, High-level)
             /______\
            /        \
           /   INTEG  \   ← Integration Tests (Some, Service-level)
          /__________\
         /            \
        /     UNIT     \  ← Unit Tests (Many, Component-level)
       /________________\
```

### Test Categories

1. **Unit Tests** (70%): Test individual functions, classes, and components
2. **Integration Tests** (20%): Test component interactions and workflows
3. **End-to-End Tests** (10%): Test complete user workflows and scenarios

## 🐍 Backend Testing Implementation

### Test Environment Setup

#### `backend/tests/conftest.py`
**Purpose**: Global test configuration and fixtures  
**Template**:
```python
"""Global test configuration and fixtures."""

import asyncio
import pytest
import os
from pathlib import Path
from unittest.mock import AsyncMock, Mock
from typing import AsyncGenerator, Generator

# Test environment setup
os.environ["GEMINI_API_KEY"] = "test_api_key"
os.environ["NODE_ENV"] = "test"
os.environ["LOG_LEVEL"] = "ERROR"

# Add src to path
import sys
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent.configuration import Configuration
from agent.orchestrator import ResearchOrchestrator
from agent.state import ResearchRequest, ResearchResponse, Source
from agent.agents.query_generation_agent import QueryGenerationAgent
from agent.agents.web_search_agent import WebSearchAgent
from agent.agents.reflection_agent import ReflectionAgent
from agent.agents.finalization_agent import FinalizationAgent


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config():
    """Create test configuration."""
    return Configuration(
        gemini_api_key="test_api_key",
        gemini_model="gemini-1.5-flash",
        search_timeout=10,
        max_sources_per_query=5,
        quality_threshold=0.5,
        default_initial_query_count=2,
        default_max_loops=1,
    )


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini API client."""
    mock_client = AsyncMock()
    
    # Mock successful generation
    mock_response = Mock()
    mock_response.text = "Mocked AI response"
    mock_client.generate_content_async.return_value = mock_response
    
    return mock_client


@pytest.fixture
def sample_research_request():
    """Create sample research request."""
    return ResearchRequest(
        question="What is artificial intelligence?",
        initial_search_query_count=2,
        max_research_loops=1,
        reasoning_model="gemini-1.5-flash",
        source_quality_filter="medium"
    )


@pytest.fixture
def sample_sources():
    """Create sample sources for testing."""
    return [
        Source(
            title="Introduction to Artificial Intelligence",
            url="https://example.com/ai-intro",
            label="[1]",
            source_credibility="high",
            domain_type="academic",
            quality_score=0.95,
        ),
        Source(
            title="AI in Modern Computing",
            url="https://example.com/ai-computing",
            label="[2]",
            source_credibility="medium",
            domain_type="news",
            quality_score=0.75,
        ),
    ]


@pytest.fixture
def mock_search_results():
    """Mock search results."""
    return [
        {
            "title": "AI Research Paper",
            "url": "https://arxiv.org/paper123",
            "snippet": "Comprehensive overview of AI techniques...",
            "source": "arxiv.org",
        },
        {
            "title": "Machine Learning Basics",
            "url": "https://example.edu/ml-basics",
            "snippet": "Introduction to machine learning concepts...",
            "source": "example.edu",
        },
    ]


@pytest.fixture
async def mock_orchestrator(test_config):
    """Create mock research orchestrator."""
    orchestrator = Mock(spec=ResearchOrchestrator)
    orchestrator.config = test_config
    
    # Mock async methods
    orchestrator.run_research_async = AsyncMock()
    
    return orchestrator


@pytest.fixture
def query_generation_agent(test_config):
    """Create query generation agent for testing."""
    return QueryGenerationAgent(test_config)


@pytest.fixture 
def web_search_agent(test_config):
    """Create web search agent for testing."""
    return WebSearchAgent(test_config)


@pytest.fixture
def reflection_agent(test_config):
    """Create reflection agent for testing."""
    return ReflectionAgent(test_config)


@pytest.fixture
def finalization_agent(test_config):
    """Create finalization agent for testing."""
    return FinalizationAgent(test_config)


# Test data fixtures
@pytest.fixture
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def mock_http_responses():
    """Mock HTTP responses for testing."""
    return {
        "https://example.com/test": {
            "status": 200,
            "content": "<html><body>Test content</body></html>",
            "headers": {"content-type": "text/html"},
        },
        "https://api.example.com/search": {
            "status": 200,
            "json": {
                "results": [
                    {"title": "Test Result", "url": "https://test.com", "snippet": "Test snippet"}
                ]
            },
        },
    }


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_environment():
    """Clean up environment after each test."""
    yield
    # Reset any global state if needed
    pass


# Performance testing fixtures
@pytest.fixture
def performance_tracker():
    """Track performance metrics during tests."""
    import time
    
    class PerformanceTracker:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.metrics = {}
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
            return self.end_time - self.start_time if self.start_time else 0
        
        def add_metric(self, name: str, value: float):
            self.metrics[name] = value
    
    return PerformanceTracker()
```

### Unit Testing Patterns

#### Agent Unit Test Template

```python
# backend/src/agent/test/test_agent_template.py
"""Unit tests for AgentTemplate following comprehensive testing patterns."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from agent.agents.agent_template import AgentTemplate, AgentInput, AgentOutput
from agent.configuration import Configuration


class TestAgentTemplate:
    """Comprehensive unit tests for AgentTemplate."""
    
    def test_agent_initialization(self, test_config):
        """Test agent initializes correctly with configuration."""
        agent = AgentTemplate(test_config)
        
        assert agent.config == test_config
        assert agent.logger is not None
        assert hasattr(agent, 'system_prompt')
    
    def test_agent_initialization_with_default_config(self):
        """Test agent initializes with default configuration."""
        agent = AgentTemplate()
        
        assert agent.config is not None
        assert agent.config.gemini_model == "gemini-1.5-flash"
    
    def test_successful_execution(self, test_config):
        """Test successful agent execution with valid input."""
        agent = AgentTemplate(test_config)
        
        # Mock the internal method
        with patch.object(agent, '_process_input') as mock_process:
            mock_process.return_value = "processed_result"
            
            input_data = AgentInput(field1="test", field2="data")
            result = agent.run(input_data)
            
            assert isinstance(result, AgentOutput)
            assert result.output_field == "processed_result"
            mock_process.assert_called_once_with(input_data)
    
    def test_input_validation(self, test_config):
        """Test input validation and error handling."""
        agent = AgentTemplate(test_config)
        
        # Test with invalid input
        with pytest.raises(ValueError, match="Invalid input"):
            invalid_input = AgentInput(field1="", field2=None)
            agent.run(invalid_input)
    
    def test_error_handling(self, test_config):
        """Test agent error handling behavior."""
        agent = AgentTemplate(test_config)
        
        with patch.object(agent, '_process_input') as mock_process:
            mock_process.side_effect = Exception("Processing failed")
            
            input_data = AgentInput(field1="test", field2="data")
            
            with pytest.raises(Exception, match="Processing failed"):
                agent.run(input_data)
    
    @patch('agent.agents.agent_template.external_api_call')
    def test_external_api_interaction(self, mock_api, test_config):
        """Test agent interaction with external APIs."""
        agent = AgentTemplate(test_config)
        
        # Setup mock response
        mock_api.return_value = {"status": "success", "data": "api_result"}
        
        input_data = AgentInput(field1="api_test", field2="data")
        result = agent.run(input_data)
        
        # Verify API was called with correct parameters
        mock_api.assert_called_once_with(
            input_data.field1, 
            config=agent.config
        )
        
        assert result.output_field is not None
    
    def test_logging_behavior(self, test_config, caplog):
        """Test agent logging functionality."""
        agent = AgentTemplate(test_config)
        
        input_data = AgentInput(field1="log_test", field2="data")
        
        with patch.object(agent, '_process_input') as mock_process:
            mock_process.return_value = "logged_result"
            agent.run(input_data)
        
        # Check that logging occurred
        assert "Starting execution" in caplog.text
        assert "Completed execution" in caplog.text
    
    @pytest.mark.asyncio
    async def test_async_operation(self, test_config):
        """Test asynchronous operations if agent supports them."""
        agent = AgentTemplate(test_config)
        
        if hasattr(agent, 'run_async'):
            input_data = AgentInput(field1="async_test", field2="data")
            
            with patch.object(agent, '_process_input_async') as mock_async:
                mock_async.return_value = "async_result"
                
                result = await agent.run_async(input_data)
                assert result.output_field == "async_result"
    
    @pytest.mark.parametrize("field1,field2,expected", [
        ("test1", "data1", "expected_result1"),
        ("test2", "data2", "expected_result2"),
        ("test3", "data3", "expected_result3"),
    ])
    def test_parameterized_inputs(self, test_config, field1, field2, expected):
        """Test agent with various input combinations."""
        agent = AgentTemplate(test_config)
        
        with patch.object(agent, '_process_input') as mock_process:
            mock_process.return_value = expected
            
            input_data = AgentInput(field1=field1, field2=field2)
            result = agent.run(input_data)
            
            assert result.output_field == expected
    
    def test_performance_requirements(self, test_config, performance_tracker):
        """Test agent performance requirements."""
        agent = AgentTemplate(test_config)
        
        input_data = AgentInput(field1="performance", field2="test")
        
        performance_tracker.start()
        with patch.object(agent, '_process_input') as mock_process:
            mock_process.return_value = "fast_result"
            agent.run(input_data)
        
        execution_time = performance_tracker.stop()
        
        # Assert performance requirements
        assert execution_time < 1.0  # Should complete within 1 second
    
    def test_configuration_impact(self):
        """Test how different configurations affect agent behavior."""
        # Test with different configurations
        config1 = Configuration(gemini_model="gemini-1.5-flash")
        config2 = Configuration(gemini_model="gemini-1.5-pro")
        
        agent1 = AgentTemplate(config1)
        agent2 = AgentTemplate(config2)
        
        # Verify configurations are applied
        assert agent1.config.gemini_model == "gemini-1.5-flash"
        assert agent2.config.gemini_model == "gemini-1.5-pro"
        
        # Test behavior differences if any
        # This would depend on specific agent implementation
```

#### Search Provider Unit Test Template

```python
# backend/src/agent/test/test_search_provider.py
"""Unit tests for search providers."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx
from agent.search.google_custom_search import GoogleCustomSearchProvider
from agent.search.base_provider import SearchResult


class TestGoogleCustomSearchProvider:
    """Test Google Custom Search provider."""
    
    @pytest.fixture
    def provider(self):
        """Create provider instance."""
        return GoogleCustomSearchProvider(
            api_key="test_key",
            search_engine_id="test_cse_id"
        )
    
    def test_provider_initialization(self, provider):
        """Test provider initializes correctly."""
        assert provider.api_key == "test_key"
        assert provider.search_engine_id == "test_cse_id"
        assert provider.provider_name == "GoogleCustomSearch"
    
    def test_is_available(self, provider):
        """Test availability check."""
        assert provider.is_available() == True
        
        # Test with missing credentials
        provider_no_key = GoogleCustomSearchProvider()
        assert provider_no_key.is_available() == False
    
    @pytest.mark.asyncio
    async def test_successful_search(self, provider):
        """Test successful search execution."""
        mock_response_data = {
            "items": [
                {
                    "title": "Test Result 1",
                    "link": "https://example.com/1",
                    "snippet": "Test snippet 1",
                },
                {
                    "title": "Test Result 2",
                    "link": "https://example.com/2",
                    "snippet": "Test snippet 2",
                },
            ]
        }
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            results = await provider.search("test query", num_results=2)
            
            assert len(results) == 2
            assert all(isinstance(r, SearchResult) for r in results)
            assert results[0].title == "Test Result 1"
            assert results[0].url == "https://example.com/1"
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, provider):
        """Test API error handling."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError(
                "API Error", 
                request=Mock(), 
                response=Mock(status_code=403)
            )
            
            results = await provider.search("test query")
            assert results == []  # Should return empty list on error
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, provider):
        """Test network error handling."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = httpx.ConnectError("Network error")
            
            results = await provider.search("test query")
            assert results == []
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, provider):
        """Test timeout handling."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Timeout")
            
            results = await provider.search("test query")
            assert results == []
    
    def test_result_parsing(self, provider):
        """Test search result parsing."""
        raw_result = {
            "title": "Test Title",
            "link": "https://example.com",
            "snippet": "Test snippet",
        }
        
        result = provider._parse_result(raw_result)
        
        assert isinstance(result, SearchResult)
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.snippet == "Test snippet"
    
    @pytest.mark.parametrize("query,num_results", [
        ("simple query", 5),
        ("complex query with multiple terms", 10),
        ("query with special chars: @#$", 3),
    ])
    @pytest.mark.asyncio
    async def test_various_queries(self, provider, query, num_results):
        """Test various query types."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"items": []}
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            results = await provider.search(query, num_results)
            
            # Verify the request was made with correct parameters
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert query in str(call_args)
```

### Integration Testing Patterns

#### API Integration Test Template

```python
# backend/tests/test_api_integration.py
"""Integration tests for the FastAPI application."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from agent.app import app
from agent.state import ResearchRequest, ResearchResponse


class TestAPIIntegration:
    """Integration tests for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
    
    @patch('agent.app.orchestrator')
    def test_research_endpoint_success(self, mock_orchestrator, client):
        """Test successful research request."""
        # Setup mock response
        mock_response = ResearchResponse(
            final_answer="Test answer about AI",
            sources=[],
            research_loops_executed=1,
            total_queries=2
        )
        mock_orchestrator.run_research_async = AsyncMock(return_value=mock_response)
        
        # Make request
        request_data = {
            "question": "What is artificial intelligence?",
            "initial_search_query_count": 2,
            "max_research_loops": 1
        }
        
        response = client.post("/research", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "final_answer" in data
        assert "sources" in data
        assert data["research_loops_executed"] == 1
        assert data["total_queries"] == 2
    
    def test_research_endpoint_validation_error(self, client):
        """Test request validation errors."""
        # Empty question should fail validation
        request_data = {
            "question": "",
            "initial_search_query_count": 2
        }
        
        response = client.post("/research", json=request_data)
        assert response.status_code == 422
    
    def test_research_endpoint_invalid_parameters(self, client):
        """Test invalid parameter handling."""
        request_data = {
            "question": "Valid question",
            "initial_search_query_count": 15,  # Too high
            "max_research_loops": -1,  # Invalid
        }
        
        response = client.post("/research", json=request_data)
        assert response.status_code == 422
    
    @patch('agent.app.orchestrator')
    def test_research_endpoint_server_error(self, mock_orchestrator, client):
        """Test server error handling."""
        mock_orchestrator.run_research_async = AsyncMock(
            side_effect=Exception("Internal processing error")
        )
        
        request_data = {
            "question": "Test question",
            "initial_search_query_count": 2
        }
        
        response = client.post("/research", json=request_data)
        assert response.status_code == 500
        assert "detail" in response.json()
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/research")
        
        # Check CORS headers
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert "access-control-allow-methods" in headers
    
    def test_openapi_docs(self, client):
        """Test OpenAPI documentation endpoints."""
        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
        
        # Test OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
    
    @pytest.mark.parametrize("question,expected_status", [
        ("What is AI?", 200),
        ("How does machine learning work?", 200),
        ("Explain neural networks", 200),
    ])
    @patch('agent.app.orchestrator')
    def test_various_research_questions(
        self, mock_orchestrator, client, question, expected_status
    ):
        """Test various research questions."""
        mock_response = ResearchResponse(
            final_answer=f"Answer for: {question}",
            sources=[],
            research_loops_executed=1,
            total_queries=2
        )
        mock_orchestrator.run_research_async = AsyncMock(return_value=mock_response)
        
        response = client.post("/research", json={"question": question})
        assert response.status_code == expected_status
```

#### Orchestrator Integration Test Template

```python
# backend/tests/test_orchestrator_integration.py
"""Integration tests for research orchestrator."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from agent.orchestrator import ResearchOrchestrator
from agent.state import ResearchRequest


class TestOrchestratorIntegration:
    """Integration tests for research orchestrator workflows."""
    
    @pytest.fixture
    async def orchestrator(self, test_config):
        """Create orchestrator with test configuration."""
        return ResearchOrchestrator(test_config)
    
    @pytest.mark.asyncio
    async def test_complete_research_workflow(self, orchestrator, sample_research_request):
        """Test complete research workflow integration."""
        # Mock all agents
        with patch.object(orchestrator, 'query_agent') as mock_query_agent, \
             patch.object(orchestrator, 'search_agent') as mock_search_agent, \
             patch.object(orchestrator, 'reflection_agent') as mock_reflection_agent, \
             patch.object(orchestrator, 'finalization_agent') as mock_finalization_agent:
            
            # Setup mock responses
            mock_query_agent.run.return_value = Mock(
                search_queries=["AI definition", "machine learning basics"]
            )
            
            mock_search_agent.run.return_value = Mock(
                processed_sources=[],
                total_results=5
            )
            
            mock_reflection_agent.run.return_value = Mock(
                is_complete=True,
                completeness_score=0.9,
                additional_queries=[]
            )
            
            mock_finalization_agent.run.return_value = Mock(
                final_answer="AI is a field of computer science...",
                citations_used=["[1]", "[2]"]
            )
            
            # Execute workflow
            result = await orchestrator.run_research_async(sample_research_request)
            
            # Verify workflow execution
            assert result is not None
            assert result.final_answer is not None
            assert isinstance(result.research_loops_executed, int)
            assert isinstance(result.total_queries, int)
    
    @pytest.mark.asyncio
    async def test_multi_loop_research(self, orchestrator):
        """Test multi-loop research workflow."""
        request = ResearchRequest(
            question="Complex research question",
            max_research_loops=3
        )
        
        with patch.object(orchestrator, '_execute_research_loop') as mock_loop:
            # Mock incomplete first loop, complete second loop
            mock_loop.side_effect = [
                Mock(is_complete=False, additional_queries=["follow-up query"]),
                Mock(is_complete=True, additional_queries=[])
            ]
            
            result = await orchestrator.run_research_async(request)
            
            # Should have executed 2 loops (stopped when complete)
            assert mock_loop.call_count == 2
    
    @pytest.mark.asyncio 
    async def test_parallel_search_execution(self, orchestrator):
        """Test parallel search execution."""
        queries = ["query1", "query2", "query3"]
        
        with patch.object(orchestrator, 'search_agent') as mock_agent:
            mock_agent.run.return_value = Mock(processed_sources=[])
            
            results = await orchestrator._parallel_web_search(queries)
            
            # Should have executed searches in parallel
            assert len(results) == 3
            assert mock_agent.run.call_count == 3
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, orchestrator, sample_research_request):
        """Test error recovery mechanisms."""
        with patch.object(orchestrator, 'search_agent') as mock_search_agent:
            # First call fails, second succeeds
            mock_search_agent.run.side_effect = [
                Exception("API failure"),
                Mock(processed_sources=[], total_results=0)
            ]
            
            # Should not raise exception, should recover
            result = await orchestrator.run_research_async(sample_research_request)
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_performance_requirements(
        self, orchestrator, sample_research_request, performance_tracker
    ):
        """Test orchestrator performance requirements."""
        # Mock quick responses
        with patch.object(orchestrator, 'query_agent') as mock_query, \
             patch.object(orchestrator, 'search_agent') as mock_search, \
             patch.object(orchestrator, 'finalization_agent') as mock_final:
            
            mock_query.run.return_value = Mock(search_queries=["test"])
            mock_search.run.return_value = Mock(processed_sources=[])
            mock_final.run.return_value = Mock(final_answer="result")
            
            performance_tracker.start()
            await orchestrator.run_research_async(sample_research_request)
            execution_time = performance_tracker.stop()
            
            # Should complete within reasonable time for mocked operations
            assert execution_time < 5.0
```

## ⚛️ Frontend Testing Implementation

### React Testing Library Patterns

#### Component Test Template

```typescript
// frontend/src/components/__tests__/ComponentTemplate.test.tsx
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import { ComponentTemplate } from '../ComponentTemplate'
import type { ComponentTemplateProps } from '../ComponentTemplate'

// Mock dependencies
vi.mock('@/services/api', () => ({
  AtomicAgentAPI: vi.fn().mockImplementation(() => ({
    conductResearch: vi.fn().mockResolvedValue({
      final_answer: 'Mocked research result',
      sources: [],
      research_loops_executed: 1,
      total_queries: 2,
    }),
    healthCheck: vi.fn().mockResolvedValue({ status: 'healthy' }),
  })),
}))

describe('ComponentTemplate', () => {
  const defaultProps: ComponentTemplateProps = {
    data: 'test data',
    onUpdate: vi.fn(),
    className: 'test-class',
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Rendering', () => {
    it('renders with default props', () => {
      render(<ComponentTemplate {...defaultProps} />)
      
      expect(screen.getByText('Expected Text')).toBeInTheDocument()
      expect(screen.getByTestId('component-container')).toHaveClass('test-class')
    })

    it('renders with different data', () => {
      const props = { ...defaultProps, data: 'different data' }
      render(<ComponentTemplate {...props} />)
      
      expect(screen.getByText('different data')).toBeInTheDocument()
    })

    it('handles missing optional props', () => {
      const { onUpdate, className, ...requiredProps } = defaultProps
      render(<ComponentTemplate {...requiredProps} />)
      
      expect(screen.getByTestId('component-container')).toBeInTheDocument()
    })
  })

  describe('User Interactions', () => {
    it('handles button clicks', async () => {
      const user = userEvent.setup()
      const mockOnUpdate = vi.fn()
      
      render(<ComponentTemplate {...defaultProps} onUpdate={mockOnUpdate} />)
      
      const button = screen.getByRole('button', { name: /submit/i })
      await user.click(button)
      
      expect(mockOnUpdate).toHaveBeenCalledWith('expected_data')
    })

    it('handles keyboard interactions', async () => {
      const user = userEvent.setup()
      render(<ComponentTemplate {...defaultProps} />)
      
      const input = screen.getByRole('textbox')
      await user.type(input, 'test input{enter}')
      
      expect(input).toHaveValue('test input')
    })

    it('handles form submission', async () => {
      const user = userEvent.setup()
      const mockOnUpdate = vi.fn()
      
      render(<ComponentTemplate {...defaultProps} onUpdate={mockOnUpdate} />)
      
      const form = screen.getByRole('form')
      await user.submit(form)
      
      await waitFor(() => {
        expect(mockOnUpdate).toHaveBeenCalled()
      })
    })
  })

  describe('State Management', () => {
    it('manages loading states correctly', async () => {
      render(<ComponentTemplate {...defaultProps} />)
      
      const button = screen.getByRole('button')
      fireEvent.click(button)
      
      // Check loading state appears
      expect(screen.getByText('Loading...')).toBeInTheDocument()
      
      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.queryByText('Loading...')).not.toBeInTheDocument()
      })
    })

    it('handles error states', async () => {
      // Mock API to throw error
      const mockError = new Error('API Error')
      vi.mocked(AtomicAgentAPI).mockImplementation(() => ({
        conductResearch: vi.fn().mockRejectedValue(mockError),
        healthCheck: vi.fn(),
      }))

      render(<ComponentTemplate {...defaultProps} />)
      
      const button = screen.getByRole('button')
      fireEvent.click(button)
      
      await waitFor(() => {
        expect(screen.getByText(/error/i)).toBeInTheDocument()
      })
    })

    it('updates internal state correctly', async () => {
      const user = userEvent.setup()
      render(<ComponentTemplate {...defaultProps} />)
      
      const input = screen.getByRole('textbox')
      await user.clear(input)
      await user.type(input, 'new value')
      
      expect(input).toHaveValue('new value')
    })
  })

  describe('Props and Callbacks', () => {
    it('calls onUpdate with correct parameters', async () => {
      const mockOnUpdate = vi.fn()
      render(<ComponentTemplate {...defaultProps} onUpdate={mockOnUpdate} />)
      
      const button = screen.getByRole('button')
      fireEvent.click(button)
      
      expect(mockOnUpdate).toHaveBeenCalledWith({
        type: 'update',
        data: expect.any(String),
        timestamp: expect.any(Date),
      })
    })

    it('handles prop changes correctly', () => {
      const { rerender } = render(<ComponentTemplate {...defaultProps} />)
      
      expect(screen.getByText('test data')).toBeInTheDocument()
      
      rerender(<ComponentTemplate {...defaultProps} data="updated data" />)
      
      expect(screen.getByText('updated data')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has correct ARIA attributes', () => {
      render(<ComponentTemplate {...defaultProps} />)
      
      const button = screen.getByRole('button')
      expect(button).toHaveAttribute('aria-label')
      expect(button).not.toHaveAttribute('aria-disabled', 'true')
    })

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup()
      render(<ComponentTemplate {...defaultProps} />)
      
      await user.tab()
      expect(screen.getByRole('button')).toHaveFocus()
      
      await user.keyboard('{space}')
      // Verify space key triggered button action
    })

    it('announces loading states to screen readers', async () => {
      render(<ComponentTemplate {...defaultProps} />)
      
      const button = screen.getByRole('button')
      fireEvent.click(button)
      
      await waitFor(() => {
        expect(screen.getByRole('status')).toHaveTextContent('Loading...')
      })
    })
  })

  describe('Performance', () => {
    it('does not re-render unnecessarily', () => {
      const renderSpy = vi.fn()
      const TestComponent = (props: ComponentTemplateProps) => {
        renderSpy()
        return <ComponentTemplate {...props} />
      }
      
      const { rerender } = render(<TestComponent {...defaultProps} />)
      
      // Initial render
      expect(renderSpy).toHaveBeenCalledTimes(1)
      
      // Re-render with same props should not cause re-render
      rerender(<TestComponent {...defaultProps} />)
      expect(renderSpy).toHaveBeenCalledTimes(1)
      
      // Re-render with different props should cause re-render
      rerender(<TestComponent {...defaultProps} data="new data" />)
      expect(renderSpy).toHaveBeenCalledTimes(2)
    })
  })

  describe('Integration', () => {
    it('integrates with API service correctly', async () => {
      const mockAPI = vi.mocked(AtomicAgentAPI)
      render(<ComponentTemplate {...defaultProps} />)
      
      const button = screen.getByRole('button')
      fireEvent.click(button)
      
      await waitFor(() => {
        expect(mockAPI).toHaveBeenCalled()
      })
    })

    it('handles API response correctly', async () => {
      render(<ComponentTemplate {...defaultProps} />)
      
      const button = screen.getByRole('button')
      fireEvent.click(button)
      
      await waitFor(() => {
        expect(screen.getByText('Mocked research result')).toBeInTheDocument()
      })
    })
  })
})
```

### E2E Testing with Playwright

#### `frontend/tests/e2e/research-workflow.spec.ts`
**Purpose**: End-to-end testing of complete research workflows  
**Template**:
```typescript
import { test, expect, type Page } from '@playwright/test'

class ResearchPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/')
  }

  async searchFor(question: string) {
    await this.page.getByPlaceholder('Ask a research question...').fill(question)
    await this.page.getByRole('button', { name: 'Start Research' }).click()
  }

  async waitForResults() {
    await this.page.waitForSelector('[data-testid="research-results"]', { 
      timeout: 30000 
    })
  }

  async getAnswer() {
    return await this.page.getByTestId('final-answer').textContent()
  }

  async getSources() {
    const sources = await this.page.getByTestId('source-item').all()
    return sources.length
  }

  async setEffortLevel(level: 'low' | 'medium' | 'high') {
    await this.page.getByTestId('effort-select').click()
    await this.page.getByRole('option', { name: level }).click()
  }
}

test.describe('Research Workflow', () => {
  let researchPage: ResearchPage

  test.beforeEach(async ({ page }) => {
    researchPage = new ResearchPage(page)
    await researchPage.goto()
  })

  test('should complete basic research workflow', async ({ page }) => {
    await researchPage.searchFor('What is artificial intelligence?')
    
    // Check loading state
    await expect(page.getByText('Generating queries...')).toBeVisible()
    
    // Wait for results
    await researchPage.waitForResults()
    
    // Verify results
    const answer = await researchPage.getAnswer()
    expect(answer).toBeTruthy()
    expect(answer!.length).toBeGreaterThan(100)
    
    const sourceCount = await researchPage.getSources()
    expect(sourceCount).toBeGreaterThan(0)
  })

  test('should handle different effort levels', async ({ page }) => {
    await researchPage.setEffortLevel('high')
    await researchPage.searchFor('How does machine learning work?')
    
    await researchPage.waitForResults()
    
    // High effort should generate more sources
    const sourceCount = await researchPage.getSources()
    expect(sourceCount).toBeGreaterThanOrEqual(3)
  })

  test('should display research progress', async ({ page }) => {
    await researchPage.searchFor('Explain neural networks')
    
    // Check progress indicators
    await expect(page.getByText('Generating queries...')).toBeVisible()
    await expect(page.getByText('Searching web...')).toBeVisible()
    await expect(page.getByText('Analyzing results...')).toBeVisible()
    
    await researchPage.waitForResults()
  })

  test('should handle errors gracefully', async ({ page }) => {
    // Mock network failure
    await page.route('**/research', route => {
      route.abort('failed')
    })
    
    await researchPage.searchFor('Test error handling')
    
    await expect(page.getByText(/error/i)).toBeVisible()
    await expect(page.getByText(/try again/i)).toBeVisible()
  })

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    
    await researchPage.searchFor('Mobile test query')
    
    // Verify mobile layout
    const container = page.getByTestId('app-container')
    await expect(container).toHaveCSS('flex-direction', 'column')
    
    await researchPage.waitForResults()
    
    // Results should be visible and properly formatted on mobile
    const answer = page.getByTestId('final-answer')
    await expect(answer).toBeVisible()
  })
})

test.describe('User Interface', () => {
  test('should have proper navigation', async ({ page }) => {
    await page.goto('/')
    
    // Check main navigation elements
    await expect(page.getByRole('heading', { name: /research/i })).toBeVisible()
    await expect(page.getByPlaceholder('Ask a research question...')).toBeVisible()
  })

  test('should support keyboard navigation', async ({ page }) => {
    await page.goto('/')
    
    // Tab through interface
    await page.keyboard.press('Tab')
    await expect(page.getByPlaceholder('Ask a research question...')).toBeFocused()
    
    await page.keyboard.press('Tab')
    await expect(page.getByRole('button', { name: 'Start Research' })).toBeFocused()
  })

  test('should persist state across page reloads', async ({ page }) => {
    await page.goto('/')
    
    const question = 'Test persistence question'
    await page.getByPlaceholder('Ask a research question...').fill(question)
    
    await page.reload()
    
    // Question should be preserved
    const input = page.getByPlaceholder('Ask a research question...')
    await expect(input).toHaveValue(question)
  })
})
```

### Performance Testing

#### `backend/tests/test_performance.py`
**Purpose**: Performance testing for backend components  
**Template**:
```python
"""Performance tests for backend components."""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import AsyncMock, Mock, patch

from agent.orchestrator import ResearchOrchestrator
from agent.state import ResearchRequest


class TestPerformanceRequirements:
    """Test performance requirements and benchmarks."""
    
    @pytest.mark.asyncio
    async def test_single_request_performance(self, test_config):
        """Test single research request performance."""
        orchestrator = ResearchOrchestrator(test_config)
        request = ResearchRequest(
            question="Performance test question",
            initial_search_query_count=3,
            max_research_loops=2
        )
        
        # Mock all external dependencies for consistent timing
        with patch.object(orchestrator, 'query_agent') as mock_query, \
             patch.object(orchestrator, 'search_agent') as mock_search, \
             patch.object(orchestrator, 'finalization_agent') as mock_final:
            
            mock_query.run.return_value = Mock(search_queries=["q1", "q2", "q3"])
            mock_search.run.return_value = Mock(processed_sources=[])
            mock_final.run.return_value = Mock(final_answer="Fast result")
            
            start_time = time.time()
            result = await orchestrator.run_research_async(request)
            execution_time = time.time() - start_time
            
            # Performance requirements
            assert execution_time < 2.0  # Should complete within 2 seconds when mocked
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_request_performance(self, test_config):
        """Test concurrent request handling."""
        orchestrator = ResearchOrchestrator(test_config)
        
        # Create multiple requests
        requests = [
            ResearchRequest(
                question=f"Concurrent test question {i}",
                initial_search_query_count=2,
                max_research_loops=1
            )
            for i in range(5)
        ]
        
        with patch.object(orchestrator, 'query_agent') as mock_query, \
             patch.object(orchestrator, 'search_agent') as mock_search, \
             patch.object(orchestrator, 'finalization_agent') as mock_final:
            
            mock_query.run.return_value = Mock(search_queries=["q1", "q2"])
            mock_search.run.return_value = Mock(processed_sources=[])
            mock_final.run.return_value = Mock(final_answer="Concurrent result")
            
            start_time = time.time()
            
            # Execute requests concurrently
            tasks = [orchestrator.run_research_async(req) for req in requests]
            results = await asyncio.gather(*tasks)
            
            execution_time = time.time() - start_time
            
            # Should handle concurrent requests efficiently
            assert len(results) == 5
            assert all(r is not None for r in results)
            assert execution_time < 5.0  # Should complete within 5 seconds
    
    def test_memory_usage_stability(self, test_config):
        """Test memory usage remains stable under load."""
        import psutil
        import gc
        
        orchestrator = ResearchOrchestrator(test_config)
        process = psutil.Process()
        
        # Measure baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss
        
        # Perform multiple operations
        with patch.object(orchestrator, 'query_agent') as mock_query:
            mock_query.run.return_value = Mock(search_queries=["test"])
            
            for _ in range(100):
                # Simulate agent operations
                agent = orchestrator.query_agent
                result = agent.run(Mock(research_topic="test", query_count=1))
                del result
        
        # Force garbage collection
        gc.collect()
        final_memory = process.memory_info().rss
        memory_increase = final_memory - baseline_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024
    
    @pytest.mark.asyncio
    async def test_search_parallelization_performance(self, test_config):
        """Test search parallelization performance."""
        orchestrator = ResearchOrchestrator(test_config)
        queries = [f"query_{i}" for i in range(10)]
        
        # Mock search agent with delay simulation
        async def mock_search_with_delay(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate API delay
            return Mock(processed_sources=[])
        
        with patch.object(orchestrator, 'search_agent') as mock_search:
            mock_search.run = AsyncMock(side_effect=mock_search_with_delay)
            
            start_time = time.time()
            results = await orchestrator._parallel_web_search(queries)
            execution_time = time.time() - start_time
            
            # Parallel execution should be much faster than sequential
            assert len(results) == 10
            assert execution_time < 0.5  # Should complete much faster than 10 * 0.1 = 1 second
    
    def test_thread_pool_efficiency(self, test_config):
        """Test thread pool configuration and efficiency."""
        orchestrator = ResearchOrchestrator(test_config)
        
        # Verify thread pool is configured optimally
        assert orchestrator._thread_pool is not None
        assert orchestrator._thread_pool._max_workers >= 4
        assert orchestrator._thread_pool._max_workers <= 10
        
        # Test thread pool can handle concurrent tasks
        def cpu_intensive_task(n):
            return sum(i * i for i in range(n))
        
        start_time = time.time()
        futures = []
        
        for i in range(8):
            future = orchestrator._thread_pool.submit(cpu_intensive_task, 10000)
            futures.append(future)
        
        results = [f.result() for f in futures]
        execution_time = time.time() - start_time
        
        assert len(results) == 8
        assert all(isinstance(r, int) for r in results)
        # Should complete efficiently with thread pool
        assert execution_time < 2.0


class TestLoadTesting:
    """Load testing for the application."""
    
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_sustained_load(self, test_config):
        """Test sustained load handling."""
        orchestrator = ResearchOrchestrator(test_config)
        
        # Mock responses for consistent testing
        with patch.object(orchestrator, 'query_agent') as mock_query, \
             patch.object(orchestrator, 'finalization_agent') as mock_final:
            
            mock_query.run.return_value = Mock(search_queries=["test"])
            mock_final.run.return_value = Mock(final_answer="Load test result")
            
            request_count = 50
            batch_size = 10
            
            total_time = 0
            successful_requests = 0
            
            # Execute in batches to simulate realistic load
            for batch in range(0, request_count, batch_size):
                batch_requests = [
                    ResearchRequest(
                        question=f"Load test question {i}",
                        initial_search_query_count=1,
                        max_research_loops=1
                    )
                    for i in range(batch, min(batch + batch_size, request_count))
                ]
                
                start_time = time.time()
                try:
                    tasks = [orchestrator.run_research_async(req) for req in batch_requests]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Count successful requests
                    successful_requests += sum(1 for r in results if not isinstance(r, Exception))
                    
                except Exception as e:
                    pytest.fail(f"Load test failed: {e}")
                
                batch_time = time.time() - start_time
                total_time += batch_time
                
                # Small delay between batches
                await asyncio.sleep(0.1)
            
            # Performance assertions
            average_time_per_request = total_time / request_count
            success_rate = successful_requests / request_count
            
            assert success_rate >= 0.95  # At least 95% success rate
            assert average_time_per_request < 1.0  # Average under 1 second per request
```

This comprehensive testing implementation guide provides complete patterns and templates for testing every aspect of the AI research application, ensuring reliability, performance, and maintainability at all levels.