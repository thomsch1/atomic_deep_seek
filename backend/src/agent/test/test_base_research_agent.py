"""
Tests for the base research agent classes.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_src))

from agent.base.base_research_agent import BaseResearchAgent, InstructorBasedAgent
from agent.configuration import Configuration


# Concrete test implementation for abstract base class
class TestResearchAgent(BaseResearchAgent[dict, dict]):
    def _initialize_agent_config(self):
        self.agent_config = MagicMock()
    
    def run(self, input_data: dict) -> dict:
        if not self._validate_input(input_data):
            return self._create_fallback_response(input_data, "invalid input")
        return {"result": "success"}
    
    def _create_fallback_response(self, input_data: dict, error_context: str) -> dict:
        return {"result": "fallback", "error": error_context}


class TestInstructorAgent(InstructorBasedAgent[dict, dict]):
    def _initialize_agent_config(self):
        self.agent_config = MagicMock()
        self.agent_config.client = MagicMock()
    
    def run(self, input_data: dict) -> dict:
        return {"result": "success"}
    
    def _create_fallback_response(self, input_data: dict, error_context: str) -> dict:
        return {"result": "fallback", "error": error_context}


class TestBaseResearchAgent:
    """Test the BaseResearchAgent abstract class."""
    
    def test_agent_initialization(self, mock_environment, test_configuration):
        """Test base agent initialization."""
        agent = TestResearchAgent(test_configuration)
        
        assert agent.config == test_configuration
        assert agent.agent_config is not None
    
    def test_validate_input(self, mock_environment, test_configuration):
        """Test input validation."""
        agent = TestResearchAgent(test_configuration)
        
        # Valid input
        assert agent._validate_input({"test": "data"}) is True
        
        # Invalid input (None)
        assert agent._validate_input(None) is False
    
    def test_handle_error(self, mock_environment, test_configuration):
        """Test error handling."""
        agent = TestResearchAgent(test_configuration)
        
        test_error = ValueError("Test error")
        
        with patch('builtins.print') as mock_print:
            agent._handle_error(test_error, "test context")
            
            # Check that error was logged
            mock_print.assert_called()
            call_args = [str(call) for call in mock_print.call_args_list]
            assert any("TestResearchAgent error in test context" in arg for arg in call_args)
    
    def test_run_with_valid_input(self, mock_environment, test_configuration):
        """Test run with valid input."""
        agent = TestResearchAgent(test_configuration)
        
        result = agent.run({"test": "data"})
        
        assert result == {"result": "success"}
    
    def test_run_with_invalid_input(self, mock_environment, test_configuration):
        """Test run with invalid input."""
        agent = TestResearchAgent(test_configuration)
        
        result = agent.run(None)
        
        assert result == {"result": "fallback", "error": "invalid input"}


class TestInstructorBasedAgent:
    """Test the InstructorBasedAgent class."""
    
    def test_agent_initialization(self, mock_environment, test_configuration):
        """Test instructor-based agent initialization."""
        agent = TestInstructorAgent(test_configuration)
        
        assert agent.config == test_configuration
        assert agent.agent_config is not None
    
    def test_safe_llm_call_success(self, mock_environment, test_configuration):
        """Test successful LLM call."""
        agent = TestInstructorAgent(test_configuration)
        
        # Mock successful response
        mock_response = {"llm_result": "success"}
        agent.agent_config.client.chat.completions.create.return_value = mock_response
        
        result = agent._safe_llm_call("test prompt", dict, "test context")
        
        assert result == mock_response
        agent.agent_config.client.chat.completions.create.assert_called_once()
    
    def test_safe_llm_call_failure(self, mock_environment, test_configuration):
        """Test LLM call failure."""
        agent = TestInstructorAgent(test_configuration)
        
        # Mock LLM call failure
        agent.agent_config.client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch('builtins.print'):  # Suppress error prints
            result = agent._safe_llm_call("test prompt", dict, "test context")
        
        assert result is None
    
    def test_safe_llm_call_no_config(self, mock_environment, test_configuration):
        """Test LLM call with no configuration."""
        agent = TestInstructorAgent(test_configuration)
        agent.agent_config = None
        
        with patch('builtins.print'):  # Suppress error prints
            result = agent._safe_llm_call("test prompt", dict, "test context")
        
        assert result is None
    
    def test_format_prompt_safely_success(self, mock_environment, test_configuration):
        """Test successful prompt formatting."""
        agent = TestInstructorAgent(test_configuration)
        
        template = "Hello {name}, today is {date}"
        result = agent._format_prompt_safely(template, name="Alice", date="2024-01-15")
        
        assert result == "Hello Alice, today is 2024-01-15"
    
    def test_format_prompt_safely_failure(self, mock_environment, test_configuration):
        """Test prompt formatting failure."""
        agent = TestInstructorAgent(test_configuration)
        
        template = "Hello {name}, today is {missing_var}"
        
        with patch('builtins.print'):  # Suppress error prints
            result = agent._format_prompt_safely(
                template, 
                name="Alice", 
                research_topic="test topic"
            )
        
        # Should return fallback with available info
        assert "Please help with:" in result
        assert "test topic" in result