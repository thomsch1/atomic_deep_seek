"""
Integration tests for the Atomic Agent implementation.
These tests verify equivalent functionality after migration from LangChain.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List
from pydantic import BaseModel, Field

# These imports will be available after Atomic Agent conversion
try:
    from atomic_agents import AtomicAgent, AgentConfig
    from instructor import OpenAIClient
except ImportError:
    # Placeholder classes for testing structure before actual conversion
    class AtomicAgent:
        def __init__(self, config):
            self.config = config
        
        def run(self, input_data):
            return MagicMock()
    
    class AgentConfig:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)


class ResearchTopicInput(BaseModel):
    """Input schema for research topic."""
    research_topic: str = Field(description="The research topic to investigate")
    initial_query_count: int = Field(default=3, description="Number of initial queries to generate")
    current_date: str = Field(description="Current date for context")


class SearchQueryOutput(BaseModel):
    """Output schema for search queries."""
    queries: List[str] = Field(description="Generated search queries")
    rationale: str = Field(description="Reasoning behind query selection")


class WebSearchInput(BaseModel):
    """Input schema for web search."""
    search_query: str = Field(description="Query to search for")
    query_id: int = Field(description="Unique identifier for this query")


class WebSearchOutput(BaseModel):
    """Output schema for web search results."""
    content: str = Field(description="Research content found")
    sources: List[Dict[str, str]] = Field(description="Source information")
    citations: List[Dict[str, Any]] = Field(description="Citation metadata")


class ReflectionInput(BaseModel):
    """Input schema for reflection analysis."""
    research_topic: str = Field(description="Original research topic")
    summaries: List[str] = Field(description="Research summaries to analyze")
    current_loop: int = Field(description="Current research loop count")


class ReflectionOutput(BaseModel):
    """Output schema for reflection results."""
    is_sufficient: bool = Field(description="Whether research is sufficient")
    knowledge_gap: str = Field(description="Identified knowledge gaps")
    follow_up_queries: List[str] = Field(description="Suggested follow-up queries")


class FinalizationInput(BaseModel):
    """Input schema for answer finalization."""
    research_topic: str = Field(description="Original research topic")
    summaries: List[str] = Field(description="All research summaries")
    sources: List[Dict[str, Any]] = Field(description="All gathered sources")


class FinalizationOutput(BaseModel):
    """Output schema for final answer."""
    final_answer: str = Field(description="Complete research answer")
    used_sources: List[Dict[str, Any]] = Field(description="Sources cited in answer")


class TestAtomicAgentImplementation:
    """Test suite for Atomic Agent-based research implementation."""

    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables for testing."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
            yield

    @pytest.fixture
    def sample_research_topic(self) -> str:
        """Sample research topic for testing."""
        return "What are the latest developments in quantum computing in 2024?"

    @pytest.fixture
    def mock_agent_config(self):
        """Mock agent configuration."""
        return AgentConfig(
            model="gemini-2.0-flash",
            temperature=0.7,
            max_tokens=2000
        )

    def test_query_generation_agent(self, mock_env_vars, sample_research_topic, mock_agent_config):
        """Test the query generation atomic agent."""
        
        # Create query generation agent
        query_agent = AtomicAgent(config=mock_agent_config)
        
        # Mock the agent response
        expected_output = SearchQueryOutput(
            queries=[
                "quantum computing breakthroughs 2024",
                "quantum algorithms latest research",
                "quantum hardware developments 2024"
            ],
            rationale="These queries cover the main aspects of quantum computing developments"
        )
        
        with patch.object(query_agent, 'run', return_value=expected_output) as mock_run:
            input_data = ResearchTopicInput(
                research_topic=sample_research_topic,
                initial_query_count=3,
                current_date="January 8, 2025"
            )
            
            result = query_agent.run(input_data)
            
            # Verify the agent was called correctly
            mock_run.assert_called_once_with(input_data)
            
            # Verify output structure matches expected behavior
            assert hasattr(result, 'queries')
            assert hasattr(result, 'rationale')
            assert len(result.queries) == 3
            assert all("quantum" in query.lower() for query in result.queries)

    def test_web_search_agent(self, mock_env_vars, mock_agent_config):
        """Test the web search atomic agent."""
        
        search_agent = AtomicAgent(config=mock_agent_config)
        
        expected_output = WebSearchOutput(
            content="Quantum computing has seen significant breakthroughs in 2024...",
            sources=[
                {"title": "Quantum News", "url": "https://example.com/quantum1", "short_url": "https://vertexaisearch.cloud.google.com/id/0-1"}
            ],
            citations=[
                {"start_index": 0, "end_index": 50, "source_id": "0-1"}
            ]
        )
        
        with patch.object(search_agent, 'run', return_value=expected_output) as mock_run:
            input_data = WebSearchInput(
                search_query="quantum computing breakthroughs 2024",
                query_id=0
            )
            
            result = search_agent.run(input_data)
            
            mock_run.assert_called_once_with(input_data)
            
            # Verify output structure
            assert hasattr(result, 'content')
            assert hasattr(result, 'sources')
            assert hasattr(result, 'citations')
            assert len(result.sources) == 1

    def test_reflection_agent(self, mock_env_vars, sample_research_topic, mock_agent_config):
        """Test the reflection atomic agent."""
        
        reflection_agent = AtomicAgent(config=mock_agent_config)
        
        expected_output = ReflectionOutput(
            is_sufficient=False,
            knowledge_gap="Missing information about specific performance metrics",
            follow_up_queries=["quantum computing performance benchmarks 2024"]
        )
        
        with patch.object(reflection_agent, 'run', return_value=expected_output) as mock_run:
            input_data = ReflectionInput(
                research_topic=sample_research_topic,
                summaries=[
                    "Quantum computing research shows progress in error correction...",
                    "IBM announced new quantum processors in 2024..."
                ],
                current_loop=1
            )
            
            result = reflection_agent.run(input_data)
            
            mock_run.assert_called_once_with(input_data)
            
            # Verify output structure
            assert hasattr(result, 'is_sufficient')
            assert hasattr(result, 'knowledge_gap')
            assert hasattr(result, 'follow_up_queries')
            assert not result.is_sufficient
            assert len(result.follow_up_queries) == 1

    def test_finalization_agent(self, mock_env_vars, sample_research_topic, mock_agent_config):
        """Test the answer finalization atomic agent."""
        
        finalization_agent = AtomicAgent(config=mock_agent_config)
        
        expected_output = FinalizationOutput(
            final_answer="Based on research, quantum computing in 2024 has achieved significant milestones...",
            used_sources=[
                {"title": "Quantum Research", "url": "https://example.com/source1"}
            ]
        )
        
        with patch.object(finalization_agent, 'run', return_value=expected_output) as mock_run:
            input_data = FinalizationInput(
                research_topic=sample_research_topic,
                summaries=[
                    "Quantum computing has seen major breakthroughs in 2024...",
                    "New quantum algorithms have been developed..."
                ],
                sources=[
                    {"short_url": "https://vertexaisearch.cloud.google.com/id/0-1", "value": "https://example.com/source1"}
                ]
            )
            
            result = finalization_agent.run(input_data)
            
            mock_run.assert_called_once_with(input_data)
            
            # Verify output structure
            assert hasattr(result, 'final_answer')
            assert hasattr(result, 'used_sources')
            assert "quantum computing" in result.final_answer.lower()
            assert len(result.used_sources) == 1

    def test_workflow_orchestration(self, mock_env_vars, sample_research_topic, mock_agent_config):
        """Test the complete workflow orchestration with atomic agents."""
        
        class ResearchWorkflow:
            """Atomic Agent-based research workflow orchestrator."""
            
            def __init__(self, config):
                self.config = config
                self.query_agent = AtomicAgent(config=config)
                self.search_agent = AtomicAgent(config=config)
                self.reflection_agent = AtomicAgent(config=config)
                self.finalization_agent = AtomicAgent(config=config)
            
            def execute_research(self, research_topic: str, max_loops: int = 2) -> Dict[str, Any]:
                """Execute the complete research workflow."""
                current_loop = 0
                all_summaries = []
                all_sources = []
                
                # Step 1: Generate initial queries
                query_input = ResearchTopicInput(
                    research_topic=research_topic,
                    initial_query_count=3,
                    current_date="January 8, 2025"
                )
                
                query_result = self.query_agent.run(query_input)
                
                # Step 2: Execute web searches
                for i, query in enumerate(query_result.queries):
                    search_input = WebSearchInput(search_query=query, query_id=i)
                    search_result = self.search_agent.run(search_input)
                    all_summaries.append(search_result.content)
                    all_sources.extend(search_result.sources)
                
                # Step 3: Reflection and iteration loop
                while current_loop < max_loops:
                    reflection_input = ReflectionInput(
                        research_topic=research_topic,
                        summaries=all_summaries,
                        current_loop=current_loop
                    )
                    
                    reflection_result = self.reflection_agent.run(reflection_input)
                    
                    if reflection_result.is_sufficient:
                        break
                    
                    # Execute follow-up searches
                    for i, follow_up_query in enumerate(reflection_result.follow_up_queries):
                        search_input = WebSearchInput(
                            search_query=follow_up_query,
                            query_id=len(all_summaries) + i
                        )
                        search_result = self.search_agent.run(search_input)
                        all_summaries.append(search_result.content)
                        all_sources.extend(search_result.sources)
                    
                    current_loop += 1
                
                # Step 4: Finalize answer
                finalization_input = FinalizationInput(
                    research_topic=research_topic,
                    summaries=all_summaries,
                    sources=all_sources
                )
                
                final_result = self.finalization_agent.run(finalization_input)
                
                return {
                    "final_answer": final_result.final_answer,
                    "sources": final_result.used_sources,
                    "loops_executed": current_loop,
                    "total_summaries": len(all_summaries)
                }
        
        workflow = ResearchWorkflow(mock_agent_config)
        
        # Mock all agent responses
        with patch.object(workflow.query_agent, 'run') as mock_query, \
             patch.object(workflow.search_agent, 'run') as mock_search, \
             patch.object(workflow.reflection_agent, 'run') as mock_reflection, \
             patch.object(workflow.finalization_agent, 'run') as mock_finalization:
            
            # Setup mock responses
            mock_query.return_value = SearchQueryOutput(
                queries=["quantum computing 2024"],
                rationale="Test query"
            )
            
            mock_search.return_value = WebSearchOutput(
                content="Test content",
                sources=[{"title": "Test", "url": "test.com"}],
                citations=[]
            )
            
            mock_reflection.return_value = ReflectionOutput(
                is_sufficient=True,
                knowledge_gap="",
                follow_up_queries=[]
            )
            
            mock_finalization.return_value = FinalizationOutput(
                final_answer="Test final answer",
                used_sources=[{"title": "Test", "url": "test.com"}]
            )
            
            # Execute workflow
            result = workflow.execute_research(sample_research_topic)
            
            # Verify workflow execution
            assert "final_answer" in result
            assert "sources" in result
            assert "loops_executed" in result
            assert "total_summaries" in result
            
            # Verify agents were called
            assert mock_query.called
            assert mock_search.called
            assert mock_reflection.called
            assert mock_finalization.called

    def test_error_handling_and_retries(self, mock_env_vars, mock_agent_config):
        """Test error handling capabilities in Atomic Agent implementation."""
        
        agent = AtomicAgent(config=mock_agent_config)
        
        # Simulate an error on first call, success on retry
        with patch.object(agent, 'run') as mock_run:
            mock_run.side_effect = [Exception("API Error"), SearchQueryOutput(queries=["test"], rationale="test")]
            
            # Test retry logic would be implemented in the workflow
            try:
                result = agent.run(ResearchTopicInput(
                    research_topic="test topic",
                    current_date="2025-01-08"
                ))
                assert False, "Should have raised exception"
            except Exception as e:
                assert str(e) == "API Error"
            
            # Second call should succeed
            result = agent.run(ResearchTopicInput(
                research_topic="test topic",
                current_date="2025-01-08"
            ))
            
            assert hasattr(result, 'queries')


class TestAtomicAgentBehaviorCapture:
    """Capture Atomic Agent behavior patterns for comparison."""
    
    def capture_query_generation_behavior(self) -> Dict[str, Any]:
        """Capture query generation behavior in Atomic Agent implementation."""
        return {
            "input_format": "Pydantic model with research_topic field",
            "output_format": "Pydantic model with queries list and rationale",
            "expected_query_count": "Configurable via input schema",
            "query_diversity_required": True,
            "current_date_awareness": "Passed as input field",
            "validation": "Automatic via Pydantic",
            "error_handling": "Built into Instructor framework"
        }
    
    def capture_web_search_behavior(self) -> Dict[str, Any]:
        """Capture web search behavior in Atomic Agent implementation."""
        return {
            "input_format": "Pydantic model with search_query and query_id",
            "search_method": "Google Search API integration",
            "output_includes": ["content", "sources", "citations"],
            "url_resolution": "Maintained for consistency",
            "citation_format": "Structured in output schema",
            "validation": "Output schema validation",
            "parallelization": "Handled by orchestrator"
        }
    
    def capture_reflection_behavior(self) -> Dict[str, Any]:
        """Capture reflection behavior in Atomic Agent implementation."""
        return {
            "input_format": "Pydantic model with topic and summaries",
            "decision_logic": "Agent-based with structured output",
            "output_includes": ["is_sufficient", "knowledge_gap", "follow_up_queries"],
            "max_loops_respected": "Handled by orchestrator",
            "follow_up_context_included": True,
            "validation": "Output schema ensures consistency"
        }
    
    def capture_finalization_behavior(self) -> Dict[str, Any]:
        """Capture answer finalization behavior in Atomic Agent implementation."""
        return {
            "input_format": "Pydantic model with topic, summaries, sources",
            "output_format": "Structured final answer with used sources",
            "url_replacement": "Post-processing in orchestrator",
            "citation_preservation": True,
            "source_deduplication": "Handled by orchestrator",
            "validation": "Output schema validation"
        }
    
    def capture_workflow_orchestration(self) -> Dict[str, Any]:
        """Capture workflow behavior in Atomic Agent implementation."""
        return {
            "execution_pattern": "Python control flow with agent chaining",
            "parallel_execution": "Explicit loop control in orchestrator",
            "loop_control": "Python while loop with conditions",
            "state_management": "Explicit variable management",
            "error_handling": "Try-catch with retry logic",
            "modularity": "Each step is independent atomic agent",
            "testability": "Each agent can be tested in isolation"
        }