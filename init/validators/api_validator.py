"""
API key validation for Gemini and LangSmith services
"""

import re
import os
import requests
from typing import Dict, Any, Optional
from urllib.parse import urljoin
from dotenv import load_dotenv

from .base import BaseValidator
from ..exceptions import ValidationResult

# Load environment variables
load_dotenv()


class APIKeyValidator(BaseValidator):
    """Validates API keys for external services"""
    
    GEMINI_KEY_PATTERN = re.compile(r'^[A-Za-z0-9_-]{39}$')
    LANGSMITH_KEY_PATTERN = re.compile(r'^ls__[A-Za-z0-9_-]{32,}$')
    
    GEMINI_TEST_URL = "https://generativelanguage.googleapis.com/v1/models"
    LANGSMITH_TEST_URL = "https://api.smith.langchain.com/info"
    
    def __init__(self, config: Dict[str, Any] = None, logger: Optional[Any] = None):
        super().__init__(config, logger)
        self.timeout = self.get_config_value('timeout', 10)
        self.skip_connectivity_test = self.get_config_value('skip_connectivity_test', False)
    
    @property
    def component_name(self) -> str:
        return "API Keys"
    
    def validate(self) -> ValidationResult:
        """Validate all required API keys"""
        results = []
        
        # Check Gemini API key (required)
        gemini_result = self._validate_gemini_key()
        results.append(gemini_result)
        
        # Check LangSmith API key (optional)
        langsmith_result = self._validate_langsmith_key()
        if langsmith_result:
            results.append(langsmith_result)
        
        # Determine overall result
        failed_results = [r for r in results if not r.success]
        if failed_results:
            # If Gemini (required) failed, that's a failure
            gemini_failed = any(r.component == "Gemini API" and not r.success for r in results)
            if gemini_failed:
                return self.create_failure_result(
                    "Required API key validation failed",
                    self._get_combined_suggestions(failed_results)
                )
        
        # All validations passed
        warnings = []
        if not self._get_langsmith_key():
            warnings.append("LangSmith API key not configured - observability features disabled")
        
        return self.create_success_result(
            "All API keys validated successfully",
            warnings=warnings,
            details={"validated_keys": [r.component for r in results if r.success]}
        )
    
    def _validate_gemini_key(self) -> ValidationResult:
        """Validate Gemini API key"""
        api_key = self._get_gemini_key()
        
        if not api_key:
            return ValidationResult(
                success=False,
                component="Gemini API",
                message="GEMINI_API_KEY environment variable not found",
                suggestions=[
                    "Get your API key from https://makersuite.google.com/app/apikey",
                    "Set GEMINI_API_KEY environment variable",
                    "Or add GEMINI_API_KEY to backend/.env file"
                ]
            )
        
        # Format validation
        if not self.GEMINI_KEY_PATTERN.match(api_key):
            return ValidationResult(
                success=False,
                component="Gemini API",
                message="GEMINI_API_KEY format is invalid",
                suggestions=[
                    "Verify API key is exactly 39 characters",
                    "Check for extra spaces or characters",
                    "Generate a new key if current one is corrupted"
                ]
            )
        
        # Connectivity test
        if not self.skip_connectivity_test:
            connectivity_result = self._test_gemini_connectivity(api_key)
            if not connectivity_result.success:
                return connectivity_result
        
        return ValidationResult(
            success=True,
            component="Gemini API",
            message="Gemini API key validated successfully"
        )
    
    def _validate_langsmith_key(self) -> Optional[ValidationResult]:
        """Validate LangSmith API key (optional)"""
        api_key = self._get_langsmith_key()
        
        if not api_key:
            return None  # Optional key, skip if not provided
        
        # Format validation
        if not self.LANGSMITH_KEY_PATTERN.match(api_key):
            return ValidationResult(
                success=False,
                component="LangSmith API",
                message="LANGSMITH_API_KEY format is invalid",
                suggestions=[
                    "Verify API key starts with 'ls__'",
                    "Check API key length (should be 36+ characters)",
                    "Generate a new key from LangSmith console"
                ]
            )
        
        # Connectivity test
        if not self.skip_connectivity_test:
            connectivity_result = self._test_langsmith_connectivity(api_key)
            if not connectivity_result.success:
                return connectivity_result
        
        return ValidationResult(
            success=True,
            component="LangSmith API",
            message="LangSmith API key validated successfully"
        )
    
    def _test_gemini_connectivity(self, api_key: str) -> ValidationResult:
        """Test Gemini API connectivity"""
        try:
            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.get(
                self.GEMINI_TEST_URL,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return ValidationResult(
                    success=True,
                    component="Gemini API",
                    message="Gemini API connectivity test passed"
                )
            elif response.status_code == 401:
                return ValidationResult(
                    success=False,
                    component="Gemini API",
                    message="Gemini API key is invalid or expired",
                    suggestions=[
                        "Verify API key is correct",
                        "Check if API key has expired",
                        "Generate a new API key"
                    ]
                )
            else:
                return ValidationResult(
                    success=False,
                    component="Gemini API",
                    message=f"Gemini API returned status {response.status_code}",
                    suggestions=[
                        "Check Gemini API service status",
                        "Verify API key permissions",
                        "Try again in a few minutes"
                    ]
                )
                
        except requests.exceptions.Timeout:
            return ValidationResult(
                success=False,
                component="Gemini API",
                message="Gemini API connectivity test timed out",
                suggestions=[
                    "Check internet connection",
                    "Verify firewall settings",
                    "Try increasing timeout in configuration"
                ]
            )
        except requests.exceptions.RequestException as e:
            return ValidationResult(
                success=False,
                component="Gemini API",
                message=f"Gemini API connectivity test failed: {str(e)}",
                suggestions=[
                    "Check internet connection",
                    "Verify proxy settings",
                    "Check DNS resolution"
                ]
            )
    
    def _test_langsmith_connectivity(self, api_key: str) -> ValidationResult:
        """Test LangSmith API connectivity"""
        try:
            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.get(
                self.LANGSMITH_TEST_URL,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return ValidationResult(
                    success=True,
                    component="LangSmith API",
                    message="LangSmith API connectivity test passed"
                )
            elif response.status_code == 401:
                return ValidationResult(
                    success=False,
                    component="LangSmith API",
                    message="LangSmith API key is invalid",
                    suggestions=[
                        "Verify API key in LangSmith console",
                        "Check if API key has proper permissions",
                        "Generate a new API key if needed"
                    ]
                )
            else:
                return ValidationResult(
                    success=False,
                    component="LangSmith API",
                    message=f"LangSmith API returned status {response.status_code}",
                    suggestions=[
                        "Check LangSmith service status",
                        "Verify API key permissions"
                    ]
                )
                
        except Exception as e:
            return ValidationResult(
                success=False,
                component="LangSmith API",
                message=f"LangSmith connectivity test failed: {str(e)}",
                suggestions=[
                    "Check internet connection",
                    "Verify API key format"
                ]
            )
    
    def _get_gemini_key(self) -> Optional[str]:
        """Get Gemini API key from environment"""
        return os.environ.get('GEMINI_API_KEY')
    
    def _get_langsmith_key(self) -> Optional[str]:
        """Get LangSmith API key from environment"""
        return os.environ.get('LANGSMITH_API_KEY')
    
    def _get_combined_suggestions(self, failed_results: list) -> list:
        """Combine suggestions from multiple failed validations"""
        suggestions = []
        for result in failed_results:
            suggestions.extend(result.suggestions)
        return list(set(suggestions))  # Remove duplicates