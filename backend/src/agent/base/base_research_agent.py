"""
Base class for all research agents providing common functionality.
"""

from typing import TypeVar, Generic, Any, Dict
from abc import ABC, abstractmethod
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig
from agent.configuration import Configuration

# Generic types for input/output
InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType')


class BaseResearchAgent(Generic[InputType, OutputType], ABC):
    """
    Abstract base class for all research agents.
    
    Provides common patterns like:
    - Configuration management
    - Error handling patterns
    - Logging integration
    - Common initialization
    """
    
    def __init__(self, config: Configuration):
        """Initialize the base research agent."""
        self.config = config
        self._initialize_agent_config()
    
    @abstractmethod
    def _initialize_agent_config(self) -> None:
        """Initialize the specific agent configuration. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def run(self, input_data: InputType) -> OutputType:
        """Execute the agent's main functionality. Must be implemented by subclasses."""
        pass
    
    def _handle_error(self, error: Exception, context: str) -> None:
        """
        Standard error handling pattern for all agents.
        
        Args:
            error: The exception that occurred
            context: Context description for the error
        """
        error_message = f"❌ {self.__class__.__name__} error in {context}: {error}"
        print(error_message)
        print(f"🔄 Using fallback method")
    
    def _validate_input(self, input_data: InputType) -> bool:
        """
        Validate input data. Can be overridden by subclasses for specific validation.
        
        Args:
            input_data: The input to validate
            
        Returns:
            True if valid, False otherwise
        """
        return input_data is not None
    
    def _create_fallback_response(self, input_data: InputType, error_context: str) -> OutputType:
        """
        Create a fallback response when the main operation fails.
        Must be implemented by subclasses.
        
        Args:
            input_data: The original input data
            error_context: Description of what failed
            
        Returns:
            A fallback response of the appropriate type
        """
        raise NotImplementedError("Subclasses must implement _create_fallback_response")


class InstructorBasedAgent(BaseResearchAgent[InputType, OutputType]):
    """
    Base class for agents using instructor-based LLM interactions.
    
    Provides common patterns for agents that use structured outputs
    with instructor and handle LLM client interactions.
    """
    
    def __init__(self, config: Configuration):
        # Initialize agent_config before calling super, so _initialize_agent_config can set it
        self.agent_config = None
        super().__init__(config)
    
    def _safe_llm_call(self, prompt: str, response_model: type, context: str) -> Any:
        """
        Safely make an LLM call with proper error handling.
        
        Args:
            prompt: The formatted prompt to send
            response_model: The Pydantic model for the response
            context: Context for error messages
            
        Returns:
            The response from the LLM or None if failed
        """
        try:
            if not self.agent_config or not hasattr(self.agent_config, 'client'):
                raise ValueError("Agent configuration not properly initialized")
            
            response = self.agent_config.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                response_model=response_model,
            )
            return response
        except Exception as e:
            self._handle_error(e, context)
            return None
    
    def _format_prompt_safely(self, template: str, **kwargs) -> str:
        """
        Safely format a prompt template with error handling.
        
        Args:
            template: The prompt template string
            **kwargs: Variables to substitute in the template
            
        Returns:
            The formatted prompt or a safe fallback
        """
        try:
            return template.format(**kwargs)
        except (KeyError, ValueError) as e:
            self._handle_error(e, "prompt formatting")
            # Return a safe fallback prompt
            return f"Please help with: {kwargs.get('research_topic', 'unknown topic')}"