"""
Base validator class for all validation components
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from ..exceptions import ValidationResult, ValidationError


class BaseValidator(ABC):
    """Base class for all validators"""
    
    def __init__(self, config: Dict[str, Any] = None, logger: Optional[logging.Logger] = None):
        self.config = config or {}
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self._validation_cache = {}
    
    @abstractmethod
    def validate(self) -> ValidationResult:
        """
        Perform validation check
        
        Returns:
            ValidationResult: Result of validation with details
        """
        pass
    
    @property
    @abstractmethod
    def component_name(self) -> str:
        """Name of the component being validated"""
        pass
    
    def get_config_value(self, key: str, default: Any = None, required: bool = False) -> Any:
        """
        Get configuration value with validation
        
        Args:
            key: Configuration key
            default: Default value if key not found
            required: Whether the key is required
            
        Returns:
            Configuration value
            
        Raises:
            ValidationError: If required key is missing
        """
        value = self.config.get(key, default)
        if required and value is None:
            raise ValidationError(
                self.component_name,
                f"Required configuration key '{key}' is missing",
                [f"Add '{key}' to configuration"]
            )
        return value
    
    def _cache_result(self, key: str, result: ValidationResult) -> ValidationResult:
        """Cache validation result for performance"""
        self._cache_result[key] = result
        return result
    
    def _get_cached_result(self, key: str) -> Optional[ValidationResult]:
        """Get cached validation result"""
        return self._validation_cache.get(key)
    
    def log_validation_start(self):
        """Log start of validation"""
        self.logger.info(f"Starting {self.component_name} validation")
    
    def log_validation_result(self, result: ValidationResult):
        """Log validation result"""
        level = logging.INFO if result.success else logging.WARNING
        self.logger.log(level, f"{self.component_name} validation: {result.message}")
        
        # Log warnings
        for warning in result.warnings:
            self.logger.warning(f"{self.component_name}: {warning}")
    
    def create_success_result(self, message: str = None, warnings: list = None, details: dict = None) -> ValidationResult:
        """Create a successful validation result"""
        return ValidationResult(
            success=True,
            component=self.component_name,
            message=message or f"{self.component_name} validation passed",
            warnings=warnings or [],
            details=details or {}
        )
    
    def create_failure_result(self, message: str, suggestions: list = None, details: dict = None) -> ValidationResult:
        """Create a failed validation result"""
        return ValidationResult(
            success=False,
            component=self.component_name,
            message=message,
            suggestions=suggestions or [],
            details=details or {}
        )
    
    def validate_with_logging(self) -> ValidationResult:
        """
        Perform validation with automatic logging
        
        Returns:
            ValidationResult: Result of validation
        """
        self.log_validation_start()
        
        try:
            result = self.validate()
            self.log_validation_result(result)
            return result
        
        except Exception as e:
            error_result = self.create_failure_result(
                f"Validation failed with error: {str(e)}",
                ["Check logs for detailed error information", "Verify system configuration"]
            )
            self.log_validation_result(error_result)
            return error_result