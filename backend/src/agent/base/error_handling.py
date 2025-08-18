"""
Standardized error handling patterns for research agents.
"""

import asyncio
import functools
from typing import Any, Callable, TypeVar, Optional, Union
from enum import Enum
import httpx


class ErrorType(Enum):
    """Classification of different error types."""
    NETWORK_ERROR = "network_error"
    API_ERROR = "api_error"
    CONFIGURATION_ERROR = "configuration_error"
    DATA_CORRUPTION_ERROR = "data_corruption_error"
    TIMEOUT_ERROR = "timeout_error"
    AUTHENTICATION_ERROR = "authentication_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    UNKNOWN_ERROR = "unknown_error"


class AgentError(Exception):
    """Base exception for agent-specific errors."""
    
    def __init__(self, message: str, error_type: ErrorType, original_error: Optional[Exception] = None):
        self.message = message
        self.error_type = error_type
        self.original_error = original_error
        super().__init__(message)


class NetworkError(AgentError):
    """Raised for network-related issues."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.NETWORK_ERROR, original_error)


class APIError(AgentError):
    """Raised for API-related issues."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.API_ERROR, original_error)


class ConfigurationError(AgentError):
    """Raised for configuration-related issues."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message, ErrorType.CONFIGURATION_ERROR, original_error)


F = TypeVar('F', bound=Callable[..., Any])


def classify_error(error: Exception) -> ErrorType:
    """
    Classify an error into a specific error type.
    
    Args:
        error: The exception to classify
        
    Returns:
        The appropriate ErrorType
    """
    if isinstance(error, (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError)):
        return ErrorType.NETWORK_ERROR
    elif isinstance(error, (httpx.HTTPStatusError, httpx.RequestError)):
        return ErrorType.API_ERROR
    elif isinstance(error, (asyncio.TimeoutError, TimeoutError)):
        return ErrorType.TIMEOUT_ERROR
    elif isinstance(error, (KeyError, AttributeError)) and "api_key" in str(error).lower():
        return ErrorType.AUTHENTICATION_ERROR
    elif isinstance(error, ValueError) and "configuration" in str(error).lower():
        return ErrorType.CONFIGURATION_ERROR
    elif isinstance(error, (TypeError, AttributeError)):
        return ErrorType.DATA_CORRUPTION_ERROR
    else:
        return ErrorType.UNKNOWN_ERROR


def handle_agent_errors(fallback_value: Any = None, context: str = "operation"):
    """
    Decorator for handling agent errors with consistent logging and fallback behavior.
    
    Args:
        fallback_value: Value to return if error occurs
        context: Context description for error logging
        
    Returns:
        The decorated function with error handling
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_type = classify_error(e)
                error_message = f"❌ Error in {context}: {error_type.value} - {str(e)}"
                print(error_message)
                
                if fallback_value is not None:
                    print(f"🔄 Using fallback value for {context}")
                    return fallback_value
                else:
                    print(f"⚠️ No fallback available for {context}")
                    raise AgentError(
                        f"Failed {context}: {str(e)}",
                        error_type,
                        e
                    )
        return wrapper
    return decorator


def handle_async_agent_errors(fallback_value: Any = None, context: str = "async operation"):
    """
    Decorator for handling async agent errors.
    
    Args:
        fallback_value: Value to return if error occurs
        context: Context description for error logging
        
    Returns:
        The decorated async function with error handling
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_type = classify_error(e)
                error_message = f"❌ Async error in {context}: {error_type.value} - {str(e)}"
                print(error_message)
                
                if fallback_value is not None:
                    print(f"🔄 Using fallback value for {context}")
                    return fallback_value
                else:
                    print(f"⚠️ No fallback available for {context}")
                    raise AgentError(
                        f"Failed async {context}: {str(e)}",
                        error_type,
                        e
                    )
        return wrapper
    return decorator


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retriable_errors: Optional[list[ErrorType]] = None
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retriable_errors = retriable_errors or [
            ErrorType.NETWORK_ERROR,
            ErrorType.TIMEOUT_ERROR,
            ErrorType.RATE_LIMIT_ERROR
        ]


def with_retry(retry_config: RetryConfig, context: str = "operation"):
    """
    Decorator for adding retry logic to functions.
    
    Args:
        retry_config: Configuration for retry behavior
        context: Context description for logging
        
    Returns:
        The decorated function with retry logic
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(retry_config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    error_type = classify_error(e)
                    
                    if error_type not in retry_config.retriable_errors:
                        print(f"❌ Non-retriable error in {context}: {error_type.value}")
                        raise
                    
                    if attempt < retry_config.max_attempts - 1:
                        delay = min(
                            retry_config.base_delay * (retry_config.exponential_base ** attempt),
                            retry_config.max_delay
                        )
                        print(f"🔄 Retrying {context} in {delay:.1f}s (attempt {attempt + 1}/{retry_config.max_attempts})")
                        await asyncio.sleep(delay)
                    else:
                        print(f"❌ All retry attempts failed for {context}")
            
            # If we get here, all retries failed
            if last_error:
                raise AgentError(
                    f"Failed {context} after {retry_config.max_attempts} attempts",
                    classify_error(last_error),
                    last_error
                )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(retry_config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    error_type = classify_error(e)
                    
                    if error_type not in retry_config.retriable_errors:
                        print(f"❌ Non-retriable error in {context}: {error_type.value}")
                        raise
                    
                    if attempt < retry_config.max_attempts - 1:
                        delay = min(
                            retry_config.base_delay * (retry_config.exponential_base ** attempt),
                            retry_config.max_delay
                        )
                        print(f"🔄 Retrying {context} in {delay:.1f}s (attempt {attempt + 1}/{retry_config.max_attempts})")
                        import time
                        time.sleep(delay)
                    else:
                        print(f"❌ All retry attempts failed for {context}")
            
            # If we get here, all retries failed
            if last_error:
                raise AgentError(
                    f"Failed {context} after {retry_config.max_attempts} attempts",
                    classify_error(last_error),
                    last_error
                )
        
        # Return the appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def safe_format_template(template: str, **kwargs) -> str:
    """
    Safely format a template string with error handling.
    
    Args:
        template: The template string to format
        **kwargs: Variables to substitute
        
    Returns:
        The formatted string or a safe fallback
    """
    try:
        return template.format(**kwargs)
    except (KeyError, ValueError, TypeError) as e:
        print(f"⚠️ Template formatting error: {e}")
        # Return a safe fallback that includes the available information
        safe_info = {k: str(v) for k, v in kwargs.items() if isinstance(v, (str, int, float, bool))}
        return f"Template formatting failed. Available info: {safe_info}"


def validate_response_structure(response: Any, expected_attributes: list[str], context: str = "response") -> bool:
    """
    Validate that a response object has the expected structure.
    
    Args:
        response: The response object to validate
        expected_attributes: List of attribute names that should exist
        context: Context for error messages
        
    Returns:
        True if valid, False otherwise
    """
    if response is None:
        print(f"⚠️ {context} is None")
        return False
    
    missing_attributes = []
    for attr in expected_attributes:
        if not hasattr(response, attr):
            missing_attributes.append(attr)
    
    if missing_attributes:
        print(f"⚠️ {context} missing attributes: {missing_attributes}")
        return False
    
    return True


def safe_getattr_chain(obj: Any, attr_path: str, default: Any = None) -> Any:
    """
    Safely get a nested attribute with error handling.
    
    Args:
        obj: The object to get attributes from
        attr_path: Dot-separated path of attributes (e.g., "a.b.c")
        default: Default value if attribute doesn't exist
        
    Returns:
        The attribute value or default
    """
    try:
        result = obj
        for attr in attr_path.split('.'):
            result = getattr(result, attr, None)
            if result is None:
                return default
        return result
    except (AttributeError, TypeError):
        return default