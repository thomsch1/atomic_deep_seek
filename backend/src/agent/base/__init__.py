"""
Base classes and utilities for research agents.
"""

from .base_research_agent import BaseResearchAgent, InstructorBasedAgent
from .error_handling import (
    ErrorType,
    AgentError,
    NetworkError,
    APIError,
    ConfigurationError,
    handle_agent_errors,
    handle_async_agent_errors,
    RetryConfig,
    with_retry,
    safe_format_template,
    validate_response_structure,
    safe_getattr_chain,
    classify_error
)

__all__ = [
    'BaseResearchAgent',
    'InstructorBasedAgent',
    'ErrorType',
    'AgentError',
    'NetworkError',
    'APIError',
    'ConfigurationError',
    'handle_agent_errors',
    'handle_async_agent_errors',
    'RetryConfig',
    'with_retry',
    'safe_format_template',
    'validate_response_structure',
    'safe_getattr_chain',
    'classify_error'
]