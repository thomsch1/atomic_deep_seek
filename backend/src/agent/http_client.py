"""
HTTP client singleton with connection pooling and timeout management.
Replaces multiple httpx.AsyncClient instances with a shared, configured client.
"""

import asyncio
import httpx
from typing import Optional, Dict, Any, Union
from contextlib import asynccontextmanager
import os
from .logging_config import get_logger

logger = get_logger(__name__)


class HTTPClientConfig:
    """Configuration class for HTTP client settings."""
    
    def __init__(
        self,
        timeout: float = 30.0,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 5.0,
        retries: int = 3,
        retry_delay: float = 1.0,
        verify_ssl: bool = True
    ):
        self.timeout = timeout
        self.max_connections = max_connections
        self.max_keepalive_connections = max_keepalive_connections
        self.keepalive_expiry = keepalive_expiry
        self.retries = retries
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl
    
    @classmethod
    def from_env(cls) -> 'HTTPClientConfig':
        """Create configuration from environment variables."""
        return cls(
            timeout=float(os.getenv('HTTP_TIMEOUT', '30.0')),
            max_connections=int(os.getenv('HTTP_MAX_CONNECTIONS', '100')),
            max_keepalive_connections=int(os.getenv('HTTP_MAX_KEEPALIVE', '20')),
            keepalive_expiry=float(os.getenv('HTTP_KEEPALIVE_EXPIRY', '5.0')),
            retries=int(os.getenv('HTTP_RETRIES', '3')),
            retry_delay=float(os.getenv('HTTP_RETRY_DELAY', '1.0')),
            verify_ssl=os.getenv('HTTP_VERIFY_SSL', 'true').lower() == 'true'
        )


class HTTPClientSingleton:
    """Singleton HTTP client with connection pooling and retry logic."""
    
    _instance: Optional['HTTPClientSingleton'] = None
    _client: Optional[httpx.AsyncClient] = None
    _config: Optional[HTTPClientConfig] = None
    _lock = asyncio.Lock()
    
    def __new__(cls, config: Optional[HTTPClientConfig] = None) -> 'HTTPClientSingleton':
        if cls._instance is None:
            cls._instance = super(HTTPClientSingleton, cls).__new__(cls)
            cls._config = config or HTTPClientConfig.from_env()
        return cls._instance
    
    async def __aenter__(self) -> httpx.AsyncClient:
        return await self.get_client()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Don't close the client here - it's a singleton
        pass
    
    async def get_client(self) -> httpx.AsyncClient:
        """Get the configured HTTP client, creating it if necessary."""
        if self._client is None:
            async with self._lock:
                if self._client is None:  # Double-check locking
                    await self._create_client()
        return self._client
    
    async def _create_client(self) -> None:
        """Create the HTTP client with proper configuration."""
        limits = httpx.Limits(
            max_connections=self._config.max_connections,
            max_keepalive_connections=self._config.max_keepalive_connections,
            keepalive_expiry=self._config.keepalive_expiry
        )
        
        timeout = httpx.Timeout(self._config.timeout)
        
        self._client = httpx.AsyncClient(
            limits=limits,
            timeout=timeout,
            verify=self._config.verify_ssl,
            headers={
                'User-Agent': 'DeepSeek-Agent/1.0',
                'Accept': 'application/json, text/html, application/xml;q=0.9, */*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
        )
        
        logger.info(f"HTTP client initialized with {self._config.max_connections} max connections")
    
    async def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.info("HTTP client closed")
    
    async def request_with_retry(
        self,
        method: str,
        url: str,
        retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        **kwargs
    ) -> httpx.Response:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            retries: Number of retries (uses config default if None)
            retry_delay: Delay between retries (uses config default if None)
            **kwargs: Additional arguments passed to httpx request
            
        Returns:
            httpx.Response: The HTTP response
            
        Raises:
            httpx.RequestError: If all retries fail
        """
        if retries is None:
            retries = self._config.retries
        if retry_delay is None:
            retry_delay = self._config.retry_delay
        
        client = await self.get_client()
        last_exception = None
        
        for attempt in range(retries + 1):
            try:
                response = await client.request(method, url, **kwargs)
                
                # Log successful request
                if attempt > 0:
                    logger.info(f"Request succeeded on attempt {attempt + 1}")
                
                return response
                
            except (httpx.RequestError, httpx.TimeoutException) as e:
                last_exception = e
                
                if attempt < retries:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Request failed (attempt {attempt + 1}/{retries + 1}): {e}")
                    logger.info(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {retries + 1} attempts failed for {method} {url}")
        
        # Re-raise the last exception if all retries failed
        raise last_exception
    
    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Make GET request with retry logic."""
        return await self.request_with_retry('GET', url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> httpx.Response:
        """Make POST request with retry logic."""
        return await self.request_with_retry('POST', url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> httpx.Response:
        """Make PUT request with retry logic."""
        return await self.request_with_retry('PUT', url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """Make DELETE request with retry logic."""
        return await self.request_with_retry('DELETE', url, **kwargs)


# Global instance for easy access
_http_client_instance: Optional[HTTPClientSingleton] = None


async def get_http_client(config: Optional[HTTPClientConfig] = None) -> httpx.AsyncClient:
    """
    Get the singleton HTTP client instance.
    
    Args:
        config: Optional configuration for the client (only used on first call)
        
    Returns:
        httpx.AsyncClient: Configured HTTP client
    """
    global _http_client_instance
    
    if _http_client_instance is None:
        _http_client_instance = HTTPClientSingleton(config)
    
    return await _http_client_instance.get_client()


@asynccontextmanager
async def http_client(config: Optional[HTTPClientConfig] = None):
    """
    Async context manager for HTTP client.
    
    Usage:
        async with http_client() as client:
            response = await client.get("https://example.com")
    """
    client = await get_http_client(config)
    try:
        yield client
    finally:
        # Don't close the client here - it's a singleton
        pass


async def cleanup_http_client() -> None:
    """Cleanup the HTTP client resources."""
    global _http_client_instance
    
    if _http_client_instance is not None:
        await _http_client_instance.close()
        _http_client_instance = None


# Convenience functions that use the singleton client with retry logic
async def get_with_retry(url: str, **kwargs) -> httpx.Response:
    """Make GET request with retry logic using singleton client."""
    global _http_client_instance
    
    if _http_client_instance is None:
        _http_client_instance = HTTPClientSingleton()
    
    return await _http_client_instance.get(url, **kwargs)


async def post_with_retry(url: str, **kwargs) -> httpx.Response:
    """Make POST request with retry logic using singleton client."""
    global _http_client_instance
    
    if _http_client_instance is None:
        _http_client_instance = HTTPClientSingleton()
    
    return await _http_client_instance.post(url, **kwargs)