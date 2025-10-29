"""
Custom Exceptions
Custom exception classes for the modular report generation system
"""


class ModularReportSystemError(Exception):
    """Base exception for modular report system"""
    pass


class TemplateError(ModularReportSystemError):
    """Base exception for template-related errors"""
    pass


class TemplateNotFoundError(TemplateError):
    """Raised when a template cannot be found"""
    pass


class TemplateValidationError(TemplateError):
    """Raised when template validation fails"""
    pass


class TemplateLoadError(TemplateError):
    """Raised when template cannot be loaded"""
    pass


class ReportGenerationError(ModularReportSystemError):
    """Base exception for report generation errors"""
    pass


class DataExtractionError(ReportGenerationError):
    """Raised when data extraction fails"""
    pass


class ReportFormatError(ReportGenerationError):
    """Raised when report formatting fails"""
    pass


class ExportError(ReportGenerationError):
    """Raised when report export fails"""
    pass


class DatabaseError(ModularReportSystemError):
    """Base exception for database-related errors"""
    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails"""
    pass


class QueryExecutionError(DatabaseError):
    """Raised when database query execution fails"""
    pass


class ConfigurationError(ModularReportSystemError):
    """Base exception for configuration-related errors"""
    pass


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration is invalid"""
    pass


class ConfigurationNotFoundError(ConfigurationError):
    """Raised when configuration cannot be found"""
    pass


class ValidationError(ModularReportSystemError):
    """Base exception for validation errors"""
    pass


class InputValidationError(ValidationError):
    """Raised when input validation fails"""
    pass


class BusinessRuleValidationError(ValidationError):
    """Raised when business rule validation fails"""
    pass


class UIError(ModularReportSystemError):
    """Base exception for UI-related errors"""
    pass


class WidgetError(UIError):
    """Raised when widget operation fails"""
    pass


class UserInteractionError(UIError):
    """Raised when user interaction fails"""
    pass


class FileSystemError(ModularReportSystemError):
    """Base exception for file system errors"""
    pass


class FileNotFoundError(FileSystemError):
    """Raised when a required file is not found"""
    pass


class FilePermissionError(FileSystemError):
    """Raised when file permission is denied"""
    pass


class DirectoryError(FileSystemError):
    """Raised when directory operation fails"""
    pass


class ProcessingError(ModularReportSystemError):
    """Base exception for processing errors"""
    pass


class DataProcessingError(ProcessingError):
    """Raised when data processing fails"""
    pass


class CalculationError(ProcessingError):
    """Raised when calculation fails"""
    pass


class TransformationError(ProcessingError):
    """Raised when data transformation fails"""
    pass


class ServiceError(ModularReportSystemError):
    """Base exception for service-related errors"""
    pass


class ServiceInitializationError(ServiceError):
    """Raised when service initialization fails"""
    pass


class ServiceOperationError(ServiceError):
    """Raised when service operation fails"""
    pass


class DependencyError(ModularReportSystemError):
    """Base exception for dependency-related errors"""
    pass


class MissingDependencyError(DependencyError):
    """Raised when required dependency is missing"""
    pass


class IncompatibleDependencyError(DependencyError):
    """Raised when dependency version is incompatible"""
    pass


class SecurityError(ModularReportSystemError):
    """Base exception for security-related errors"""
    pass


class AccessDeniedError(SecurityError):
    """Raised when access is denied"""
    pass


class AuthenticationError(SecurityError):
    """Raised when authentication fails"""
    pass


class AuthorizationError(SecurityError):
    """Raised when authorization fails"""
    pass


class ConcurrencyError(ModularReportSystemError):
    """Base exception for concurrency-related errors"""
    pass


class ResourceLockError(ConcurrencyError):
    """Raised when resource cannot be locked"""
    pass


class ThreadingError(ConcurrencyError):
    """Raised when threading operation fails"""
    pass


class TimeoutError(ModularReportSystemError):
    """Raised when operation times out"""
    pass


class NetworkError(ModularReportSystemError):
    """Base exception for network-related errors"""
    pass


class ConnectionTimeoutError(NetworkError):
    """Raised when network connection times out"""
    pass


class NetworkUnavailableError(NetworkError):
    """Raised when network is unavailable"""
    pass


# Exception mapping for easier error handling
EXCEPTION_MAPPING = {
    'template_not_found': TemplateNotFoundError,
    'template_validation': TemplateValidationError,
    'template_load': TemplateLoadError,
    'report_generation': ReportGenerationError,
    'data_extraction': DataExtractionError,
    'report_format': ReportFormatError,
    'export': ExportError,
    'database_connection': DatabaseConnectionError,
    'query_execution': QueryExecutionError,
    'invalid_configuration': InvalidConfigurationError,
    'configuration_not_found': ConfigurationNotFoundError,
    'input_validation': InputValidationError,
    'business_rule_validation': BusinessRuleValidationError,
    'widget': WidgetError,
    'user_interaction': UserInteractionError,
    'file_not_found': FileNotFoundError,
    'file_permission': FilePermissionError,
    'directory': DirectoryError,
    'data_processing': DataProcessingError,
    'calculation': CalculationError,
    'transformation': TransformationError,
    'service_initialization': ServiceInitializationError,
    'service_operation': ServiceOperationError,
    'missing_dependency': MissingDependencyError,
    'incompatible_dependency': IncompatibleDependencyError,
    'access_denied': AccessDeniedError,
    'authentication': AuthenticationError,
    'authorization': AuthorizationError,
    'resource_lock': ResourceLockError,
    'threading': ThreadingError,
    'timeout': TimeoutError,
    'connection_timeout': ConnectionTimeoutError,
    'network_unavailable': NetworkUnavailableError
}


def get_exception_class(error_type: str) -> type:
    """
    Get exception class by error type
    
    Args:
        error_type: Error type string
        
    Returns:
        Exception class
    """
    return EXCEPTION_MAPPING.get(error_type, ModularReportSystemError)


def create_exception(error_type: str, message: str) -> Exception:
    """
    Create exception instance by error type
    
    Args:
        error_type: Error type string
        message: Error message
        
    Returns:
        Exception instance
    """
    exception_class = get_exception_class(error_type)
    return exception_class(message)