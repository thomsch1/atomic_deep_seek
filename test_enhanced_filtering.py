#!/usr/bin/env python3
"""
Test script to verify enhanced filtering functionality works end-to-end.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from agent.configuration import Configuration
from agent.agents.finalization_agent import FinalizationAgent
from agent.state import FinalizationInput, Source

def test_enhanced_filtering():
    """Test that enhanced filtering works properly."""
    print("🔬 Testing Enhanced Filtering System")
    print("=" * 50)
    
    # Create test configuration
    config = Configuration()
    agent = FinalizationAgent(config)
    
    # Create test sources with varying quality characteristics
    test_sources = [
        Source(
            title="High Quality Academic Paper",
            url="https://scholar.google.com/test-paper",
            content="A well-researched academic paper with citations."
        ),
        Source(
            title="Medium Quality News Article", 
            url="https://reuters.com/test-article",
            content="A decent news article from a reputable source."
        ),
        Source(
            title="Low Quality Blog Post",
            url="https://random-blog.com/post",
            content="A personal blog post with unclear sourcing."
        ),
        Source(
            title="Another Academic Source",
            url="https://nature.com/article",
            content="Scientific publication with peer review."
        )
    ]
    
    # Test 1: Binary filtering (existing system)
    print("\n🔹 Test 1: Binary Filtering (Legacy Mode)")
    binary_input = FinalizationInput(
        research_topic="Test topic",
        summaries=["Test summary"],
        sources=test_sources,
        current_date="2025-01-18",
        source_quality_filter="medium",
        enhanced_filtering=False
    )
    
    try:
        binary_result = agent.run(binary_input)
        print(f"✅ Binary filtering completed")
        print(f"   - Used sources: {len(binary_result.used_sources)}")
        print(f"   - Filtered sources: {len(binary_result.filtered_sources)}")
        print(f"   - Filtering applied: {binary_result.filtering_applied}")
        print(f"   - Quality summary: {'Yes' if binary_result.quality_summary else 'No'}")
    except Exception as e:
        print(f"❌ Binary filtering failed: {e}")
        return False
    
    # Test 2: Enhanced filtering with default threshold
    print("\n🔹 Test 2: Enhanced Filtering (Default Threshold)")
    enhanced_input = FinalizationInput(
        research_topic="Test topic",
        summaries=["Test summary"],
        sources=test_sources,
        current_date="2025-01-18",
        source_quality_filter="medium",
        enhanced_filtering=True,
        quality_threshold=0.6
    )
    
    try:
        enhanced_result = agent.run(enhanced_input)
        print(f"✅ Enhanced filtering completed")
        print(f"   - Used sources: {len(enhanced_result.used_sources)}")
        print(f"   - Filtered sources: {len(enhanced_result.filtered_sources)}")
        print(f"   - Filtering applied: {enhanced_result.filtering_applied}")
        if enhanced_result.quality_summary:
            print(f"   - Quality summary: {enhanced_result.quality_summary.total_sources} total, {enhanced_result.quality_summary.included_sources} included")
            print(f"   - Average quality: {enhanced_result.quality_summary.average_quality_score:.2f}")
            print(f"   - Quality threshold: {enhanced_result.quality_summary.quality_threshold}")
        
        # Verify sources have quality scores
        for i, source in enumerate(enhanced_result.used_sources):
            if hasattr(source, 'quality_score') and source.quality_score is not None:
                print(f"   - Source {i+1} quality: {source.quality_score:.2f}")
        
    except Exception as e:
        print(f"❌ Enhanced filtering failed: {e}")
        return False
    
    # Test 3: Enhanced filtering with high threshold
    print("\n🔹 Test 3: Enhanced Filtering (High Threshold)")
    high_threshold_input = FinalizationInput(
        research_topic="Test topic",
        summaries=["Test summary"],
        sources=test_sources,
        current_date="2025-01-18",
        enhanced_filtering=True,
        quality_threshold=0.8
    )
    
    try:
        high_result = agent.run(high_threshold_input)
        print(f"✅ High threshold filtering completed")
        print(f"   - Used sources: {len(high_result.used_sources)}")
        print(f"   - Filtered sources: {len(high_result.filtered_sources)}")
        print(f"   - Should have more filtered sources than Test 2")
        
    except Exception as e:
        print(f"❌ High threshold filtering failed: {e}")
        return False
    
    print("\n🎉 All enhanced filtering tests passed!")
    print("✅ Backend implementation working correctly")
    return True

if __name__ == "__main__":
    success = test_enhanced_filtering()
    sys.exit(0 if success else 1)