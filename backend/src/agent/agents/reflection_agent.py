"""
Agent for reflection and knowledge gap analysis.
"""

from typing import List
from agent.base import InstructorBasedAgent, handle_agent_errors, safe_format_template
from agent.state import ReflectionInput, ReflectionOutput
from agent.configuration import Configuration
from agent.prompts import reflection_instructions


class ReflectionAgent(InstructorBasedAgent[ReflectionInput, ReflectionOutput]):
    """Atomic agent for reflection and knowledge gap analysis."""
    
    def _initialize_agent_config(self) -> None:
        """Initialize the agent configuration."""
        self.agent_config = self.config.create_reflection_config()
    
    @handle_agent_errors(context="reflection")
    def run(self, input_data: ReflectionInput) -> ReflectionOutput:
        """Analyze research sufficiency and generate follow-up queries."""
        
        if not self._validate_input(input_data):
            return self._create_fallback_response(input_data, "invalid input")
        
        # Format the prompt using reflection instructions
        formatted_prompt = safe_format_template(
            reflection_instructions,
            research_topic=input_data.research_topic,
            summaries="\n".join(input_data.summaries) if input_data.summaries else "No summaries available."
        )
        
        # Make LLM call safely
        response = self._safe_llm_call(
            formatted_prompt,
            ReflectionOutput,
            "reflection analysis"
        )
        
        if response is not None:
            return response
        else:
            return self._create_fallback_response(input_data, "LLM call failed")
    
    def _create_fallback_response(self, input_data: ReflectionInput, error_context: str) -> ReflectionOutput:
        """Create a fallback response when reflection fails."""
        # Handle None input_data safely
        topic = "the topic"
        has_summaries = False
        
        if input_data is not None:
            topic = getattr(input_data, 'research_topic', None) or "the topic"
            summaries = getattr(input_data, 'summaries', None)
            has_summaries = summaries and len(summaries) > 0
        
        print(f"🔄 Using fallback reflection for: {topic}")
        
        if has_summaries:
            return ReflectionOutput(
                is_sufficient=True,
                knowledge_gap=f"Research appears sufficient based on available summaries (fallback due to: {error_context})",
                follow_up_queries=[]
            )
        else:
            return ReflectionOutput(
                is_sufficient=False,
                knowledge_gap=f"No research summaries available for {topic}. Basic research is needed (fallback due to: {error_context})",
                follow_up_queries=[
                    f"What is {topic}?",
                    f"Key aspects of {topic}",
                    f"Current state of {topic}"
                ]
            )