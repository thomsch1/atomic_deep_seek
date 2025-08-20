"""
Quality validation framework for ensuring functionality preservation during optimizations.
Provides automated testing and scoring for research quality and consistency.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re
import hashlib
from urllib.parse import urlparse
from agent.state import Source


@dataclass
class QualityMetrics:
    """Quality metrics for a research response."""
    answer_completeness: float  # 0-1 score
    source_attribution: float   # 0-1 score
    content_relevance: float    # 0-1 score
    format_consistency: float   # 0-1 score
    error_rate: float          # 0-1 (0 = no errors)
    response_time: float       # seconds
    
    overall_score: float = 0.0
    
    def __post_init__(self):
        """Calculate overall score."""
        self.overall_score = (
            self.answer_completeness * 0.3 +
            self.source_attribution * 0.25 +
            self.content_relevance * 0.25 +
            self.format_consistency * 0.1 +
            (1 - self.error_rate) * 0.1
        )


@dataclass
class ComparisonResult:
    """Result of comparing two research responses."""
    baseline_metrics: QualityMetrics
    optimized_metrics: QualityMetrics
    quality_preserved: bool
    performance_improvement: float  # percentage
    issues: List[str] = field(default_factory=list)
    
    @property
    def quality_degradation(self) -> float:
        """Calculate quality degradation percentage."""
        return (self.baseline_metrics.overall_score - self.optimized_metrics.overall_score) * 100
    
    @property
    def passes_quality_gate(self) -> bool:
        """Check if quality degradation is within acceptable limits (≤5%)."""
        return self.quality_degradation <= 5.0


class QualityValidator:
    """Validates research quality and compares implementations."""
    
    def __init__(self):
        self.baseline_responses: Dict[str, Dict[str, Any]] = {}
        self.quality_thresholds = {
            'answer_completeness': 0.7,
            'source_attribution': 0.8,
            'content_relevance': 0.7,
            'format_consistency': 0.9,
            'error_rate': 0.1,
            'overall_score': 0.7
        }
    
    def evaluate_response(self, response: Dict[str, Any], question: str, 
                         response_time: float) -> QualityMetrics:
        """Evaluate the quality of a research response."""
        
        final_answer = response.get('final_answer', '')
        sources = response.get('sources_gathered', [])
        
        # Answer completeness - based on length and content structure
        completeness = self._score_completeness(final_answer, question)
        
        # Source attribution - check if sources are properly cited
        attribution = self._score_source_attribution(final_answer, sources)
        
        # Content relevance - check if answer addresses the question
        relevance = self._score_content_relevance(final_answer, question)
        
        # Format consistency - check response structure
        format_consistency = self._score_format_consistency(response)
        
        # Error rate - check for error indicators
        error_rate = self._calculate_error_rate(response)
        
        return QualityMetrics(
            answer_completeness=completeness,
            source_attribution=attribution,
            content_relevance=relevance,
            format_consistency=format_consistency,
            error_rate=error_rate,
            response_time=response_time
        )
    
    def _score_completeness(self, answer: str, question: str) -> float:
        """Score answer completeness based on length and structure."""
        if not answer:
            return 0.0
        
        # Basic length scoring
        length_score = min(len(answer) / 500, 1.0)  # Optimal around 500+ chars
        
        # Structure scoring - look for well-formed sentences
        sentences = [s.strip() for s in answer.split('.') if s.strip()]
        structure_score = min(len(sentences) / 3, 1.0)  # Optimal around 3+ sentences
        
        # Content depth - look for explanatory words
        depth_indicators = ['because', 'therefore', 'however', 'additionally', 'furthermore', 'specifically']
        depth_score = min(sum(1 for word in depth_indicators if word in answer.lower()) / 3, 1.0)
        
        return (length_score * 0.4 + structure_score * 0.3 + depth_score * 0.3)
    
    def _score_source_attribution(self, answer: str, sources: List[Dict]) -> float:
        """Score source attribution quality."""
        if not sources:
            return 0.0
        
        # Count citation patterns in the answer
        citation_patterns = [
            r'\[(\d+)\]',  # [1], [2], etc.
            r'\(\d+\)',    # (1), (2), etc.
            r'Source \d+', # Source 1, Source 2, etc.
        ]
        
        total_citations = 0
        for pattern in citation_patterns:
            total_citations += len(re.findall(pattern, answer))
        
        # Score based on ratio of citations to sources
        if len(sources) == 0:
            return 0.0
        
        citation_ratio = min(total_citations / len(sources), 1.0)
        
        # Check for source URLs in response
        url_mentions = sum(1 for source in sources if source.get('url', '') in answer)
        url_score = url_mentions / len(sources) if sources else 0
        
        return (citation_ratio * 0.7 + url_score * 0.3)
    
    def _score_content_relevance(self, answer: str, question: str) -> float:
        """Score how well the answer addresses the question."""
        if not answer or not question:
            return 0.0
        
        # Extract key terms from question
        question_terms = set(re.findall(r'\b\w{3,}\b', question.lower()))
        answer_terms = set(re.findall(r'\b\w{3,}\b', answer.lower()))
        
        # Calculate term overlap
        overlap = len(question_terms.intersection(answer_terms))
        relevance_score = overlap / len(question_terms) if question_terms else 0
        
        # Boost score if question type is addressed
        question_types = {
            'what': ['is', 'are', 'definition', 'explanation'],
            'how': ['process', 'method', 'way', 'steps'],
            'why': ['because', 'reason', 'due to', 'caused'],
            'when': ['time', 'date', 'period', 'during'],
            'where': ['location', 'place', 'in', 'at']
        }
        
        for q_type, indicators in question_types.items():
            if q_type in question.lower():
                if any(indicator in answer.lower() for indicator in indicators):
                    relevance_score += 0.2
                break
        
        return min(relevance_score, 1.0)
    
    def _score_format_consistency(self, response: Dict[str, Any]) -> float:
        """Score response format consistency."""
        required_fields = ['final_answer', 'sources_gathered', 'research_loops_executed']
        field_score = sum(1 for field in required_fields if field in response) / len(required_fields)
        
        # Check data types
        type_checks = [
            isinstance(response.get('final_answer'), str),
            isinstance(response.get('sources_gathered'), list),
            isinstance(response.get('research_loops_executed'), int),
        ]
        type_score = sum(type_checks) / len(type_checks)
        
        return (field_score * 0.6 + type_score * 0.4)
    
    def _calculate_error_rate(self, response: Dict[str, Any]) -> float:
        """Calculate error rate based on error indicators."""
        final_answer = response.get('final_answer', '')
        
        # Look for error indicators
        error_indicators = [
            'error', 'failed', 'unable to', 'could not', 'timeout',
            'fallback', 'placeholder', 'no results', 'try again'
        ]
        
        error_count = sum(1 for indicator in error_indicators if indicator in final_answer.lower())
        
        # Check for empty or very short responses
        if len(final_answer.strip()) < 50:
            error_count += 1
        
        # Check for fallback URLs
        sources = response.get('sources_gathered', [])
        fallback_sources = sum(1 for s in sources if 'example.com' in s.get('url', ''))
        
        total_errors = error_count + fallback_sources
        max_possible_errors = 5  # Reasonable maximum for scoring
        
        return min(total_errors / max_possible_errors, 1.0)
    
    def store_baseline(self, question: str, response: Dict[str, Any], 
                      response_time: float) -> QualityMetrics:
        """Store a baseline response for comparison."""
        metrics = self.evaluate_response(response, question, response_time)
        
        # Create a hash of the question for consistent storage
        question_hash = hashlib.md5(question.encode()).hexdigest()[:8]
        
        self.baseline_responses[question_hash] = {
            'question': question,
            'response': response,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        return metrics
    
    def compare_with_baseline(self, question: str, optimized_response: Dict[str, Any],
                            optimized_time: float) -> ComparisonResult:
        """Compare an optimized response with the baseline."""
        question_hash = hashlib.md5(question.encode()).hexdigest()[:8]
        
        if question_hash not in self.baseline_responses:
            raise ValueError(f"No baseline found for question: {question[:50]}...")
        
        baseline_data = self.baseline_responses[question_hash]
        baseline_metrics = baseline_data['metrics']
        
        optimized_metrics = self.evaluate_response(optimized_response, question, optimized_time)
        
        # Calculate performance improvement
        perf_improvement = ((baseline_metrics.response_time - optimized_time) / 
                          baseline_metrics.response_time) * 100
        
        # Check for quality preservation
        quality_preserved = optimized_metrics.overall_score >= (baseline_metrics.overall_score * 0.95)
        
        # Identify specific issues
        issues = []
        if optimized_metrics.answer_completeness < baseline_metrics.answer_completeness * 0.9:
            issues.append("Answer completeness degraded")
        if optimized_metrics.source_attribution < baseline_metrics.source_attribution * 0.9:
            issues.append("Source attribution quality decreased")
        if optimized_metrics.content_relevance < baseline_metrics.content_relevance * 0.9:
            issues.append("Content relevance decreased")
        if optimized_metrics.error_rate > baseline_metrics.error_rate * 1.5:
            issues.append("Error rate increased significantly")
        
        return ComparisonResult(
            baseline_metrics=baseline_metrics,
            optimized_metrics=optimized_metrics,
            quality_preserved=quality_preserved,
            performance_improvement=perf_improvement,
            issues=issues
        )
    
    def run_quality_gate(self, comparison: ComparisonResult) -> bool:
        """Run quality gate checks."""
        print(f"\n🔍 Quality Gate Analysis")
        print(f"   Performance Improvement: {comparison.performance_improvement:.1f}%")
        print(f"   Quality Degradation: {comparison.quality_degradation:.1f}%")
        print(f"   Overall Quality Preserved: {comparison.quality_preserved}")
        
        if comparison.issues:
            print(f"   Issues Detected:")
            for issue in comparison.issues:
                print(f"     - {issue}")
        
        gate_passed = comparison.passes_quality_gate and comparison.performance_improvement > 0
        
        if gate_passed:
            print("   ✅ Quality Gate: PASSED")
        else:
            print("   ❌ Quality Gate: FAILED")
        
        return gate_passed
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality report."""
        if not self.baseline_responses:
            return {"error": "No baseline data available"}
        
        report = {
            "total_baselines": len(self.baseline_responses),
            "quality_thresholds": self.quality_thresholds,
            "baselines": {}
        }
        
        for question_hash, data in self.baseline_responses.items():
            metrics = data['metrics']
            report["baselines"][question_hash] = {
                "question": data['question'][:100] + "...",
                "timestamp": data['timestamp'],
                "metrics": {
                    "overall_score": metrics.overall_score,
                    "answer_completeness": metrics.answer_completeness,
                    "source_attribution": metrics.source_attribution,
                    "content_relevance": metrics.content_relevance,
                    "format_consistency": metrics.format_consistency,
                    "error_rate": metrics.error_rate,
                    "response_time": metrics.response_time
                }
            }
        
        return report
    
    def save_report(self, filename: Optional[str] = None) -> str:
        """Save quality report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quality_report_{timestamp}.json"
        
        report = self.generate_quality_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return filename
    
    def calculate_user_facing_quality_score(self, source: Source, query: str) -> Dict[str, float]:
        """
        Return granular quality metrics for user transparency:
        - source_credibility: 0-1 (domain authority, https, etc.)
        - content_relevance: 0-1 (how well it answers the query)
        - information_completeness: 0-1 (depth and detail level)
        - recency_score: 0-1 (how recent the information is)
        """
        # Source credibility based on domain and URL structure
        credibility = self._calculate_source_credibility(source.url)
        
        # Content relevance based on title and query matching
        relevance = self._calculate_content_relevance(source.title, query)
        
        # Information completeness based on title length and structure
        completeness = self._calculate_information_completeness(source.title, source.url)
        
        # Recency score (basic implementation - could be enhanced with actual dates)
        recency = self._calculate_recency_score(source.url, source.title)
        
        # Overall score weighted average
        overall_score = (credibility * 0.3 + relevance * 0.3 + completeness * 0.25 + recency * 0.15)
        
        return {
            'source_credibility': credibility,
            'content_relevance': relevance,
            'information_completeness': completeness,
            'recency_score': recency,
            'overall_score': overall_score
        }
    
    def _calculate_source_credibility(self, url: str) -> float:
        """Calculate source credibility based on domain characteristics."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # High credibility domains
            if any(domain.endswith(suffix) for suffix in ['.edu', '.gov', '.org']):
                base_score = 0.9
            # Medium credibility news and established sites
            elif any(domain.endswith(suffix) for suffix in ['.com', '.net']) and len(domain.split('.')) >= 2:
                base_score = 0.7
            # Unknown or potentially less credible
            else:
                base_score = 0.5
            
            # Boost for HTTPS
            if parsed.scheme == 'https':
                base_score += 0.1
            
            # Penalty for very long or suspicious domains
            if len(domain) > 30 or domain.count('-') > 3:
                base_score -= 0.2
            
            # Known high-quality domains
            high_quality_domains = [
                'wikipedia.org', 'reuters.com', 'bbc.com', 'nature.com',
                'science.org', 'ncbi.nlm.nih.gov', 'who.int', 'cdc.gov'
            ]
            
            if any(domain.endswith(hq_domain) for hq_domain in high_quality_domains):
                base_score = 0.95
            
            return min(max(base_score, 0.0), 1.0)
            
        except Exception:
            return 0.5  # Default moderate credibility if parsing fails
    
    def _calculate_content_relevance(self, title: str, query: str) -> float:
        """Calculate how relevant the content is to the query."""
        if not title or not query:
            return 0.5
        
        # Extract key terms from query and title
        query_terms = set(re.findall(r'\b\w{3,}\b', query.lower()))
        title_terms = set(re.findall(r'\b\w{3,}\b', title.lower()))
        
        if not query_terms:
            return 0.5
        
        # Calculate term overlap
        overlap = len(query_terms.intersection(title_terms))
        relevance_score = overlap / len(query_terms)
        
        # Boost for exact phrase matches
        if query.lower() in title.lower():
            relevance_score += 0.3
        
        # Boost for question type indicators
        question_indicators = {
            'what': ['definition', 'explanation', 'meaning'],
            'how': ['tutorial', 'guide', 'method', 'steps'],
            'why': ['reason', 'because', 'explanation'],
            'when': ['date', 'time', 'history', 'timeline'],
            'where': ['location', 'place', 'geography']
        }
        
        query_lower = query.lower()
        title_lower = title.lower()
        
        for question_word, indicators in question_indicators.items():
            if question_word in query_lower:
                if any(indicator in title_lower for indicator in indicators):
                    relevance_score += 0.2
                break
        
        return min(max(relevance_score, 0.0), 1.0)
    
    def _calculate_information_completeness(self, title: str, url: str) -> float:
        """Estimate information completeness based on title and URL structure."""
        if not title:
            return 0.3
        
        base_score = 0.5
        
        # Title length indicator (longer often means more comprehensive)
        title_length = len(title.split())
        if title_length >= 8:
            base_score += 0.2
        elif title_length >= 5:
            base_score += 0.1
        elif title_length <= 2:
            base_score -= 0.2
        
        # Look for completeness indicators in title
        completeness_indicators = [
            'complete', 'comprehensive', 'detailed', 'full', 'ultimate',
            'guide', 'tutorial', 'handbook', 'reference', 'overview'
        ]
        
        if any(indicator in title.lower() for indicator in completeness_indicators):
            base_score += 0.3
        
        # URL structure indicators (deeper paths often mean more specific content)
        try:
            parsed = urlparse(url)
            path_parts = [part for part in parsed.path.split('/') if part]
            if len(path_parts) >= 3:
                base_score += 0.1
            elif len(path_parts) <= 1:
                base_score -= 0.1
        except Exception:
            pass
        
        # Penalty for very short titles (likely incomplete)
        if len(title) < 20:
            base_score -= 0.2
        
        return min(max(base_score, 0.0), 1.0)
    
    def _calculate_recency_score(self, url: str, title: str) -> float:
        """Estimate content recency based on URL patterns and title indicators."""
        base_score = 0.6  # Default moderate recency
        
        # Look for year indicators in URL
        current_year = datetime.now().year
        years_pattern = r'\b(19|20)\d{2}\b'
        
        url_years = re.findall(years_pattern, url)
        title_years = re.findall(years_pattern, title)
        
        all_years = []
        for match in url_years + title_years:
            try:
                year = int(match + re.search(r'\d{2}', url + title).group())
                if 1990 <= year <= current_year + 1:
                    all_years.append(year)
            except (ValueError, AttributeError):
                continue
        
        if all_years:
            latest_year = max(all_years)
            years_ago = current_year - latest_year
            
            if years_ago <= 1:
                base_score = 0.95
            elif years_ago <= 2:
                base_score = 0.8
            elif years_ago <= 5:
                base_score = 0.6
            else:
                base_score = 0.3
        
        # Look for recency indicators in title
        recent_indicators = [
            '2024', '2023', 'latest', 'recent', 'new', 'current',
            'updated', 'breaking', 'today', 'this year'
        ]
        
        if any(indicator in title.lower() for indicator in recent_indicators):
            base_score += 0.2
        
        # Old indicators penalty
        old_indicators = ['archive', 'historical', 'vintage', 'classic', 'old']
        if any(indicator in title.lower() for indicator in old_indicators):
            base_score -= 0.3
        
        return min(max(base_score, 0.0), 1.0)
    
    def classify_and_filter_sources_graduated(self, sources: List[Source], 
                                             source_quality_filter: str = None,
                                             quality_threshold: float = None) -> Dict[str, Any]:
        """
        Return both included and filtered sources with quality scores.
        
        Args:
            sources: List of sources to classify
            source_quality_filter: Quality filter level ('any', 'medium', 'high')
            quality_threshold: Custom quality threshold (0.0-1.0)
        
        Returns:
            {
                "included": [high_quality_sources],
                "filtered": [lower_quality_sources_with_scores],
                "quality_summary": {"avg_score": 0.8, "total_sources": 10, ...}
            }
        """
        if not sources:
            return {
                "included": [],
                "filtered": [],
                "quality_summary": {
                    "total_sources": 0,
                    "included_sources": 0,
                    "filtered_sources": 0,
                    "average_quality_score": 0.0,
                    "quality_threshold": quality_threshold or 0.0
                }
            }
        
        # Determine quality threshold
        if quality_threshold is not None:
            threshold = quality_threshold
        elif source_quality_filter == 'high':
            threshold = 0.8
        elif source_quality_filter == 'medium':
            threshold = 0.6
        else:  # 'any' or None
            threshold = 0.0
        
        # Calculate quality scores for all sources
        sources_with_scores = []
        for source in sources:
            # Use a default query for scoring if not available
            quality_metrics = self.calculate_user_facing_quality_score(source, "")
            
            # Update source with quality information
            source.quality_score = quality_metrics['overall_score']
            source.quality_breakdown = quality_metrics
            
            sources_with_scores.append(source)
        
        # Separate included and filtered sources
        included_sources = [s for s in sources_with_scores if s.quality_score >= threshold]
        filtered_sources = [s for s in sources_with_scores if s.quality_score < threshold]
        
        # Calculate quality summary
        if included_sources:
            avg_score = sum(s.quality_score for s in included_sources) / len(included_sources)
        else:
            avg_score = 0.0
        
        quality_summary = {
            "total_sources": len(sources),
            "included_sources": len(included_sources),
            "filtered_sources": len(filtered_sources),
            "average_quality_score": avg_score,
            "quality_threshold": threshold
        }
        
        return {
            "included": included_sources,
            "filtered": filtered_sources,
            "quality_summary": quality_summary
        }


# Global quality validator instance
quality_validator = QualityValidator()