"""
Tests for http_client module.
"""

import pytest
import asyncio
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
from agent.http_client import (
    HTTPClientConfig,
    HTTPClientSingleton,
    get_http_client,
    http_client,
    cleanup_http_client,
    get_with_retry,
    post_with_retry
)


class TestHTTPClientConfig:
    """Test HTTP client configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = HTTPClientConfig()
        
        assert config.timeout == 30.0
        assert config.max_connections == 100
        assert config.max_keepalive_connections == 20
        assert config.keepalive_expiry == 5.0
        assert config.retries == 3
        assert config.retry_delay == 1.0
        assert config.verify_ssl is True
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = HTTPClientConfig(
            timeout=60.0,
            max_connections=50,
            retries=5,
            verify_ssl=False
        )
        
        assert config.timeout == 60.0
        assert config.max_connections == 50
        assert config.retries == 5
        assert config.verify_ssl is False
    
    @patch.dict('os.environ', {
        'HTTP_TIMEOUT': '45.0',
        'HTTP_MAX_CONNECTIONS': '200',
        'HTTP_RETRIES': '2',
        'HTTP_VERIFY_SSL': 'false'
    })
    def test_config_from_env(self):
        """Test configuration from environment variables."""
        config = HTTPClientConfig.from_env()
        
        assert config.timeout == 45.0
        assert config.max_connections == 200
        assert config.retries == 2
        assert config.verify_ssl is False
    
    @patch.dict('os.environ', {}, clear=True)
    def test_config_from_env_defaults(self):
        """Test configuration from environment with defaults."""
        config = HTTPClientConfig.from_env()
        
        assert config.timeout == 30.0
        assert config.max_connections == 100
        assert config.retries == 3
        assert config.verify_ssl is True


class TestHTTPClientSingleton:
    """Test HTTP client singleton functionality."""
    
    def setup_method(self):
        """Reset singleton for each test."""
        HTTPClientSingleton._instance = None
        HTTPClientSingleton._client = None
        HTTPClientSingleton._config = None
    
    @pytest.mark.asyncio
    async def test_singleton_behavior(self):
        """Test that HTTPClientSingleton maintains singleton behavior."""
        config = HTTPClientConfig()
        
        client1 = HTTPClientSingleton(config)
        client2 = HTTPClientSingleton()
        
        assert client1 is client2
    
    @patch('agent.http_client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_client_creation(self, mock_async_client):
        """Test HTTP client creation with proper configuration."""
        mock_client_instance = AsyncMock()
        mock_async_client.return_value = mock_client_instance
        
        config = HTTPClientConfig(timeout=45.0, max_connections=50)
        singleton = HTTPClientSingleton(config)
        
        client = await singleton.get_client()
        
        assert client is mock_client_instance
        mock_async_client.assert_called_once()
        
        # Verify configuration was applied
        call_args = mock_async_client.call_args
        assert call_args is not None
        assert 'limits' in call_args.kwargs
        assert 'timeout' in call_args.kwargs
        assert 'verify' in call_args.kwargs
    
    @patch('agent.http_client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_client_reuse(self, mock_async_client):
        """Test that client is reused across calls."""
        mock_client_instance = AsyncMock()
        mock_async_client.return_value = mock_client_instance
        
        singleton = HTTPClientSingleton()
        
        client1 = await singleton.get_client()
        client2 = await singleton.get_client()
        
        assert client1 is client2
        assert mock_async_client.call_count == 1
    
    @patch('agent.http_client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_client_cleanup(self, mock_async_client):
        """Test client cleanup functionality."""
        mock_client_instance = AsyncMock()
        mock_async_client.return_value = mock_client_instance
        
        singleton = HTTPClientSingleton()
        await singleton.get_client()  # Create client
        
        await singleton.close()
        
        mock_client_instance.aclose.assert_called_once()
        assert singleton._client is None


class TestHTTPClientSingletonRequests:
    """Test HTTP client singleton request methods."""
    
    def setup_method(self):
        """Reset singleton for each test."""
        HTTPClientSingleton._instance = None
        HTTPClientSingleton._client = None
        HTTPClientSingleton._config = None
    
    @patch('agent.http_client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_get_request_success(self, mock_async_client):
        """Test successful GET request."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_client.request.return_value = mock_response
        mock_async_client.return_value = mock_client
        
        singleton = HTTPClientSingleton()
        
        response = await singleton.get("https://example.com")
        
        assert response is mock_response
        mock_client.request.assert_called_once_with(
            'GET', 'https://example.com'
        )
    
    @patch('agent.http_client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_post_request_success(self, mock_async_client):
        """Test successful POST request."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_client.request.return_value = mock_response
        mock_async_client.return_value = mock_client
        
        singleton = HTTPClientSingleton()
        
        response = await singleton.post("https://example.com", json={"key": "value"})
        
        assert response is mock_response
        mock_client.request.assert_called_once_with(
            'POST', 'https://example.com', json={"key": "value"}
        )
    
    @patch('agent.http_client.httpx.AsyncClient')
    @patch('agent.http_client.asyncio.sleep')
    @pytest.mark.asyncio
    async def test_request_retry_logic(self, mock_sleep, mock_async_client):
        """Test request retry logic with exponential backoff."""
        mock_client = AsyncMock()
        mock_async_client.return_value = mock_client
        
        # First two calls fail, third succeeds
        mock_response = MagicMock()
        mock_client.request.side_effect = [
            httpx.RequestError("Connection failed"),
            httpx.RequestError("Connection failed"),
            mock_response
        ]
        
        config = HTTPClientConfig(retries=3, retry_delay=1.0)
        singleton = HTTPClientSingleton(config)
        
        response = await singleton.request_with_retry('GET', 'https://example.com')
        
        assert response is mock_response
        assert mock_client.request.call_count == 3
        
        # Check exponential backoff
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1.0)  # First retry
        mock_sleep.assert_any_call(2.0)  # Second retry
    
    @patch('agent.http_client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_request_retry_exhaustion(self, mock_async_client):
        """Test request failure after retry exhaustion."""
        mock_client = AsyncMock()
        mock_async_client.return_value = mock_client
        
        # All calls fail
        exception = httpx.RequestError("Connection failed")
        mock_client.request.side_effect = exception
        
        config = HTTPClientConfig(retries=2)
        singleton = HTTPClientSingleton(config)
        
        with pytest.raises(httpx.RequestError):
            await singleton.request_with_retry('GET', 'https://example.com')
        
        assert mock_client.request.call_count == 3  # Initial + 2 retries


class TestGlobalFunctions:
    """Test global convenience functions."""
    
    def setup_method(self):
        """Reset global state for each test."""
        HTTPClientSingleton._instance = None
        HTTPClientSingleton._client = None
        HTTPClientSingleton._config = None
        import agent.http_client
        agent.http_client._http_client_instance = None
    
    @patch('agent.http_client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_get_http_client(self, mock_async_client):
        """Test global get_http_client function."""
        mock_client_instance = AsyncMock()
        mock_async_client.return_value = mock_client_instance
        
        client = await get_http_client()
        
        assert client is mock_client_instance
    
    @patch('agent.http_client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_http_client_context_manager(self, mock_async_client):
        """Test HTTP client context manager."""
        mock_client_instance = AsyncMock()
        mock_async_client.return_value = mock_client_instance
        
        async with http_client() as client:
            assert client is mock_client_instance
    
    @patch('agent.http_client.HTTPClientSingleton')
    @pytest.mark.asyncio
    async def test_cleanup_http_client(self, mock_singleton_class):
        """Test global HTTP client cleanup."""
        mock_instance = AsyncMock()
        mock_singleton_class.return_value = mock_instance
        
        import agent.http_client
        agent.http_client._http_client_instance = mock_instance
        
        await cleanup_http_client()
        
        mock_instance.close.assert_called_once()
        assert agent.http_client._http_client_instance is None
    
    @patch('agent.http_client.HTTPClientSingleton')
    @pytest.mark.asyncio
    async def test_get_with_retry(self, mock_singleton_class):
        """Test global get_with_retry function."""
        mock_instance = AsyncMock()
        mock_response = MagicMock()
        mock_instance.get.return_value = mock_response
        mock_singleton_class.return_value = mock_instance
        
        response = await get_with_retry("https://example.com")
        
        assert response is mock_response
        mock_instance.get.assert_called_once_with("https://example.com")
    
    @patch('agent.http_client.HTTPClientSingleton')
    @pytest.mark.asyncio
    async def test_post_with_retry(self, mock_singleton_class):
        """Test global post_with_retry function."""
        mock_instance = AsyncMock()
        mock_response = MagicMock()
        mock_instance.post.return_value = mock_response
        mock_singleton_class.return_value = mock_instance
        
        response = await post_with_retry("https://example.com", json={"test": "data"})
        
        assert response is mock_response
        mock_instance.post.assert_called_once_with(
            "https://example.com", 
            json={"test": "data"}
        )


class TestAsyncContextManager:
    """Test async context manager functionality."""
    
    def setup_method(self):
        """Reset singleton for each test.""" 
        HTTPClientSingleton._instance = None
        HTTPClientSingleton._client = None
        HTTPClientSingleton._config = None
    
    @patch('agent.http_client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_context_manager_usage(self, mock_async_client):
        """Test using HTTPClientSingleton as context manager."""
        mock_client_instance = AsyncMock()
        mock_async_client.return_value = mock_client_instance
        
        singleton = HTTPClientSingleton()
        
        async with singleton as client:
            assert client is mock_client_instance
        
        # Client should not be closed after context exit (it's a singleton)
        mock_client_instance.aclose.assert_not_called()