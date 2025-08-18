"""
Tests for the error handling module.
"""

import pytest
import asyncio
import httpx
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_src))

from agent.base.error_handling import (
    ErrorType,
    AgentError,
    NetworkError,
    APIError,
    ConfigurationError,
    classify_error,
    handle_agent_errors,
    handle_async_agent_errors,
    RetryConfig,
    with_retry,
    safe_format_template,
    validate_response_structure,
    safe_getattr_chain
)


class TestErrorClassification:
    """Test error classification functionality."""
    
    def test_classify_network_errors(self):
        """Test classification of network errors."""
        # HTTPx network errors
        assert classify_error(httpx.ConnectError("Connection failed")) == ErrorType.NETWORK_ERROR
        assert classify_error(httpx.TimeoutException("Timeout")) == ErrorType.NETWORK_ERROR
        assert classify_error(httpx.NetworkError("Network error")) == ErrorType.NETWORK_ERROR
    
    def test_classify_api_errors(self):
        """Test classification of API errors."""
        assert classify_error(httpx.HTTPStatusError("HTTP 500", request=MagicMock(), response=MagicMock())) == ErrorType.API_ERROR
        assert classify_error(httpx.RequestError("Request failed")) == ErrorType.API_ERROR
    
    def test_classify_timeout_errors(self):
        """Test classification of timeout errors."""
        assert classify_error(asyncio.TimeoutError()) == ErrorType.TIMEOUT_ERROR
        assert classify_error(TimeoutError()) == ErrorType.TIMEOUT_ERROR
    
    def test_classify_authentication_errors(self):
        """Test classification of authentication errors."""
        assert classify_error(KeyError("api_key")) == ErrorType.AUTHENTICATION_ERROR
        assert classify_error(AttributeError("API_KEY not found")) == ErrorType.AUTHENTICATION_ERROR
    
    def test_classify_configuration_errors(self):
        """Test classification of configuration errors."""
        assert classify_error(ValueError("Invalid configuration")) == ErrorType.CONFIGURATION_ERROR
    
    def test_classify_data_corruption_errors(self):
        """Test classification of data corruption errors."""
        assert classify_error(TypeError("Type mismatch")) == ErrorType.DATA_CORRUPTION_ERROR
        assert classify_error(AttributeError("Missing attribute")) == ErrorType.DATA_CORRUPTION_ERROR
    
    def test_classify_unknown_errors(self):
        """Test classification of unknown errors."""
        assert classify_error(RuntimeError("Unknown error")) == ErrorType.UNKNOWN_ERROR


class TestAgentErrors:
    """Test custom agent error classes."""
    
    def test_agent_error(self):
        """Test AgentError creation."""
        original = ValueError("Original error")
        error = AgentError("Test message", ErrorType.API_ERROR, original)
        
        assert error.message == "Test message"
        assert error.error_type == ErrorType.API_ERROR
        assert error.original_error == original
        assert str(error) == "Test message"
    
    def test_network_error(self):
        """Test NetworkError creation."""
        original = httpx.ConnectError("Connection failed")
        error = NetworkError("Network failed", original)
        
        assert error.error_type == ErrorType.NETWORK_ERROR
        assert error.original_error == original
    
    def test_api_error(self):
        """Test APIError creation."""
        original = httpx.HTTPStatusError("HTTP 500", request=MagicMock(), response=MagicMock())
        error = APIError("API failed", original)
        
        assert error.error_type == ErrorType.API_ERROR
        assert error.original_error == original
    
    def test_configuration_error(self):
        """Test ConfigurationError creation."""
        original = ValueError("Invalid config")
        error = ConfigurationError("Config failed", original)
        
        assert error.error_type == ErrorType.CONFIGURATION_ERROR
        assert error.original_error == original


class TestErrorHandlingDecorators:
    """Test error handling decorators."""
    
    def test_handle_agent_errors_success(self):
        """Test successful function execution with decorator."""
        @handle_agent_errors(fallback_value="fallback", context="test")
        def test_function(x, y):
            return x + y
        
        result = test_function(1, 2)
        assert result == 3
    
    def test_handle_agent_errors_with_fallback(self):
        """Test error handling with fallback value."""
        @handle_agent_errors(fallback_value="fallback", context="test")
        def test_function():
            raise ValueError("Test error")
        
        with patch('builtins.print'):  # Suppress error prints
            result = test_function()
        
        assert result == "fallback"
    
    def test_handle_agent_errors_no_fallback(self):
        """Test error handling without fallback value."""
        @handle_agent_errors(context="test")
        def test_function():
            raise ValueError("Test error")
        
        with patch('builtins.print'):  # Suppress error prints
            with pytest.raises(AgentError):
                test_function()
    
    @pytest.mark.asyncio
    async def test_handle_async_agent_errors_success(self):
        """Test successful async function execution with decorator."""
        @handle_async_agent_errors(fallback_value="fallback", context="test")
        async def test_function(x, y):
            return x + y
        
        result = await test_function(1, 2)
        assert result == 3
    
    @pytest.mark.asyncio
    async def test_handle_async_agent_errors_with_fallback(self):
        """Test async error handling with fallback value."""
        @handle_async_agent_errors(fallback_value="fallback", context="test")
        async def test_function():
            raise ValueError("Test error")
        
        with patch('builtins.print'):  # Suppress error prints
            result = await test_function()
        
        assert result == "fallback"


class TestRetryLogic:
    """Test retry functionality."""
    
    @pytest.mark.asyncio
    async def test_with_retry_success(self):
        """Test successful execution with retry decorator."""
        config = RetryConfig(max_attempts=3)
        
        @with_retry(config, "test")
        async def test_function():
            return "success"
        
        result = await test_function()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_with_retry_eventual_success(self):
        """Test retry with eventual success."""
        config = RetryConfig(max_attempts=3, base_delay=0.01)  # Fast retry for testing
        call_count = 0
        
        @with_retry(config, "test")
        async def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.TimeoutException("Timeout")
            return "success"
        
        with patch('builtins.print'):  # Suppress retry prints
            result = await test_function()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_with_retry_all_attempts_fail(self):
        """Test retry when all attempts fail."""
        config = RetryConfig(max_attempts=2, base_delay=0.01)
        
        @with_retry(config, "test")
        async def test_function():
            raise httpx.TimeoutException("Timeout")
        
        with patch('builtins.print'):  # Suppress retry prints
            with pytest.raises(AgentError):
                await test_function()
    
    @pytest.mark.asyncio
    async def test_with_retry_non_retriable_error(self):
        """Test retry with non-retriable error."""
        config = RetryConfig(max_attempts=3)
        
        @with_retry(config, "test")
        async def test_function():
            raise ValueError("Non-retriable error")  # Not in retriable errors
        
        with patch('builtins.print'):  # Suppress error prints
            with pytest.raises(ValueError):
                await test_function()


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_safe_format_template_success(self):
        """Test successful template formatting."""
        result = safe_format_template("Hello {name}", name="Alice")
        assert result == "Hello Alice"
    
    def test_safe_format_template_missing_key(self):
        """Test template formatting with missing key."""
        with patch('builtins.print'):  # Suppress error prints
            result = safe_format_template("Hello {name} {missing}", name="Alice")
        
        assert "Template formatting failed" in result
        assert "Alice" in result
    
    def test_validate_response_structure_success(self):
        """Test successful response validation."""
        class MockResponse:
            def __init__(self):
                self.attr1 = "value1"
                self.attr2 = "value2"
        
        response = MockResponse()
        result = validate_response_structure(response, ["attr1", "attr2"])
        assert result is True
    
    def test_validate_response_structure_missing_attributes(self):
        """Test response validation with missing attributes."""
        class MockResponse:
            def __init__(self):
                self.attr1 = "value1"
        
        response = MockResponse()
        
        with patch('builtins.print'):  # Suppress error prints
            result = validate_response_structure(response, ["attr1", "attr2"])
        
        assert result is False
    
    def test_validate_response_structure_none_response(self):
        """Test response validation with None response."""
        with patch('builtins.print'):  # Suppress error prints
            result = validate_response_structure(None, ["attr1"])
        
        assert result is False
    
    def test_safe_getattr_chain_success(self):
        """Test successful nested attribute access."""
        class Level2:
            def __init__(self):
                self.value = "success"
        
        class Level1:
            def __init__(self):
                self.level2 = Level2()
        
        obj = Level1()
        result = safe_getattr_chain(obj, "level2.value", "default")
        assert result == "success"
    
    def test_safe_getattr_chain_missing_attribute(self):
        """Test nested attribute access with missing attribute."""
        class Level1:
            pass
        
        obj = Level1()
        result = safe_getattr_chain(obj, "level2.value", "default")
        assert result == "default"
    
    def test_safe_getattr_chain_none_intermediate(self):
        """Test nested attribute access with None intermediate value."""
        class Level1:
            def __init__(self):
                self.level2 = None
        
        obj = Level1()
        result = safe_getattr_chain(obj, "level2.value", "default")
        assert result == "default"