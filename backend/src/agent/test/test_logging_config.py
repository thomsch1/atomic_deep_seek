"""
Tests for logging_config module.
"""

import pytest
import logging
import json
from unittest.mock import patch, MagicMock
from agent.logging_config import (
    configure_logging,
    get_logger,
    set_correlation_id,
    get_correlation_id,
    AgentLogger,
    CorrelationIDFormatter,
    StructuredFormatter,
    correlation_id
)


class TestLoggingConfiguration:
    """Test logging configuration functionality."""
    
    def test_configure_logging_default(self):
        """Test default logging configuration."""
        configure_logging()
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) == 1
        assert isinstance(root_logger.handlers[0], logging.StreamHandler)
    
    def test_configure_logging_with_level(self):
        """Test logging configuration with custom level."""
        configure_logging(level="DEBUG")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
    
    def test_configure_logging_structured(self):
        """Test structured logging configuration."""
        configure_logging(use_structured=True)
        
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        assert isinstance(handler.formatter, StructuredFormatter)
    
    def test_configure_logging_with_correlation(self):
        """Test logging configuration with correlation ID."""
        configure_logging(include_correlation=True)
        
        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        assert isinstance(handler.formatter, CorrelationIDFormatter)


class TestCorrelationID:
    """Test correlation ID functionality."""
    
    def test_set_and_get_correlation_id(self):
        """Test setting and getting correlation ID."""
        test_id = "test123"
        result = set_correlation_id(test_id)
        
        assert result == test_id
        assert get_correlation_id() == test_id
    
    def test_set_correlation_id_auto_generate(self):
        """Test auto-generating correlation ID."""
        result = set_correlation_id()
        
        assert result is not None
        assert len(result) == 8  # Short UUID
        assert get_correlation_id() == result
    
    def test_correlation_id_context_isolation(self):
        """Test that correlation IDs are isolated per context."""
        # This test would require async context testing
        # For now, just test basic functionality
        set_correlation_id("ctx1")
        assert get_correlation_id() == "ctx1"


class TestCorrelationIDFormatter:
    """Test correlation ID formatter."""
    
    def test_formatter_includes_correlation_id(self):
        """Test that formatter includes correlation ID in output."""
        formatter = CorrelationIDFormatter(
            fmt='%(correlation_id)s: %(message)s'
        )
        
        set_correlation_id("test123")
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        assert "test123: Test message" in formatted
    
    def test_formatter_handles_no_correlation_id(self):
        """Test formatter handles missing correlation ID."""
        formatter = CorrelationIDFormatter(
            fmt='%(correlation_id)s: %(message)s'
        )
        
        # Clear correlation ID
        correlation_id.set(None)
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        assert "N/A: Test message" in formatted


class TestStructuredFormatter:
    """Test structured JSON formatter."""
    
    def test_structured_formatter_json_output(self):
        """Test that structured formatter produces valid JSON."""
        formatter = StructuredFormatter()
        
        set_correlation_id("test123")
        
        record = logging.LogRecord(
            name="test.module",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.module = "test_module"
        record.funcName = "test_function"
        
        formatted = formatter.format(record)
        
        # Should be valid JSON
        parsed = json.loads(formatted)
        
        assert parsed['level'] == 'INFO'
        assert parsed['logger'] == 'test.module'
        assert parsed['message'] == 'Test message'
        assert parsed['correlation_id'] == 'test123'
        assert parsed['module'] == 'test_module'
        assert parsed['function'] == 'test_function'
        assert parsed['line'] == 42
        assert 'timestamp' in parsed
    
    def test_structured_formatter_with_exception(self):
        """Test structured formatter with exception info."""
        formatter = StructuredFormatter()
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
        
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )
        record.module = "test_module"
        record.funcName = "test_function"
        
        formatted = formatter.format(record)
        parsed = json.loads(formatted)
        
        assert 'exception' in parsed
        assert 'ValueError: Test exception' in parsed['exception']


class TestAgentLogger:
    """Test AgentLogger convenience class."""
    
    def setup_method(self):
        """Set up test logger."""
        configure_logging(level="DEBUG")
        self.agent_logger = AgentLogger("test.agent")
    
    @patch('agent.logging_config.get_logger')
    def test_agent_logger_success(self, mock_get_logger):
        """Test success logging with emoji."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        agent_logger = AgentLogger("test")
        agent_logger.info_success("Operation completed")
        
        mock_logger.info.assert_called_once_with("✅ Operation completed", extra={})
    
    @patch('agent.logging_config.get_logger')
    def test_agent_logger_fallback(self, mock_get_logger):
        """Test fallback logging with emoji."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        agent_logger = AgentLogger("test")
        agent_logger.info_fallback("Using fallback method")
        
        mock_logger.info.assert_called_once_with("🔄 Using fallback method", extra={})
    
    @patch('agent.logging_config.get_logger')
    def test_agent_logger_knowledge(self, mock_get_logger):
        """Test knowledge logging with emoji."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        agent_logger = AgentLogger("test")
        agent_logger.info_knowledge("Using knowledge base")
        
        mock_logger.info.assert_called_once_with("ℹ️ Using knowledge base", extra={})
    
    @patch('agent.logging_config.get_logger')
    def test_agent_logger_error_with_fallback(self, mock_get_logger):
        """Test error with fallback logging."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        agent_logger = AgentLogger("test")
        agent_logger.error_with_fallback("Primary failed", "Using backup")
        
        assert mock_logger.error.call_count == 1
        assert mock_logger.info.call_count == 1
        mock_logger.error.assert_called_with("❌ Primary failed", extra={})
        mock_logger.info.assert_called_with("🔄 Using backup", extra={})
    
    @patch('agent.logging_config.get_logger')
    def test_agent_logger_warning_skip(self, mock_get_logger):
        """Test warning skip logging with emoji."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        agent_logger = AgentLogger("test")
        agent_logger.warning_skip("Skipping invalid item")
        
        mock_logger.warning.assert_called_once_with("⚠️ Skipping invalid item", extra={})


class TestGetLogger:
    """Test logger retrieval."""
    
    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a proper logger instance."""
        logger = get_logger("test.module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"
    
    def test_get_logger_same_name_same_instance(self):
        """Test that same logger name returns same instance."""
        logger1 = get_logger("test.module")
        logger2 = get_logger("test.module")
        
        assert logger1 is logger2