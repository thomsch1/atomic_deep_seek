"""
Comprehensive test suite for FastAPI endpoints.
Tests API functionality, request/response validation, error handling, and CORS.
"""

import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any
from fastapi.testclient import TestClient

from agent.app import app, ResearchRequest, ResearchResponse
from agent.orchestrator import ResearchOrchestrator
from agent.state import Source


class TestResearchAPI:
    """Test suite for research API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    async def async_client(self):
        """Create async test client."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    def mock_research_result(self):
        """Mock research result."""
        return {
            'final_answer': 'Electric vehicles significantly reduce carbon emissions compared to gasoline cars, with a 60-70% reduction in lifetime emissions when powered by clean electricity.',
            'sources_gathered': [
                {
                    'url': 'https://example.com/ev-emissions',
                    'title': 'EV Carbon Footprint Analysis',
                    'content': 'Electric vehicles produce significantly lower emissions...',
                    'raw_content': '<html>Electric vehicles produce...</html>'
                },
                {
                    'url': 'https://example.com/lifecycle-assessment', 
                    'title': 'EV Lifecycle Environmental Impact',
                    'content': 'Manufacturing and battery production have environmental costs...',
                    'raw_content': '<html>Manufacturing and battery...</html>'
                }
            ],
            'research_loops_executed': 2,
            'total_queries': 4
        }
    
    @pytest.fixture
    def valid_research_request(self):
        """Valid research request payload."""
        return {
            "question": "What are the environmental impacts of electric vehicles?",
            "initial_search_query_count": 3,
            "max_research_loops": 2,
            "reasoning_model": "gemini-2.0-flash-exp"
        }
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "atomic-research-agent"
    
    @pytest.mark.asyncio
    async def test_research_endpoint_success(self, async_client, valid_research_request, mock_research_result):
        """Test successful research request."""
        with patch('agent.app.orchestrator.run_research_async', return_value=mock_research_result):
            response = await async_client.post("/research", json=valid_research_request)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure matches ResearchResponse model
            assert "final_answer" in data
            assert "sources" in data
            assert "research_loops_executed" in data
            assert "total_queries" in data
            
            # Verify content
            assert data["final_answer"] == mock_research_result["final_answer"]
            assert len(data["sources"]) == 2
            assert data["research_loops_executed"] == 2
            assert data["total_queries"] == 4
    
    @pytest.mark.asyncio
    async def test_research_endpoint_minimal_request(self, async_client, mock_research_result):
        """Test research endpoint with minimal required fields."""
        minimal_request = {"question": "What is renewable energy?"}
        
        with patch('agent.app.orchestrator.run_research_async', return_value=mock_research_result):
            response = await async_client.post("/research", json=minimal_request)
            
            assert response.status_code == 200
            data = response.json()
            assert "final_answer" in data
    
    @pytest.mark.asyncio
    async def test_research_endpoint_validation_error(self, async_client):
        """Test research endpoint with invalid request."""
        # Missing required 'question' field
        invalid_request = {
            "initial_search_query_count": 3,
            "max_research_loops": 2
        }
        
        response = await async_client.post("/research", json=invalid_request)
        
        assert response.status_code == 422  # Validation error
        error_data = response.json()
        assert "detail" in error_data
    
    @pytest.mark.asyncio
    async def test_research_endpoint_empty_question(self, async_client):
        """Test research endpoint with empty question."""
        empty_request = {"question": ""}
        
        # Should still process, but orchestrator might handle empty question
        with patch('agent.app.orchestrator.run_research_async', side_effect=ValueError("Empty question")):
            response = await async_client.post("/research", json=empty_request)
            
            assert response.status_code == 500
            error_data = response.json()
            assert "detail" in error_data
    
    @pytest.mark.asyncio
    async def test_research_endpoint_orchestrator_error(self, async_client, valid_research_request):
        """Test research endpoint when orchestrator raises an error."""
        with patch('agent.app.orchestrator.run_research_async', 
                  side_effect=Exception("Research failed")):
            response = await async_client.post("/research", json=valid_request)
            
            assert response.status_code == 500
            error_data = response.json()
            assert error_data["detail"] == "Research failed"
    
    @pytest.mark.asyncio
    async def test_research_endpoint_parameter_validation(self, async_client, mock_research_result):
        """Test parameter validation in research endpoint."""
        test_cases = [
            # Valid parameters
            {
                "question": "Test question",
                "initial_search_query_count": 5,
                "max_research_loops": 3,
                "reasoning_model": "gemini-2.5-pro"
            },
            # Zero values (should be handled gracefully)
            {
                "question": "Test question",
                "initial_search_query_count": 0,
                "max_research_loops": 0
            },
            # Negative values (should be validated by orchestrator)
            {
                "question": "Test question", 
                "initial_search_query_count": -1,
                "max_research_loops": -1
            }
        ]
        
        with patch('agent.app.orchestrator.run_research_async', return_value=mock_research_result):
            for test_request in test_cases:
                response = await async_client.post("/research", json=test_request)
                
                # Should either succeed or fail gracefully
                assert response.status_code in [200, 422, 500]
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        # Preflight request
        response = client.options(
            "/research",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # Should have CORS headers
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert "access-control-allow-methods" in headers
        assert "access-control-allow-headers" in headers
    
    def test_content_type_validation(self, client):
        """Test API validates content type."""
        # Send request with wrong content type
        response = client.post(
            "/research",
            data="invalid data",  # Not JSON
            headers={"Content-Type": "text/plain"}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_concurrent_research_requests(self, async_client, mock_research_result):
        """Test handling multiple concurrent research requests."""
        request_payload = {
            "question": "What is artificial intelligence?",
            "initial_search_query_count": 2,
            "max_research_loops": 1
        }
        
        with patch('agent.app.orchestrator.run_research_async', return_value=mock_research_result):
            # Send 5 concurrent requests
            tasks = []
            for i in range(5):
                task = async_client.post("/research", json=request_payload)
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            
            # All should succeed
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert "final_answer" in data
    
    def test_large_request_payload(self, client, mock_research_result):
        """Test handling of large request payloads."""
        large_question = "What is the impact of climate change? " * 1000  # Very long question
        
        large_request = {
            "question": large_question,
            "initial_search_query_count": 3
        }
        
        with patch('agent.app.orchestrator.run_research_async', return_value=mock_research_result):
            response = client.post("/research", json=large_request)
            
            # Should handle large payloads (up to server limits)
            assert response.status_code in [200, 413]  # OK or Payload Too Large


class TestAPIModels:
    """Test Pydantic models used by the API."""
    
    def test_research_request_model(self):
        """Test ResearchRequest model validation."""
        # Valid request
        valid_data = {
            "question": "What is quantum computing?",
            "initial_search_query_count": 3,
            "max_research_loops": 2,
            "reasoning_model": "gemini-2.0-flash-exp"
        }
        request = ResearchRequest(**valid_data)
        
        assert request.question == valid_data["question"]
        assert request.initial_search_query_count == 3
        assert request.max_research_loops == 2
        assert request.reasoning_model == valid_data["reasoning_model"]
    
    def test_research_request_defaults(self):
        """Test ResearchRequest model default values."""
        minimal_data = {"question": "Test question"}
        request = ResearchRequest(**minimal_data)
        
        assert request.question == "Test question"
        assert request.initial_search_query_count == 3  # Default
        assert request.max_research_loops == 2  # Default
        assert request.reasoning_model is None  # Default
    
    def test_research_response_model(self):
        """Test ResearchResponse model."""
        response_data = {
            "final_answer": "Quantum computing uses quantum mechanics principles...",
            "sources": [
                {
                    "url": "https://example.com/quantum",
                    "title": "Quantum Computing Explained",
                    "content": "Quantum computers leverage quantum mechanics...",
                    "raw_content": "<html>Quantum computers...</html>"
                }
            ],
            "research_loops_executed": 2,
            "total_queries": 4
        }
        
        response = ResearchResponse(**response_data)
        
        assert response.final_answer == response_data["final_answer"]
        assert len(response.sources) == 1
        assert response.research_loops_executed == 2
        assert response.total_queries == 4
    
    def test_research_request_validation_errors(self):
        """Test ResearchRequest validation errors."""
        # Test invalid types
        with pytest.raises((ValueError, TypeError)):
            ResearchRequest(
                question=123,  # Should be string
                initial_search_query_count="invalid",  # Should be int
                max_research_loops=None  # Should be int if provided
            )


class TestFrontendRouting:
    """Test frontend static file serving."""
    
    def test_frontend_mount_point(self, client):
        """Test frontend is mounted at /app."""
        # This will return 404 or 503 depending on whether frontend is built
        response = client.get("/app")
        
        # Should not be 404 (not found) - route should exist
        assert response.status_code in [200, 503]  # Built or not built
    
    def test_frontend_not_built_message(self, client):
        """Test message when frontend is not built."""
        # If frontend build doesn't exist, should get helpful message
        response = client.get("/app")
        
        if response.status_code == 503:
            assert "Frontend not built" in response.text
    
    def test_api_routes_not_conflicting(self, client):
        """Test API routes don't conflict with frontend routes."""
        # API routes should still work when frontend is mounted
        response = client.get("/health")
        assert response.status_code == 200
        
        # Research endpoint should be accessible
        response = client.post("/research", json={"question": "test"})
        # May fail due to orchestrator, but route should exist
        assert response.status_code != 404


class TestAPIDocumentation:
    """Test API documentation endpoints."""
    
    def test_openapi_schema(self, client):
        """Test OpenAPI schema is available."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        assert "openapi" in schema
        assert "paths" in schema
        assert "/research" in schema["paths"]
        assert "/health" in schema["paths"]
    
    def test_docs_endpoint(self, client):
        """Test Swagger UI documentation."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
    
    def test_redoc_endpoint(self, client):
        """Test ReDoc documentation."""
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "redoc" in response.text.lower() or "documentation" in response.text.lower()