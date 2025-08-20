"""
Integration tests for text display enhancement features.
Tests the graduated quality filtering system end-to-end.
"""

import pytest
from typing import Dict, Any, List
from agent.quality_validator import quality_validator
from agent.state import Source, FinalizationInput, QualityMetrics, QualitySummary
from agent.configuration import Configuration


class TestTextDisplayIntegration:
    """Test text display enhancement features integration."""
    
    def test_quality_validator_basic_functionality(self):
        """Test basic quality validator functionality."""
        # Create test sources with varying quality
        sources = [
            Source(
                title="High Quality Academic Source",
                url="https://www.example.edu/research/paper",
                label="Source 1"
            ),
            Source(
                title="Medium Quality News Article",
                url="https://www.reputablenews.com/article/123",
                label="Source 2"
            ),
            Source(
                title="Low Quality Blog Post",
                url="http://random-blog.info/post",
                label="Source 3"
            )
        ]
        
        # Test graduated filtering
        result = quality_validator.classify_and_filter_sources_graduated(
            sources=sources,
            source_quality_filter="medium",
            quality_threshold=None
        )
        
        # Validate structure
        assert "included" in result
        assert "filtered" in result
        assert "quality_summary" in result
        
        # Validate quality summary
        summary = result["quality_summary"]
        assert summary["total_sources"] == 3
        assert summary["quality_threshold"] == 0.6  # Medium threshold
        assert summary["included_sources"] + summary["filtered_sources"] == 3
        
        # Validate all sources have quality scores
        all_sources = result["included"] + result["filtered"]
        for source in all_sources:
            assert hasattr(source, 'quality_score')
            assert hasattr(source, 'quality_breakdown')
            assert 0.0 <= source.quality_score <= 1.0
            
    def test_quality_thresholds(self):
        """Test different quality threshold levels."""
        sources = [
            Source(
                title="Wikipedia Article", 
                url="https://en.wikipedia.org/wiki/Test",
                label="High Quality"
            ),
            Source(
                title="News Article", 
                url="https://example.com/news",
                label="Medium Quality"
            ),
            Source(
                title="Random Blog", 
                url="http://blog.example/post",
                label="Low Quality"
            )
        ]
        
        # Test "any" filter (should include all)
        result_any = quality_validator.classify_and_filter_sources_graduated(
            sources=sources,
            source_quality_filter="any"
        )
        assert result_any["quality_summary"]["included_sources"] == 3
        assert result_any["quality_summary"]["filtered_sources"] == 0
        
        # Test "high" filter (should be more selective)
        result_high = quality_validator.classify_and_filter_sources_graduated(
            sources=sources,
            source_quality_filter="high"
        )
        assert result_high["quality_summary"]["filtered_sources"] >= 0
        assert result_high["quality_summary"]["quality_threshold"] == 0.8
        
    def test_quality_breakdown_metrics(self):
        """Test detailed quality breakdown metrics."""
        source = Source(
            title="Test Source for Quality Analysis",
            url="https://www.example.edu/research/comprehensive-study",
            label="Test Source"
        )
        
        quality_metrics = quality_validator.calculate_user_facing_quality_score(
            source=source,
            query="research study analysis"
        )
        
        # Validate structure
        expected_keys = [
            'source_credibility',
            'content_relevance', 
            'information_completeness',
            'recency_score',
            'overall_score'
        ]
        
        for key in expected_keys:
            assert key in quality_metrics
            assert 0.0 <= quality_metrics[key] <= 1.0
            
        # Test that overall score is calculated correctly
        expected_overall = (
            quality_metrics['source_credibility'] * 0.3 +
            quality_metrics['content_relevance'] * 0.3 +
            quality_metrics['information_completeness'] * 0.25 +
            quality_metrics['recency_score'] * 0.15
        )
        
        assert abs(quality_metrics['overall_score'] - expected_overall) < 0.01
        
    def test_empty_sources_handling(self):
        """Test handling of empty source lists."""
        result = quality_validator.classify_and_filter_sources_graduated(
            sources=[],
            source_quality_filter="medium"
        )
        
        assert result["quality_summary"]["total_sources"] == 0
        assert result["quality_summary"]["included_sources"] == 0
        assert result["quality_summary"]["filtered_sources"] == 0
        assert len(result["included"]) == 0
        assert len(result["filtered"]) == 0
        
    def test_configuration_quality_settings(self):
        """Test quality configuration settings."""
        config = Configuration()
        
        # Test default values
        assert config.quality_transparency_enabled == True
        assert config.default_quality_threshold == 0.6
        assert config.enable_graduated_filtering == True
        assert config.max_filtered_sources_returned == 5
        assert config.quality_preference_learning == True
        
        # Test quality thresholds mapping
        expected_thresholds = {
            "any": 0.0,
            "medium": 0.6,
            "high": 0.8
        }
        
        assert config.quality_thresholds == expected_thresholds
        
    def test_source_quality_assignment(self):
        """Test that sources are properly assigned quality scores."""
        sources = [
            Source(title="Test 1", url="https://example.edu", label="S1"),
            Source(title="Test 2", url="https://news.com", label="S2")
        ]
        
        result = quality_validator.classify_and_filter_sources_graduated(
            sources=sources,
            source_quality_filter="medium"
        )
        
        # Check that all sources (included and filtered) have quality data
        all_sources = result["included"] + result["filtered"]
        
        for source in all_sources:
            # Quality score should be assigned
            assert hasattr(source, 'quality_score')
            assert source.quality_score is not None
            assert 0.0 <= source.quality_score <= 1.0
            
            # Quality breakdown should be assigned
            assert hasattr(source, 'quality_breakdown')
            assert source.quality_breakdown is not None
            assert isinstance(source.quality_breakdown, dict)
            
            # Required breakdown keys should exist
            breakdown_keys = [
                'source_credibility',
                'content_relevance',
                'information_completeness', 
                'recency_score',
                'overall_score'
            ]
            
            for key in breakdown_keys:
                assert key in source.quality_breakdown
                assert 0.0 <= source.quality_breakdown[key] <= 1.0
                
    def test_quality_thresholds_custom_values(self):
        """Test custom quality thresholds."""
        sources = [
            Source(title="Test", url="https://example.com", label="Test")
        ]
        
        # Test custom threshold
        result = quality_validator.classify_and_filter_sources_graduated(
            sources=sources,
            source_quality_filter=None,
            quality_threshold=0.75
        )
        
        assert result["quality_summary"]["quality_threshold"] == 0.75
        
        # Sources should be classified based on custom threshold
        included_count = result["quality_summary"]["included_sources"]
        filtered_count = result["quality_summary"]["filtered_sources"]
        assert included_count + filtered_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])