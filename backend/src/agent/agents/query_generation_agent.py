"""
Agent for generating search queries from research topics.
"""

from typing import List
from agent.base import InstructorBasedAgent, handle_agent_errors, safe_format_template
from agent.state import QueryGenerationInput, QueryGenerationOutput
from agent.configuration import Configuration
from agent.prompts import query_writer_instructions


class QueryGenerationAgent(InstructorBasedAgent[QueryGenerationInput, QueryGenerationOutput]):
    """Atomic agent for generating search queries."""
    
    def _initialize_agent_config(self) -> None:
        """Initialize the agent configuration."""
        self.agent_config = self.config.create_agent_config()
    
    @handle_agent_errors(context="query generation")
    def run(self, input_data: QueryGenerationInput) -> QueryGenerationOutput:
        """Generate search queries based on research topic."""
        
        if not self._validate_input(input_data):
            return self._create_fallback_response(input_data, "invalid input")
        
        # Format the prompt safely
        formatted_prompt = safe_format_template(
            query_writer_instructions,
            current_date=input_data.current_date,
            research_topic=input_data.research_topic,
            number_queries=input_data.number_of_queries,
        )
        
        # Make LLM call safely
        response = self._safe_llm_call(
            formatted_prompt,
            QueryGenerationOutput,
            "query generation"
        )
        
        if response is not None:
            return response
        else:
            return self._create_fallback_response(input_data, "LLM call failed")
    
    def _create_fallback_response(self, input_data: QueryGenerationInput, error_context: str) -> QueryGenerationOutput:
        """Create a fallback response when query generation fails."""
        # Handle None input_data safely
        topic = "general topic"
        requested_count = 3
        
        if input_data is not None:
            topic = getattr(input_data, 'research_topic', None) or "general topic"
            requested_count = getattr(input_data, 'number_of_queries', 3)
        
        print(f"🔄 Using fallback query generation for: {topic}")
        
        # Create basic fallback queries based on the topic
        fallback_queries = [
            f"What is {topic}?",
            f"Information about {topic}",
            f"Recent developments in {topic}"
        ]
        
        # Limit to requested number of queries
        fallback_queries = fallback_queries[:requested_count]
        
        return QueryGenerationOutput(
            queries=fallback_queries,
            rationale=f"Generated basic search queries for: {topic} (fallback due to: {error_context})"
        )