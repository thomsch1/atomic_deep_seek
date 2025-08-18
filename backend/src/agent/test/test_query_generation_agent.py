"""
Tests for the refactored QueryGenerationAgent.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_src))

from agent.agents.query_generation_agent import QueryGenerationAgent
from agent.state import QueryGenerationInput, QueryGenerationOutput
from agent.configuration import Configuration


class TestQueryGenerationAgent:
    """Test the refactored QueryGenerationAgent class."""
    
    def test_agent_initialization(self, mock_environment, test_configuration):
        """Test agent initialization with valid configuration."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            agent = QueryGenerationAgent(test_configuration)
            
            assert agent.config == test_configuration
            assert agent.agent_config == mock_agent_config
            mock_create_config.assert_called_once()
    
    def test_run_successful_query_generation(self, mock_environment, test_configuration):
        """Test successful query generation."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            # Setup mocks
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_response = QueryGenerationOutput(
                queries=["What is quantum computing?", "How does quantum computing work?", "Applications of quantum computing"],
                rationale="Generated search queries for quantum computing research"
            )
            mock_completions.create.return_value = mock_response
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_create_config.return_value = mock_agent_config
            
            # Test
            agent = QueryGenerationAgent(test_configuration)
            input_data = QueryGenerationInput(
                research_topic="quantum computing",
                number_of_queries=3,
                current_date="January 15, 2024"
            )
            result = agent.run(input_data)
            
            # Verify
            assert isinstance(result, QueryGenerationOutput)
            assert len(result.queries) == 3
            assert result.rationale is not None
            assert "quantum computing" in result.queries[0].lower()
            
            # Verify the client was called
            mock_completions.create.assert_called_once()
    
    def test_run_with_llm_failure(self, mock_environment, test_configuration):
        """Test query generation when LLM call fails."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            # Setup mocks to fail
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.side_effect = Exception("API Error")
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_create_config.return_value = mock_agent_config
            
            # Test
            with patch('builtins.print'):  # Suppress error prints
                agent = QueryGenerationAgent(test_configuration)
                input_data = QueryGenerationInput(
                    research_topic="quantum computing",
                    number_of_queries=3,
                    current_date="January 15, 2024"
                )
                result = agent.run(input_data)
            
            # Should return fallback response
            assert isinstance(result, QueryGenerationOutput)
            assert len(result.queries) >= 1
            assert "quantum computing" in result.queries[0].lower()
            assert "fallback" in result.rationale.lower()
    
    def test_run_with_invalid_input(self, mock_environment, test_configuration):
        """Test query generation with invalid input."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            agent = QueryGenerationAgent(test_configuration)
            
            # Test with None input
            with patch('builtins.print'):  # Suppress error prints
                result = agent.run(None)
            
            assert isinstance(result, QueryGenerationOutput)
            assert len(result.queries) >= 1
    
    def test_fallback_response_creation(self, mock_environment, test_configuration):
        """Test fallback response creation."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            agent = QueryGenerationAgent(test_configuration)
            input_data = QueryGenerationInput(
                research_topic="test topic",
                number_of_queries=2,
                current_date="January 15, 2024"
            )
            
            result = agent._create_fallback_response(input_data, "test error")
            
            assert isinstance(result, QueryGenerationOutput)
            assert len(result.queries) == 2  # Should respect number_of_queries
            assert "test topic" in result.queries[0].lower()
            assert "test error" in result.rationale
    
    def test_validate_input(self, mock_environment, test_configuration):
        """Test input validation."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            agent = QueryGenerationAgent(test_configuration)
            
            # Valid input
            valid_input = QueryGenerationInput(
                research_topic="test",
                number_of_queries=1,
                current_date="2024"
            )
            assert agent._validate_input(valid_input) is True
            
            # Invalid input (None)
            assert agent._validate_input(None) is False