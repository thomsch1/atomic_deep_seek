#!/usr/bin/env python3
"""
Simple migration test to verify that the Atomic Agent implementation works.
This test bypasses the old LangChain dependencies and focuses on the new implementation.
"""

import os
import sys
sys.path.insert(0, './src')

import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

# Test imports
def test_imports():
    """Test that all new modules can be imported successfully."""
    
    # Test state models import
    from agent.state import (
        ResearchState, Message, Source, Citation,
        QueryGenerationInput, QueryGenerationOutput,
        WebSearchInput, WebSearchOutput,
        ReflectionInput, ReflectionOutput,
        FinalizationInput, FinalizationOutput
    )
    
    # Test configuration import
    from agent.configuration import Configuration
    
    # Test orchestrator import  
    from agent.orchestrator import ResearchOrchestrator, invoke_research
    
    print("✅ All imports successful")


def test_pydantic_models():
    """Test that Pydantic models work correctly."""
    
    from agent.state import ResearchState, Message, Source
    
    # Test Message creation
    message = Message(role="user", content="Test message")
    assert message.role == "user"
    assert message.content == "Test message"
    
    # Test Source creation
    source = Source(
        title="Test Source",
        url="https://example.com",
        short_url="https://short.url/1"
    )
    assert source.title == "Test Source"
    assert source.url == "https://example.com"
    
    # Test ResearchState creation
    state = ResearchState()
    assert len(state.messages) == 0
    assert len(state.search_queries) == 0
    assert state.initial_search_query_count == 3
    assert state.max_research_loops == 2
    
    # Test adding messages
    state.add_message("user", "Hello")
    assert len(state.messages) == 1
    assert state.messages[0].role == "user"
    assert state.messages[0].content == "Hello"
    
    print("✅ Pydantic models working correctly")


def test_configuration():
    """Test the configuration system."""
    
    from agent.configuration import Configuration
    
    # Test default configuration
    config = Configuration()
    assert config.query_generator_model == "gemini-2.0-flash"
    assert config.reflection_model == "gemini-2.5-flash"
    assert config.answer_model == "gemini-2.5-pro"
    assert config.number_of_initial_queries == 3
    assert config.max_research_loops == 2
    
    # Test custom configuration
    config = Configuration(
        query_generator_model="custom-model",
        max_research_loops=5
    )
    assert config.query_generator_model == "custom-model"
    assert config.max_research_loops == 5
    
    # Test from_config_dict
    config_dict = {"max_research_loops": 3}
    config = Configuration.from_config_dict(config_dict)
    assert config.max_research_loops == 3
    
    print("✅ Configuration system working correctly")


@patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
def test_orchestrator_creation():
    """Test that the orchestrator can be created."""
    
    from agent.orchestrator import ResearchOrchestrator
    
    # Test creation with default config
    orchestrator = ResearchOrchestrator()
    assert orchestrator.config is not None
    assert hasattr(orchestrator, 'query_agent')
    assert hasattr(orchestrator, 'search_agent')
    assert hasattr(orchestrator, 'reflection_agent')
    assert hasattr(orchestrator, 'finalization_agent')
    
    # Test creation with custom config
    config = {"max_research_loops": 5}
    orchestrator = ResearchOrchestrator(config)
    assert orchestrator.config.max_research_loops == 5
    
    print("✅ Orchestrator creation successful")


def test_input_output_schemas():
    """Test that input/output schemas validate correctly."""
    
    from agent.state import (
        QueryGenerationInput, QueryGenerationOutput,
        WebSearchInput, WebSearchOutput,
        ReflectionInput, ReflectionOutput,
        FinalizationInput, FinalizationOutput
    )
    
    # Test QueryGeneration schemas
    query_input = QueryGenerationInput(
        research_topic="Test topic",
        current_date="2025-01-08"
    )
    assert query_input.research_topic == "Test topic"
    assert query_input.number_of_queries == 3  # default
    
    query_output = QueryGenerationOutput(
        queries=["query1", "query2", "query3"],
        rationale="Test rationale"
    )
    assert len(query_output.queries) == 3
    
    # Test WebSearch schemas
    search_input = WebSearchInput(
        search_query="test query",
        query_id=0,
        current_date="2025-01-08"
    )
    assert search_input.search_query == "test query"
    
    search_output = WebSearchOutput(
        content="Test content",
        sources=[],
        citations=[]
    )
    assert search_output.content == "Test content"
    
    # Test Reflection schemas
    reflection_input = ReflectionInput(
        research_topic="Test topic",
        summaries=["Summary 1", "Summary 2"],
        current_loop=1
    )
    assert len(reflection_input.summaries) == 2
    
    reflection_output = ReflectionOutput(
        is_sufficient=True,
        knowledge_gap="",
        follow_up_queries=[]
    )
    assert reflection_output.is_sufficient is True
    
    print("✅ Input/output schemas validation successful")


def test_compatibility_interface():
    """Test that the compatibility interface works."""
    
    # This tests the graph.py compatibility wrapper
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}):
        from agent.orchestrator import ResearchOrchestrator
        from agent.configuration import Configuration
        
        # Test that ResearchOrchestrator exists and can be instantiated
        config = Configuration()
        orchestrator = ResearchOrchestrator(config)
        assert hasattr(orchestrator, 'run_research')
        assert hasattr(orchestrator, 'arun_research')
        assert graph.name == "atomic-research-agent"
        
        print("✅ Compatibility interface working")


@patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
def test_invoke_research_interface():
    """Test the invoke_research compatibility function."""
    
    from agent.orchestrator import invoke_research
    
    # Create test state similar to LangGraph format
    test_state = {
        "messages": [{"role": "user", "content": "Test research question"}],
        "initial_search_query_count": 2,
        "max_research_loops": 1
    }
    
    # Mock the orchestrator run_research method to avoid actual API calls
    with patch('agent.orchestrator.ResearchOrchestrator.run_research') as mock_run:
        mock_run.return_value = {
            "messages": [
                {"role": "user", "content": "Test research question"},
                {"role": "assistant", "content": "Test answer"}
            ],
            "sources_gathered": [
                {"title": "Test Source", "url": "https://test.com"}
            ],
            "research_loops_executed": 1,
            "total_queries": 2,
            "final_answer": "Test answer"
        }
        
        result = invoke_research(test_state)
        
        # Verify the result has the expected structure
        assert "messages" in result
        assert "sources_gathered" in result
        assert "research_loops_executed" in result
        assert "total_queries" in result
        assert "final_answer" in result
        
        # Verify the orchestrator was called with correct parameters
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "initial_search_query_count" in call_args.kwargs
        assert call_args.kwargs["initial_search_query_count"] == 2
        assert call_args.kwargs["max_research_loops"] == 1
        
    print("✅ invoke_research interface working correctly")


def test_error_handling():
    """Test error handling in various scenarios."""
    
    from agent.state import Message
    from agent.orchestrator import invoke_research
    
    # Test invalid message format
    with pytest.raises(ValueError, match="No messages provided"):
        invoke_research({})
    
    # Test invalid pydantic model
    with pytest.raises(ValidationError):
        Message(content="Test")  # Missing required 'role' field
    
    print("✅ Error handling working correctly")


def run_all_tests():
    """Run all tests and provide a summary."""
    
    test_functions = [
        test_imports,
        test_pydantic_models, 
        test_configuration,
        test_orchestrator_creation,
        test_input_output_schemas,
        test_compatibility_interface,
        test_invoke_research_interface,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    print("🧪 Starting Atomic Agent Migration Tests...")
    print("=" * 60)
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} FAILED: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED - Migration is successful!")
        return True
    else:
        print(f"⚠️  {failed} tests failed - Migration needs attention")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)