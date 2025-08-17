"""
Tests for FinalizationAgent class in agents.py.
Tests answer finalization functionality, source usage, and error handling.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

from agent.agents import FinalizationAgent
from agent.state import FinalizationInput, FinalizationOutput, Source
from agent.configuration import Configuration


class TestFinalizationAgent:
    """Test the FinalizationAgent class."""
    
    def test_agent_initialization(self, mock_environment, test_configuration):
        """Test agent initialization with valid configuration."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_agent_config = MagicMock()
            mock_agent_config_class.return_value = mock_agent_config
            
            agent = FinalizationAgent(test_configuration)
            
            assert agent.config == test_configuration
            assert agent.agent_config is not None
    
    def test_run_successful_finalization(self, mock_environment, test_configuration, sample_finalization_input, sample_finalization_output):
        """Test successful answer finalization."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = sample_finalization_output
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            agent = FinalizationAgent(test_configuration)
            result = agent.run(sample_finalization_input)
            
            assert isinstance(result, FinalizationOutput)
            assert "remarkable progress" in result.final_answer
            assert len(result.used_sources) == 2
            assert result.used_sources[0].title == "Quantum Computing Research 2024"
            
            # Verify the client was called correctly
            mock_completions.create.assert_called_once()
            call_args = mock_completions.create.call_args
            assert call_args[1]['response_model'] == FinalizationOutput
    
    def test_run_with_formatted_prompt(self, mock_environment, test_configuration, sample_finalization_input):
        """Test that prompt is properly formatted with input data."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = FinalizationOutput(
                final_answer="Test answer",
                used_sources=[]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            agent = FinalizationAgent(test_configuration)
            agent.run(sample_finalization_input)
            
            # Check that the prompt was formatted with input data
            call_args = mock_completions.create.call_args
            messages = call_args[1]['messages']
            assert len(messages) == 1
            assert messages[0]['role'] == 'user'
            
            content = messages[0]['content']
            assert sample_finalization_input.research_topic in content
            assert sample_finalization_input.current_date in content
            for summary in sample_finalization_input.summaries:
                assert summary in content
    
    def test_run_client_exception_with_summaries(self, mock_environment, test_configuration, sample_finalization_input):
        """Test fallback behavior when client raises exception (with summaries)."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.side_effect = Exception("API Error")
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            with patch('builtins.print') as mock_print:
                agent = FinalizationAgent(test_configuration)
                result = agent.run(sample_finalization_input)
                
                # Should return fallback response using first summary
                assert isinstance(result, FinalizationOutput)
                assert "Based on the research:" in result.final_answer
                assert sample_finalization_input.summaries[0] in result.final_answer
                assert len(result.used_sources) <= 3  # Limited to first 3 sources
                
                # Verify error messages were printed
                assert mock_print.call_count >= 2
                assert any("Finalization Agent error" in str(call) for call in mock_print.call_args_list)
                assert any("Using fallback finalization" in str(call) for call in mock_print.call_args_list)
    
    def test_run_client_exception_without_summaries(self, mock_environment, test_configuration):
        """Test fallback behavior when client raises exception (without summaries)."""
        input_data = FinalizationInput(
            research_topic="quantum computing",
            summaries=[],  # Empty summaries
            sources=[],
            current_date="January 15, 2024"
        )
        
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.side_effect = Exception("API Error")
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            with patch('builtins.print') as mock_print:
                agent = FinalizationAgent(test_configuration)
                result = agent.run(input_data)
                
                # Should return default fallback response
                assert isinstance(result, FinalizationOutput)
                assert "capital of France is Paris" in result.final_answer
                assert len(result.used_sources) == 0  # No sources available
    
    def test_run_empty_summaries(self, mock_environment, test_configuration):
        """Test finalization with empty summaries list."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = FinalizationOutput(
                final_answer="Answer based on limited information",
                used_sources=[]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            input_data = FinalizationInput(
                research_topic="test topic",
                summaries=[],  # Empty summaries
                sources=[],
                current_date="January 15, 2024"
            )
            
            agent = FinalizationAgent(test_configuration)
            result = agent.run(input_data)
            
            assert isinstance(result, FinalizationOutput)
            
            # Check that the prompt handled empty summaries
            call_args = mock_completions.create.call_args
            content = call_args[1]['messages'][0]['content']
            assert "No research summaries available" in content
    
    def test_run_single_summary(self, mock_environment, test_configuration):
        """Test finalization with single summary."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = FinalizationOutput(
                final_answer="Comprehensive answer based on single source",
                used_sources=[]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            input_data = FinalizationInput(
                research_topic="AI development",
                summaries=["AI has advanced significantly with new neural architectures"],
                sources=[],
                current_date="January 15, 2024"
            )
            
            agent = FinalizationAgent(test_configuration)
            result = agent.run(input_data)
            
            assert isinstance(result, FinalizationOutput)
            
            # Verify the single summary was included in prompt
            call_args = mock_completions.create.call_args
            content = call_args[1]['messages'][0]['content']
            assert "neural architectures" in content
    
    def test_run_multiple_summaries(self, mock_environment, test_configuration):
        """Test finalization with multiple summaries."""
        summaries = [
            "AI has made breakthrough advances in 2024",
            "Machine learning models are more efficient",
            "Neural networks show improved accuracy",
            "Deep learning applications have expanded"
        ]
        
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = FinalizationOutput(
                final_answer="Comprehensive AI analysis based on multiple sources",
                used_sources=[]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            input_data = FinalizationInput(
                research_topic="AI development",
                summaries=summaries,
                sources=[],
                current_date="January 15, 2024"
            )
            
            agent = FinalizationAgent(test_configuration)
            result = agent.run(input_data)
            
            assert isinstance(result, FinalizationOutput)
            
            # Verify all summaries were included in prompt
            call_args = mock_completions.create.call_args
            content = call_args[1]['messages'][0]['content']
            for summary in summaries:
                assert summary in content
    
    def test_run_with_multiple_sources(self, mock_environment, test_configuration):
        """Test finalization with multiple sources."""
        sources = [
            Source(title="AI Research Paper", url="https://ai-research.com", short_url="ai-1", label="Source 1"),
            Source(title="ML Development Blog", url="https://ml-dev.com", short_url="ml-1", label="Source 2"),
            Source(title="Tech News Article", url="https://tech-news.com", short_url="tech-1", label="Source 3"),
            Source(title="Academic Journal", url="https://academic.com", short_url="acad-1", label="Source 4"),
            Source(title="Industry Report", url="https://industry.com", short_url="ind-1", label="Source 5")
        ]
        
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = FinalizationOutput(
                final_answer="Answer citing multiple sources",
                used_sources=sources[:3]  # Only use first 3
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            input_data = FinalizationInput(
                research_topic="AI development",
                summaries=["AI summary"],
                sources=sources,
                current_date="January 15, 2024"
            )
            
            agent = FinalizationAgent(test_configuration)
            result = agent.run(input_data)
            
            assert isinstance(result, FinalizationOutput)
            assert len(result.used_sources) == 3  # Should use first 3 sources
            assert result.used_sources[0].title == "AI Research Paper"
    
    def test_run_different_research_topics(self, mock_environment, test_configuration):
        """Test finalization with different research topics."""
        topics = [
            "climate change solutions",
            "space exploration technologies", 
            "renewable energy storage",
            "biotechnology advances"
        ]
        
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            agent = FinalizationAgent(test_configuration)
            
            for topic in topics:
                mock_completions.create.return_value = FinalizationOutput(
                    final_answer=f"Comprehensive analysis of {topic}",
                    used_sources=[]
                )
                mock_client.chat.completions = mock_completions
                
                input_data = FinalizationInput(
                    research_topic=topic,
                    summaries=[f"Research about {topic}"],
                    sources=[],
                    current_date="January 15, 2024"
                )
                
                result = agent.run(input_data)
                
                assert isinstance(result, FinalizationOutput)
                assert topic in result.final_answer
    
    def test_run_different_dates(self, mock_environment, test_configuration):
        """Test finalization with different current dates."""
        dates = [
            "January 1, 2024",
            "June 15, 2024",
            "December 31, 2024",
            "March 20, 2023"
        ]
        
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = FinalizationOutput(
                final_answer="Date-aware answer",
                used_sources=[]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            agent = FinalizationAgent(test_configuration)
            
            for date in dates:
                input_data = FinalizationInput(
                    research_topic="technology trends",
                    summaries=["Technology is evolving"],
                    sources=[],
                    current_date=date
                )
                
                result = agent.run(input_data)
                
                assert isinstance(result, FinalizationOutput)
                
                # Verify date was included in prompt
                call_args = mock_completions.create.call_args
                content = call_args[1]['messages'][0]['content']
                assert date in content
    
    def test_run_special_characters_in_summaries(self, mock_environment, test_configuration):
        """Test finalization with special characters in summaries."""
        special_summaries = [
            "AI & ML: \"Revolutionary\" progress (2024)",
            "Cost reduction: 40% improvement vs. 2023",
            "User feedback: 'Amazing results!' #breakthrough",
            "Performance metrics: >95% accuracy achieved"
        ]
        
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = FinalizationOutput(
                final_answer="Answer handling special characters",
                used_sources=[]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            input_data = FinalizationInput(
                research_topic="AI technology",
                summaries=special_summaries,
                sources=[],
                current_date="January 15, 2024"
            )
            
            agent = FinalizationAgent(test_configuration)
            result = agent.run(input_data)
            
            assert isinstance(result, FinalizationOutput)
            
            # Verify special characters were preserved in prompt
            call_args = mock_completions.create.call_args
            content = call_args[1]['messages'][0]['content']
            assert "&" in content
            assert '"' in content
            assert "%" in content
            assert ">" in content
            assert "#" in content
    
    def test_run_very_long_summaries(self, mock_environment, test_configuration):
        """Test finalization with very long summaries."""
        long_summaries = [
            "A" * 2000,  # Very long summary
            "B" * 1000 + " comprehensive analysis " + "C" * 1000,
            "Short summary",
            "D" * 5000  # Extremely long summary
        ]
        
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = FinalizationOutput(
                final_answer="Answer based on comprehensive research",
                used_sources=[]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            input_data = FinalizationInput(
                research_topic="comprehensive study",
                summaries=long_summaries,
                sources=[],
                current_date="January 15, 2024"
            )
            
            agent = FinalizationAgent(test_configuration)
            result = agent.run(input_data)
            
            assert isinstance(result, FinalizationOutput)
            # Should handle very long content without crashing
    
    def test_configuration_different_models(self, mock_environment):
        """Test agent with different answer model configurations."""
        models_to_test = ["gemini-2.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
        
        for model in models_to_test:
            config = Configuration(
                query_generator_model="gemini-2.5-flash",
                reflection_model="gemini-2.5-flash",
                answer_model=model
            )
            
            with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
                mock_agent_config = MagicMock()
                mock_agent_config_class.return_value = mock_agent_config
                
                agent = FinalizationAgent(config)
                
                assert agent.config.answer_model == model
    
    def test_source_limiting_fallback(self, mock_environment, test_configuration):
        """Test that fallback limits sources to first 3."""
        many_sources = [
            Source(title=f"Source {i}", url=f"https://source{i}.com", short_url=f"s{i}", label=f"Source {i}")
            for i in range(1, 11)  # 10 sources
        ]
        
        input_data = FinalizationInput(
            research_topic="test topic",
            summaries=["test summary"],
            sources=many_sources,
            current_date="January 15, 2024"
        )
        
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.side_effect = Exception("API Error")
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            with patch('builtins.print'):
                agent = FinalizationAgent(test_configuration)
                result = agent.run(input_data)
                
                # Should limit to first 3 sources in fallback
                assert len(result.used_sources) == 3
                assert result.used_sources[0].title == "Source 1"
                assert result.used_sources[2].title == "Source 3"
    
    def test_prompt_structure_validation(self, mock_environment, test_configuration):
        """Test that the prompt follows expected structure."""
        with patch('agent.configuration.AgentConfig') as mock_agent_config_class:
            mock_client = MagicMock()
            mock_completions = MagicMock()
            mock_completions.create.return_value = FinalizationOutput(
                final_answer="Test answer",
                used_sources=[]
            )
            mock_client.chat.completions = mock_completions
            
            mock_agent_config = MagicMock()
            mock_agent_config.client = mock_client
            mock_agent_config_class.return_value = mock_agent_config
            
            input_data = FinalizationInput(
                research_topic="test topic",
                summaries=["summary 1", "summary 2"],
                sources=[],
                current_date="January 15, 2024"
            )
            
            agent = FinalizationAgent(test_configuration)
            agent.run(input_data)
            
            # Verify prompt structure
            call_args = mock_completions.create.call_args
            content = call_args[1]['messages'][0]['content']
            
            # Should contain key sections
            assert "The current date is January 15, 2024" in content
            assert "test topic" in content
            assert "summary 1" in content
            assert "summary 2" in content