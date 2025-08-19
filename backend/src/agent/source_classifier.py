"""Source bias assessment and classification service."""

from typing import Optional, Dict, Set
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class SourceClassifier:
    """Lightweight source classifier for domain-based credibility assessment."""
    
    def __init__(self):
        # Academic domains (high credibility)
        self.academic_domains = {
            '.edu', '.ac.uk', '.edu.au', '.ac.jp', '.uni-', '.univ-',
            'arxiv.org', 'pubmed.ncbi.nlm.nih.gov', 'scholar.google.com',
            'ieee.org', 'acm.org', 'springer.com', 'elsevier.com',
            'nature.com', 'science.org', 'cell.com', 'pnas.org'
        }
        
        # Trusted news sources (medium-high credibility)
        self.news_domains = {
            'reuters.com', 'ap.org', 'bbc.com', 'npr.org', 'pbs.org',
            'wsj.com', 'nytimes.com', 'washingtonpost.com', 'ft.com',
            'economist.com', 'theguardian.com', 'cnn.com', 'abcnews.go.com'
        }
        
        # Government/official domains (high credibility)
        self.official_domains = {
            '.gov', '.mil', '.gov.uk', '.gov.au', '.gov.ca',
            'who.int', 'un.org', 'europa.eu', 'oecd.org'
        }
        
        # Commercial software/tech domains (medium credibility with bias risk)
        self.tech_commercial_domains = {
            'microsoft.com', 'google.com', 'amazon.com', 'apple.com',
            'github.com', 'stackoverflow.com', 'medium.com', 'dev.to',
            'docs.microsoft.com', 'developer.mozilla.org', 'docs.google.com'
        }
        
        # Cache for classification results
        self._classification_cache: Dict[str, Dict[str, str]] = {}
    
    def classify_source(self, url: str) -> Dict[str, Optional[str]]:
        """
        Classify a source based on its URL.
        
        Args:
            url: Source URL to classify
            
        Returns:
            Dict containing source_credibility and domain_type
        """
        if url in self._classification_cache:
            return self._classification_cache[url]
        
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc.lower()
            
            # Remove www. prefix for consistency
            if domain.startswith('www.'):
                domain = domain[4:]
            
            credibility, domain_type = self._classify_domain(domain)
            
            result = {
                'source_credibility': credibility,
                'domain_type': domain_type
            }
            
            # Cache the result
            self._classification_cache[url] = result
            return result
            
        except Exception as e:
            logger.warning(f"Error classifying source {url}: {e}")
            return {
                'source_credibility': None,
                'domain_type': None
            }
    
    def _classify_domain(self, domain: str) -> tuple[Optional[str], Optional[str]]:
        """Classify domain based on rules."""
        
        # Check academic domains
        if self._matches_domains(domain, self.academic_domains):
            return "high", "academic"
        
        # Check official/government domains
        if self._matches_domains(domain, self.official_domains):
            return "high", "official"
        
        # Check news domains
        if domain in self.news_domains:
            return "medium", "news"
        
        # Check tech/commercial domains
        if domain in self.tech_commercial_domains:
            return "medium", "commercial"
        
        # Generic commercial detection (.com domains not in trusted lists)
        if domain.endswith('.com') and domain not in self.news_domains:
            return "low", "commercial"
        
        # Default classification for unknown domains
        return "medium", "other"
    
    def _matches_domains(self, domain: str, domain_set: Set[str]) -> bool:
        """Check if domain matches any pattern in the domain set."""
        for pattern in domain_set:
            if pattern.startswith('.'):
                # TLD or suffix check - handle compound TLDs like .gov.uk
                if domain.endswith(pattern):
                    return True
                # Handle exact match for TLD patterns (e.g., 'gov.uk' matches '.gov.uk')
                if domain == pattern[1:]:  # Remove leading dot and compare
                    return True
            elif '-' in pattern and pattern.endswith('-'):
                # Prefix check (like 'uni-', 'univ-')
                if pattern[:-1] in domain:
                    return True
            elif domain == pattern or domain.endswith('.' + pattern):
                # Exact domain match
                return True
        return False
    
    def should_filter_source(self, credibility: Optional[str], 
                           min_credibility: str) -> bool:
        """
        Determine if source should be filtered based on credibility threshold.
        
        Args:
            credibility: Source credibility level
            min_credibility: Minimum required credibility level
            
        Returns:
            True if source should be filtered (excluded)
        """
        if not credibility:
            return False  # Don't filter sources we couldn't classify
        
        credibility_order = {"low": 0, "medium": 1, "high": 2}
        
        source_level = credibility_order.get(credibility, 1)  # Default to medium
        min_level = credibility_order.get(min_credibility, 0)
        
        return source_level < min_level
    
    def get_classification_stats(self) -> Dict[str, int]:
        """Get statistics about cached classifications."""
        stats = {
            "total_classified": len(self._classification_cache),
            "high_credibility": 0,
            "medium_credibility": 0,
            "low_credibility": 0,
            "academic": 0,
            "news": 0,
            "commercial": 0,
            "official": 0,
            "other": 0
        }
        
        for classification in self._classification_cache.values():
            cred = classification.get('source_credibility')
            domain_type = classification.get('domain_type')
            
            if cred:
                stats[f"{cred}_credibility"] += 1
            if domain_type:
                stats[domain_type] += 1
        
        return stats