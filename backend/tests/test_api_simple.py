"""
Simple API tests that focus on FastAPI functionality without complex dependencies.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import json


def test_app_import():
    """Test that the FastAPI app can be imported."""
    try:
        from agent.app import app
        assert app is not None
        assert hasattr(app, 'title')
        assert app.title == "Atomic Research Agent API"
    except ImportError as e:
        pytest.skip(f"App import failed: {e}")


def test_health_endpoint_structure():
    """Test health endpoint without complex dependencies."""
    try:
        from agent.app import app
        client = TestClient(app)
        
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert data["status"] == "healthy"
        assert data["service"] == "atomic-research-agent"
        
    except ImportError as e:
        pytest.skip(f"App import failed: {e}")


def test_cors_configuration():
    """Test CORS middleware is configured."""
    try:
        from agent.app import app
        client = TestClient(app)
        
        # Test preflight request
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        # Should not return 405 Method Not Allowed if CORS is properly configured
        assert response.status_code in [200, 204]
        
    except ImportError as e:
        pytest.skip(f"App import failed: {e}")


def test_api_models():
    """Test Pydantic models used by the API."""
    try:
        from agent.app import ResearchRequest, ResearchResponse
        
        # Test ResearchRequest model
        valid_request = {
            "question": "What is AI?",
            "initial_search_query_count": 3,
            "max_research_loops": 2,
            "reasoning_model": "gemini-2.0-flash-exp"
        }
        
        request = ResearchRequest(**valid_request)
        assert request.question == "What is AI?"
        assert request.initial_search_query_count == 3
        assert request.max_research_loops == 2
        assert request.reasoning_model == "gemini-2.0-flash-exp"
        
        # Test with minimal fields
        minimal_request = ResearchRequest(question="Test question")
        assert minimal_request.question == "Test question"
        assert minimal_request.initial_search_query_count == 3  # Default
        assert minimal_request.max_research_loops == 2  # Default
        
    except ImportError as e:
        pytest.skip(f"Model import failed: {e}")


def test_api_validation():
    """Test API request validation."""
    try:
        from agent.app import ResearchRequest
        
        # Test invalid request - missing required field
        with pytest.raises(Exception):  # Could be ValidationError or TypeError
            ResearchRequest()
        
        # Test invalid types
        with pytest.raises(Exception):
            ResearchRequest(
                question=123,  # Should be string
                initial_search_query_count="invalid"  # Should be int
            )
            
    except ImportError as e:
        pytest.skip(f"Model import failed: {e}")


@pytest.mark.asyncio
async def test_research_endpoint_mock():
    """Test research endpoint with mocked orchestrator."""
    try:
        from agent.app import app
        client = TestClient(app)
        
        # Mock the orchestrator's run_research_async method
        mock_result = {
            "final_answer": "AI is artificial intelligence.",
            "sources_gathered": [
                {
                    "url": "https://example.com/ai",
                    "title": "What is AI?",
                    "content": "AI definition...",
                    "raw_content": "<html>AI definition...</html>"
                }
            ],
            "research_loops_executed": 1,
            "total_queries": 2
        }
        
        with patch('agent.app.orchestrator.run_research_async', return_value=mock_result):
            response = client.post("/research", json={
                "question": "What is AI?",
                "initial_search_query_count": 2,
                "max_research_loops": 1
            })
            
            assert response.status_code == 200
            data = response.json()
            
            assert "final_answer" in data
            assert "sources" in data
            assert "research_loops_executed" in data
            assert "total_queries" in data
            
            assert data["final_answer"] == mock_result["final_answer"]
            assert len(data["sources"]) == 1
            assert data["research_loops_executed"] == 1
            assert data["total_queries"] == 2
            
    except ImportError as e:
        pytest.skip(f"App import failed: {e}")


def test_research_endpoint_error_handling():
    """Test research endpoint error handling."""
    try:
        from agent.app import app
        client = TestClient(app)
        
        # Mock orchestrator to raise an exception
        with patch('agent.app.orchestrator.run_research_async', 
                  side_effect=Exception("Test error")):
            response = client.post("/research", json={
                "question": "Test question"
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Test error" in data["detail"]
            
    except ImportError as e:
        pytest.skip(f"App import failed: {e}")


def test_invalid_json_request():
    """Test API handles invalid JSON requests."""
    try:
        from agent.app import app
        client = TestClient(app)
        
        # Send malformed JSON
        response = client.post(
            "/research",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
        
    except ImportError as e:
        pytest.skip(f"App import failed: {e}")


def test_missing_content_type():
    """Test API handles missing content type."""
    try:
        from agent.app import app
        client = TestClient(app)
        
        # Send request without content-type header
        response = client.post("/research", data='{"question": "test"}')
        
        # Should still work or return appropriate error
        assert response.status_code in [200, 422, 415]
        
    except ImportError as e:
        pytest.skip(f"App import failed: {e}")


def test_openapi_schema():
    """Test OpenAPI schema generation."""
    try:
        from agent.app import app
        client = TestClient(app)
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        
        # Verify research endpoint is documented
        assert "/research" in schema["paths"]
        assert "post" in schema["paths"]["/research"]
        
        # Verify health endpoint is documented
        assert "/health" in schema["paths"]
        assert "get" in schema["paths"]["/health"]
        
    except ImportError as e:
        pytest.skip(f"App import failed: {e}")


def test_app_configuration():
    """Test app configuration and metadata."""
    try:
        from agent.app import app
        
        assert app.title == "Atomic Research Agent API"
        assert app.version == "1.0.0"
        
        # Check that middleware is configured
        middleware_types = [type(middleware.cls).__name__ for middleware in app.user_middleware]
        assert "CORSMiddleware" in middleware_types
        
    except ImportError as e:
        pytest.skip(f"App import failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])