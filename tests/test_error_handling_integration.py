"""
Integration tests for the comprehensive error handling system.

Tests error handling across the entire application stack including
AI generator, API calls, UI components, and recovery mechanisms.
"""

import unittest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime

# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.error_handler import (
    global_error_handler,
    ErrorCategory,
    ErrorSeverity,
    ErrorContext,
    ApplicationError,
    APIError,
    RateLimitError,
    ValidationError
)
from ai.generator import InterviewQuestionGenerator
from models.enums import InterviewType, ExperienceLevel, PromptTechnique, AIModel
from models.simple_schemas import GenerationRequest


class TestGeneratorErrorHandling(unittest.TestCase):
    """Test error handling integration with AI generator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"
        self.generator = InterviewQuestionGenerator(self.api_key, AIModel.GPT_4O)
        global_error_handler.clear_error_history()
        
        # Sample generation request
        self.sample_request = GenerationRequest(
            job_description="Senior Python Developer at Tech Company",
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR,
            prompt_technique=PromptTechnique.STRUCTURED_OUTPUT,
            question_count=5
        )
    
    @patch('ai.generator.AsyncOpenAI')
    async def test_api_error_handling(self, mock_openai_class):
        """Test API error handling in generator."""
        # Setup mock to raise API error
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API server error")
        )
        
        # Re-create generator with mocked client
        self.generator.client = mock_client
        
        # Generate questions - should handle error gracefully
        result = await self.generator.generate_questions(self.sample_request)
        
        # Verify error was handled
        self.assertFalse(result.success)
        self.assertIn("failed", result.error_message.lower())
        
        # Verify error was logged
        self.assertGreater(len(global_error_handler.error_history), 0)
        error_record = global_error_handler.error_history[-1]
        self.assertEqual(error_record.category, ErrorCategory.API_ERROR)
    
    @patch('utils.rate_limiter.rate_limiter')
    async def test_rate_limit_error_handling(self, mock_rate_limiter):
        """Test rate limit error handling."""
        # Mock rate limiter to indicate limit exceeded
        mock_rate_limiter.can_make_call.return_value = False
        mock_status = Mock()
        mock_status.time_until_reset.total_seconds.return_value = 300
        mock_rate_limiter.get_rate_limit_status.return_value = mock_status
        
        # Attempt generation
        result = await self.generator.generate_questions(self.sample_request)
        
        # Verify rate limit error was handled
        self.assertFalse(result.success)
        self.assertIn("rate limit", result.error_message.lower())
        
        # Verify error categorization
        error_record = global_error_handler.error_history[-1]
        self.assertEqual(error_record.category, ErrorCategory.RATE_LIMIT_ERROR)
    
    async def test_validation_error_handling(self):
        """Test validation error handling."""
        # Create request with invalid data
        invalid_request = GenerationRequest(
            job_description="",  # Too short
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR,
            prompt_technique=PromptTechnique.STRUCTURED_OUTPUT,
            question_count=5
        )
        
        # Should handle validation error
        result = await self.generator.generate_questions(invalid_request)
        
        self.assertFalse(result.success)
        self.assertIn("validation", result.error_message.lower())
        
        # Check error categorization
        error_record = global_error_handler.error_history[-1]
        self.assertEqual(error_record.category, ErrorCategory.VALIDATION_ERROR)
    
    @patch('ai.generator.AsyncOpenAI')
    async def test_parsing_error_handling(self, mock_openai_class):
        """Test response parsing error handling."""
        # Setup mock to return malformed response
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = AsyncMock()
        mock_response.choices = [
            Mock(message=Mock(content="Invalid JSON {{{{{"))
        ]
        mock_response.usage = Mock(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150
        )
        mock_response.model = "gpt-4o"
        mock_response.choices[0].finish_reason = "stop"
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        # Re-create generator with mocked client
        self.generator.client = mock_client
        
        # Should handle parsing error and try fallback
        result = await self.generator.generate_questions(self.sample_request)
        
        # May succeed with fallback parsing or fail gracefully
        if not result.success:
            self.assertIsNotNone(result.error_message)
        
        # Check that errors were logged
        self.assertGreater(len(global_error_handler.error_history), 0)
    
    @patch('ai.generator.AsyncOpenAI')
    async def test_recovery_mechanism(self, mock_openai_class):
        """Test error recovery mechanisms."""
        # Setup mock to fail then succeed
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        # First call fails, second succeeds
        success_response = AsyncMock()
        success_response.choices = [
            Mock(message=Mock(content='{"questions": ["Q1", "Q2"], "recommendations": ["R1"]}'))
        ]
        success_response.usage = Mock(
            prompt_tokens=500,
            completion_tokens=200,
            total_tokens=700
        )
        success_response.model = "gpt-4o"
        success_response.choices[0].finish_reason = "stop"
        
        mock_client.chat.completions.create = AsyncMock(
            side_effect=[
                Exception("First attempt fails"),
                Exception("Second attempt fails"),
                success_response  # Third attempt succeeds
            ]
        )
        
        # Re-create generator with mocked client
        self.generator.client = mock_client
        
        # Should eventually succeed due to retry mechanism
        result = await self.generator.generate_questions(self.sample_request)
        
        # Verify final success (retry mechanism should work)
        self.assertTrue(result.success or len(result.questions) > 0)
        
        # Verify retry attempts were logged
        api_errors = [
            e for e in global_error_handler.error_history 
            if e.category == ErrorCategory.API_ERROR
        ]
        self.assertGreater(len(api_errors), 0)


class TestAppErrorHandling(unittest.TestCase):
    """Test error handling in the main application."""
    
    def setUp(self):
        """Set up test fixtures."""
        global_error_handler.clear_error_history()
    
    @patch('streamlit.error')
    @patch('streamlit.warning')
    @patch('streamlit.info')
    def test_streamlit_error_display_integration(self, mock_info, mock_warning, mock_error):
        """Test error display integration with Streamlit."""
        from ui.error_display import ErrorDisplayManager
        
        # Create test error
        error = APIError("Test API error")
        context = ErrorContext(operation="streamlit_test")
        
        # Handle error
        global_error_handler.handle_error(error, context)
        
        # Get error record and display
        error_record = global_error_handler.error_history[-1]
        ErrorDisplayManager.show_error_message(error_record)
        
        # Verify Streamlit error display was called
        mock_error.assert_called()
    
    def test_error_context_propagation(self):
        """Test error context propagation through application layers."""
        # Simulate app-level error with rich context
        context = ErrorContext(
            operation="question_generation",
            user_id="test_user",
            session_id="session_123",
            request_data={
                "interview_type": "technical",
                "experience_level": "senior"
            },
            additional_info={
                "model": "gpt-4o",
                "technique": "structured_output",
                "retry_count": 2
            }
        )
        
        error = ApplicationError(
            "Complex application error",
            category=ErrorCategory.API_ERROR,
            severity=ErrorSeverity.HIGH,
            context=context
        )
        
        # Handle error
        global_error_handler.handle_error(error, context)
        
        # Verify context was preserved
        error_record = global_error_handler.error_history[-1]
        self.assertEqual(error_record.context.user_id, "test_user")
        self.assertEqual(error_record.context.session_id, "session_123")
        self.assertEqual(error_record.context.additional_info["model"], "gpt-4o")
        self.assertEqual(error_record.context.additional_info["retry_count"], 2)
    
    def test_error_statistics_integration(self):
        """Test error statistics collection across components."""
        # Simulate various errors from different components
        errors = [
            # API errors
            APIError("API error 1"),
            APIError("API error 2"),
            # Validation errors
            ValidationError("Validation error 1", field_name="job_description"),
            ValidationError("Validation error 2", field_name="question_count"),
            # Rate limit error
            RateLimitError("Rate limit exceeded", retry_after=300),
            # Network error
            ApplicationError("Network timeout", category=ErrorCategory.NETWORK_ERROR)
        ]
        
        # Handle all errors
        for i, error in enumerate(errors):
            context = ErrorContext(
                operation=f"test_operation_{i}",
                additional_info={"component": f"component_{i % 3}"}
            )
            global_error_handler.handle_error(error, context)
        
        # Verify statistics
        stats = global_error_handler.get_error_statistics()
        
        self.assertEqual(stats["total_errors"], 6)
        self.assertEqual(stats["errors_by_category"][ErrorCategory.API_ERROR], 2)
        self.assertEqual(stats["errors_by_category"][ErrorCategory.VALIDATION_ERROR], 2)
        self.assertEqual(stats["errors_by_category"][ErrorCategory.RATE_LIMIT_ERROR], 1)
        self.assertEqual(stats["errors_by_category"][ErrorCategory.NETWORK_ERROR], 1)
        
        # Check most common errors
        most_common = stats["most_common_errors"]
        self.assertGreater(len(most_common), 0)
    
    def test_error_export_integration(self):
        """Test error log export functionality."""
        # Create various errors with different contexts
        test_errors = [
            {
                "error": APIError("API connection failed"),
                "context": ErrorContext(
                    operation="api_call",
                    additional_info={"endpoint": "/chat/completions", "model": "gpt-4o"}
                )
            },
            {
                "error": ValidationError("Invalid job description", field_name="job_description"),
                "context": ErrorContext(
                    operation="input_validation",
                    user_id="user_123",
                    additional_info={"input_length": 5}
                )
            }
        ]
        
        # Handle errors
        for error_data in test_errors:
            global_error_handler.handle_error(
                error_data["error"], 
                error_data["context"]
            )
        
        # Export error log
        exported_log = global_error_handler.export_error_log(include_stack_traces=True)
        
        # Verify export structure
        self.assertEqual(len(exported_log), 2)
        
        # Check first error export
        api_error_export = exported_log[0]
        self.assertEqual(api_error_export["error_type"], "APIError")
        self.assertEqual(api_error_export["category"], "api_error")
        self.assertEqual(api_error_export["operation"], "api_call")
        self.assertIn("stack_trace", api_error_export)
        
        # Check second error export
        validation_error_export = exported_log[1]
        self.assertEqual(validation_error_export["error_type"], "ValidationError")
        self.assertEqual(validation_error_export["category"], "validation_error")
        self.assertEqual(validation_error_export["operation"], "input_validation")
    
    def test_error_recovery_integration(self):
        """Test integrated error recovery across components."""
        # Custom recovery strategy for testing
        def test_recovery_strategy(error, record):
            if "recoverable" in error.message:
                return {"recovery_data": "test_recovery_result"}
            return None
        
        # Register recovery strategy
        global_error_handler.register_recovery_strategy(
            ErrorCategory.API_ERROR,
            test_recovery_strategy
        )
        
        # Test recoverable error
        recoverable_error = APIError("This is a recoverable error")
        context = ErrorContext(operation="recovery_test")
        
        recovery_successful, user_message, recovery_result = global_error_handler.handle_error(
            recoverable_error, context, attempt_recovery=True
        )
        
        # Verify recovery worked
        self.assertTrue(recovery_successful)
        self.assertEqual(recovery_result["recovery_data"], "test_recovery_result")
        
        # Verify error record shows successful recovery
        error_record = global_error_handler.error_history[-1]
        self.assertTrue(error_record.recovery_attempted)
        self.assertTrue(error_record.recovery_successful)
        
        # Test non-recoverable error
        non_recoverable_error = APIError("This is not recoverable")
        
        recovery_successful_2, user_message_2, recovery_result_2 = global_error_handler.handle_error(
            non_recoverable_error, context, attempt_recovery=True
        )
        
        # Verify recovery failed
        self.assertFalse(recovery_successful_2)
        self.assertIsNone(recovery_result_2)


class TestErrorHandlingEndToEnd(unittest.TestCase):
    """End-to-end error handling tests."""
    
    def setUp(self):
        """Set up test fixtures."""
        global_error_handler.clear_error_history()
    
    @patch('ai.generator.AsyncOpenAI')
    async def test_complete_error_flow(self, mock_openai_class):
        """Test complete error handling flow from API to UI."""
        # Setup generator
        generator = InterviewQuestionGenerator("test-key", AIModel.GPT_4O)
        
        # Mock API to fail
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("Simulated API failure")
        )
        generator.client = mock_client
        
        # Create request
        request = GenerationRequest(
            job_description="Test job description for error flow",
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR,
            prompt_technique=PromptTechnique.ZERO_SHOT,
            question_count=5
        )
        
        # Generate questions (should fail gracefully)
        result = await generator.generate_questions(request)
        
        # Verify error handling
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        
        # Verify error was logged with proper context
        self.assertGreater(len(global_error_handler.error_history), 0)
        
        error_record = global_error_handler.error_history[-1]
        self.assertEqual(error_record.category, ErrorCategory.API_ERROR)
        self.assertEqual(error_record.context.operation, "generate_questions")
        self.assertIn("technical", error_record.context.additional_info["interview_type"])
        
        # Verify user-friendly message was generated
        self.assertIsNotNone(error_record.user_message)
        self.assertIn("error id:", error_record.user_message.lower())
        
        # Test error statistics
        stats = global_error_handler.get_error_statistics()
        self.assertEqual(stats["total_errors"], 1)
        self.assertEqual(stats["errors_by_category"][ErrorCategory.API_ERROR], 1)
    
    def test_multiple_component_error_aggregation(self):
        """Test error aggregation across multiple components."""
        # Simulate errors from various components
        component_errors = [
            {
                "component": "security_validator",
                "error": ValidationError("Input too long", field_name="job_description"),
                "operation": "input_validation"
            },
            {
                "component": "rate_limiter", 
                "error": RateLimitError("Rate limit exceeded", retry_after=60),
                "operation": "rate_check"
            },
            {
                "component": "ai_generator",
                "error": APIError("Model unavailable"),
                "operation": "model_call"
            },
            {
                "component": "cost_calculator",
                "error": ApplicationError("Pricing data unavailable", category=ErrorCategory.RESOURCE_ERROR),
                "operation": "cost_calculation"
            }
        ]
        
        # Handle all errors
        for error_data in component_errors:
            context = ErrorContext(
                operation=error_data["operation"],
                additional_info={"component": error_data["component"]}
            )
            global_error_handler.handle_error(error_data["error"], context)
        
        # Verify comprehensive error tracking
        stats = global_error_handler.get_error_statistics()
        self.assertEqual(stats["total_errors"], 4)
        
        # Verify different categories are tracked
        self.assertEqual(stats["errors_by_category"][ErrorCategory.VALIDATION_ERROR], 1)
        self.assertEqual(stats["errors_by_category"][ErrorCategory.RATE_LIMIT_ERROR], 1)
        self.assertEqual(stats["errors_by_category"][ErrorCategory.API_ERROR], 1)
        self.assertEqual(stats["errors_by_category"][ErrorCategory.RESOURCE_ERROR], 1)
        
        # Verify error history contains all components
        components = [
            e.context.additional_info.get("component") 
            for e in global_error_handler.error_history
        ]
        self.assertIn("security_validator", components)
        self.assertIn("rate_limiter", components)
        self.assertIn("ai_generator", components)
        self.assertIn("cost_calculator", components)


def run_async_test(coro):
    """Helper to run async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


if __name__ == "__main__":
    # Run tests
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Wrap async tests
    for test_case in [TestGeneratorErrorHandling, TestErrorHandlingEndToEnd]:
        for test_name in dir(test_case):
            if test_name.startswith('test_') and asyncio.iscoroutinefunction(getattr(test_case, test_name)):
                original_test = getattr(test_case, test_name)
                
                def make_sync_test(async_test):
                    def sync_test(self):
                        return run_async_test(async_test(self))
                    return sync_test
                
                setattr(test_case, test_name, make_sync_test(original_test))
    
    runner.run(suite)