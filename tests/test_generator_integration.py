"""
Integration tests for AI Question Generator with mocked API responses.

Tests the complete generation workflow including:
- API call handling and retry logic
- Response parsing (JSON and text)
- Fallback mechanisms
- Error handling
- Cost tracking
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import asyncio
import json
# Add parent directory to path
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from src.ai.generator import (GenerationResult,
                              InterviewQuestionGenerator, ParsingError)
from src.models.enums import (AIModel, ExperienceLevel, InterviewType,
                              PromptTechnique)
from src.models.simple_schemas import SimpleGenerationRequest


class TestGeneratorIntegration(unittest.TestCase):
    """Integration tests for InterviewQuestionGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"
        self.generator = InterviewQuestionGenerator(self.api_key, AIModel.GPT_4O)
        
        # Sample generation request
        self.sample_request = SimpleGenerationRequest(
            job_description="Senior Python Developer at Tech Company",
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR,
            question_count=5,
            prompt_technique=PromptTechnique.STRUCTURED_OUTPUT
        )
        
        # Mock API responses
        self.mock_structured_response = {
            "content": json.dumps({
                "questions": [
                    {
                        "question": "Explain the GIL in Python",
                        "difficulty": "hard",
                        "category": "technical",
                        "time_estimate": 10
                    },
                    {
                        "question": "Design a distributed cache system",
                        "difficulty": "hard",
                        "category": "system_design",
                        "time_estimate": 20
                    },
                    {
                        "question": "How do you handle database migrations?",
                        "difficulty": "medium",
                        "category": "technical",
                        "time_estimate": 8
                    },
                    {
                        "question": "Describe your experience with microservices",
                        "difficulty": "medium",
                        "category": "technical",
                        "time_estimate": 10
                    },
                    {
                        "question": "What's your approach to code reviews?",
                        "difficulty": "medium",
                        "category": "behavioral",
                        "time_estimate": 5
                    }
                ],
                "recommendations": [
                    "Review Python internals and advanced features",
                    "Practice system design problems",
                    "Prepare examples of past projects"
                ],
                "metadata": {
                    "generation_technique": "structured_output",
                    "total_questions": 5
                }
            }),
            "usage": {
                "prompt_tokens": 500,
                "completion_tokens": 200,
                "total_tokens": 700
            },
            "model": "gpt-4o",
            "finish_reason": "stop"
        }
        
        self.mock_text_response = {
            "content": """Here are interview questions for a Senior Python Developer:

Questions:
1. Explain the GIL in Python and its implications
2. Design a distributed cache system
3. How do you handle database migrations in production?
4. Describe your experience with microservices architecture
5. What's your approach to code reviews?

Recommendations:
- Review Python internals and advanced features
- Practice system design problems
- Prepare specific examples from past projects""",
            "usage": {
                "prompt_tokens": 450,
                "completion_tokens": 150,
                "total_tokens": 600
            },
            "model": "gpt-4o",
            "finish_reason": "stop"
        }
    
    @patch('ai.generator.AsyncOpenAI')
    async def test_successful_generation_structured(self, mock_openai_class):
        """Test successful generation with structured output."""
        # Setup mock
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        # Mock the completion response
        mock_response = AsyncMock()
        mock_response.choices = [
            Mock(message=Mock(content=self.mock_structured_response["content"]))
        ]
        mock_response.usage = Mock(
            prompt_tokens=500,
            completion_tokens=200,
            total_tokens=700
        )
        mock_response.model = "gpt-4o"
        mock_response.choices[0].finish_reason = "stop"
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        # Re-create generator with mocked client
        self.generator.client = mock_client
        
        # Generate questions
        result = await self.generator.generate_questions(self.sample_request)
        
        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(len(result.questions), 5)
        self.assertIn("Explain the GIL", result.questions[0])
        self.assertEqual(len(result.recommendations), 3)
        self.assertEqual(result.technique_used, PromptTechnique.STRUCTURED_OUTPUT)
        self.assertEqual(result.cost_breakdown.total_cost, 0.0105)  # Based on GPT-4o pricing
    
    @patch('ai.generator.AsyncOpenAI')
    async def test_successful_generation_text(self, mock_openai_class):
        """Test successful generation with text parsing."""
        # Setup mock
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        # Mock the completion response
        mock_response = AsyncMock()
        mock_response.choices = [
            Mock(message=Mock(content=self.mock_text_response["content"]))
        ]
        mock_response.usage = Mock(
            prompt_tokens=450,
            completion_tokens=150,
            total_tokens=600
        )
        mock_response.model = "gpt-4o"
        mock_response.choices[0].finish_reason = "stop"
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        # Re-create generator with mocked client
        self.generator.client = mock_client
        
        # Use zero-shot for text response
        request = SimpleGenerationRequest(
            job_description="Python Developer",
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.MID,
            num_questions=5,
            prompt_technique=PromptTechnique.ZERO_SHOT
        )
        
        # Generate questions
        result = await self.generator.generate_questions(request)
        
        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(len(result.questions), 5)
        self.assertIn("GIL", result.questions[0])
        self.assertTrue(len(result.recommendations) > 0)
    
    @patch('ai.generator.AsyncOpenAI')
    async def test_retry_on_api_error(self, mock_openai_class):
        """Test retry logic on API errors."""
        # Setup mock
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        # First two calls fail, third succeeds
        mock_response = AsyncMock()
        mock_response.choices = [
            Mock(message=Mock(content=self.mock_text_response["content"]))
        ]
        mock_response.usage = Mock(
            prompt_tokens=450,
            completion_tokens=150,
            total_tokens=600
        )
        mock_response.model = "gpt-4o"
        mock_response.choices[0].finish_reason = "stop"
        
        mock_client.chat.completions.create = AsyncMock(
            side_effect=[
                Exception("Network error"),
                Exception("Timeout"),
                mock_response
            ]
        )
        
        # Re-create generator with mocked client
        self.generator.client = mock_client
        
        # Generate questions
        result = await self.generator.generate_questions(self.sample_request)
        
        # Should eventually succeed
        self.assertTrue(result.success)
        self.assertEqual(mock_client.chat.completions.create.call_count, 3)
    
    @patch('ai.generator.rate_limiter')
    async def test_rate_limit_error(self, mock_rate_limiter):
        """Test handling of rate limit errors."""
        # Mock rate limiter to return false
        mock_rate_limiter.can_make_call.return_value = False
        mock_status = Mock()
        mock_status.time_until_reset.total_seconds.return_value = 3600
        mock_rate_limiter.get_rate_limit_status.return_value = mock_status
        
        # Try to generate questions
        result = await self.generator.generate_questions(self.sample_request)
        
        # Should fail with rate limit error
        self.assertFalse(result.success)
        self.assertIn("Rate limit", result.error_message or "")
    
    @patch('ai.generator.AsyncOpenAI')
    async def test_fallback_techniques(self, mock_openai_class):
        """Test fallback to different techniques on failure."""
        # Setup mock
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        # Structured output fails with malformed JSON, fallback to text works
        responses = [
            # First response: malformed JSON
            AsyncMock(
                choices=[Mock(message=Mock(content="Invalid JSON {{{"))],
                usage=Mock(prompt_tokens=100, completion_tokens=50, total_tokens=150),
                model="gpt-4o"
            ),
            # Second response: valid text
            AsyncMock(
                choices=[Mock(message=Mock(content=self.mock_text_response["content"]))],
                usage=Mock(prompt_tokens=450, completion_tokens=150, total_tokens=600),
                model="gpt-4o"
            )
        ]
        
        for r in responses:
            r.choices[0].finish_reason = "stop"
        
        mock_client.chat.completions.create = AsyncMock(side_effect=responses)
        
        # Re-create generator with mocked client
        self.generator.client = mock_client
        
        # Generate questions
        result = await self.generator.generate_questions(self.sample_request)
        
        # Should succeed with fallback
        self.assertTrue(result.success)
        self.assertTrue(len(result.questions) > 0)
    
    def test_parse_json_response(self):
        """Test JSON response parsing."""
        # Test valid JSON
        json_str = json.dumps({
            "questions": ["Q1", "Q2"],
            "recommendations": ["R1"],
            "metadata": {"test": "data"}
        })
        result = self.generator._parse_json_response(json_str)
        self.assertEqual(result["questions"], ["Q1", "Q2"])
        
        # Test JSON in markdown code block
        markdown_json = f"```json\n{json_str}\n```"
        result = self.generator._parse_json_response(markdown_json)
        self.assertEqual(result["questions"], ["Q1", "Q2"])
        
        # Test invalid JSON
        with self.assertRaises(ParsingError):
            self.generator._parse_json_response("Invalid JSON {{{")
    
    def test_parse_text_response(self):
        """Test text response parsing."""
        # Test question extraction
        text = """Questions:
1. What is Python?
2. Explain OOP concepts
3. How does async work?

Recommendations:
- Study Python basics
- Practice coding"""
        
        result = self.generator._parse_text_response(text)
        self.assertEqual(len(result["questions"]), 3)
        self.assertEqual(len(result["recommendations"]), 2)
        self.assertIn("Python", result["questions"][0])
        
        # Test with bullet points
        text = """Interview Questions:
• What is Python?
• Explain OOP
- How does async work?

Tips:
- Study basics
- Practice daily"""
        
        result = self.generator._parse_text_response(text)
        self.assertEqual(len(result["questions"]), 3)
        self.assertEqual(len(result["recommendations"]), 2)
    
    def test_build_prompt(self):
        """Test prompt building with variable substitution."""
        from ai.prompts import PromptTemplate
        
        template = PromptTemplate(
            id="test",
            name="Test Template",
            technique=PromptTechnique.ZERO_SHOT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR,
            content="Generate {num_questions} questions for {job_description} at {experience_level} level",
            variables=["num_questions", "job_description", "experience_level"],
            metadata={}
        )
        
        prompt = self.generator._build_prompt(self.sample_request, template)
        
        self.assertIn("5 questions", prompt)
        self.assertIn("Senior Python Developer", prompt)
        self.assertIn("senior level", prompt)
    
    @patch('ai.generator.AsyncOpenAI')
    async def test_validate_api_key(self, mock_openai_class):
        """Test API key validation."""
        # Setup mock
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        # Mock successful validation
        mock_client.models.list = AsyncMock(return_value=Mock())
        self.generator.client = mock_client
        
        result = await self.generator.validate_api_key()
        self.assertTrue(result)
        
        # Mock failed validation
        mock_client.models.list = AsyncMock(side_effect=Exception("Invalid API key"))
        
        result = await self.generator.validate_api_key()
        self.assertFalse(result)
    
    def test_generation_stats(self):
        """Test generation statistics retrieval."""
        stats = self.generator.get_generation_stats()
        
        self.assertIn("model", stats)
        self.assertEqual(stats["model"], "gpt-4o-2024-08-06")
        self.assertIn("total_cost", stats)
        self.assertIn("rate_limit_status", stats)
    
    def test_sync_generation_wrapper(self):
        """Test synchronous wrapper for async generation."""
        with patch.object(self.generator, 'generate_questions') as mock_async:
            # Mock the async method
            mock_result = GenerationResult(
                questions=["Q1", "Q2"],
                recommendations=["R1"],
                metadata={},
                cost_breakdown=Mock(),
                raw_response="test",
                technique_used=PromptTechnique.ZERO_SHOT,
                model_used=AIModel.GPT_4O,
                success=True
            )
            
            async def async_return():
                return mock_result
            
            mock_async.return_value = async_return()
            
            # Call sync wrapper
            result = self.generator.generate_questions_sync(self.sample_request)
            
            self.assertTrue(result.success)
            self.assertEqual(len(result.questions), 2)


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
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGeneratorIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Wrap async tests
    for test in suite:
        if asyncio.iscoroutinefunction(test._testMethodName):
            original_test = getattr(test, test._testMethodName)
            wrapped_test = lambda self, orig=original_test: run_async_test(orig(self))
            setattr(test, test._testMethodName, wrapped_test)
    
    runner.run(suite)