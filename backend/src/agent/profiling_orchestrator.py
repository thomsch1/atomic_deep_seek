"""
Performance profiling orchestrator with detailed timing instrumentation.
Extends the base orchestrator to collect comprehensive performance metrics.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

from agent.orchestrator import ResearchOrchestrator
from agent.state import ResearchState, WebSearchInput
from agent.prompts import get_current_date


@dataclass
class StepTiming:
    """Individual step timing information."""
    step_name: str
    start_time: float
    end_time: float
    duration: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceProfile:
    """Complete performance profile for a research request."""
    total_duration: float
    frontend_to_backend: Optional[float] = None
    backend_processing: Optional[float] = None
    backend_to_frontend: Optional[float] = None
    
    # Detailed step timings
    query_generation: Optional[StepTiming] = None
    initial_searches: List[StepTiming] = field(default_factory=list)
    reflection_loops: List[StepTiming] = field(default_factory=list)
    finalization: Optional[StepTiming] = None
    
    # System metrics
    memory_usage: Dict[str, Any] = field(default_factory=dict)
    concurrency_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_duration": self.total_duration,
            "frontend_to_backend": self.frontend_to_backend,
            "backend_processing": self.backend_processing,
            "backend_to_frontend": self.backend_to_frontend,
            "query_generation": {
                "duration": self.query_generation.duration if self.query_generation else None,
                "details": self.query_generation.details if self.query_generation else {}
            },
            "initial_searches": [
                {
                    "duration": timing.duration,
                    "details": timing.details
                } for timing in self.initial_searches
            ],
            "reflection_loops": [
                {
                    "duration": timing.duration,
                    "details": timing.details
                } for timing in self.reflection_loops
            ],
            "finalization": {
                "duration": self.finalization.duration if self.finalization else None,
                "details": self.finalization.details if self.finalization else {}
            },
            "memory_usage": self.memory_usage,
            "concurrency_metrics": self.concurrency_metrics
        }


class ProfilingOrchestrator(ResearchOrchestrator):
    """Research orchestrator with performance profiling instrumentation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.performance_profile = PerformanceProfile(total_duration=0.0)
        self._request_start_time = None
    
    def start_profiling(self) -> None:
        """Start performance profiling for this request."""
        self._request_start_time = time.perf_counter()
        self.performance_profile = PerformanceProfile(total_duration=0.0)
    
    def _time_step(self, step_name: str, func, *args, **kwargs):
        """Time a specific step and record metrics."""
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            # Create timing record
            timing = StepTiming(
                step_name=step_name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                details={
                    "success": True,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys())
                }
            )
            
            # Store timing based on step type
            if step_name == "query_generation":
                self.performance_profile.query_generation = timing
                timing.details["queries_generated"] = len(result.queries) if hasattr(result, 'queries') else 0
            elif step_name.startswith("search_"):
                self.performance_profile.initial_searches.append(timing)
            elif step_name.startswith("reflection_"):
                self.performance_profile.reflection_loops.append(timing)
                timing.details["is_sufficient"] = getattr(result, 'is_sufficient', None)
                timing.details["follow_up_count"] = len(getattr(result, 'follow_up_queries', []))
            elif step_name == "finalization":
                self.performance_profile.finalization = timing
                timing.details["answer_length"] = len(getattr(result, 'final_answer', ''))
                timing.details["sources_used"] = len(getattr(result, 'used_sources', []))
            
            return result
            
        except Exception as e:
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            timing = StepTiming(
                step_name=step_name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                details={
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            
            # Store even failed timings
            if step_name.startswith("search_"):
                self.performance_profile.initial_searches.append(timing)
            elif step_name.startswith("reflection_"):
                self.performance_profile.reflection_loops.append(timing)
            
            raise
    
    def run_research(self, research_question: str, **kwargs) -> Dict[str, Any]:
        """Instrumented version of run_research with comprehensive profiling."""
        if not self._request_start_time:
            self.start_profiling()
            
        backend_start = time.perf_counter()
        
        try:
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
            
            # Step 1: Generate initial queries (timed)
            query_result = self._time_step("query_generation", self._generate_queries, state)
            state.add_search_queries(query_result.queries)
            
            # Step 2: Perform initial web searches (timed parallel)
            research_topic = self._get_research_topic(state.messages)
            search_results = self._time_step("search_initial", 
                self._perform_web_searches_profiled, 
                query_result.queries, research_topic, "initial"
            )
            
            # Batch update state for better performance
            self._batch_update_state(state, search_results)
            
            # Step 3: Research loop with reflection (timed)
            loop_index = 0
            while state.research_loop_count < state.max_research_loops:
                reflection_result = self._time_step(f"reflection_{loop_index}", 
                    self._reflect_on_research, state
                )
                
                if reflection_result.is_sufficient:
                    break
                
                # Perform follow-up searches
                if reflection_result.follow_up_queries:
                    follow_up_results = self._time_step(f"search_followup_{loop_index}",
                        self._perform_web_searches_profiled,
                        reflection_result.follow_up_queries, research_topic, f"followup_{loop_index}"
                    )
                    
                    # Batch update state for better performance
                    self._batch_update_state(state, follow_up_results)
                
                state.research_loop_count += 1
                loop_index += 1
            
            # Step 4: Finalize answer (timed)
            final_result = self._time_step("finalization", self._finalize_answer, state)
            
            # Add final message to state
            state.add_message("assistant", final_result.final_answer)
            
            # Calculate backend processing time
            backend_end = time.perf_counter()
            self.performance_profile.backend_processing = backend_end - backend_start
            
            # Validate search quality (check for fallback usage)
            search_quality = self._validate_search_quality(state.sources_gathered)
            
            # Build result with profiling data
            result = {
                "messages": [msg.model_dump() for msg in state.messages],
                "sources_gathered": [src.model_dump() for src in final_result.used_sources],
                "research_loops_executed": state.research_loop_count,
                "total_queries": len(state.search_queries),
                "final_answer": final_result.final_answer,
                "performance_profile": self.performance_profile.to_dict(),
                "search_quality": search_quality
            }
            
            # Calculate total duration
            if self._request_start_time:
                self.performance_profile.total_duration = time.perf_counter() - self._request_start_time
            
            return result
            
        except Exception as e:
            # Even on error, record what we can
            backend_end = time.perf_counter()
            self.performance_profile.backend_processing = backend_end - backend_start
            if self._request_start_time:
                self.performance_profile.total_duration = time.perf_counter() - self._request_start_time
            raise
    
    def _perform_web_searches_profiled(self, queries: List[str], research_topic: str, search_type: str) -> List[Any]:
        """Profiled version of web searches with concurrency metrics."""
        results = []
        current_date = self._get_current_date()
        
        # Handle empty queries list
        if not queries:
            return results
        
        # Record concurrency metrics
        concurrency_start = time.perf_counter()
        
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
        individual_timings = []
        for future in as_completed(future_to_query):
            search_start = time.perf_counter()
            try:
                result = future.result()
                search_end = time.perf_counter()
                individual_timings.append(search_end - search_start)
                results.append(result)
            except Exception as e:
                search_end = time.perf_counter()
                individual_timings.append(search_end - search_start)
                error_msg = f"Search failed for query '{future_to_query[future]}': {e}"
                print(f"❌ {error_msg}")
                # Continue with other searches
        
        # Record concurrency metrics
        concurrency_end = time.perf_counter()
        concurrency_key = f"{search_type}_searches"
        self.performance_profile.concurrency_metrics[concurrency_key] = {
            "total_duration": concurrency_end - concurrency_start,
            "queries_count": len(queries),
            "successful_results": len(results),
            "individual_timings": individual_timings,
            "min_timing": min(individual_timings) if individual_timings else 0,
            "max_timing": max(individual_timings) if individual_timings else 0,
            "avg_timing": sum(individual_timings) / len(individual_timings) if individual_timings else 0
        }
        
        return results
    
    async def run_research_async(self, research_question: str, **kwargs) -> Dict[str, Any]:
        """Async version with profiling."""
        self.start_profiling()
        
        # Record frontend to backend timing (if available)
        if "frontend_start_time" in kwargs:
            frontend_start = kwargs.pop("frontend_start_time")
            self.performance_profile.frontend_to_backend = time.perf_counter() - frontend_start
        
        loop = asyncio.get_event_loop()
        
        # Create a wrapper function to handle kwargs properly
        def research_wrapper():
            return self.run_research(research_question, **kwargs)
            
        result = await loop.run_in_executor(None, research_wrapper)
        
        # Record backend to frontend timing
        self.performance_profile.backend_to_frontend = time.perf_counter() - self._request_start_time
        
        # Update the performance profile in the result
        result["performance_profile"] = self.performance_profile.to_dict()
        
        return result
    
    def _validate_search_quality(self, sources: List) -> Dict[str, Any]:
        """Validate search quality and detect fallback usage."""
        if not sources:
            return {
                "total_sources": 0,
                "quality_score": 0.0,
                "has_real_search": False,
                "has_fallback": False,
                "warning": "No sources found"
            }
        
        source_types = {
            "gemini_grounding": 0,
            "google_custom": 0,
            "searchapi": 0,
            "duckduckgo": 0,
            "gemini_knowledge": 0,
            "knowledge_base": 0,
            "unknown": 0
        }
        
        for source in sources:
            url = source.url if hasattr(source, 'url') else ""
            
            if "grounding-api-redirect" in url:
                source_types["gemini_grounding"] += 1
            elif "example.com" in url:
                source_types["knowledge_base"] += 1
            elif url and url.startswith("http"):
                source_types["unknown"] += 1
            else:
                source_types["unknown"] += 1
        
        total_sources = len(sources)
        has_real_search = (source_types["gemini_grounding"] + 
                          source_types["google_custom"] + 
                          source_types["searchapi"] + 
                          source_types["duckduckgo"]) > 0
        has_fallback = source_types["knowledge_base"] > 0
        
        # Calculate quality score (0-1)
        quality_score = 0.0
        if total_sources > 0:
            quality_score = (
                source_types["gemini_grounding"] * 1.0 +
                source_types["google_custom"] * 0.8 +
                source_types["searchapi"] * 0.7 +
                source_types["duckduckgo"] * 0.6 +
                source_types["gemini_knowledge"] * 0.4 +
                source_types["knowledge_base"] * 0.1
            ) / total_sources
        
        return {
            "total_sources": total_sources,
            "source_breakdown": source_types,
            "quality_score": quality_score,
            "has_real_search": has_real_search,
            "has_fallback": has_fallback,
            "is_high_quality": quality_score > 0.7 and has_real_search and not has_fallback
        }


def create_profiling_orchestrator(config: Optional[Dict[str, Any]] = None) -> ProfilingOrchestrator:
    """Create a profiling orchestrator instance."""
    return ProfilingOrchestrator(config)