"""
Tests for the refactored FinalizationAgent.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_src))

from agent.agents.finalization_agent import FinalizationAgent
from agent.state import FinalizationInput, FinalizationOutput, Source
from agent.configuration import Configuration


class TestFinalizationAgent:
    """Test the refactored FinalizationAgent class."""
    
    def test_agent_initialization(self, mock_environment, test_configuration):
        """Test agent initialization with valid configuration."""
        with patch('agent.configuration.Configuration.create_answer_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            agent = FinalizationAgent(test_configuration)
            
            assert agent.config == test_configuration
            assert agent.agent_config == mock_agent_config
            mock_create_config.assert_called_once()
    
    def test_run_successful_finalization(self, mock_environment, test_configuration):
        """Test successful finalization."""
        with patch('agent.configuration.Configuration.create_answer_config') as mock_create_config:
            # Setup mocks
            mock_client = MagicMock()
            mock_completions = MagicMock()
            
            test_sources = [
                Source(title="Source 1", url="http://test1.com", short_url="test1", label="Source 1"),
                Source(title="Source 2", url="http://test2.com", short_url="test2", label="Source 2")
            ]
            
            mock_response = FinalizationOutput(
                final_answer="Quantum computing is a revolutionary technology that uses quantum mechanics principles...",
                used_sources=test_sources
            )
            mock_completions.create.return_value = mock_response
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_create_config.return_value = mock_agent_config
            
            # Test
            agent = FinalizationAgent(test_configuration)
            input_data = FinalizationInput(
                research_topic="quantum computing",
                summaries=["Quantum computing overview", "Quantum applications"],
                sources=test_sources,
                current_date="January 15, 2024"
            )
            result = agent.run(input_data)
            
            # Verify
            assert isinstance(result, FinalizationOutput)
            assert "quantum computing" in result.final_answer.lower()
            assert len(result.used_sources) == 2
            
            # Verify the client was called
            mock_completions.create.assert_called_once()
    
    def test_run_with_llm_failure(self, mock_environment, test_configuration):
        """Test finalization when LLM call fails."""
        with patch('agent.configuration.Configuration.create_answer_config') as mock_create_config:
            # Setup mocks to fail
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.side_effect = Exception("API Error")
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_create_config.return_value = mock_agent_config
            
            # Test with summaries
            with patch('builtins.print'):  # Suppress error prints
                agent = FinalizationAgent(test_configuration)
                input_data = FinalizationInput(
                    research_topic="quantum computing",
                    summaries=["Research summary about quantum computing"],
                    sources=[],
                    current_date="January 15, 2024"
                )
                result = agent.run(input_data)
            
            # Should return fallback response using the summary
            assert isinstance(result, FinalizationOutput)
            assert "Based on the research:" in result.final_answer
            assert "quantum computing" in result.final_answer
    
    def test_run_with_invalid_input(self, mock_environment, test_configuration):
        """Test finalization with invalid input."""
        with patch('agent.configuration.Configuration.create_answer_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            agent = FinalizationAgent(test_configuration)
            
            # Test with None input
            with patch('builtins.print'):  # Suppress error prints
                result = agent.run(None)
            
            assert isinstance(result, FinalizationOutput)
            assert "Unable to provide comprehensive information" in result.final_answer
    
    def test_fallback_response_with_summaries(self, mock_environment, test_configuration):
        """Test fallback response when summaries are available."""
        with patch('agent.configuration.Configuration.create_answer_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            agent = FinalizationAgent(test_configuration)
            
            test_sources = [
                Source(title="Source 1", url="http://test1.com", short_url="test1", label="Source 1"),
                Source(title="Source 2", url="http://test2.com", short_url="test2", label="Source 2"),
                Source(title="Source 3", url="http://test3.com", short_url="test3", label="Source 3"),
                Source(title="Source 4", url="http://test4.com", short_url="test4", label="Source 4")
            ]
            
            input_data = FinalizationInput(
                research_topic="test topic",
                summaries=["Summary 1", "Summary 2"],
                sources=test_sources,
                current_date="2024"
            )
            
            result = agent._create_fallback_response(input_data, "test error")
            
            assert isinstance(result, FinalizationOutput)
            assert "Based on the research: Summary 1" in result.final_answer
            assert "Additional findings:" in result.final_answer
            assert "Summary 2" in result.final_answer
            assert "test error" in result.final_answer
            assert len(result.used_sources) == 3  # Should limit to 3 sources
    
    def test_fallback_response_without_summaries(self, mock_environment, test_configuration):
        """Test fallback response when no summaries are available."""
        with patch('agent.configuration.Configuration.create_answer_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            agent = FinalizationAgent(test_configuration)
            input_data = FinalizationInput(
                research_topic="test topic",
                summaries=[],
                sources=[],
                current_date="2024"
            )
            
            result = agent._create_fallback_response(input_data, "test error")
            
            assert isinstance(result, FinalizationOutput)
            assert "Unable to provide comprehensive information" in result.final_answer
            assert "test topic" in result.final_answer
            assert "test error" in result.final_answer
            assert len(result.used_sources) == 0
    
    def test_validate_input(self, mock_environment, test_configuration):
        """Test input validation."""
        with patch('agent.configuration.Configuration.create_answer_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            agent = FinalizationAgent(test_configuration)
            
            # Valid input
            valid_input = FinalizationInput(
                research_topic="test",
                summaries=["summary"],
                sources=[],
                current_date="2024"
            )
            assert agent._validate_input(valid_input) is True
            
            # Invalid input (None)
            assert agent._validate_input(None) is False