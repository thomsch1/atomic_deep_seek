"""
Agent for finalizing research answers with proper citations.
"""

from typing import List
from agent.base import InstructorBasedAgent, handle_agent_errors, safe_format_template
from agent.state import FinalizationInput, FinalizationOutput, Source
from agent.configuration import Configuration
from agent.prompts import answer_instructions


class FinalizationAgent(InstructorBasedAgent[FinalizationInput, FinalizationOutput]):
    """Atomic agent for finalizing research answers."""
    
    def _initialize_agent_config(self) -> None:
        """Initialize the agent configuration."""
        self.agent_config = self.config.create_answer_config()
    
    @handle_agent_errors(context="finalization")
    def run(self, input_data: FinalizationInput) -> FinalizationOutput:
        """Finalize the research answer with proper citations."""
        
        if not self._validate_input(input_data):
            return self._create_fallback_response(input_data, "invalid input")
        
        # Format the prompt using answer instructions
        formatted_prompt = safe_format_template(
            answer_instructions,
            current_date=input_data.current_date,
            research_topic=input_data.research_topic,
            summaries="\n".join(input_data.summaries) if input_data.summaries else "No research summaries available."
        )
        
        # Make LLM call safely
        response = self._safe_llm_call(
            formatted_prompt,
            FinalizationOutput,
            "answer finalization"
        )
        
        if response is not None:
            return response
        else:
            return self._create_fallback_response(input_data, "LLM call failed")
    
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