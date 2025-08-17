"""
Tests for QueryGenerationAgent class in agents.py.
Tests query generation functionality, input validation, and error handling.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from agent.agents import QueryGenerationAgent
from agent.state import QueryGenerationInput, QueryGenerationOutput
from agent.configuration import Configuration


class TestQueryGenerationAgent:
    """Test the QueryGenerationAgent class."""
    
    def test_agent_initialization(self, mock_environment, test_configuration, mock_agent_dependencies):
        """Test agent initialization with valid configuration."""
        agent = QueryGenerationAgent(test_configuration)
        
        assert agent.config == test_configuration
        assert agent.agent_config is not None
        assert agent.agent is not None
    
    def test_run_successful_query_generation(self, mock_environment, test_configuration, sample_query_generation_input, sample_query_generation_output, mock_agent_dependencies):
        """Test successful query generation."""
        mock_client = mock_agent_dependencies['client']
        mock_completions = MagicMock()
        mock_completions.create.return_value = sample_query_generation_output
        mock_client.chat.completions = mock_completions
        
        agent = QueryGenerationAgent(test_configuration)
        result = agent.run(sample_query_generation_input)
        
        assert isinstance(result, QueryGenerationOutput)
        assert len(result.queries) == 3
        assert result.rationale is not None
        assert "quantum computing" in result.queries[0].lower()
        
        # Verify the client was called with correct parameters
        mock_completions.create.assert_called_once()
        call_args = mock_completions.create.call_args
        assert call_args[1]['response_model'] == QueryGenerationOutput
    
    def test_run_with_formatted_prompt(self, mock_environment, test_configuration, sample_query_generation_input, mock_agent_dependencies):
        """Test that prompt is properly formatted with input data."""
        mock_client = mock_agent_dependencies['client']
        mock_completions = MagicMock()
        mock_completions.create.return_value = QueryGenerationOutput(
            queries=["test query"], rationale="test rationale"
        )
        mock_client.chat.completions = mock_completions
        
        agent = QueryGenerationAgent(test_configuration)
        agent.run(sample_query_generation_input)
        
        # Check that the prompt was formatted with input data
        call_args = mock_completions.create.call_args
        messages = call_args[1]['messages']
        assert len(messages) == 1
        assert messages[0]['role'] == 'user'
        
        content = messages[0]['content']
        assert sample_query_generation_input.research_topic in content
        assert sample_query_generation_input.current_date in content
        assert str(sample_query_generation_input.number_of_queries) in content
    
    def test_run_client_exception_fallback(self, mock_environment, test_configuration, sample_query_generation_input, mock_agent_dependencies):
        """Test fallback behavior when client raises exception."""
        mock_client = mock_agent_dependencies['client']
        mock_completions = MagicMock()
        mock_completions.create.side_effect = Exception("API Error")
        mock_client.chat.completions = mock_completions
        
        with patch('builtins.print') as mock_print:
            agent = QueryGenerationAgent(test_configuration)
            result = agent.run(sample_query_generation_input)
            
            # Should return fallback response
            assert isinstance(result, QueryGenerationOutput)
            assert len(result.queries) == 1
            assert "capital of France" in result.queries[0]
            assert sample_query_generation_input.research_topic in result.rationale
            
            # Verify error messages were printed
            assert mock_print.call_count >= 2
            assert any("Query Generation Agent error" in str(call) for call in mock_print.call_args_list)
    
    def test_run_different_research_topics(self, mock_environment, test_configuration, mock_agent_dependencies):
        """Test query generation with different research topics."""
        research_topics = [
            "artificial intelligence in healthcare",
            "climate change solutions", 
            "space exploration missions",
            "renewable energy technologies"
        ]
        
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_create_config.return_value = mock_agent_config
            
            with patch('atomic_agents.agents.base_agent.BaseAgent'):
                agent = QueryGenerationAgent(test_configuration)
                
                for topic in research_topics:
                    # Create different responses for different topics
                    mock_completions.create.return_value = QueryGenerationOutput(
                        queries=[f"{topic} query 1", f"{topic} query 2"],
                        rationale=f"Generated queries for {topic}"
                    )
                    mock_client.chat.completions = mock_completions
                    
                    input_data = QueryGenerationInput(
                        research_topic=topic,
                        number_of_queries=2,
                        current_date="January 15, 2024"
                    )
                    
                    result = agent.run(input_data)
                    
                    assert isinstance(result, QueryGenerationOutput)
                    assert len(result.queries) == 2
                    assert topic in result.rationale
    
    def test_run_different_query_counts(self, mock_environment, test_configuration, sample_query_generation_input, mock_agent_dependencies):
        """Test query generation with different query counts."""
        query_counts = [1, 3, 5, 10]
        
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_create_config.return_value = mock_agent_config
            
            with patch('atomic_agents.agents.base_agent.BaseAgent'):
                agent = QueryGenerationAgent(test_configuration)
                
                for count in query_counts:
                    # Create response with requested number of queries
                    mock_completions.create.return_value = QueryGenerationOutput(
                        queries=[f"query {i+1}" for i in range(count)],
                        rationale=f"Generated {count} queries"
                    )
                    mock_client.chat.completions = mock_completions
                    
                    input_data = QueryGenerationInput(
                        research_topic=sample_query_generation_input.research_topic,
                        number_of_queries=count,
                        current_date=sample_query_generation_input.current_date
                    )
                    
                    result = agent.run(input_data)
                    
                    assert isinstance(result, QueryGenerationOutput)
                    assert len(result.queries) == count
    
    def test_run_empty_research_topic(self, mock_environment, test_configuration):
        """Test handling of empty research topic."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = QueryGenerationOutput(
                queries=["generic query"], rationale="Generic response"
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            with patch('atomic_agents.agents.base_agent.BaseAgent'):
                agent = QueryGenerationAgent(test_configuration)
                
                input_data = QueryGenerationInput(
                    research_topic="",  # Empty topic
                    number_of_queries=3,
                    current_date="January 15, 2024"
                )
                
                result = agent.run(input_data)
                
                assert isinstance(result, QueryGenerationOutput)
                assert len(result.queries) >= 1
    
    def test_run_special_characters_in_topic(self, mock_environment, test_configuration):
        """Test handling of special characters in research topic."""
        special_topic = "AI & ML: How do robots \"think\" (2024)?"
        
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = QueryGenerationOutput(
                queries=["AI ML query"], rationale="Handled special characters"
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            with patch('atomic_agents.agents.base_agent.BaseAgent'):
                agent = QueryGenerationAgent(test_configuration)
                
                input_data = QueryGenerationInput(
                    research_topic=special_topic,
                    number_of_queries=1,
                    current_date="January 15, 2024"
                )
                
                result = agent.run(input_data)
                
                assert isinstance(result, QueryGenerationOutput)
                
                # Verify the special characters were included in the prompt
                call_args = mock_completions.create.call_args
                content = call_args[1]['messages'][0]['content']
                assert special_topic in content
    
    def test_configuration_different_models(self, mock_environment, mock_agent_dependencies):
        """Test agent with different model configurations."""
        models_to_test = ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
        
        for model in models_to_test:
            config = Configuration(
                query_generator_model=model,
                reflection_model="gemini-2.5-flash",
                answer_model="gemini-2.5-flash"
            )
            
            # Patch the Configuration class method instead of instance method
            with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
                mock_agent_config = MagicMock()
                mock_create_config.return_value = mock_agent_config
                
                with patch('atomic_agents.agents.base_agent.BaseAgent'):
                    agent = QueryGenerationAgent(config)
                    
                    assert agent.config.query_generator_model == model
                    # Verify that create_agent_config was called (which validates the model)
                    mock_create_config.assert_called()
    
    def test_agent_config_creation(self, mock_environment, test_configuration):
        """Test that agent config is properly created."""
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_create_config.return_value = mock_agent_config
            
            with patch('agent.agents.BaseAgent') as mock_base_agent:
                mock_agent_instance = MagicMock()
                # Handle the generic type syntax BaseAgent[QueryGenerationInput, QueryGenerationOutput]
                mock_base_agent.__getitem__.return_value = MagicMock(return_value=mock_agent_instance)
                
                agent = QueryGenerationAgent(test_configuration)
                
                # Verify that create_agent_config was called
                assert agent.agent_config is not None
                
                # Verify BaseAgent was accessed for generic typing
                mock_base_agent.__getitem__.assert_called_once()
                # Verify the generic BaseAgent was called with config
                mock_base_agent.__getitem__.return_value.assert_called_once_with(config=mock_agent_config)
                # Verify the agent attribute was set correctly
                assert agent.agent == mock_agent_instance
    
    def test_unreachable_code_paths(self, mock_environment, test_configuration, mock_agent_dependencies):
        """Test unreachable code paths in the run method."""
        # Note: The unreachable code paths at lines 498-506 in agents.py cannot be reached
        # because the code always returns at line 488 or 496. This test documents this fact.
        mock_client = MagicMock()
        mock_completions = MagicMock()
        
        # Return a properly structured response (normal path)
        mock_completions.create.return_value = QueryGenerationOutput(
            queries=["test query"],
            rationale="test rationale"
        )
        mock_client.chat.completions = mock_completions
        
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_create_config.return_value = mock_agent_config
            
            with patch('atomic_agents.agents.base_agent.BaseAgent'):
                agent = QueryGenerationAgent(test_configuration)
                
                input_data = QueryGenerationInput(
                    research_topic="test topic",
                    number_of_queries=1,
                    current_date="January 15, 2024"
                )
                
                # The code should handle this case normally
                result = agent.run(input_data)
                assert isinstance(result, QueryGenerationOutput)
                assert result.queries == ["test query"]
    
    def test_input_validation(self, mock_environment, test_configuration, mock_agent_dependencies):
        """Test input validation with various input scenarios."""
        mock_client = MagicMock()
        mock_completions = MagicMock()
        mock_completions.create.return_value = QueryGenerationOutput(
            queries=["valid query"], rationale="valid rationale"
        )
        mock_client.chat.completions = mock_completions
        
        with patch('agent.configuration.Configuration.create_agent_config') as mock_create_config:
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_create_config.return_value = mock_agent_config
            
            with patch('atomic_agents.agents.base_agent.BaseAgent'):
                agent = QueryGenerationAgent(test_configuration)
                
                # Test with minimum valid input
                min_input = QueryGenerationInput(
                    research_topic="minimal topic",
                    number_of_queries=1,
                    current_date="2024-01-01"
                )
                
                result = agent.run(min_input)
                assert isinstance(result, QueryGenerationOutput)
                
                # Test with maximum realistic input
                max_input = QueryGenerationInput(
                    research_topic="A" * 1000,  # Very long topic
                    number_of_queries=100,      # Many queries
                    current_date="December 31, 2024"
                )
                
                result = agent.run(max_input)
                assert isinstance(result, QueryGenerationOutput)