#!/usr/bin/env python3
"""
Search quality validation test for performance profiling.
Ensures that performance tests are using real search APIs, not fallback responses.
"""

import sys
import os
import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime

# Add backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent.agents import search_web
from agent.profiling_orchestrator import create_profiling_orchestrator


class SearchQualityValidator:
    """Validates that search operations are using real APIs, not fallbacks."""
    
    def __init__(self):
        self.test_questions = [
            # Performance test questions
            "What is the capital of France?",
            "What are the latest developments in quantum computing in 2024?",
            "Compare the economic impacts of renewable energy adoption vs traditional fossil fuels in developing countries",
            "Explain the technical architecture and performance characteristics of Kubernetes container orchestration, including recent improvements in version 1.29",
            
            # Additional validation questions
            "What happened in the 2024 US presidential election?",
            "What are the current stock market trends for AI companies?",
            "How does ChatGPT-4 compare to other large language models?",
            "What are the environmental benefits of electric vehicles?",
        ]
    
    async def validate_search_api(self, question: str) -> Dict[str, Any]:
        """Validate a single search query for real API usage."""
        print(f"🔍 Testing: {question[:60]}{'...' if len(question) > 60 else ''}")
        
        try:
            results = await search_web(question, 3)
            
            # Analyze results
            analysis = {
                "question": question,
                "total_results": len(results),
                "sources": {},
                "is_real_search": False,
                "has_fallback": False,
                "quality_score": 0.0,
                "details": []
            }
            
            # Count source types
            for result in results:
                source = result.get("source", "unknown")
                analysis["sources"][source] = analysis["sources"].get(source, 0) + 1
                
                # Check for specific indicators
                if source == "gemini_grounding":
                    analysis["is_real_search"] = True
                    analysis["quality_score"] += 2.0  # High quality
                elif source in ["google_custom", "searchapi", "duckduckgo"]:
                    analysis["is_real_search"] = True
                    analysis["quality_score"] += 1.5  # Good quality
                elif source == "gemini_knowledge":
                    analysis["quality_score"] += 1.0  # Moderate quality
                elif source == "knowledge_base":
                    analysis["has_fallback"] = True
                    analysis["quality_score"] += 0.2  # Low quality fallback
                
                # Extract URL domains for analysis
                url = result.get("url", "")
                if "grounding-api-redirect" in url:
                    analysis["details"].append("Uses Gemini grounding API")
                elif "example.com" in url:
                    analysis["details"].append("Uses placeholder URL (fallback)")
            
            # Calculate final quality score
            if analysis["total_results"] > 0:
                analysis["quality_score"] /= analysis["total_results"]
            
            # Determine status
            if analysis["is_real_search"] and not analysis["has_fallback"]:
                status = "✅ REAL SEARCH"
            elif analysis["is_real_search"] and analysis["has_fallback"]:
                status = "⚠️ MIXED (real + fallback)"
            else:
                status = "❌ FALLBACK ONLY"
            
            print(f"   {status} - {analysis['total_results']} results")
            print(f"   Sources: {', '.join(f'{k}: {v}' for k, v in analysis['sources'].items())}")
            print(f"   Quality score: {analysis['quality_score']:.1f}")
            
            return analysis
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            return {
                "question": question,
                "error": str(e),
                "is_real_search": False,
                "has_fallback": True,
                "quality_score": 0.0
            }
    
    async def validate_orchestrator_search(self, question: str) -> Dict[str, Any]:
        """Validate search through the full orchestrator pipeline."""
        print(f"\n🔬 Full orchestrator test: {question[:40]}{'...' if len(question) > 40 else ''}")
        
        orchestrator = create_profiling_orchestrator()
        
        try:
            result = await orchestrator.run_research_async(
                question,
                initial_search_query_count=2,
                max_research_loops=1
            )
            
            # Extract source analysis
            sources = result.get("sources_gathered", [])
            performance = result.get("performance_profile", {})
            
            analysis = {
                "question": question,
                "total_sources": len(sources),
                "search_timing": {},
                "source_domains": set(),
                "is_comprehensive": False,
                "performance_data": performance
            }
            
            # Analyze sources
            for source in sources:
                url = source.get("url", "")
                if url:
                    if "grounding-api-redirect" in url:
                        analysis["source_domains"].add("gemini_grounding")
                    elif "wikipedia.org" in url:
                        analysis["source_domains"].add("wikipedia")
                    elif "example.com" in url:
                        analysis["source_domains"].add("fallback")
                    else:
                        # Extract domain
                        try:
                            from urllib.parse import urlparse
                            domain = urlparse(url).netloc
                            analysis["source_domains"].add(domain)
                        except:
                            analysis["source_domains"].add("unknown")
            
            # Check if comprehensive
            analysis["is_comprehensive"] = (
                analysis["total_sources"] >= 2 and
                "fallback" not in analysis["source_domains"] and
                len(analysis["source_domains"]) > 0
            )
            
            # Extract timing data
            concurrency = performance.get("concurrency_metrics", {})
            for search_type, metrics in concurrency.items():
                analysis["search_timing"][search_type] = {
                    "duration": metrics.get("total_duration", 0),
                    "queries": metrics.get("queries_count", 0)
                }
            
            status = "✅ COMPREHENSIVE" if analysis["is_comprehensive"] else "⚠️ LIMITED"
            print(f"   {status} - {analysis['total_sources']} sources from {len(analysis['source_domains'])} domains")
            print(f"   Domains: {', '.join(analysis['source_domains'])}")
            
            return analysis
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            return {
                "question": question,
                "error": str(e),
                "is_comprehensive": False
            }
        
        finally:
            orchestrator._cleanup_thread_pool()
    
    async def run_validation_suite(self) -> Dict[str, Any]:
        """Run complete search quality validation."""
        print("🧪 Search Quality Validation Suite")
        print("=" * 50)
        
        # Test direct search API
        print("\n📡 Direct Search API Validation")
        print("-" * 30)
        
        direct_results = []
        for question in self.test_questions[:4]:  # Test performance questions
            result = await self.validate_search_api(question)
            direct_results.append(result)
            await asyncio.sleep(1)  # Rate limiting
        
        # Test full orchestrator
        print("\n🔬 Full Orchestrator Validation")
        print("-" * 30)
        
        orchestrator_results = []
        for question in self.test_questions[:2]:  # Test fewer for orchestrator
            result = await self.validate_orchestrator_search(question)
            orchestrator_results.append(result)
            await asyncio.sleep(2)  # More rate limiting for full tests
        
        # Generate report
        report = self.generate_validation_report(direct_results, orchestrator_results)
        
        return report
    
    def generate_validation_report(self, direct_results: List[Dict], orchestrator_results: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        
        # Analyze direct search results
        real_search_count = sum(1 for r in direct_results if r.get("is_real_search", False))
        fallback_count = sum(1 for r in direct_results if r.get("has_fallback", False))
        avg_quality = sum(r.get("quality_score", 0) for r in direct_results) / len(direct_results) if direct_results else 0
        
        # Analyze orchestrator results
        comprehensive_count = sum(1 for r in orchestrator_results if r.get("is_comprehensive", False))
        
        # Source distribution
        all_sources = {}
        for result in direct_results:
            for source, count in result.get("sources", {}).items():
                all_sources[source] = all_sources.get(source, 0) + count
        
        # Generate insights
        insights = []
        
        if real_search_count == len(direct_results):
            insights.append("✅ All test questions use real search APIs")
        elif real_search_count > len(direct_results) * 0.8:
            insights.append("⚡ Most test questions use real search APIs")
        else:
            insights.append("⚠️ Some test questions may be using fallback responses")
        
        if fallback_count == 0:
            insights.append("✅ No fallback responses detected")
        else:
            insights.append(f"⚠️ {fallback_count} questions triggered fallback responses")
        
        if avg_quality > 1.5:
            insights.append("🚀 High quality search results")
        elif avg_quality > 1.0:
            insights.append("⚡ Good quality search results")
        else:
            insights.append("📊 Search quality could be improved")
        
        if comprehensive_count == len(orchestrator_results):
            insights.append("✅ Full orchestrator provides comprehensive results")
        else:
            insights.append("📋 Some orchestrator tests had limited results")
        
        # Performance insights
        performance_data = []
        for result in orchestrator_results:
            perf = result.get("performance_data", {})
            if perf.get("backend_processing"):
                performance_data.append(perf["backend_processing"])
        
        if performance_data:
            avg_perf = sum(performance_data) / len(performance_data)
            if avg_perf < 10:
                insights.append("🚀 Good performance with real search")
            elif avg_perf < 20:
                insights.append("⚡ Acceptable performance with real search")
            else:
                insights.append("📊 Performance could be optimized")
        
        report = {
            "validation_summary": {
                "total_direct_tests": len(direct_results),
                "real_search_count": real_search_count,
                "fallback_count": fallback_count,
                "average_quality_score": avg_quality,
                "comprehensive_orchestrator_count": comprehensive_count,
                "total_orchestrator_tests": len(orchestrator_results)
            },
            "source_distribution": all_sources,
            "insights": insights,
            "direct_search_results": direct_results,
            "orchestrator_results": orchestrator_results,
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def print_validation_summary(self, report: Dict[str, Any]):
        """Print validation summary."""
        print("\n" + "=" * 50)
        print("📊 SEARCH QUALITY VALIDATION SUMMARY")
        print("=" * 50)
        
        summary = report["validation_summary"]
        
        print(f"Direct Search Tests: {summary['real_search_count']}/{summary['total_direct_tests']} using real APIs")
        print(f"Fallback Responses: {summary['fallback_count']}")
        print(f"Average Quality Score: {summary['average_quality_score']:.2f}/2.0")
        print(f"Comprehensive Results: {summary['comprehensive_orchestrator_count']}/{summary['total_orchestrator_tests']}")
        
        print(f"\nSource Distribution:")
        for source, count in report["source_distribution"].items():
            print(f"  {source}: {count}")
        
        print(f"\nKey Insights:")
        for insight in report["insights"]:
            print(f"  {insight}")


async def main():
    """Main validation runner."""
    validator = SearchQualityValidator()
    
    # Run validation
    report = await validator.run_validation_suite()
    
    # Print summary
    validator.print_validation_summary(report)
    
    # Save detailed report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"search_quality_validation_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: {filename}")
    
    # Return exit code based on validation results
    summary = report["validation_summary"]
    success_rate = summary["real_search_count"] / summary["total_direct_tests"] if summary["total_direct_tests"] > 0 else 0
    
    if success_rate >= 0.9 and summary["fallback_count"] == 0:
        print("\n🎉 Search quality validation PASSED")
        return 0
    elif success_rate >= 0.7:
        print("\n⚠️ Search quality validation PARTIAL")
        return 1
    else:
        print("\n❌ Search quality validation FAILED")
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)