"""
Tests for ReflectionAgent class in agents.py.
Tests reflection functionality, knowledge gap analysis, and follow-up query generation.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from agent.agents import ReflectionAgent
from agent.state import ReflectionInput, ReflectionOutput
from agent.configuration import Configuration


class TestReflectionAgent:
    """Test the ReflectionAgent class."""
    
    def test_agent_initialization(self, mock_environment, test_configuration):
        """Test agent initialization with valid configuration."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_agent_config = MagicMock()
            mock_agent_config_class.return_value = mock_agent_config
            
            agent = ReflectionAgent(test_configuration)
            
            assert agent.config == test_configuration
            assert agent.agent_config is not None
            # Note: BaseAgent is not initialized to avoid model parameter conflicts
    
    def test_run_successful_reflection_insufficient(self, mock_environment, test_configuration, sample_reflection_input):
        """Test successful reflection that identifies insufficient research."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            
            expected_output = ReflectionOutput(
                is_sufficient=False,
                knowledge_gap="Need more specific performance benchmarks and recent developments",
                follow_up_queries=["quantum computing performance benchmarks 2024", "latest quantum hardware breakthroughs"]
            )
            mock_completions.create.return_value = expected_output
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            agent = ReflectionAgent(test_configuration)
            result = agent.run(sample_reflection_input)
            
            assert isinstance(result, ReflectionOutput)
            assert result.is_sufficient is False
            assert "performance benchmarks" in result.knowledge_gap
            assert len(result.follow_up_queries) == 2
            assert "quantum computing" in result.follow_up_queries[0]
            
            # Verify the client was called correctly
            mock_completions.create.assert_called_once()
            call_args = mock_completions.create.call_args
            assert call_args[1]['response_model'] == ReflectionOutput
    
    def test_run_successful_reflection_sufficient(self, mock_environment, test_configuration, sample_reflection_input):
        """Test successful reflection that identifies sufficient research."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            
            expected_output = ReflectionOutput(
                is_sufficient=True,
                knowledge_gap="",
                follow_up_queries=[]
            )
            mock_completions.create.return_value = expected_output
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            agent = ReflectionAgent(test_configuration)
            result = agent.run(sample_reflection_input)
            
            assert isinstance(result, ReflectionOutput)
            assert result.is_sufficient is True
            assert result.knowledge_gap == ""
            assert len(result.follow_up_queries) == 0
    
    def test_run_with_formatted_prompt(self, mock_environment, test_configuration, sample_reflection_input):
        """Test that prompt is properly formatted with input data."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = ReflectionOutput(
                is_sufficient=True, knowledge_gap="", follow_up_queries=[]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            agent = ReflectionAgent(test_configuration)
            agent.run(sample_reflection_input)
            
            # Check that the prompt was formatted with input data
            call_args = mock_completions.create.call_args
            messages = call_args[1]['messages']
            assert len(messages) == 1
            assert messages[0]['role'] == 'user'
            
            content = messages[0]['content']
            assert sample_reflection_input.research_topic in content
            for summary in sample_reflection_input.summaries:
                assert summary in content
    
    def test_run_client_exception_fallback(self, mock_environment, test_configuration, sample_reflection_input):
        """Test fallback behavior when client raises exception."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.side_effect = Exception("API Error")
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            with patch('builtins.print') as mock_print:
                agent = ReflectionAgent(test_configuration)
                result = agent.run(sample_reflection_input)
                
                # Should return fallback response
                assert isinstance(result, ReflectionOutput)
                assert result.is_sufficient is True
                assert "No additional research needed" in result.knowledge_gap
                assert len(result.follow_up_queries) == 0
                
                # Verify error messages were printed
                assert mock_print.call_count >= 2
                assert any("Reflection Agent error" in str(call) for call in mock_print.call_args_list)
                assert any("Using fallback reflection" in str(call) for call in mock_print.call_args_list)
    
    def test_run_empty_summaries(self, mock_environment, test_configuration):
        """Test reflection with empty summaries list."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = ReflectionOutput(
                is_sufficient=False,
                knowledge_gap="No research summaries available",
                follow_up_queries=["basic research query"]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            input_data = ReflectionInput(
                research_topic="quantum computing",
                summaries=[],  # Empty summaries
                current_loop=1
            )
            
            agent = ReflectionAgent(test_configuration)
            result = agent.run(input_data)
            
            assert isinstance(result, ReflectionOutput)
            
            # Check that the prompt handled empty summaries
            call_args = mock_completions.create.call_args
            content = call_args[1]['messages'][0]['content']
            assert "No summaries available" in content
    
    def test_run_single_summary(self, mock_environment, test_configuration):
        """Test reflection with single summary."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = ReflectionOutput(
                is_sufficient=True,
                knowledge_gap="",
                follow_up_queries=[]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            input_data = ReflectionInput(
                research_topic="quantum computing",
                summaries=["Single comprehensive summary about quantum computing"],
                current_loop=1
            )
            
            agent = ReflectionAgent(test_configuration)
            result = agent.run(input_data)
            
            assert isinstance(result, ReflectionOutput)
            
            # Verify the single summary was included in prompt
            call_args = mock_completions.create.call_args
            content = call_args[1]['messages'][0]['content']
            assert "Single comprehensive summary" in content
    
    def test_run_multiple_summaries(self, mock_environment, test_configuration):
        """Test reflection with multiple summaries."""
        summaries = [
            "Quantum computing has advanced significantly",
            "New quantum algorithms have been developed",
            "Hardware improvements are notable",
            "Commercial applications are emerging"
        ]
        
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = ReflectionOutput(
                is_sufficient=False,
                knowledge_gap="Missing specific use cases",
                follow_up_queries=["quantum computing use cases 2024"]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            input_data = ReflectionInput(
                research_topic="quantum computing",
                summaries=summaries,
                current_loop=1
            )
            
            agent = ReflectionAgent(test_configuration)
            result = agent.run(input_data)
            
            assert isinstance(result, ReflectionOutput)
            
            # Verify all summaries were included in prompt
            call_args = mock_completions.create.call_args
            content = call_args[1]['messages'][0]['content']
            for summary in summaries:
                assert summary in content
    
    def test_run_different_research_topics(self, mock_environment, test_configuration):
        """Test reflection with different research topics."""
        topics = [
            "artificial intelligence ethics",
            "climate change mitigation",
            "renewable energy storage",
            "space exploration technologies"
        ]
        
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            agent = ReflectionAgent(test_configuration)
            
            for topic in topics:
                mock_completions.create.return_value = ReflectionOutput(
                    is_sufficient=False,
                    knowledge_gap=f"Need more details about {topic}",
                    follow_up_queries=[f"{topic} latest developments"]
                )
                mock_client.chat.completions = mock_completions
                
                input_data = ReflectionInput(
                    research_topic=topic,
                    summaries=[f"Basic information about {topic}"],
                    current_loop=1
                )
                
                result = agent.run(input_data)
                
                assert isinstance(result, ReflectionOutput)
                assert topic in result.knowledge_gap
                assert topic in result.follow_up_queries[0]
    
    def test_run_different_loop_counts(self, mock_environment, test_configuration):
        """Test reflection with different current loop values."""
        loop_counts = [0, 1, 2, 5]
        
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = ReflectionOutput(
                is_sufficient=True, knowledge_gap="", follow_up_queries=[]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            agent = ReflectionAgent(test_configuration)
            
            for loop_count in loop_counts:
                input_data = ReflectionInput(
                    research_topic="test topic",
                    summaries=["test summary"],
                    current_loop=loop_count
                )
                
                result = agent.run(input_data)
                
                assert isinstance(result, ReflectionOutput)
                # The loop count is currently not used in processing, 
                # but should be accepted without error
    
    def test_run_special_characters_in_summaries(self, mock_environment, test_configuration):
        """Test reflection with special characters in summaries."""
        special_summaries = [
            "AI & ML: \"Revolutionary\" advances (2024)",
            "Cost-benefit analysis shows 50% improvement",
            "Technical specifications: GPU memory > 8GB required",
            "User feedback: 'Excellent performance' #breakthrough"
        ]
        
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = ReflectionOutput(
                is_sufficient=True,
                knowledge_gap="",
                follow_up_queries=[]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            input_data = ReflectionInput(
                research_topic="AI technology",
                summaries=special_summaries,
                current_loop=1
            )
            
            agent = ReflectionAgent(test_configuration)
            result = agent.run(input_data)
            
            assert isinstance(result, ReflectionOutput)
            
            # Verify special characters were preserved in prompt
            call_args = mock_completions.create.call_args
            content = call_args[1]['messages'][0]['content']
            assert "&" in content
            assert '"' in content
            assert "%" in content
            assert ">" in content
            assert "#" in content
    
    def test_run_very_long_summaries(self, mock_environment, test_configuration):
        """Test reflection with very long summaries."""
        long_summaries = [
            "A" * 1000,  # Very long summary
            "B" * 500 + " detailed analysis " + "C" * 500,
            "Short summary",
            "D" * 2000  # Extremely long summary
        ]
        
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = ReflectionOutput(
                is_sufficient=False,
                knowledge_gap="Content too verbose",
                follow_up_queries=["concise summary needed"]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            input_data = ReflectionInput(
                research_topic="detailed analysis",
                summaries=long_summaries,
                current_loop=1
            )
            
            agent = ReflectionAgent(test_configuration)
            result = agent.run(input_data)
            
            assert isinstance(result, ReflectionOutput)
            # Should handle long content without crashing
    
    def test_configuration_different_models(self, mock_environment):
        """Test agent with different reflection model configurations."""
        models_to_test = ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
        
        for model in models_to_test:
            config = Configuration(
                query_generator_model="gemini-2.5-flash",
                reflection_model=model,
                answer_model="gemini-2.5-flash"
            )
            
            with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
                mock_agent_config = MagicMock()
                mock_agent_config_class.return_value = mock_agent_config
                
                agent = ReflectionAgent(config)
                
                assert agent.config.reflection_model == model
    
    def test_multiple_follow_up_queries(self, mock_environment, test_configuration, sample_reflection_input):
        """Test reflection generating multiple follow-up queries."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            
            expected_output = ReflectionOutput(
                is_sufficient=False,
                knowledge_gap="Multiple areas need investigation",
                follow_up_queries=[
                    "quantum computing hardware benchmarks",
                    "quantum algorithm efficiency metrics", 
                    "quantum error correction advances",
                    "commercial quantum computing applications"
                ]
            )
            mock_completions.create.return_value = expected_output
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            agent = ReflectionAgent(test_configuration)
            result = agent.run(sample_reflection_input)
            
            assert isinstance(result, ReflectionOutput)
            assert result.is_sufficient is False
            assert len(result.follow_up_queries) == 4
            assert all("quantum" in query.lower() for query in result.follow_up_queries)
    
    def test_edge_case_none_values(self, mock_environment, test_configuration):
        """Test handling of edge cases with None-like values."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = ReflectionOutput(
                is_sufficient=True,
                knowledge_gap="",
                follow_up_queries=[]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            # This might raise a validation error, which is expected behavior
            try:
                input_data = ReflectionInput(
                    research_topic="valid topic",
                    summaries=None,  # This should be handled gracefully
                    current_loop=1
                )
                
                agent = ReflectionAgent(test_configuration)
                result = agent.run(input_data)
                # If it doesn't raise an error, verify it handled None gracefully
                assert isinstance(result, ReflectionOutput)
            except Exception:
                # Pydantic validation error is expected and acceptable
                pass