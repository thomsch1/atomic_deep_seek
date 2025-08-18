"""
Centralized logging configuration for the agent module.
Replaces print statements with structured logging and provides correlation ID support.
"""

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Optional, Dict, Any
import json


# Context variable for request correlation ID
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class CorrelationIDFormatter(logging.Formatter):
    """Custom formatter that includes correlation ID in log messages."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Add correlation ID to the log record
        record.correlation_id = correlation_id.get() or "N/A"
        return super().format(record)


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': correlation_id.get() or "N/A",
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)


def configure_logging(
    level: str = "INFO",
    use_structured: bool = False,
    include_correlation: bool = True
) -> None:
    """
    Configure logging for the agent module.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_structured: Whether to use JSON structured logging
        include_correlation: Whether to include correlation IDs
    """
    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Choose formatter
    if use_structured:
        formatter = StructuredFormatter()
    elif include_correlation:
        formatter = CorrelationIDFormatter(
            fmt='%(asctime)s [%(correlation_id)s] %(levelname)s %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)s %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels for external libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)


def set_correlation_id(corr_id: Optional[str] = None) -> str:
    """Set correlation ID for the current context."""
    if corr_id is None:
        corr_id = str(uuid.uuid4())[:8]  # Short UUID
    correlation_id.set(corr_id)
    return corr_id


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID."""
    return correlation_id.get()


class AgentLogger:
    """Convenience logger class with emoji-based status logging."""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def info_success(self, message: str, **kwargs) -> None:
        """Log success message with ✅ emoji."""
        self.logger.info(f"✅ {message}", extra=kwargs)
    
    def info_fallback(self, message: str, **kwargs) -> None:
        """Log fallback message with 🔄 emoji."""
        self.logger.info(f"🔄 {message}", extra=kwargs)
    
    def info_knowledge(self, message: str, **kwargs) -> None:
        """Log knowledge-based message with ℹ️ emoji.""" 
        self.logger.info(f"ℹ️ {message}", extra=kwargs)
    
    def error_with_fallback(self, message: str, fallback_msg: str = None, **kwargs) -> None:
        """Log error with ❌ emoji and optional fallback message."""
        self.logger.error(f"❌ {message}", extra=kwargs)
        if fallback_msg:
            self.info_fallback(fallback_msg, **kwargs)
    
    def warning_skip(self, message: str, **kwargs) -> None:
        """Log warning with ⚠️ emoji."""
        self.logger.warning(f"⚠️ {message}", extra=kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message.""" 
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, extra=kwargs)


# Initialize default logging configuration
configure_logging()