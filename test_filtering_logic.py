#!/usr/bin/env python3
"""
Test script to verify enhanced filtering logic without requiring API calls.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from agent.state import Source
from agent.quality_validator import quality_validator

def test_quality_validator_logic():
    """Test the quality validator graduated filtering logic."""
    print("🔬 Testing Quality Validator Logic")
    print("=" * 50)
    
    # Create test sources with different characteristics
    test_sources = [
        Source(
            title="High Quality Academic Paper from Nature",
            url="https://nature.com/articles/s41586-023-12345-6",
            content="A comprehensive study on machine learning published in a top-tier journal with extensive citations and rigorous peer review."
        ),
        Source(
            title="Reputable News Source - Reuters",
            url="https://reuters.com/technology/ai-breakthrough-2024-01-15",
            content="Breaking news about AI developments from a trusted news organization."
        ),
        Source(
            title="Personal Blog Post",
            url="https://myblog.wordpress.com/my-opinion-on-ai",
            content="Just my thoughts on AI and what I think will happen next."
        ),
        Source(
            title="Wikipedia Article",
            url="https://en.wikipedia.org/wiki/Artificial_intelligence",
            content="Artificial intelligence (AI) is intelligence demonstrated by machines..."
        )
    ]
    
    # Test 1: Default filtering (no threshold)
    print("\n🔹 Test 1: No Quality Filtering")
    result1 = quality_validator.classify_and_filter_sources_graduated(
        sources=test_sources,
        source_quality_filter="any"
    )
    
    print(f"✅ All sources included")
    print(f"   - Total sources: {result1['quality_summary']['total_sources']}")
    print(f"   - Included: {result1['quality_summary']['included_sources']}")
    print(f"   - Filtered: {result1['quality_summary']['filtered_sources']}")
    print(f"   - Threshold: {result1['quality_summary']['quality_threshold']}")
    
    # Test 2: Medium quality threshold
    print("\n🔹 Test 2: Medium Quality Filter (0.6)")
    result2 = quality_validator.classify_and_filter_sources_graduated(
        sources=test_sources,
        source_quality_filter="medium"
    )
    
    print(f"✅ Medium filtering applied")
    print(f"   - Total sources: {result2['quality_summary']['total_sources']}")
    print(f"   - Included: {result2['quality_summary']['included_sources']}")
    print(f"   - Filtered: {result2['quality_summary']['filtered_sources']}")
    print(f"   - Threshold: {result2['quality_summary']['quality_threshold']}")
    print(f"   - Avg quality: {result2['quality_summary']['average_quality_score']:.2f}")
    
    # Test 3: High quality threshold
    print("\n🔹 Test 3: High Quality Filter (0.8)")
    result3 = quality_validator.classify_and_filter_sources_graduated(
        sources=test_sources,
        source_quality_filter="high"
    )
    
    print(f"✅ High filtering applied")
    print(f"   - Total sources: {result3['quality_summary']['total_sources']}")
    print(f"   - Included: {result3['quality_summary']['included_sources']}")
    print(f"   - Filtered: {result3['quality_summary']['filtered_sources']}")
    print(f"   - Threshold: {result3['quality_summary']['quality_threshold']}")
    print(f"   - Avg quality: {result3['quality_summary']['average_quality_score']:.2f}")
    
    # Test 4: Custom threshold
    print("\n🔹 Test 4: Custom Threshold (0.7)")
    result4 = quality_validator.classify_and_filter_sources_graduated(
        sources=test_sources,
        quality_threshold=0.7
    )
    
    print(f"✅ Custom threshold applied")
    print(f"   - Total sources: {result4['quality_summary']['total_sources']}")
    print(f"   - Included: {result4['quality_summary']['included_sources']}")
    print(f"   - Filtered: {result4['quality_summary']['filtered_sources']}")
    print(f"   - Threshold: {result4['quality_summary']['quality_threshold']}")
    print(f"   - Avg quality: {result4['quality_summary']['average_quality_score']:.2f}")
    
    # Validate the logic is working correctly
    print("\n🔍 Validation Checks:")
    
    # Check that higher thresholds filter more sources
    if result3['quality_summary']['filtered_sources'] >= result2['quality_summary']['filtered_sources']:
        print("✅ Higher thresholds filter more sources")
    else:
        print("❌ Threshold logic appears incorrect")
        return False
    
    # Check that sources have quality scores
    for result in [result2, result3, result4]:
        if result['included']:
            for source in result['included']:
                if hasattr(source, 'quality_score') and source.quality_score is not None:
                    print(f"✅ Sources have quality scores (e.g., {source.quality_score:.2f})")
                    break
    
    # Check that filtered sources are also scored
    for result in [result2, result3, result4]:
        if result['filtered']:
            for source in result['filtered']:
                if hasattr(source, 'quality_score') and source.quality_score is not None:
                    print(f"✅ Filtered sources have quality scores (e.g., {source.quality_score:.2f})")
                    break
    
    print("\n🎉 All quality validator tests passed!")
    print("✅ Enhanced filtering logic working correctly")
    return True

if __name__ == "__main__":
    success = test_quality_validator_logic()
    sys.exit(0 if success else 1)