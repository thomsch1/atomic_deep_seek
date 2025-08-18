"""
Research workflow orchestrator using Atomic Agents.
Replaces the LangGraph-based execution with Python control flow.
"""

import asyncio
import atexit
import os
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from agent.agents.query_generation_agent import QueryGenerationAgent
from agent.agents.web_search_agent import WebSearchAgent
from agent.agents.reflection_agent import ReflectionAgent
from agent.agents.finalization_agent import FinalizationAgent
from agent.configuration import Configuration
from agent.state import (
    ResearchState,
    Message,
    Source,
    QueryGenerationInput,
    WebSearchInput,
    ReflectionInput,
    FinalizationInput,
)
from agent.prompts import get_current_date
from agent.utils import get_research_topic


class ResearchOrchestrator:
    """Orchestrates the complete research workflow using Atomic Agents."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the orchestrator with configuration."""
        self.config = Configuration.from_config_dict(config)
        
        # Lazy-initialized agents (created on first access)
        self._query_agent = None
        self._search_agent = None
        self._reflection_agent = None
        self._finalization_agent = None
        
        # Persistent thread pool for better performance
        self._thread_pool = None
        self._init_thread_pool()
        
        # Request-scoped cache for expensive operations
        self._research_topic_cache = None
        self._current_date_cache = None
    
    def _init_thread_pool(self):
        """Initialize persistent thread pool with optimal sizing."""
        # Optimal thread count: CPU cores + I/O factor
        max_workers = min(max(os.cpu_count() * 2, 4), 10)
        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        
        # Register cleanup on exit
        atexit.register(self._cleanup_thread_pool)
    
    def _cleanup_thread_pool(self):
        """Clean up thread pool resources."""
        if self._thread_pool and not self._thread_pool._shutdown:
            self._thread_pool.shutdown(wait=True)
    
    @property
    def query_agent(self):
        """Lazy-loaded query generation agent."""
        if self._query_agent is None:
            self._query_agent = QueryGenerationAgent(self.config)
        return self._query_agent
    
    @property
    def search_agent(self):
        """Lazy-loaded web search agent."""
        if self._search_agent is None:
            self._search_agent = WebSearchAgent(self.config)
        return self._search_agent
    
    @property
    def reflection_agent(self):
        """Lazy-loaded reflection agent."""
        if self._reflection_agent is None:
            self._reflection_agent = ReflectionAgent(self.config)
        return self._reflection_agent
    
    def create_finalization_agent(self, model_override: Optional[str] = None):
        """Create a finalization agent with optional model override."""
        return FinalizationAgent(self.config, model_override)
    
    @property
    def finalization_agent(self):
        """Lazy-loaded finalization agent (for backward compatibility)."""
        if self._finalization_agent is None:
            self._finalization_agent = FinalizationAgent(self.config)
        return self._finalization_agent
    
    def _get_research_topic(self, messages):
        """Get research topic with request-scoped caching."""
        if self._research_topic_cache is None:
            self._research_topic_cache = get_research_topic(messages)
        return self._research_topic_cache
    
    def _get_current_date(self):
        """Get current date with request-scoped caching."""
        if self._current_date_cache is None:
            self._current_date_cache = get_current_date()
        return self._current_date_cache
    
    def _clear_request_cache(self):
        """Clear request-scoped cache for new request."""
        self._research_topic_cache = None
        self._current_date_cache = None
    
    def run_research(self, research_question: str, **kwargs) -> Dict[str, Any]:
        """
        Run the complete research workflow.
        
        Args:
            research_question: The research question to investigate
            **kwargs: Optional parameters like initial_search_query_count, 
                     max_research_loops, reasoning_model
        
        Returns:
            Dictionary containing the final answer and metadata
        """
        
        # Clear request-scoped cache for new request
        self._clear_request_cache()
        
        # Initialize state
        state = ResearchState(
            initial_search_query_count=kwargs.get('initial_search_query_count', 3),
            max_research_loops=kwargs.get('max_research_loops', 2),
            reasoning_model=kwargs.get('reasoning_model')
        )
        
        # Add initial user message
        state.add_message("user", research_question)
        
        # Step 1: Generate initial queries
        query_result = self._generate_queries(state)
        state.add_search_queries(query_result.queries)
        
        # Step 2: Perform initial web searches (parallel)
        research_topic = self._get_research_topic(state.messages)
        search_results = self._perform_web_searches(
            query_result.queries, 
            research_topic
        )
        
        # Batch update state for better performance
        self._batch_update_state(state, search_results)
        
        # Step 3: Research loop with reflection
        while state.research_loop_count < state.max_research_loops:
            reflection_result = self._reflect_on_research(state)
            
            if reflection_result.is_sufficient:
                break
            
            # Perform follow-up searches
            if reflection_result.follow_up_queries:
                follow_up_results = self._perform_web_searches(
                    reflection_result.follow_up_queries,
                    research_topic
                )
                
                # Batch update state for better performance
                self._batch_update_state(state, follow_up_results)
            
            state.research_loop_count += 1
        
        # Step 4: Finalize answer
        final_result = self._finalize_answer(state)
        
        # Add final message to state
        state.add_message("assistant", final_result.final_answer)
        
        return {
            "messages": [msg.model_dump() for msg in state.messages],
            "sources_gathered": [src.model_dump() for src in final_result.used_sources],
            "research_loops_executed": state.research_loop_count,
            "total_queries": len(state.search_queries),
            "final_answer": final_result.final_answer
        }
    
    def _generate_queries(self, state: ResearchState):
        """Generate initial search queries."""
        input_data = QueryGenerationInput(
            research_topic=self._get_research_topic(state.messages),
            number_of_queries=state.initial_search_query_count,
            current_date=self._get_current_date()
        )
        
        return self.query_agent.run(input_data)
    
    def _perform_web_searches(self, queries: List[str], research_topic: str) -> List[Any]:
        """Perform web searches in parallel."""
        results = []
        current_date = self._get_current_date()
        
        # Handle empty queries list
        if not queries:
            return results
        
        # Use persistent ThreadPool for parallel execution
        executor = self._thread_pool
        # Submit all search tasks
        future_to_query = {
            executor.submit(
                self.search_agent.run,
                WebSearchInput(
                    search_query=query,
                    query_id=idx,
                    current_date=current_date
                )
            ): query for idx, query in enumerate(queries)
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_query):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                error_msg = f"Search failed for query '{future_to_query[future]}': {e}"
                print(f"❌ {error_msg}")
                # TODO: Consider adding this error to the final result metadata
                # Continue with other searches
        
        return results
    
    def _reflect_on_research(self, state: ResearchState):
        """Analyze research sufficiency."""
        input_data = ReflectionInput(
            research_topic=self._get_research_topic(state.messages),
            summaries=state.web_research_results,
            current_loop=state.research_loop_count
        )
        
        return self.reflection_agent.run(input_data)
    
    def _finalize_answer(self, state: ResearchState):
        """Generate final answer."""
        input_data = FinalizationInput(
            research_topic=self._get_research_topic(state.messages),
            summaries=state.web_research_results,
            sources=state.sources_gathered,
            current_date=self._get_current_date()
        )
        
        # Use reasoning_model override if provided, otherwise use default
        finalization_agent = self.create_finalization_agent(state.reasoning_model)
        return finalization_agent.run(input_data)
    
    def _batch_update_state(self, state: ResearchState, search_results: List[Any]):
        """Batch update state to minimize memory operations."""
        if not search_results:
            return
        
        # Collect all content and sources first
        contents = []
        all_sources = []
        
        for result in search_results:
            if result.content:
                contents.append(result.content)
            if result.sources:
                all_sources.extend(result.sources)
        
        # Batch update state
        if contents:
            state.web_research_results.extend(contents)
        if all_sources:
            state.sources_gathered.extend(all_sources)
    
    async def run_research_async(self, research_question: str, **kwargs) -> Dict[str, Any]:
        """Async version of research workflow."""
        # For now, wrap the sync version
        # In the future, this could be fully async with async agents
        loop = asyncio.get_event_loop()
        
        # Create a wrapper function to handle kwargs properly
        def research_wrapper():
            return self.run_research(research_question, **kwargs)
            
        return await loop.run_in_executor(None, research_wrapper)


# Compatibility function to maintain existing interface
def create_research_graph(config: Optional[Dict[str, Any]] = None):
    """Create a research orchestrator (replaces LangGraph graph)."""
    return ResearchOrchestrator(config)


# Factory function for creating orchestrator instances (thread-safe)
def create_orchestrator(config: Optional[Dict[str, Any]] = None) -> ResearchOrchestrator:
    """Create a new orchestrator instance for each request to ensure thread safety."""
    return ResearchOrchestrator(config)


def invoke_research(state_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoke research workflow (replaces graph.invoke).
    Thread-safe version that creates a new orchestrator per request.
    
    Args:
        state_dict: Dictionary containing messages and config parameters
    
    Returns:
        Dictionary with results in LangGraph-compatible format
    """
    
    # Extract research question from messages
    messages = state_dict.get("messages", [])
    if not messages:
        raise ValueError("No messages provided")
    
    # Handle both Message objects and dicts
    if isinstance(messages[-1], dict):
        research_question = messages[-1]["content"]
    else:
        research_question = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
    
    # Extract configuration parameters
    config_params = {
        "initial_search_query_count": state_dict.get("initial_search_query_count", 3),
        "max_research_loops": state_dict.get("max_research_loops", 2),
        "reasoning_model": state_dict.get("reasoning_model")
    }
    
    # Create new orchestrator instance for this request (thread-safe)
    orchestrator = create_orchestrator()
    
    try:
        # Run the research
        return orchestrator.run_research(research_question, **config_params)
    finally:
        # Ensure thread pool cleanup
        orchestrator._cleanup_thread_pool()