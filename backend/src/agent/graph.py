"""
Research agent workflow using Atomic Agents.
This file maintains compatibility with existing interfaces while using the new orchestrator.
"""

from agent.orchestrator import ResearchOrchestrator, invoke_research

# Create the main orchestrator instance
orchestrator = ResearchOrchestrator()

# Compatibility object that mimics the old LangGraph interface
class GraphCompat:
    """Compatibility wrapper to maintain existing graph interface."""
    
    def __init__(self, orchestrator: ResearchOrchestrator):
        self.orchestrator = orchestrator
        self.name = "atomic-research-agent"
    
    def invoke(self, state_dict, config=None):
        """Invoke the research workflow (replaces LangGraph invoke)."""
        return invoke_research(state_dict)
    
    async def ainvoke(self, state_dict, config=None):
        """Async invoke (replaces LangGraph ainvoke)."""
        return await self.orchestrator.run_research_async(
            state_dict.get("messages", [{}])[-1].get("content", ""),
            **{
                k: v for k, v in state_dict.items() 
                if k in ["initial_search_query_count", "max_research_loops", "reasoning_model"]
            }
        )

# Create the graph object for backward compatibility
graph = GraphCompat(orchestrator)

# Export the main components
__all__ = ["graph", "orchestrator", "invoke_research"]