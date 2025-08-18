"""
Tests for the refactored ReflectionAgent.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_src))

from agent.agents.reflection_agent import ReflectionAgent
from agent.state import ReflectionInput, ReflectionOutput
from agent.configuration import Configuration


class TestReflectionAgent:
    """Test the refactored ReflectionAgent class."""
    
    def test_agent_initialization(self, mock_environment, test_configuration):
        """Test agent initialization with valid configuration."""
        with patch('agent.configuration.Configuration.create_reflection_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            agent = ReflectionAgent(test_configuration)
            
            assert agent.config == test_configuration
            assert agent.agent_config == mock_agent_config
            mock_create_config.assert_called_once()
    
    def test_run_successful_reflection(self, mock_environment, test_configuration):
        """Test successful reflection analysis."""
        with patch('agent.configuration.Configuration.create_reflection_config') as mock_create_config:
            # Setup mocks
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_response = ReflectionOutput(
                is_sufficient=False,
                knowledge_gap="Need more information about quantum applications",
                follow_up_queries=["What are practical applications of quantum computing?"]
            )
            mock_completions.create.return_value = mock_response
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_create_config.return_value = mock_agent_config
            
            # Test
            agent = ReflectionAgent(test_configuration)
            input_data = ReflectionInput(
                research_topic="quantum computing",
                summaries=["Basic quantum computing overview"],
                current_loop=1
            )
            result = agent.run(input_data)
            
            # Verify
            assert isinstance(result, ReflectionOutput)
            assert result.is_sufficient is False
            assert "quantum applications" in result.knowledge_gap
            assert len(result.follow_up_queries) == 1
            
            # Verify the client was called
            mock_completions.create.assert_called_once()
    
    def test_run_with_llm_failure(self, mock_environment, test_configuration):
        """Test reflection when LLM call fails."""
        with patch('agent.configuration.Configuration.create_reflection_config') as mock_create_config:
            # Setup mocks to fail
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.side_effect = Exception("API Error")
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_create_config.return_value = mock_agent_config
            
            # Test with existing summaries
            with patch('builtins.print'):  # Suppress error prints
                agent = ReflectionAgent(test_configuration)
                input_data = ReflectionInput(
                    research_topic="quantum computing",
                    summaries=["Some research summary"],
                    current_loop=1
                )
                result = agent.run(input_data)
            
            # Should return fallback response indicating research is sufficient
            assert isinstance(result, ReflectionOutput)
            assert result.is_sufficient is True
            assert "fallback" in result.knowledge_gap.lower()
    
    def test_run_with_invalid_input(self, mock_environment, test_configuration):
        """Test reflection with invalid input."""
        with patch('agent.configuration.Configuration.create_reflection_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            agent = ReflectionAgent(test_configuration)
            
            # Test with None input
            with patch('builtins.print'):  # Suppress error prints
                result = agent.run(None)
            
            assert isinstance(result, ReflectionOutput)
            assert result.is_sufficient is False  # No summaries available
    
    def test_fallback_response_with_summaries(self, mock_environment, test_configuration):
        """Test fallback response when summaries are available."""
        with patch('agent.configuration.Configuration.create_reflection_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            agent = ReflectionAgent(test_configuration)
            input_data = ReflectionInput(
                research_topic="test topic",
                summaries=["Summary 1", "Summary 2"],
                current_loop=1
            )
            
            result = agent._create_fallback_response(input_data, "test error")
            
            assert isinstance(result, ReflectionOutput)
            assert result.is_sufficient is True  # Has summaries
            assert "test error" in result.knowledge_gap
            assert len(result.follow_up_queries) == 0
    
    def test_fallback_response_without_summaries(self, mock_environment, test_configuration):
        """Test fallback response when no summaries are available."""
        with patch('agent.configuration.Configuration.create_reflection_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            agent = ReflectionAgent(test_configuration)
            input_data = ReflectionInput(
                research_topic="test topic",
                summaries=[],
                current_loop=1
            )
            
            result = agent._create_fallback_response(input_data, "test error")
            
            assert isinstance(result, ReflectionOutput)
            assert result.is_sufficient is False  # No summaries
            assert "test error" in result.knowledge_gap
            assert len(result.follow_up_queries) == 3  # Should suggest basic queries
            assert "test topic" in result.follow_up_queries[0]
    
    def test_validate_input(self, mock_environment, test_configuration):
        """Test input validation."""
        with patch('agent.configuration.Configuration.create_reflection_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            agent = ReflectionAgent(test_configuration)
            
            # Valid input
            valid_input = ReflectionInput(
                research_topic="test",
                summaries=["summary"],
                current_loop=1
            )
            assert agent._validate_input(valid_input) is True
            
            # Invalid input (None)
            assert agent._validate_input(None) is False