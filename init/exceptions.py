"""
Custom exceptions for initialization system
"""

from typing import List, Optional


class InitializationError(Exception):
    """Base exception for initialization errors"""
    
    def __init__(self, message: str, component: str = None, suggestions: List[str] = None):
        self.message = message
        self.component = component
        self.suggestions = suggestions or []
        super().__init__(message)


class ValidationError(InitializationError):
    """Exception raised when environment validation fails"""
    
    def __init__(self, component: str, message: str, suggestions: List[str] = None):
        super().__init__(message, component, suggestions)


class OrchestrationError(InitializationError):
    """Exception raised when service orchestration fails"""
    
    def __init__(self, service: str, message: str, retry_count: int = 0):
        self.service = service
        self.retry_count = retry_count
        super().__init__(f"Service {service}: {message}")


class ConfigurationError(InitializationError):
    """Exception raised when configuration loading fails"""
    
    def __init__(self, config_key: str, message: str, expected_type: str = None):
        self.config_key = config_key
        self.expected_type = expected_type
        super().__init__(f"Configuration error for {config_key}: {message}")


class HealthCheckError(InitializationError):
    """Exception raised when health checks fail"""
    
    def __init__(self, service: str, endpoint: str, status_code: int = None):
        self.service = service
        self.endpoint = endpoint
        self.status_code = status_code
        message = f"Health check failed for {service} at {endpoint}"
        if status_code:
            message += f" (status: {status_code})"
        super().__init__(message)


class ValidationResult:
    """Result of a validation check"""
    
    def __init__(
        self, 
        success: bool, 
        component: str,
        message: str = None,
        suggestions: List[str] = None,
        warnings: List[str] = None,
        details: dict = None
    ):
        self.success = success
        self.component = component
        self.message = message or ("Validation passed" if success else "Validation failed")
        self.suggestions = suggestions or []
        self.warnings = warnings or []
        self.details = details or {}

    def __bool__(self):
        return self.success

    def __str__(self):
        status = "✅" if self.success else "❌"
        return f"{status} {self.component}: {self.message}"


class ValidationResults:
    """Collection of validation results"""
    
    def __init__(self, results: List[ValidationResult] = None):
        self.results = results or []

    def add(self, result: ValidationResult):
        """Add a validation result"""
        self.results.append(result)

    @property
    def all_passed(self) -> bool:
        """Check if all validations passed"""
        return all(result.success for result in self.results)

    @property
    def failed_validations(self) -> List[ValidationResult]:
        """Get only failed validation results"""
        return [result for result in self.results if not result.success]

    @property
    def passed_validations(self) -> List[ValidationResult]:
        """Get only passed validation results"""
        return [result for result in self.results if result.success]

    @property
    def warnings(self) -> List[str]:
        """Get all warnings from all results"""
        warnings = []
        for result in self.results:
            warnings.extend(result.warnings)
        return warnings

    def get_summary(self) -> str:
        """Get a summary of all validation results"""
        total = len(self.results)
        passed = len(self.passed_validations)
        failed = len(self.failed_validations)
        
        summary = f"Validation Summary: {passed}/{total} passed"
        if failed > 0:
            summary += f", {failed} failed"
        
        return summary

    def __bool__(self):
        return self.all_passed

    def __iter__(self):
        return iter(self.results)

    def __len__(self):
        return len(self.results)