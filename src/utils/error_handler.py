"""
Comprehensive error handling system for Interview Prep Application.

Provides centralized error handling, logging, recovery mechanisms, and user-friendly
error messages for all major operations in the application.
"""

import logging
import traceback
import functools
from datetime import datetime
from typing import Any, Callable
from dataclasses import dataclass, field
from enum import Enum

class ErrorSeverity(Enum):
    """Error severity levels for categorization."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""
    API_ERROR = "api_error"
    VALIDATION_ERROR = "validation_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    PARSING_ERROR = "parsing_error"
    SECURITY_ERROR = "security_error"
    CONFIGURATION_ERROR = "configuration_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    AUTHENTICATION_ERROR = "authentication_error"
    RESOURCE_ERROR = "resource_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class ErrorContext:
    """Context information for error handling."""
    operation: str
    user_id: str | None = None
    session_id: str | None = None
    request_data: dict[str, Any] | None = None
    additional_info: dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorRecord:
    """Detailed error record for logging and analysis."""
    timestamp: datetime
    error_type: str
    error_message: str
    category: ErrorCategory
    severity: ErrorSeverity
    context: ErrorContext
    stack_trace: str | None = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    user_message: str | None = None
    error_id: str | None = None


class ApplicationError(Exception):
    """Base application error with enhanced context."""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN_ERROR,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: ErrorContext | None = None,
        cause: Exception | None = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or ErrorContext(operation="unknown")
        self.cause = cause
        self.timestamp = datetime.now()


class ValidationError(ApplicationError):
    """Input validation errors."""
    
    def __init__(self, message: str, field_name: str | None = None, **kwargs):
        super().__init__(
            message, 
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.LOW,
            **kwargs
        )
        self.field_name = field_name


class APIError(ApplicationError):
    """API-related errors."""
    
    def __init__(self, message: str, status_code: int | None = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.API_ERROR,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        self.status_code = status_code


class RateLimitError(ApplicationError):
    """Rate limiting errors."""
    
    def __init__(self, message: str, retry_after: int | None = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.RATE_LIMIT_ERROR,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )
        self.retry_after = retry_after


class SecurityError(ApplicationError):
    """Security-related errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.SECURITY_ERROR,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class ConfigurationError(ApplicationError):
    """Configuration and setup errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION_ERROR,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class ErrorHandler:
    """
    Centralized error handling system.
    
    Features:
    - Error categorization and severity assessment
    - User-friendly error message generation
    - Error logging with context
    - Recovery mechanism coordination
    - Error statistics and monitoring
    """
    
    def __init__(self, logger_name: str = "interview_prep"):
        """Initialize error handler with logger."""
        self.logger = logging.getLogger(logger_name)
        self.error_history: list[ErrorRecord] = []
        self.recovery_strategies: dict[ErrorCategory, list[Callable[..., Any]]] = {}
        self.user_message_templates = self._init_user_messages()
        
        # Error statistics
        self.error_counts: dict[ErrorCategory, int] = {
            category: 0 for category in ErrorCategory
        }
        
    def _init_user_messages(self) -> dict[ErrorCategory, str]:
        """Initialize user-friendly error message templates."""
        return {
            ErrorCategory.API_ERROR: (
                "We're having trouble connecting to our AI service. "
                "Please try again in a moment. If the problem persists, "
                "check your internet connection or API key."
            ),
            ErrorCategory.VALIDATION_ERROR: (
                "Please check your input and try again. "
                "Make sure all required fields are filled correctly."
            ),
            ErrorCategory.RATE_LIMIT_ERROR: (
                "You've reached the rate limit for API calls. "
                "Please wait a moment before trying again."
            ),
            ErrorCategory.PARSING_ERROR: (
                "We received an unexpected response format. "
                "Please try again or try a different prompt technique."
            ),
            ErrorCategory.SECURITY_ERROR: (
                "Your input contains content that cannot be processed. "
                "Please review and modify your input."
            ),
            ErrorCategory.CONFIGURATION_ERROR: (
                "There's a configuration issue. Please check your "
                "API key and settings, or contact support."
            ),
            ErrorCategory.NETWORK_ERROR: (
                "Network connection issue detected. "
                "Please check your internet connection and try again."
            ),
            ErrorCategory.TIMEOUT_ERROR: (
                "The operation timed out. This might be due to a slow "
                "connection or high server load. Please try again."
            ),
            ErrorCategory.AUTHENTICATION_ERROR: (
                "Authentication failed. Please check your API key "
                "and ensure it's valid and has sufficient credits."
            ),
            ErrorCategory.RESOURCE_ERROR: (
                "System resources are temporarily unavailable. "
                "Please try again in a moment."
            ),
            ErrorCategory.UNKNOWN_ERROR: (
                "An unexpected error occurred. Please try again. "
                "If the problem persists, contact support."
            )
        }
    
    def handle_error(
        self,
        error: Exception,
        context: ErrorContext | None = None,
        attempt_recovery: bool = True
    ) -> tuple[bool, str | None, Any | None]:
        """
        Handle an error with comprehensive logging and recovery.
        
        Args:
            error: The exception that occurred
            context: Context information about the operation
            attempt_recovery: Whether to attempt automatic recovery
            
        Returns:
            Tuple of (recovery_successful, user_message, recovery_result)
        """
        # Categorize the error
        app_error = self._convert_to_app_error(error, context)
        
        # Create error record
        error_record = ErrorRecord(
            timestamp=datetime.now(),
            error_type=type(error).__name__,
            error_message=str(error),
            category=app_error.category,
            severity=app_error.severity,
            context=context or ErrorContext(operation="unknown"),
            stack_trace=traceback.format_exc(),
            error_id=f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.error_history)}"
        )
        
        # Log the error
        self._log_error(error_record)
        
        # Update statistics
        self.error_counts[app_error.category] += 1
        
        # Generate user-friendly message
        user_message = self._generate_user_message(app_error, error_record)
        error_record.user_message = user_message
        
        # Attempt recovery if requested
        recovery_result = None
        if attempt_recovery:
            recovery_successful, recovery_result = self._attempt_recovery(app_error, error_record)
            error_record.recovery_attempted = True
            error_record.recovery_successful = recovery_successful
        else:
            recovery_successful = False
        
        # Store error record
        self.error_history.append(error_record)
        
        # Keep only recent errors (last 100)
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
        
        return recovery_successful, user_message, recovery_result
    
    def _convert_to_app_error(
        self,
        error: Exception,
        context: ErrorContext | None
    ) -> ApplicationError:
        """Convert any exception to an ApplicationError."""
        if isinstance(error, ApplicationError):
            return error
        
        # Categorize based on error type and message
        error_msg = str(error).lower()
        
        if isinstance(error, ValueError):
            return ValidationError(str(error), context=context)
        elif isinstance(error, ConnectionError) or "connection" in error_msg:
            return ApplicationError(
                str(error), 
                ErrorCategory.NETWORK_ERROR, 
                ErrorSeverity.MEDIUM,
                context=context,
                cause=error
            )
        elif isinstance(error, TimeoutError) or "timeout" in error_msg:
            return ApplicationError(
                str(error),
                ErrorCategory.TIMEOUT_ERROR,
                ErrorSeverity.MEDIUM,
                context=context,
                cause=error
            )
        elif "api key" in error_msg or "authentication" in error_msg:
            return ApplicationError(
                str(error),
                ErrorCategory.AUTHENTICATION_ERROR,
                ErrorSeverity.HIGH,
                context=context,
                cause=error
            )
        elif "rate limit" in error_msg:
            return RateLimitError(str(error), context=context, cause=error)
        elif "json" in error_msg or "parsing" in error_msg:
            return ApplicationError(
                str(error),
                ErrorCategory.PARSING_ERROR,
                ErrorSeverity.LOW,
                context=context,
                cause=error
            )
        else:
            return ApplicationError(
                str(error),
                ErrorCategory.UNKNOWN_ERROR,
                ErrorSeverity.MEDIUM,
                context=context,
                cause=error
            )
    
    def _log_error(self, record: ErrorRecord) -> None:
        """Log error with appropriate level based on severity."""
        log_message = (
            f"[{record.error_id}] {record.category.value.upper()}: {record.error_message} "
            f"(Operation: {record.context.operation})"
        )
        
        if record.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message, extra={"error_record": record})
        elif record.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message, extra={"error_record": record})
        elif record.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message, extra={"error_record": record})
        else:
            self.logger.info(log_message, extra={"error_record": record})
        
        # Log stack trace for debugging
        if record.stack_trace and record.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.debug(f"Stack trace for {record.error_id}:\n{record.stack_trace}")
    
    def _generate_user_message(self, app_error: ApplicationError, record: ErrorRecord) -> str:
        """Generate user-friendly error message."""
        base_message = self.user_message_templates.get(
            app_error.category,
            self.user_message_templates[ErrorCategory.UNKNOWN_ERROR]
        )
        
        # Add specific details for certain error types
        if app_error.category == ErrorCategory.RATE_LIMIT_ERROR and isinstance(app_error, RateLimitError):
            if app_error.retry_after:
                base_message += f" Please wait {app_error.retry_after} seconds."
        
        # Add error ID for debugging in debug mode
        base_message += f"\n\n🔍 Error ID: {record.error_id}"
        
        return base_message
    
    def _attempt_recovery(
        self,
        app_error: ApplicationError,
        record: ErrorRecord
    ) -> tuple[bool, Any | None]:
        """Attempt automatic error recovery."""
        recovery_strategies = self.recovery_strategies.get(app_error.category, [])
        
        for strategy in recovery_strategies:
            try:
                result = strategy(app_error, record)
                if result is not None:
                    self.logger.info(f"Recovery successful for {record.error_id} using {strategy.__name__}")
                    return True, result
            except Exception as recovery_error:
                self.logger.warning(
                    f"Recovery strategy {strategy.__name__} failed for {record.error_id}: {recovery_error}"
                )
        
        return False, None
    
    def register_recovery_strategy(
        self, 
        category: ErrorCategory, 
        strategy: Callable[..., Any]
    ) -> None:
        """Register a recovery strategy for a specific error category."""
        if category not in self.recovery_strategies:
            self.recovery_strategies[category] = []
        self.recovery_strategies[category].append(strategy)
    
    def get_error_statistics(self) -> dict[str, Any]:
        """Get comprehensive error statistics."""
        total_errors = sum(self.error_counts.values())
        
        return {
            "total_errors": total_errors,
            "errors_by_category": dict(self.error_counts),
            "error_rate_by_category": {
                category.value: (count / total_errors * 100) if total_errors > 0 else 0
                for category, count in self.error_counts.items()
            },
            "recent_errors": len([
                e for e in self.error_history 
                if (datetime.now() - e.timestamp).total_seconds() < 3600  # Last hour
            ]),
            "recovery_success_rate": self._calculate_recovery_rate(),
            "most_common_errors": self._get_most_common_errors(),
            "last_error": self.error_history[-1] if self.error_history else None
        }
    
    def _calculate_recovery_rate(self) -> float:
        """Calculate the success rate of recovery attempts."""
        recovery_attempts = [e for e in self.error_history if e.recovery_attempted]
        if not recovery_attempts:
            return 0.0
        
        successful_recoveries = [e for e in recovery_attempts if e.recovery_successful]
        return len(successful_recoveries) / len(recovery_attempts) * 100
    
    def _get_most_common_errors(self, limit: int = 5) -> list[tuple[str, int]]:
        """Get the most common error types."""
        error_type_counts: dict[str, int] = {}
        
        for record in self.error_history:
            error_type_counts[record.error_type] = error_type_counts.get(record.error_type, 0) + 1
        
        return sorted(error_type_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_recent_errors(self, limit: int = 10) -> list[ErrorRecord]:
        """Get recent error records."""
        return self.error_history[-limit:]
    
    def clear_error_history(self) -> None:
        """Clear error history and reset counters."""
        self.error_history.clear()
        self.error_counts = {category: 0 for category in ErrorCategory}
    
    def export_error_log(self, include_stack_traces: bool = False) -> list[dict[str, Any]]:
        """Export error log for analysis."""
        return [
            {
                "timestamp": record.timestamp.isoformat(),
                "error_id": record.error_id,
                "error_type": record.error_type,
                "error_message": record.error_message,
                "category": record.category.value,
                "severity": record.severity.value,
                "operation": record.context.operation,
                "recovery_attempted": record.recovery_attempted,
                "recovery_successful": record.recovery_successful,
                "user_message": record.user_message,
                **({"stack_trace": record.stack_trace} if include_stack_traces else {})
            }
            for record in self.error_history
        ]


# Decorators for error handling

def handle_errors(
    error_handler: ErrorHandler | None = None,
    context: ErrorContext | None = None,
    attempt_recovery: bool = True,
    reraise: bool = False
):
    """
    Decorator for automatic error handling.
    
    Args:
        error_handler: ErrorHandler instance (uses global if None)
        context: Error context information
        attempt_recovery: Whether to attempt automatic recovery
        reraise: Whether to reraise the exception after handling
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            handler = error_handler or global_error_handler
            op_context = context or ErrorContext(operation=func.__name__)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                recovery_successful, user_message, recovery_result = handler.handle_error(
                    e, op_context, attempt_recovery
                )
                
                if recovery_successful and recovery_result is not None:
                    return recovery_result
                
                if reraise:
                    raise
                
                return None
        
        return wrapper
    return decorator


def handle_async_errors(
    error_handler: ErrorHandler | None = None,
    context: ErrorContext | None = None,
    attempt_recovery: bool = True,
    reraise: bool = False
):
    """Async version of error handling decorator."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            handler = error_handler or global_error_handler
            op_context = context or ErrorContext(operation=func.__name__)
            
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                recovery_successful, user_message, recovery_result = handler.handle_error(
                    e, op_context, attempt_recovery
                )
                
                if recovery_successful and recovery_result is not None:
                    return recovery_result
                
                if reraise:
                    raise
                
                return None
        
        return wrapper
    return decorator


# Global error handler instance
global_error_handler = ErrorHandler()


# Recovery strategies

def api_retry_strategy(error: ApplicationError, record: ErrorRecord) -> Any | None:
    """Recovery strategy for API errors with exponential backoff."""
    if record.context.additional_info.get("retry_count", 0) >= 3:
        return None
    
    import time
    retry_count = record.context.additional_info.get("retry_count", 0) + 1
    wait_time = min(2 ** retry_count, 30)  # Exponential backoff, max 30s
    
    time.sleep(wait_time)
    record.context.additional_info["retry_count"] = retry_count
    
    # Return indicator that retry should be attempted
    return {"retry": True, "wait_time": wait_time}


def rate_limit_wait_strategy(error: ApplicationError, record: ErrorRecord) -> Any | None:
    """Recovery strategy for rate limit errors."""
    if isinstance(error, RateLimitError) and error.retry_after:
        import time
        time.sleep(min(error.retry_after, 300))  # Max 5 minutes
        return {"retry": True, "wait_time": error.retry_after}
    
    return None


def validation_fix_strategy(error: ApplicationError, record: ErrorRecord) -> Any | None:
    """Recovery strategy for validation errors."""
    if isinstance(error, ValidationError):
        # Return suggestions for fixing validation errors
        return {
            "suggestions": [
                "Check input length requirements",
                "Verify all required fields are filled",
                "Remove special characters if any",
                "Ensure values are within valid ranges"
            ]
        }
    
    return None


# Register default recovery strategies
global_error_handler.register_recovery_strategy(ErrorCategory.API_ERROR, api_retry_strategy)
global_error_handler.register_recovery_strategy(ErrorCategory.RATE_LIMIT_ERROR, rate_limit_wait_strategy)
global_error_handler.register_recovery_strategy(ErrorCategory.VALIDATION_ERROR, validation_fix_strategy)