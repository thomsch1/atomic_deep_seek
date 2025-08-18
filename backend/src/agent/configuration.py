import os
from pydantic import BaseModel, Field, field_validator
from typing import Any, Optional, Dict, ClassVar
from atomic_agents.agents.base_agent import BaseAgentConfig
import instructor
import google.generativeai as genai
from .logging_config import get_logger
from .http_client import HTTPClientConfig

logger = get_logger(__name__)


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
    
    # HTTP Client Configuration
    http_timeout: float = Field(
        default=30.0,
        metadata={"description": "HTTP request timeout in seconds."},
    )
    
    http_max_connections: int = Field(
        default=100,
        metadata={"description": "Maximum number of HTTP connections."},
    )
    
    http_max_keepalive: int = Field(
        default=20,
        metadata={"description": "Maximum number of keep-alive connections."},
    )
    
    http_keepalive_expiry: float = Field(
        default=5.0,
        metadata={"description": "Keep-alive connection expiry time in seconds."},
    )
    
    http_retries: int = Field(
        default=3,
        metadata={"description": "Number of HTTP request retries."},
    )
    
    http_retry_delay: float = Field(
        default=1.0,
        metadata={"description": "Base delay between HTTP retries in seconds."},
    )
    
    http_verify_ssl: bool = Field(
        default=True,
        metadata={"description": "Whether to verify SSL certificates."},
    )
    
    # Rate Limiting Configuration
    rate_limit_requests_per_minute: int = Field(
        default=60,
        metadata={"description": "Maximum requests per minute for rate limiting."},
    )
    
    rate_limit_burst: int = Field(
        default=10,
        metadata={"description": "Maximum burst requests for rate limiting."},
    )
    
    # Connection Pool Configuration  
    connection_pool_maxsize: int = Field(
        default=20,
        metadata={"description": "Maximum size of connection pool."},
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
    
    @field_validator('http_timeout')
    def validate_http_timeout(cls, v):
        """Validate HTTP timeout is positive."""
        if v <= 0:
            raise ValueError("HTTP timeout must be positive")
        return v
    
    @field_validator('http_retries')
    def validate_http_retries(cls, v):
        """Validate HTTP retries is non-negative."""
        if v < 0:
            raise ValueError("HTTP retries must be non-negative")
        return v
    
    @field_validator('rate_limit_requests_per_minute')
    def validate_rate_limit_rpm(cls, v):
        """Validate rate limit RPM is positive."""
        if v <= 0:
            raise ValueError("Rate limit requests per minute must be positive")
        return v

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
    
    def create_http_config(self) -> HTTPClientConfig:
        """Create HTTP client configuration."""
        return HTTPClientConfig(
            timeout=self.http_timeout,
            max_connections=self.http_max_connections,
            max_keepalive_connections=self.http_max_keepalive,
            keepalive_expiry=self.http_keepalive_expiry,
            retries=self.http_retries,
            retry_delay=self.http_retry_delay,
            verify_ssl=self.http_verify_ssl
        )
    
    def validate_environment(self) -> Dict[str, str]:
        """Validate required environment variables and return status."""
        required_vars = {
            'GEMINI_API_KEY': 'Required for Gemini AI API access',
            'GOOGLE_API_KEY': 'Alternative to GEMINI_API_KEY for Google services'
        }
        
        optional_vars = {
            'GOOGLE_SEARCH_ENGINE_ID': 'Required for Google Custom Search API',
            'SEARCHAPI_API_KEY': 'Required for SearchAPI.io service',
            'HTTP_TIMEOUT': 'HTTP request timeout (default: 30.0)',
            'HTTP_MAX_CONNECTIONS': 'Max HTTP connections (default: 100)',
            'HTTP_RETRIES': 'HTTP retry attempts (default: 3)',
        }
        
        status = {}
        
        # Check required variables (at least one API key must be present)
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            status['error'] = 'Missing required API key: GEMINI_API_KEY or GOOGLE_API_KEY'
            logger.error(status['error'])
        else:
            status['api_key'] = 'OK'
        
        # Check optional variables
        for var, description in optional_vars.items():
            value = os.getenv(var)
            status[var] = 'Set' if value else 'Not set'
            if not value:
                logger.warning(f"{var} not set: {description}")
        
        # Validate API keys format (basic checks)
        if api_key:
            if len(api_key) < 10:
                status['api_key_warning'] = 'API key seems too short'
                logger.warning('API key seems unusually short')
        
        # Check search configuration
        google_api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        searchapi_key = os.getenv('SEARCHAPI_API_KEY')
        
        search_providers = 0
        if google_api_key and search_engine_id:
            search_providers += 1
        if searchapi_key:
            search_providers += 1
        
        if search_providers == 0:
            status['search_warning'] = 'No search providers configured - will use DuckDuckGo only'
            logger.warning('No external search providers configured - performance may be limited')
        else:
            status['search_providers'] = f'{search_providers} configured'
        
        return status
    
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
