"""
Shared pytest configuration and fixtures for migration testing.
"""

import pytest
import os
from unittest.mock import patch
from typing import Dict, Any


@pytest.fixture
def mock_environment():
    """Mock environment variables for all tests."""
    env_vars = {
        "GEMINI_API_KEY": "test-gemini-key",
        "GOOGLE_SEARCH_API_KEY": "test-search-key",
        "GOOGLE_SEARCH_ENGINE_ID": "test-engine-id"
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def sample_research_topics():
    """Provide sample research topics for testing."""
    return [
        "What are the latest developments in quantum computing in 2024?",
        "How has artificial intelligence evolved in the healthcare sector?",
        "What are the current trends in renewable energy technology?",
        "What breakthroughs have been made in space exploration recently?"
    ]


@pytest.fixture
def expected_test_outputs():
    """Define expected outputs for comparison testing."""
    return {
        "query_generation": {
            "langchain": {
                "search_query": ["query1", "query2", "query3"],
                "rationale": "Generated queries for research"
            },
            "atomic_agent": {
                "queries": ["query1", "query2", "query3"],
                "rationale": "Generated queries for research"
            }
        },
        "web_research": {
            "langchain": {
                "sources_gathered": [{"url": "test.com", "title": "Test Source"}],
                "web_research_result": ["Research content"],
                "search_query": ["test query"]
            },
            "atomic_agent": {
                "content": "Research content",
                "sources": [{"url": "test.com", "title": "Test Source"}],
                "citations": [{"start": 0, "end": 10}]
            }
        },
        "reflection": {
            "langchain": {
                "is_sufficient": False,
                "knowledge_gap": "Missing performance data",
                "follow_up_queries": ["performance metrics query"],
                "research_loop_count": 1
            },
            "atomic_agent": {
                "is_sufficient": False,
                "knowledge_gap": "Missing performance data",
                "follow_up_queries": ["performance metrics query"]
            }
        },
        "finalization": {
            "langchain": {
                "messages": [{"role": "assistant", "content": "Final answer"}],
                "sources_gathered": [{"url": "source.com", "title": "Source"}]
            },
            "atomic_agent": {
                "final_answer": "Final answer",
                "used_sources": [{"url": "source.com", "title": "Source"}]
            }
        }
    }


@pytest.fixture
def performance_thresholds():
    """Define performance thresholds for comparison."""
    return {
        "max_acceptable_slowdown": 2.0,  # 2x slower is acceptable
        "min_functionality_match": 0.9,  # 90% functionality match required
        "min_maintainability_score": 6    # Minimum maintainability score
    }


@pytest.fixture
def mock_llm_responses():
    """Provide mock LLM responses for consistent testing."""
    return {
        "query_generation": {
            "queries": [
                "quantum computing breakthroughs 2024",
                "quantum algorithms research latest",
                "quantum hardware developments"
            ],
            "rationale": "These queries comprehensively cover quantum computing developments"
        },
        "web_search": {
            "content": "Quantum computing has achieved significant milestones in 2024...",
            "sources": [
                {"title": "Quantum Research Journal", "url": "https://quantum-research.com/2024"}
            ]
        },
        "reflection": {
            "is_sufficient": False,
            "knowledge_gap": "Need more specific performance benchmarks",
            "follow_up_queries": ["quantum computing performance benchmarks 2024"]
        },
        "finalization": {
            "final_answer": "Based on comprehensive research, quantum computing in 2024 has seen remarkable progress...",
            "citations": ["quantum-research.com", "nature.com/quantum"]
        }
    }


class TestHelpers:
    """Helper functions for testing."""
    
    @staticmethod
    def validate_output_structure(output: Dict[str, Any], expected_fields: list) -> bool:
        """Validate that output contains all expected fields."""
        return all(field in output for field in expected_fields)
    
    @staticmethod
    def compare_lists_content(list1: list, list2: list, tolerance: float = 0.8) -> bool:
        """Compare two lists with tolerance for minor differences."""
        if not list1 and not list2:
            return True
        
        if len(list1) == 0 or len(list2) == 0:
            return False
        
        # For string lists, compare content similarity
        if isinstance(list1[0], str) and isinstance(list2[0], str):
            matches = sum(1 for item1 in list1 if any(
                item1.lower() in item2.lower() or item2.lower() in item1.lower()
                for item2 in list2
            ))
            return (matches / len(list1)) >= tolerance
        
        # For other types, do exact comparison
        return list1 == list2
    
    @staticmethod
    def extract_metrics_from_result(result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from test result."""
        return {
            "execution_time": result.get("execution_time", 0),
            "success": result.get("success", False),
            "output_keys": list(result.get("output_structure", {}).keys()),
            "error_message": result.get("error_message", "")
        }


@pytest.fixture
def test_helpers():
    """Provide test helper functions."""
    return TestHelpers()