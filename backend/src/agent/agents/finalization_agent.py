"""
Agent for finalizing research answers with proper citations.
"""

from typing import List
from agent.base import InstructorBasedAgent, handle_agent_errors, safe_format_template
from agent.state import FinalizationInput, FinalizationOutput, Source, QualitySummary
from agent.configuration import Configuration
from agent.prompts import answer_instructions
from agent.source_classifier import SourceClassifier
from agent.quality_validator import quality_validator


class FinalizationAgent(InstructorBasedAgent[FinalizationInput, FinalizationOutput]):
    """Atomic agent for finalizing research answers."""
    
    def __init__(self, config: Configuration, model_override: str = None):
        """Initialize with optional model override."""
        self.model_override = model_override
        self.source_classifier = SourceClassifier()
        super().__init__(config)
    
    def _initialize_agent_config(self) -> None:
        """Initialize the agent configuration."""
        if self.model_override:
            # Create answer config with model override
            self.agent_config = self.config.create_agent_config(self.model_override)
        else:
            self.agent_config = self.config.create_answer_config()
    
    @handle_agent_errors(context="finalization")
    def run(self, input_data: FinalizationInput) -> FinalizationOutput:
        """Finalize the research answer with proper citations."""
        
        if not self._validate_input(input_data):
            return self._create_fallback_response(input_data, "invalid input")
        
        # Classify and optionally filter sources using appropriate method
        if input_data.enhanced_filtering:
            filtering_result = self._classify_and_filter_sources_enhanced(
                input_data.sources, 
                input_data.source_quality_filter,
                input_data.quality_threshold
            )
            classified_sources = filtering_result["included"]
            filtered_sources = filtering_result["filtered"]
            quality_summary = filtering_result["quality_summary"]
            filtering_applied = len(filtered_sources) > 0
        else:
            classified_sources = self._classify_and_filter_sources(
                input_data.sources, 
                input_data.source_quality_filter
            )
            filtered_sources = []
            quality_summary = None
            filtering_applied = len(classified_sources) < len(input_data.sources)
        
        # Create modified input with classified sources for downstream processing
        modified_input = FinalizationInput(
            research_topic=input_data.research_topic,
            summaries=input_data.summaries,
            sources=classified_sources,
            current_date=input_data.current_date,
            source_quality_filter=input_data.source_quality_filter,
            enhanced_filtering=input_data.enhanced_filtering,
            quality_threshold=input_data.quality_threshold
        )
        
        # Format the prompt using answer instructions
        formatted_prompt = safe_format_template(
            answer_instructions,
            current_date=modified_input.current_date,
            research_topic=modified_input.research_topic,
            summaries="\n".join(modified_input.summaries) if modified_input.summaries else "No research summaries available."
        )
        
        # Make LLM call safely
        response = self._safe_llm_call(
            formatted_prompt,
            FinalizationOutput,
            "answer finalization"
        )
        
        if response is not None:
            # Ensure response uses classified sources
            response.used_sources = [s for s in response.used_sources if s in classified_sources]
            
            # Add transparency information for enhanced filtering
            if input_data.enhanced_filtering:
                response.filtered_sources = filtered_sources
                response.quality_summary = QualitySummary(
                    total_sources=quality_summary["total_sources"],
                    included_sources=quality_summary["included_sources"],
                    filtered_sources=quality_summary["filtered_sources"],
                    average_quality_score=quality_summary["average_quality_score"],
                    quality_threshold=quality_summary["quality_threshold"]
                )
                response.filtering_applied = filtering_applied
            
            return response
        else:
            return self._create_fallback_response(modified_input, "LLM call failed")
    
    def _create_fallback_response(self, input_data: FinalizationInput, error_context: str) -> FinalizationOutput:
        """Create a fallback response when finalization fails."""
        # Handle None input_data safely
        topic = "the requested topic"
        summaries = []
        sources = []
        
        if input_data is not None:
            topic = getattr(input_data, 'research_topic', None) or "the requested topic"
            summaries = getattr(input_data, 'summaries', None) or []
            sources = getattr(input_data, 'sources', None) or []
        
        print(f"🔄 Using fallback finalization for: {topic}")
        
        # Create a basic final answer from the research content
        if summaries and len(summaries) > 0:
            # Use the first summary as the base for the final answer
            final_answer = f"Based on the research: {summaries[0]}"
            
            # Add additional summaries if available
            if len(summaries) > 1:
                final_answer += f"\n\nAdditional findings:\n"
                for i, summary in enumerate(summaries[1:], 2):
                    final_answer += f"{i}. {summary}\n"
            
            final_answer += f"\n\n(Note: This is a fallback response due to: {error_context})"
        else:
            # No summaries available, create a basic response
            final_answer = f"Unable to provide comprehensive information about {topic}. "
            final_answer += f"Research data was not available. "
            final_answer += f"(Fallback response due to: {error_context})"
        
        # Use up to 3 sources if available
        used_sources = sources[:3] if sources else []
        
        return FinalizationOutput(
            final_answer=final_answer,
            used_sources=used_sources
        )
    
    def _classify_and_filter_sources(self, sources: List[Source], 
                                   source_quality_filter: str = None) -> List[Source]:
        """Classify sources and optionally filter by quality."""
        if not sources:
            return sources
        
        classified_sources = []
        
        for source in sources:
            try:
                # Classify the source
                classification = self.source_classifier.classify_source(source.url)
                
                # Update source with classification data
                source.source_credibility = classification.get('source_credibility')
                source.domain_type = classification.get('domain_type')
                
                # Apply filtering if requested
                if source_quality_filter:
                    if not self.source_classifier.should_filter_source(
                        source.source_credibility, 
                        source_quality_filter
                    ):
                        classified_sources.append(source)
                else:
                    # No filtering requested, include all classified sources
                    classified_sources.append(source)
                    
            except Exception as e:
                # If classification fails, include the source without classification
                print(f"Warning: Failed to classify source {source.url}: {e}")
                classified_sources.append(source)
        
        return classified_sources
    
    def _classify_and_filter_sources_enhanced(self, sources: List[Source], 
                                            source_quality_filter: str = None,
                                            quality_threshold: float = None) -> dict:
        """Enhanced source classification and filtering using graduated quality scores."""
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
        
        # First apply basic classification for compatibility
        classified_sources = []
        for source in sources:
            try:
                # Classify the source using existing method
                classification = self.source_classifier.classify_source(source.url)
                
                # Update source with classification data
                source.source_credibility = classification.get('source_credibility')
                source.domain_type = classification.get('domain_type')
                
                classified_sources.append(source)
                    
            except Exception as e:
                # If classification fails, include the source without classification
                print(f"Warning: Failed to classify source {source.url}: {e}")
                classified_sources.append(source)
        
        # Apply enhanced graduated filtering
        return quality_validator.classify_and_filter_sources_graduated(
            classified_sources,
            source_quality_filter,
            quality_threshold
        )