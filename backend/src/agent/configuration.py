import os
from pydantic import BaseModel, Field
from typing import Any, Optional, Dict, ClassVar
from atomic_agents.agents.base_agent import BaseAgentConfig
import instructor
import google.generativeai as genai


class AgentConfig:
    """Agent configuration class for compatibility."""
    def __init__(self, client=None, temperature=1.0, max_retries=2):
        self.client = client
        self.temperature = temperature
        self.max_retries = max_retries


class Configuration(BaseModel):
    """The configuration for the agent."""

    query_generator_model: str = Field(
        default="gemini-2.5-flash",
        metadata={
            "description": "The name of the language model to use for the agent's query generation."
        },
    )

    reflection_model: str = Field(
        default="gemini-2.5-flash",
        metadata={
            "description": "The name of the language model to use for the agent's reflection."
        },
    )

    answer_model: str = Field(
        default="gemini-2.5-flash",
        metadata={
            "description": "The name of the language model to use for the agent's answer."
        },
    )

    number_of_initial_queries: int = Field(
        default=3,
        metadata={"description": "The number of initial search queries to generate."},
    )

    max_research_loops: int = Field(
        default=2,
        metadata={"description": "The maximum number of research loops to perform."},
    )
    
    # Supported model names as per Google AI API documentation
    SUPPORTED_MODELS: ClassVar[set[str]] = {
        "gemini-2.5-pro",
        "gemini-2.5-flash", 
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b", 
        "gemini-1.5-pro"
    }

    def validate_model(self, model_name: str) -> bool:
        """Validate that the model name is supported by Google AI API."""
        return model_name in self.SUPPORTED_MODELS
    
    def get_supported_models(self) -> list[str]:
        """Return a list of supported model names."""
        return sorted(list(self.SUPPORTED_MODELS))

    def create_agent_config(self, model_override: Optional[str] = None) -> AgentConfig:
        """Create an AgentConfig instance for Atomic Agents."""
        model = model_override or self.query_generator_model
        
        # Validate model is supported
        if not self.validate_model(model):
            supported = ", ".join(self.get_supported_models())
            raise ValueError(f"Unsupported model '{model}'. Supported models are: {supported}")
        
        # Configure Google GenerativeAI
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
        
        # Create instructor client using the Gemini API
        client = instructor.from_gemini(
            client=genai.GenerativeModel(model),
            mode=instructor.Mode.GEMINI_JSON
        )
        
        return AgentConfig(
            client=client,
            temperature=1.0,
            max_retries=2
        )
    
    def create_reflection_config(self) -> AgentConfig:
        """Create config for reflection agent."""
        return self.create_agent_config(self.reflection_model)
    
    def create_answer_config(self) -> AgentConfig:
        """Create config for answer agent."""
        return self.create_agent_config(self.answer_model)
    
    @classmethod
    def from_config_dict(cls, config: Optional[Dict[str, Any]] = None) -> "Configuration":
        """Create a Configuration instance from a config dictionary."""
        config_dict = config or {}

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), config_dict.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
