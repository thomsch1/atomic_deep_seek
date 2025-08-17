#!/usr/bin/env python3
"""
Demo script to show the performance profiling in action.
Shows detailed timing breakdown for a simple research query.
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# Add backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent.profiling_orchestrator import create_profiling_orchestrator


async def demo_profiling():
    """Demonstrate the performance profiling capabilities."""
    
    print("🚀 Performance Profiling Demo")
    print("=" * 50)
    print()
    
    # Create profiling orchestrator
    orchestrator = create_profiling_orchestrator()
    
    # Test question
    question = "Give an overview of all models that are suitable to predict with intermittent demand order data in a warehouse."
    print(f"📋 Research Question: {question}")
    print()
    
    try:
        print("⏱️  Starting timed research...")
        
        # Run research with profiling
        result = await orchestrator.run_research_async(
            question,
            initial_search_query_count=2,
            max_research_loops=1
        )
        
        print("✅ Research completed!")
        print()
        
        # Extract and display performance data
        profile = result.get('performance_profile', {})
        
        print("📊 Performance Breakdown")
        print("-" * 30)
        
        # Total timing
        total_duration = profile.get('total_duration', 0)
        backend_duration = profile.get('backend_processing', 0)
        print(f"Total Duration: {total_duration:.3f}s")
        print(f"Backend Processing: {backend_duration:.3f}s")
        print()
        
        # Step-by-step timing
        print("🔍 Step-by-Step Timing:")
        
        # Query generation
        query_gen = profile.get('query_generation', {})
        if query_gen.get('duration'):
            print(f"  Query Generation: {query_gen['duration']:.3f}s")
            if query_gen.get('details', {}).get('queries_generated'):
                print(f"    Generated {query_gen['details']['queries_generated']} queries")
        
        # Initial searches
        initial_searches = profile.get('initial_searches', [])
        if initial_searches:
            search_durations = [s['duration'] for s in initial_searches if 'duration' in s]
            if search_durations:
                total_search_time = sum(search_durations)
                avg_search_time = total_search_time / len(search_durations)
                print(f"  Initial Searches: {total_search_time:.3f}s total, {avg_search_time:.3f}s avg")
                print(f"    {len(search_durations)} searches completed")
        
        # Reflection loops
        reflection_loops = profile.get('reflection_loops', [])
        if reflection_loops:
            reflection_durations = [r['duration'] for r in reflection_loops if 'duration' in r]
            if reflection_durations:
                total_reflection_time = sum(reflection_durations)
                print(f"  Reflection Analysis: {total_reflection_time:.3f}s")
                for i, loop in enumerate(reflection_loops):
                    if 'duration' in loop:
                        details = loop.get('details', {})
                        sufficient = details.get('is_sufficient', 'unknown')
                        followup_count = details.get('follow_up_count', 0)
                        print(f"    Loop {i+1}: {loop['duration']:.3f}s (sufficient: {sufficient}, follow-ups: {followup_count})")
        
        # Finalization
        finalization = profile.get('finalization', {})
        if finalization.get('duration'):
            print(f"  Answer Finalization: {finalization['duration']:.3f}s")
            details = finalization.get('details', {})
            answer_length = details.get('answer_length', 0)
            sources_used = details.get('sources_used', 0)
            print(f"    Answer length: {answer_length} chars, Sources used: {sources_used}")
        
        print()
        
        # Concurrency metrics
        concurrency = profile.get('concurrency_metrics', {})
        if concurrency:
            print("🚀 Concurrency Analysis:")
            for search_type, metrics in concurrency.items():
                queries_count = metrics.get('queries_count', 0)
                total_time = metrics.get('total_duration', 0)
                avg_time = metrics.get('avg_timing', 0)
                min_time = metrics.get('min_timing', 0)
                max_time = metrics.get('max_timing', 0)
                
                print(f"  {search_type}:")
                print(f"    Queries: {queries_count}, Total: {total_time:.3f}s")
                print(f"    Individual: min {min_time:.3f}s, max {max_time:.3f}s, avg {avg_time:.3f}s")
                
                # Calculate parallel efficiency
                if queries_count > 1 and max_time > 0:
                    efficiency = total_time / max_time
                    print(f"    Parallel efficiency: {efficiency:.1%}")
        
        print()
        
        # Research results summary
        print("📋 Research Results Summary:")
        print(f"  Final answer length: {len(result.get('final_answer', ''))}")
        print(f"  Sources gathered: {len(result.get('sources_gathered', []))}")
        print(f"  Research loops: {result.get('research_loops_executed', 0)}")
        print(f"  Total queries: {result.get('total_queries', 0)}")
        
        print()
        print("💡 Performance Insights:")
        
        # Generate insights
        if backend_duration > 10:
            print("  ⚠️ Backend processing exceeded 10 seconds")
        elif backend_duration > 5:
            print("  ⚡ Backend processing time is moderate")
        else:
            print("  ✅ Backend processing time is good")
        
        # Check search efficiency
        if concurrency:
            for search_type, metrics in concurrency.items():
                if metrics.get('queries_count', 0) > 1:
                    efficiency = metrics.get('total_duration', 0) / metrics.get('max_timing', 1)
                    if efficiency < 0.6:
                        print(f"  🚀 {search_type} shows excellent parallel efficiency")
                    elif efficiency < 0.8:
                        print(f"  ⚡ {search_type} shows good parallel efficiency")
                    else:
                        print(f"  ⚠️ {search_type} may benefit from optimization")
        
        # Save detailed profile to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        profile_file = f"demo_profile_{timestamp}.json"
        
        with open(profile_file, 'w') as f:
            json.dump({
                'question': question,
                'performance_profile': profile,
                'result_summary': {
                    'answer_length': len(result.get('final_answer', '')),
                    'sources_count': len(result.get('sources_gathered', [])),
                    'loops_executed': result.get('research_loops_executed', 0),
                    'total_queries': result.get('total_queries', 0)
                },
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"\n💾 Detailed profile saved to: {profile_file}")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        raise
    
    finally:
        # Clean up
        orchestrator._cleanup_thread_pool()


if __name__ == "__main__":
    asyncio.run(demo_profiling())