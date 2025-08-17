#!/usr/bin/env python3
"""
Comprehensive performance profiling test for the deep search system.
Tests end-to-end timing from frontend input to final answer display.
"""

import sys
import os
import time
import json
import asyncio
import aiohttp
import statistics
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import argparse

# Add backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/src'))

from agent.profiling_orchestrator import ProfilingOrchestrator, create_profiling_orchestrator


@dataclass
class TestScenario:
    """A test scenario with specific parameters."""
    name: str
    question: str
    initial_search_query_count: int = 3
    max_research_loops: int = 2
    reasoning_model: Optional[str] = None
    expected_duration_range: tuple = (5.0, 30.0)  # (min, max) expected seconds


@dataclass
class TestResult:
    """Results from a single test run."""
    scenario_name: str
    success: bool
    total_duration: float
    performance_profile: Dict[str, Any]
    error_message: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class PerformanceProfiler:
    """Comprehensive performance profiling test suite."""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url.rstrip('/')
        self.results: List[TestResult] = []
        
        # Define test scenarios
        self.scenarios = [
            TestScenario(
                name="simple_factual",
                question="What is the largest city and capital of France?",
                initial_search_query_count=1,
                max_research_loops=1,
                expected_duration_range=(2.0, 8.0)
            ),
            TestScenario(
                name="medium_research",
                question="What are the latest developments in quantum computing in 2024?",
                initial_search_query_count=3,
                max_research_loops=2,
                expected_duration_range=(8.0, 20.0)
            ),
            TestScenario(
                name="complex_analysis",
                question="Compare the economic impacts of renewable energy adoption vs traditional fossil fuels in developing countries",
                initial_search_query_count=5,
                max_research_loops=3,
                expected_duration_range=(15.0, 40.0)
            ),
            TestScenario(
                name="technical_deep_dive",
                question="Explain the technical architecture and performance characteristics of Kubernetes container orchestration, including recent improvements in version 1.29",
                initial_search_query_count=4,
                max_research_loops=2,
                expected_duration_range=(10.0, 25.0)
            )
        ]
    
    async def test_direct_orchestrator(self, scenario: TestScenario, iterations: int = 1) -> List[TestResult]:
        """Test direct orchestrator performance (bypass HTTP)."""
        print(f"\n🧪 Testing Direct Orchestrator: {scenario.name}")
        print(f"   Question: {scenario.question}")
        print(f"   Parameters: {scenario.initial_search_query_count} queries, {scenario.max_research_loops} loops")
        
        results = []
        
        for i in range(iterations):
            print(f"   Run {i+1}/{iterations}...")
            
            # Create fresh orchestrator for each test
            orchestrator = create_profiling_orchestrator()
            
            try:
                start_time = time.perf_counter()
                
                # Run the research with profiling
                result = await orchestrator.run_research_async(
                    scenario.question,
                    initial_search_query_count=scenario.initial_search_query_count,
                    max_research_loops=scenario.max_research_loops,
                    reasoning_model=scenario.reasoning_model,
                    frontend_start_time=start_time  # Simulate frontend timing
                )
                
                end_time = time.perf_counter()
                total_duration = end_time - start_time
                
                # Create test result
                test_result = TestResult(
                    scenario_name=f"{scenario.name}_direct",
                    success=True,
                    total_duration=total_duration,
                    performance_profile=result.get("performance_profile", {}),
                )
                
                results.append(test_result)
                
                print(f"   ✅ Completed in {total_duration:.2f}s")
                
            except Exception as e:
                end_time = time.perf_counter()
                total_duration = end_time - start_time
                
                test_result = TestResult(
                    scenario_name=f"{scenario.name}_direct",
                    success=False,
                    total_duration=total_duration,
                    performance_profile={},
                    error_message=str(e)
                )
                
                results.append(test_result)
                print(f"   ❌ Failed after {total_duration:.2f}s: {e}")
            
            finally:
                # Clean up orchestrator
                orchestrator._cleanup_thread_pool()
        
        return results
    
    async def test_http_api(self, scenario: TestScenario, iterations: int = 1) -> List[TestResult]:
        """Test HTTP API performance (full frontend-to-backend simulation)."""
        print(f"\n🌐 Testing HTTP API: {scenario.name}")
        print(f"   URL: {self.backend_url}/research")
        print(f"   Question: {scenario.question}")
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            for i in range(iterations):
                print(f"   Run {i+1}/{iterations}...")
                
                try:
                    # Simulate frontend timing
                    frontend_start = time.perf_counter()
                    
                    # Prepare request
                    request_data = {
                        "question": scenario.question,
                        "initial_search_query_count": scenario.initial_search_query_count,
                        "max_research_loops": scenario.max_research_loops
                    }
                    
                    if scenario.reasoning_model:
                        request_data["reasoning_model"] = scenario.reasoning_model
                    
                    # Make HTTP request
                    async with session.post(
                        f"{self.backend_url}/research",
                        json=request_data,
                        timeout=aiohttp.ClientTimeout(total=120)  # 2 minute timeout
                    ) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            end_time = time.perf_counter()
                            total_duration = end_time - frontend_start
                            
                            # Extract performance profile if available
                            performance_profile = result.get("performance_profile", {})
                            
                            test_result = TestResult(
                                scenario_name=f"{scenario.name}_http",
                                success=True,
                                total_duration=total_duration,
                                performance_profile=performance_profile
                            )
                            
                            results.append(test_result)
                            print(f"   ✅ Completed in {total_duration:.2f}s")
                            
                        else:
                            error_text = await response.text()
                            end_time = time.perf_counter()
                            total_duration = end_time - frontend_start
                            
                            test_result = TestResult(
                                scenario_name=f"{scenario.name}_http",
                                success=False,
                                total_duration=total_duration,
                                performance_profile={},
                                error_message=f"HTTP {response.status}: {error_text}"
                            )
                            
                            results.append(test_result)
                            print(f"   ❌ Failed after {total_duration:.2f}s: HTTP {response.status}")
                
                except Exception as e:
                    end_time = time.perf_counter()
                    total_duration = end_time - frontend_start
                    
                    test_result = TestResult(
                        scenario_name=f"{scenario.name}_http",
                        success=False,
                        total_duration=total_duration,
                        performance_profile={},
                        error_message=str(e)
                    )
                    
                    results.append(test_result)
                    print(f"   ❌ Failed after {total_duration:.2f}s: {e}")
        
        return results
    
    async def check_backend_health(self) -> bool:
        """Check if the backend is healthy and responding."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        print(f"✅ Backend healthy: {health_data}")
                        return True
                    else:
                        print(f"❌ Backend unhealthy: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Backend unreachable: {e}")
            return False
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        if not self.results:
            return {"error": "No test results available"}
        
        # Separate successful and failed results
        successful_results = [r for r in self.results if r.success]
        failed_results = [r for r in self.results if not r.success]
        
        # Calculate summary statistics
        if successful_results:
            durations = [r.total_duration for r in successful_results]
            duration_stats = {
                "count": len(durations),
                "min": min(durations),
                "max": max(durations),
                "mean": statistics.mean(durations),
                "median": statistics.median(durations),
                "stdev": statistics.stdev(durations) if len(durations) > 1 else 0.0
            }
        else:
            duration_stats = {"count": 0}
        
        # Analyze step timings
        step_analysis = self._analyze_step_timings(successful_results)
        
        # Performance insights
        insights = self._generate_insights(successful_results)
        
        report = {
            "test_summary": {
                "total_tests": len(self.results),
                "successful_tests": len(successful_results),
                "failed_tests": len(failed_results),
                "success_rate": len(successful_results) / len(self.results) * 100 if self.results else 0
            },
            "duration_statistics": duration_stats,
            "step_analysis": step_analysis,
            "performance_insights": insights,
            "detailed_results": [asdict(result) for result in self.results],
            "failed_tests": [
                {
                    "scenario": result.scenario_name,
                    "error": result.error_message,
                    "duration": result.total_duration
                } for result in failed_results
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def _analyze_step_timings(self, successful_results: List[TestResult]) -> Dict[str, Any]:
        """Analyze timing for individual steps."""
        step_timings = {
            "query_generation": [],
            "initial_searches": [],
            "reflection_loops": [],
            "finalization": []
        }
        
        for result in successful_results:
            profile = result.performance_profile
            
            # Query generation timing
            if profile.get("query_generation", {}).get("duration"):
                step_timings["query_generation"].append(profile["query_generation"]["duration"])
            
            # Search timings
            for search in profile.get("initial_searches", []):
                if search.get("duration"):
                    step_timings["initial_searches"].append(search["duration"])
            
            # Reflection timings
            for reflection in profile.get("reflection_loops", []):
                if reflection.get("duration"):
                    step_timings["reflection_loops"].append(reflection["duration"])
            
            # Finalization timing
            if profile.get("finalization", {}).get("duration"):
                step_timings["finalization"].append(profile["finalization"]["duration"])
        
        # Calculate statistics for each step
        step_stats = {}
        for step_name, timings in step_timings.items():
            if timings:
                step_stats[step_name] = {
                    "count": len(timings),
                    "min": min(timings),
                    "max": max(timings),
                    "mean": statistics.mean(timings),
                    "median": statistics.median(timings),
                    "total": sum(timings)
                }
            else:
                step_stats[step_name] = {"count": 0}
        
        return step_stats
    
    def _generate_insights(self, successful_results: List[TestResult]) -> List[str]:
        """Generate performance insights and recommendations."""
        insights = []
        
        if not successful_results:
            return ["No successful tests to analyze"]
        
        # Analyze bottlenecks
        total_durations = [r.total_duration for r in successful_results]
        avg_duration = statistics.mean(total_durations)
        
        if avg_duration > 20:
            insights.append("⚠️ Average response time exceeds 20 seconds - consider optimization")
        elif avg_duration > 10:
            insights.append("⚡ Response times are moderate but could be improved")
        else:
            insights.append("✅ Response times are within acceptable range")
        
        # Analyze step performance
        step_analysis = self._analyze_step_timings(successful_results)
        
        if step_analysis.get("initial_searches", {}).get("mean", 0) > 5:
            insights.append("🔍 Initial searches taking longer than expected - check search API performance")
        
        if step_analysis.get("reflection_loops", {}).get("mean", 0) > 3:
            insights.append("🤔 Reflection loops are slow - consider model optimization")
        
        # Check concurrency effectiveness
        for result in successful_results:
            concurrency_metrics = result.performance_profile.get("concurrency_metrics", {})
            for search_type, metrics in concurrency_metrics.items():
                if metrics.get("queries_count", 0) > 1:
                    parallel_efficiency = metrics.get("total_duration", 0) / metrics.get("max_timing", 1)
                    if parallel_efficiency > 0.7:  # Good parallel efficiency
                        insights.append(f"✅ {search_type} shows good parallel execution efficiency")
                    else:
                        insights.append(f"⚠️ {search_type} may benefit from better parallelization")
        
        return insights
    
    async def run_full_test_suite(self, iterations: int = 1, test_http: bool = True, test_direct: bool = True) -> Dict[str, Any]:
        """Run the complete performance test suite."""
        print("🚀 Starting Comprehensive Performance Test Suite")
        print("=" * 60)
        
        # Check backend health first
        if test_http:
            print("\n📡 Checking backend health...")
            if not await self.check_backend_health():
                print("❌ Backend is not healthy. Skipping HTTP tests.")
                test_http = False
        
        # Run tests for each scenario
        for scenario in self.scenarios:
            print(f"\n📋 Scenario: {scenario.name.upper()}")
            print(f"   Expected duration: {scenario.expected_duration_range[0]:.1f}s - {scenario.expected_duration_range[1]:.1f}s")
            
            # Test direct orchestrator
            if test_direct:
                direct_results = await self.test_direct_orchestrator(scenario, iterations)
                self.results.extend(direct_results)
            
            # Test HTTP API
            if test_http:
                http_results = await self.test_http_api(scenario, iterations)
                self.results.extend(http_results)
        
        # Generate and return report
        print("\n📊 Generating performance report...")
        report = self.generate_performance_report()
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save performance report to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filename


async def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Performance profiling test for deep search system")
    parser.add_argument("--backend-url", default="http://localhost:8000", help="Backend URL")
    parser.add_argument("--iterations", type=int, default=1, help="Number of iterations per test")
    parser.add_argument("--no-http", action="store_true", help="Skip HTTP API tests")
    parser.add_argument("--no-direct", action="store_true", help="Skip direct orchestrator tests")
    parser.add_argument("--output", help="Output filename for performance report")
    
    args = parser.parse_args()
    
    # Create profiler
    profiler = PerformanceProfiler(args.backend_url)
    
    # Run tests
    report = await profiler.run_full_test_suite(
        iterations=args.iterations,
        test_http=not args.no_http,
        test_direct=not args.no_direct
    )
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE TEST SUMMARY")
    print("=" * 60)
    
    summary = report["test_summary"]
    print(f"Total tests: {summary['total_tests']}")
    print(f"Successful: {summary['successful_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success rate: {summary['success_rate']:.1f}%")
    
    if report["duration_statistics"]["count"] > 0:
        stats = report["duration_statistics"]
        print(f"\nDuration statistics:")
        print(f"  Min: {stats['min']:.2f}s")
        print(f"  Max: {stats['max']:.2f}s")
        print(f"  Mean: {stats['mean']:.2f}s")
        print(f"  Median: {stats['median']:.2f}s")
        print(f"  Std Dev: {stats['stdev']:.2f}s")
    
    print(f"\nPerformance insights:")
    for insight in report["performance_insights"]:
        print(f"  {insight}")
    
    # Save report
    filename = profiler.save_report(report, args.output)
    print(f"\n💾 Detailed report saved to: {filename}")
    
    return 0 if summary["failed_tests"] == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)