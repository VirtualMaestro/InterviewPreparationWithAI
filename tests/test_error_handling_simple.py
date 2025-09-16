"""
Unit tests for the comprehensive error handling system.

Tests error classification, logging, recovery mechanisms, and user message generation.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
import logging
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add parent directory to path
import sys
from pathlib import Path

from src.utils.error_handler import (
    ErrorHandler,
    ErrorCategory,
    ErrorSeverity,
    ErrorContext,
    ErrorRecord,
    ApplicationError,
    ValidationError,
    APIError,
    RateLimitError,
    SecurityError,
    ConfigurationError,
    handle_errors,
    handle_async_errors,
    global_error_handler
)


class TestErrorClassification(unittest.TestCase):
    """Test error classification and categorization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.error_handler = ErrorHandler("test_logger")
    
    def test_application_error_creation(self):
        """Test ApplicationError creation with context."""
        context = ErrorContext(
            operation="test_operation",
            additional_info={"test_key": "test_value"}
        )
        
        error = ApplicationError(
            "Test error message",
            category=ErrorCategory.API_ERROR,
            severity=ErrorSeverity.HIGH,
            context=context
        )
        
        self.assertEqual(error.message, "Test error message")
        self.assertEqual(error.category, ErrorCategory.API_ERROR)
        self.assertEqual(error.severity, ErrorSeverity.HIGH)
        self.assertEqual(error.context.operation, "test_operation")
        self.assertIsInstance(error.timestamp, datetime)
    
    def test_validation_error(self):
        """Test ValidationError specific functionality."""
        error = ValidationError("Invalid input", field_name="job_description")
        
        self.assertEqual(error.category, ErrorCategory.VALIDATION_ERROR)
        self.assertEqual(error.severity, ErrorSeverity.LOW)
        self.assertEqual(error.field_name, "job_description")
    
    def test_api_error(self):
        """Test APIError specific functionality."""
        error = APIError("API call failed", status_code=500)
        
        self.assertEqual(error.category, ErrorCategory.API_ERROR)
        self.assertEqual(error.severity, ErrorSeverity.HIGH)
        self.assertEqual(error.status_code, 500)
    
    def test_rate_limit_error(self):
        """Test RateLimitError specific functionality."""
        error = RateLimitError("Rate limit exceeded", retry_after=300)
        
        self.assertEqual(error.category, ErrorCategory.RATE_LIMIT_ERROR)
        self.assertEqual(error.severity, ErrorSeverity.MEDIUM)
        self.assertEqual(error.retry_after, 300)
    
    def test_security_error(self):
        """Test SecurityError classification."""
        error = SecurityError("Malicious input detected")
        
        self.assertEqual(error.category, ErrorCategory.SECURITY_ERROR)
        self.assertEqual(error.severity, ErrorSeverity.HIGH)
    
    def test_configuration_error(self):
        """Test ConfigurationError classification."""
        error = ConfigurationError("Missing API key")
        
        self.assertEqual(error.category, ErrorCategory.CONFIGURATION_ERROR)
        self.assertEqual(error.severity, ErrorSeverity.HIGH)


class TestErrorHandler(unittest.TestCase):
    """Test ErrorHandler functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.error_handler = ErrorHandler("test_logger")
        self.error_handler.clear_error_history()
    
    def test_error_conversion(self):
        """Test conversion of standard exceptions to ApplicationErrors."""
        # ValueError should become ValidationError
        value_error = ValueError("Invalid value")
        app_error = self.error_handler._convert_to_app_error(value_error, None)
        self.assertIsInstance(app_error, ValidationError)
        
        # ConnectionError should become network error
        connection_error = ConnectionError("Connection failed")
        app_error = self.error_handler._convert_to_app_error(connection_error, None)
        self.assertEqual(app_error.category, ErrorCategory.NETWORK_ERROR)
        
        # TimeoutError should become timeout error
        timeout_error = TimeoutError("Operation timed out")
        app_error = self.error_handler._convert_to_app_error(timeout_error, None)
        self.assertEqual(app_error.category, ErrorCategory.TIMEOUT_ERROR)
    
    def test_error_handling_workflow(self):
        """Test complete error handling workflow."""
        context = ErrorContext(
            operation="test_operation",
            additional_info={"test_data": "value"}
        )
        
        test_error = ValueError("Test validation error")
        
        # Handle the error
        recovery_successful, user_message, recovery_result = self.error_handler.handle_error(
            test_error, context, attempt_recovery=False
        )
        
        # Verify results
        self.assertFalse(recovery_successful)  # No recovery attempted
        self.assertIsInstance(user_message, str)
        self.assertIsNone(recovery_result)
        
        # Verify error was recorded
        self.assertEqual(len(self.error_handler.error_history), 1)
        
        error_record = self.error_handler.error_history[0]
        self.assertEqual(error_record.error_type, "ValueError")
        self.assertEqual(error_record.context.operation, "test_operation")
        self.assertIsNotNone(error_record.error_id)
    
    def test_user_message_generation(self):
        """Test user-friendly message generation."""
        # Test API error message
        api_error = APIError("Connection failed")
        context = ErrorContext(operation="api_call")
        
        recovery_successful, user_message, recovery_result = self.error_handler.handle_error(
            api_error, context, attempt_recovery=False
        )
        
        self.assertIn("trouble connecting", user_message.lower())
        self.assertIn("error id:", user_message.lower())
    
    def test_error_statistics(self):
        """Test error statistics collection."""
        # Add various errors
        errors = [
            ValueError("Validation error 1"),
            ConnectionError("Network error 1"),
            ValueError("Validation error 2"),
            TimeoutError("Timeout error 1")
        ]
        
        for error in errors:
            self.error_handler.handle_error(error, ErrorContext(operation="test"))
        
        stats = self.error_handler.get_error_statistics()
        
        self.assertEqual(stats["total_errors"], 4)
        self.assertEqual(stats["errors_by_category"][ErrorCategory.VALIDATION_ERROR], 2)
        self.assertEqual(stats["errors_by_category"][ErrorCategory.NETWORK_ERROR], 1)
        self.assertEqual(stats["errors_by_category"][ErrorCategory.TIMEOUT_ERROR], 1)
    
    def test_recovery_strategy_registration(self):
        """Test recovery strategy registration and execution."""
        # Mock recovery strategy
        def mock_recovery_strategy(error, record):
            if isinstance(error, ValidationError):
                return {"recovered": True}
            return None
        
        # Register strategy
        self.error_handler.register_recovery_strategy(
            ErrorCategory.VALIDATION_ERROR,
            mock_recovery_strategy
        )
        
        # Test recovery
        validation_error = ValidationError("Test error")
        context = ErrorContext(operation="test")
        
        recovery_successful, user_message, recovery_result = self.error_handler.handle_error(
            validation_error, context, attempt_recovery=True
        )
        
        self.assertTrue(recovery_successful)
        self.assertEqual(recovery_result, {"recovered": True})
    
    def test_error_history_management(self):
        """Test error history storage and cleanup."""
        # Add many errors to test history limit
        for i in range(150):  # More than the 100 limit
            error = ValueError(f"Error {i}")
            self.error_handler.handle_error(error, ErrorContext(operation="test"))
        
        # Should only keep last 100
        self.assertEqual(len(self.error_handler.error_history), 100)
        
        # Test clear functionality
        self.error_handler.clear_error_history()
        self.assertEqual(len(self.error_handler.error_history), 0)
        self.assertEqual(self.error_handler.error_counts[ErrorCategory.VALIDATION_ERROR], 0)
    
    def test_recent_errors(self):
        """Test recent error retrieval."""
        # Add some errors
        for i in range(5):
            error = ValueError(f"Error {i}")
            self.error_handler.handle_error(error, ErrorContext(operation="test"))
        
        recent = self.error_handler.get_recent_errors(3)
        self.assertEqual(len(recent), 3)
        
        # Should be most recent first
        self.assertIn("Error 4", recent[0].error_message)
        self.assertIn("Error 3", recent[1].error_message)
        self.assertIn("Error 2", recent[2].error_message)
    
    def test_export_error_log(self):
        """Test error log export functionality."""
        # Add an error
        error = ValidationError("Test export error")
        context = ErrorContext(
            operation="export_test",
            additional_info={"export_test": True}
        )
        
        self.error_handler.handle_error(error, context)
        
        # Export without stack traces
        export_data = self.error_handler.export_error_log(include_stack_traces=False)
        self.assertEqual(len(export_data), 1)
        self.assertNotIn("stack_trace", export_data[0])
        self.assertEqual(export_data[0]["operation"], "export_test")
        
        # Export with stack traces
        export_data_with_traces = self.error_handler.export_error_log(include_stack_traces=True)
        self.assertIn("stack_trace", export_data_with_traces[0])


class TestErrorDecorators(unittest.TestCase):
    """Test error handling decorators."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_handler = ErrorHandler("decorator_test")
        self.test_handler.clear_error_history()
    
    def test_handle_errors_decorator(self):
        """Test synchronous error handling decorator."""
        @handle_errors(
            error_handler=self.test_handler,
            attempt_recovery=False,
            reraise=False
        )
        def test_function():
            raise ValueError("Test decorator error")
        
        result = test_function()
        self.assertIsNone(result)  # Should return None when error is handled
        
        # Check error was recorded
        self.assertEqual(len(self.test_handler.error_history), 1)
        self.assertEqual(self.test_handler.error_history[0].error_type, "ValueError")
    
    def test_handle_async_errors_decorator(self):
        """Test asynchronous error handling decorator."""
        @handle_async_errors(
            error_handler=self.test_handler,
            attempt_recovery=False,
            reraise=False
        )
        async def async_test_function():
            raise ConnectionError("Async test error")
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(async_test_function())
            self.assertIsNone(result)
        finally:
            loop.close()
        
        # Check error was recorded
        self.assertEqual(len(self.test_handler.error_history), 1)
        self.assertEqual(self.test_handler.error_history[0].error_type, "ConnectionError")
    
    def test_decorator_with_recovery(self):
        """Test decorator with recovery functionality."""
        # Mock recovery strategy
        def mock_recovery(error, record):
            return "recovered_value"
        
        self.test_handler.register_recovery_strategy(
            ErrorCategory.VALIDATION_ERROR,
            mock_recovery
        )
        
        @handle_errors(
            error_handler=self.test_handler,
            attempt_recovery=True,
            reraise=False
        )
        def recoverable_function():
            raise ValueError("Recoverable error")
        
        result = recoverable_function()
        self.assertEqual(result, "recovered_value")
        
        # Check recovery was successful
        error_record = self.test_handler.error_history[-1]
        self.assertTrue(error_record.recovery_attempted)
        self.assertTrue(error_record.recovery_successful)
    
    def test_decorator_with_reraise(self):
        """Test decorator with reraise option."""
        @handle_errors(
            error_handler=self.test_handler,
            attempt_recovery=False,
            reraise=True
        )
        def reraise_function():
            raise RuntimeError("Should be reraised")
        
        with self.assertRaises(RuntimeError):
            reraise_function()
        
        # Error should still be recorded
        self.assertEqual(len(self.test_handler.error_history), 1)


class TestRecoveryStrategies(unittest.TestCase):
    """Test built-in recovery strategies."""
    
    def test_api_retry_strategy(self):
        """Test API retry recovery strategy."""
        from utils.error_handler import api_retry_strategy
        
        # Create test error and record
        error = APIError("API call failed")
        context = ErrorContext(operation="api_test")
        record = ErrorRecord(
            timestamp=datetime.now(),
            error_type="APIError",
            error_message="API call failed",
            category=ErrorCategory.API_ERROR,
            severity=ErrorSeverity.HIGH,
            context=context
        )
        
        # Test retry strategy
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = api_retry_strategy(error, record)
            
            self.assertIsNotNone(result)
            self.assertTrue(result["retry"])
            self.assertEqual(record.context.additional_info["retry_count"], 1)
    
    def test_rate_limit_wait_strategy(self):
        """Test rate limit wait recovery strategy."""
        from utils.error_handler import rate_limit_wait_strategy
        
        # Create rate limit error
        error = RateLimitError("Rate limit exceeded", retry_after=5)
        context = ErrorContext(operation="rate_limit_test")
        record = ErrorRecord(
            timestamp=datetime.now(),
            error_type="RateLimitError",
            error_message="Rate limit exceeded",
            category=ErrorCategory.RATE_LIMIT_ERROR,
            severity=ErrorSeverity.MEDIUM,
            context=context
        )
        
        # Test wait strategy
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = rate_limit_wait_strategy(error, record)
            
            self.assertIsNotNone(result)
            self.assertTrue(result["retry"])
            self.assertEqual(result["wait_time"], 5)
    
    def test_validation_fix_strategy(self):
        """Test validation error fix strategy."""
        from utils.error_handler import validation_fix_strategy
        
        # Create validation error
        error = ValidationError("Invalid input", field_name="test_field")
        context = ErrorContext(operation="validation_test")
        record = ErrorRecord(
            timestamp=datetime.now(),
            error_type="ValidationError",
            error_message="Invalid input",
            category=ErrorCategory.VALIDATION_ERROR,
            severity=ErrorSeverity.LOW,
            context=context
        )
        
        # Test fix strategy
        result = validation_fix_strategy(error, record)
        
        self.assertIsNotNone(result)
        self.assertIn("suggestions", result)
        self.assertIsInstance(result["suggestions"], list)
        self.assertTrue(len(result["suggestions"]) > 0)


class TestErrorIntegration(unittest.TestCase):
    """Test error handling integration scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        global_error_handler.clear_error_history()
    
    def test_global_error_handler(self):
        """Test global error handler functionality."""
        # Use global handler
        error = ValueError("Global handler test")
        context = ErrorContext(operation="global_test")
        
        recovery_successful, user_message, recovery_result = global_error_handler.handle_error(
            error, context
        )
        
        self.assertIsInstance(user_message, str)
        self.assertEqual(len(global_error_handler.error_history), 1)
    
    def test_error_context_enrichment(self):
        """Test error context information enrichment."""
        context = ErrorContext(
            operation="complex_operation",
            user_id="test_user",
            session_id="test_session",
            request_data={"param1": "value1"},
            additional_info={
                "custom_field": "custom_value",
                "nested_data": {"key": "value"}
            }
        )
        
        error = RuntimeError("Context test error")
        global_error_handler.handle_error(error, context)
        
        error_record = global_error_handler.error_history[-1]
        self.assertEqual(error_record.context.operation, "complex_operation")
        self.assertEqual(error_record.context.user_id, "test_user")
        self.assertEqual(error_record.context.session_id, "test_session")
        self.assertEqual(error_record.context.additional_info["custom_field"], "custom_value")
    
    def test_error_severity_logging(self):
        """Test that errors are logged with appropriate severity."""
        with patch('logging.Logger.critical') as mock_critical, \
             patch('logging.Logger.error') as mock_error, \
             patch('logging.Logger.warning') as mock_warning, \
             patch('logging.Logger.info') as mock_info:
            
            # Test different severity levels
            errors = [
                ApplicationError("Critical error", severity=ErrorSeverity.CRITICAL),
                ApplicationError("High error", severity=ErrorSeverity.HIGH),
                ApplicationError("Medium error", severity=ErrorSeverity.MEDIUM),
                ApplicationError("Low error", severity=ErrorSeverity.LOW)
            ]
            
            for error in errors:
                global_error_handler.handle_error(error, ErrorContext(operation="test"))
            
            # Verify appropriate logging methods were called
            mock_critical.assert_called_once()
            mock_error.assert_called_once()
            mock_warning.assert_called_once()
            mock_info.assert_called_once()


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)