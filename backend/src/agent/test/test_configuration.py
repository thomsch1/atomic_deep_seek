"""
Tests for enhanced configuration module.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from pydantic import ValidationError
import instructor
from agent.configuration import Configuration, AgentConfig
from agent.http_client import HTTPClientConfig


class TestConfiguration:
    """Test Configuration class functionality."""
    
    def test_default_configuration(self):
        """Test default configuration values."""
        config = Configuration()
        
        assert config.query_generator_model == "gemini-2.5-flash"
        assert config.reflection_model == "gemini-2.5-flash"
        assert config.answer_model == "gemini-2.5-flash"
        assert config.number_of_initial_queries == 3
        assert config.max_research_loops == 2
        assert config.http_timeout == 30.0
        assert config.http_max_connections == 100
        assert config.http_retries == 3
        assert config.rate_limit_requests_per_minute == 60
    
    def test_custom_configuration(self):
        """Test custom configuration values."""
        config = Configuration(
            query_generator_model="gemini-2.0-flash",
            http_timeout=45.0,
            http_retries=5,
            rate_limit_requests_per_minute=120
        )
        
        assert config.query_generator_model == "gemini-2.0-flash"
        assert config.http_timeout == 45.0
        assert config.http_retries == 5
        assert config.rate_limit_requests_per_minute == 120
    
    def test_supported_models(self):
        """Test supported models functionality."""
        config = Configuration()
        
        supported_models = config.get_supported_models()
        assert isinstance(supported_models, list)
        assert "gemini-2.5-flash" in supported_models
        assert "gemini-1.5-pro" in supported_models
        assert len(supported_models) > 0
    
    def test_validate_model_supported(self):
        """Test model validation for supported models."""
        config = Configuration()
        
        assert config.validate_model("gemini-2.5-flash") is True
        assert config.validate_model("gemini-1.5-pro") is True
    
    def test_validate_model_unsupported(self):
        """Test model validation for unsupported models."""
        config = Configuration()
        
        assert config.validate_model("unsupported-model") is False
        assert config.validate_model("gpt-4") is False
    
    @patch.dict('os.environ', {
        'QUERY_GENERATOR_MODEL': 'gemini-2.0-flash',
        'HTTP_TIMEOUT': '60.0',
        'HTTP_RETRIES': '5'
    })
    def test_from_config_dict_with_env(self):
        """Test configuration creation from environment variables."""
        config = Configuration.from_config_dict()
        
        assert config.query_generator_model == "gemini-2.0-flash"
        assert config.http_timeout == 60.0
        assert config.http_retries == 5
    
    def test_from_config_dict_with_dict(self):
        """Test configuration creation from config dictionary."""
        config_dict = {
            'query_generator_model': 'gemini-1.5-pro',
            'http_timeout': 25.0,
            'max_research_loops': 3
        }
        
        config = Configuration.from_config_dict(config_dict)
        
        assert config.query_generator_model == "gemini-1.5-pro"
        assert config.http_timeout == 25.0
        assert config.max_research_loops == 3


class TestConfigurationValidation:
    """Test configuration validation functionality."""
    
    def test_http_timeout_positive(self):
        """Test HTTP timeout validation for positive values."""
        config = Configuration(http_timeout=30.0)
        assert config.http_timeout == 30.0
    
    def test_http_timeout_negative_raises_error(self):
        """Test HTTP timeout validation raises error for negative values."""
        with pytest.raises(ValidationError):
            Configuration(http_timeout=-5.0)
    
    def test_http_timeout_zero_raises_error(self):
        """Test HTTP timeout validation raises error for zero."""
        with pytest.raises(ValidationError):
            Configuration(http_timeout=0.0)
    
    def test_http_retries_non_negative(self):
        """Test HTTP retries validation for non-negative values."""
        config = Configuration(http_retries=3)
        assert config.http_retries == 3
        
        config_zero = Configuration(http_retries=0)
        assert config_zero.http_retries == 0
    
    def test_http_retries_negative_raises_error(self):
        """Test HTTP retries validation raises error for negative values."""
        with pytest.raises(ValidationError):
            Configuration(http_retries=-1)
    
    def test_rate_limit_rpm_positive(self):
        """Test rate limit RPM validation for positive values."""
        config = Configuration(rate_limit_requests_per_minute=120)
        assert config.rate_limit_requests_per_minute == 120
    
    def test_rate_limit_rpm_zero_raises_error(self):
        """Test rate limit RPM validation raises error for zero."""
        with pytest.raises(ValidationError):
            Configuration(rate_limit_requests_per_minute=0)
    
    def test_rate_limit_rpm_negative_raises_error(self):
        """Test rate limit RPM validation raises error for negative values."""
        with pytest.raises(ValidationError):
            Configuration(rate_limit_requests_per_minute=-10)


class TestAgentConfigCreation:
    """Test agent configuration creation."""
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_api_key'})
    @patch('agent.configuration.genai.Client')
    @patch('agent.configuration.instructor.from_genai')
    def test_create_agent_config_success(self, mock_instructor, mock_client_class):
        """Test successful agent config creation."""
        mock_genai_client = MagicMock()
        mock_client_class.return_value = mock_genai_client
        mock_instructor_client = MagicMock()
        mock_instructor.return_value = mock_instructor_client
        
        config = Configuration()
        agent_config = config.create_agent_config()
        
        assert isinstance(agent_config, AgentConfig)
        assert agent_config.client is mock_instructor_client
        assert agent_config.temperature == 1.0
        assert agent_config.max_retries == 2
        
        mock_client_class.assert_called_once_with(api_key='test_api_key')
        mock_instructor.assert_called_once_with(client=mock_genai_client, mode=instructor.Mode.GENAI_STRUCTURED_OUTPUTS)
    
    @patch.dict('os.environ', {'GOOGLE_API_KEY': 'google_test_key'})
    @patch('agent.configuration.genai.Client')
    @patch('agent.configuration.instructor.from_genai')
    def test_create_agent_config_with_google_api_key(self, mock_instructor, mock_client_class):
        """Test agent config creation with Google API key."""
        mock_genai_client = MagicMock()
        mock_client_class.return_value = mock_genai_client
        mock_instructor_client = MagicMock()
        mock_instructor.return_value = mock_instructor_client
        
        config = Configuration()
        agent_config = config.create_agent_config()
        
        mock_client_class.assert_called_once_with(api_key='google_test_key')
    
    def test_create_agent_config_unsupported_model(self):
        """Test agent config creation with unsupported model."""
        config = Configuration()
        
        with pytest.raises(ValueError, match="Unsupported model"):
            config.create_agent_config(model_override="unsupported-model")
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'})
    @patch('agent.configuration.genai.Client')
    @patch('agent.configuration.instructor.from_genai')
    def test_create_reflection_config(self, mock_instructor, mock_client_class):
        """Test reflection config creation."""
        mock_genai_client = MagicMock()
        mock_client_class.return_value = mock_genai_client
        mock_instructor_client = MagicMock()
        mock_instructor.return_value = mock_instructor_client
        
        config = Configuration(reflection_model="gemini-2.0-flash")
        
        reflection_config = config.create_reflection_config()
        
        assert isinstance(reflection_config, AgentConfig)
        mock_client_class.assert_called_with(api_key='test_key')
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'})
    @patch('agent.configuration.genai.Client')
    @patch('agent.configuration.instructor.from_genai')
    def test_create_answer_config(self, mock_instructor, mock_client_class):
        """Test answer config creation."""
        mock_genai_client = MagicMock()
        mock_client_class.return_value = mock_genai_client
        mock_instructor_client = MagicMock()
        mock_instructor.return_value = mock_instructor_client
        
        config = Configuration(answer_model="gemini-1.5-pro")
        
        answer_config = config.create_answer_config()
        
        assert isinstance(answer_config, AgentConfig)
        mock_client_class.assert_called_with(api_key='test_key')


class TestHTTPConfigCreation:
    """Test HTTP client configuration creation."""
    
    def test_create_http_config_default(self):
        """Test HTTP config creation with default values."""
        config = Configuration()
        http_config = config.create_http_config()
        
        assert isinstance(http_config, HTTPClientConfig)
        assert http_config.timeout == 30.0
        assert http_config.max_connections == 100
        assert http_config.retries == 3
    
    def test_create_http_config_custom(self):
        """Test HTTP config creation with custom values."""
        config = Configuration(
            http_timeout=45.0,
            http_max_connections=200,
            http_retries=5,
            http_verify_ssl=False
        )
        
        http_config = config.create_http_config()
        
        assert http_config.timeout == 45.0
        assert http_config.max_connections == 200
        assert http_config.retries == 5
        assert http_config.verify_ssl is False


class TestEnvironmentValidation:
    """Test environment validation functionality."""
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'valid_api_key_12345'})
    def test_validate_environment_with_gemini_key(self):
        """Test environment validation with Gemini API key."""
        config = Configuration()
        status = config.validate_environment()
        
        assert status['api_key'] == 'OK'
        assert 'error' not in status
    
    @patch.dict('os.environ', {'GOOGLE_API_KEY': 'valid_google_key_12345'})
    def test_validate_environment_with_google_key(self):
        """Test environment validation with Google API key."""
        config = Configuration()
        status = config.validate_environment()
        
        assert status['api_key'] == 'OK'
        assert 'error' not in status
    
    @patch.dict('os.environ', {}, clear=True)
    def test_validate_environment_missing_api_key(self):
        """Test environment validation with missing API key."""
        config = Configuration()
        status = config.validate_environment()
        
        assert 'error' in status
        assert 'Missing required API key' in status['error']
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'short'})
    def test_validate_environment_short_api_key(self):
        """Test environment validation with suspiciously short API key."""
        config = Configuration()
        status = config.validate_environment()
        
        assert 'api_key_warning' in status
        assert status['api_key_warning'] == 'API key seems too short'
    
    @patch.dict('os.environ', {
        'GEMINI_API_KEY': 'valid_key_12345',
        'GOOGLE_SEARCH_ENGINE_ID': 'search_engine_id',
        'SEARCHAPI_API_KEY': 'searchapi_key'
    })
    def test_validate_environment_multiple_search_providers(self):
        """Test environment validation with multiple search providers."""
        config = Configuration()
        status = config.validate_environment()
        
        assert status['search_providers'] == '2 configured'
        assert 'search_warning' not in status
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'valid_key_12345'})
    def test_validate_environment_no_search_providers(self):
        """Test environment validation with no search providers."""
        config = Configuration()
        status = config.validate_environment()
        
        assert 'search_warning' in status
        assert 'No search providers configured' in status['search_warning']
    
    @patch.dict('os.environ', {
        'GEMINI_API_KEY': 'valid_key_12345',
        'HTTP_TIMEOUT': '60.0',
        'HTTP_MAX_CONNECTIONS': '150'
    })
    def test_validate_environment_optional_vars_set(self):
        """Test environment validation with optional variables set."""
        config = Configuration()
        status = config.validate_environment()
        
        assert status['HTTP_TIMEOUT'] == 'Set'
        assert status['HTTP_MAX_CONNECTIONS'] == 'Set'
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'valid_key_12345'})
    def test_validate_environment_optional_vars_not_set(self):
        """Test environment validation with optional variables not set.""" 
        config = Configuration()
        status = config.validate_environment()
        
        assert status['HTTP_TIMEOUT'] == 'Not set'
        assert status['HTTP_MAX_CONNECTIONS'] == 'Not set'


class TestAgentConfigClass:
    """Test AgentConfig class functionality."""
    
    def test_agent_config_initialization_default(self):
        """Test AgentConfig initialization with default values."""
        config = AgentConfig()
        
        assert config.client is None
        assert config.temperature == 1.0
        assert config.max_retries == 2
    
    def test_agent_config_initialization_custom(self):
        """Test AgentConfig initialization with custom values."""
        mock_client = MagicMock()
        config = AgentConfig(
            client=mock_client,
            temperature=0.7,
            max_retries=5
        )
        
        assert config.client is mock_client
        assert config.temperature == 0.7
        assert config.max_retries == 5