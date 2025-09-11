"""
Simple unit tests for AI Question Generator.

Basic tests without complex mocking for core functionality.
"""

import unittest
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai.generator import (
    InterviewQuestionGenerator,
    GeneratorError,
    APIError,
    ParsingError,
    RateLimitError,
    GenerationResult
)
from models.enums import (
    InterviewType,
    ExperienceLevel,
    PromptTechnique,
    AIModel
)
from models.simple_schemas import GenerationRequest
from ai.prompts import PromptTemplate


class TestGeneratorSimple(unittest.TestCase):
    """Simple unit tests for generator components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = InterviewQuestionGenerator("test-key", AIModel.GPT_4O)
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        self.assertEqual(self.generator.api_key, "test-key")
        self.assertEqual(self.generator.model, AIModel.GPT_4O)
        self.assertEqual(self.generator.max_retries, 3)
        self.assertIsNotNone(self.generator.security)
    
    def test_parse_json_response_valid(self):
        """Test parsing valid JSON responses."""
        # Plain JSON
        json_data = {
            "questions": ["Q1", "Q2", "Q3"],
            "recommendations": ["R1", "R2"],
            "metadata": {"technique": "structured"}
        }
        json_str = json.dumps(json_data)
        
        result = self.generator._parse_json_response(json_str)
        self.assertEqual(result["questions"], ["Q1", "Q2", "Q3"])
        self.assertEqual(result["recommendations"], ["R1", "R2"])
        self.assertEqual(result["metadata"]["technique"], "structured")
    
    def test_parse_json_response_with_markdown(self):
        """Test parsing JSON from markdown code blocks."""
        json_data = {"questions": ["Q1"], "recommendations": []}
        
        # JSON in markdown block
        markdown_json = f"```json\n{json.dumps(json_data)}\n```"
        result = self.generator._parse_json_response(markdown_json)
        self.assertEqual(result["questions"], ["Q1"])
        
        # JSON in generic code block
        generic_block = f"```\n{json.dumps(json_data)}\n```"
        result = self.generator._parse_json_response(generic_block)
        self.assertEqual(result["questions"], ["Q1"])
    
    def test_parse_json_response_invalid(self):
        """Test parsing invalid JSON raises error."""
        invalid_jsons = [
            "Not JSON at all",
            "{invalid: json}",
            '{"unclosed": ',
            "```json\n{bad json}\n```"
        ]
        
        for invalid in invalid_jsons:
            with self.assertRaises(ParsingError):
                self.generator._parse_json_response(invalid)
    
    def test_parse_text_response_questions(self):
        """Test parsing questions from text response."""
        text = """Here are the interview questions:
        
1. What is your experience with Python?
2. How do you handle errors in production?
3. Describe a challenging project.
4. What are your thoughts on testing?
5. How do you stay updated with technology?"""
        
        result = self.generator._parse_text_response(text)
        self.assertEqual(len(result["questions"]), 5)
        self.assertIn("Python", result["questions"][0])
        self.assertIn("errors", result["questions"][1])
    
    def test_parse_text_response_with_recommendations(self):
        """Test parsing text with both questions and recommendations."""
        text = """Interview Questions:
- What is Python's GIL?
- Explain async/await
- How does garbage collection work?

Recommendations:
- Review Python internals
- Practice system design
- Prepare behavioral examples"""
        
        result = self.generator._parse_text_response(text)
        self.assertEqual(len(result["questions"]), 3)
        self.assertEqual(len(result["recommendations"]), 3)
        self.assertIn("GIL", result["questions"][0])
        self.assertIn("Python internals", result["recommendations"][0])
    
    def test_parse_text_response_mixed_formats(self):
        """Test parsing text with mixed numbering formats."""
        text = """Questions for the interview:
1) First question about experience
2. Second question about skills
• Third question with bullet point
- Fourth question with dash
5) Fifth question back to parentheses

Tips for preparation:
• Review fundamentals
- Practice coding
• Mock interviews"""
        
        result = self.generator._parse_text_response(text)
        self.assertEqual(len(result["questions"]), 5)
        self.assertEqual(len(result["recommendations"]), 3)
    
    def test_build_prompt_with_substitution(self):
        """Test prompt building with variable substitution."""
        template = PromptTemplate(
            name="Test",
            technique=PromptTechnique.ZERO_SHOT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.MID,
            template="Generate {num_questions} {interview_type} questions for {job_description}",
            variables=["num_questions", "interview_type", "job_description"],
            metadata={}
        )
        
        request = GenerationRequest(
            job_description="Python Developer at StartupCo",
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.MID,
            prompt_technique=PromptTechnique.ZERO_SHOT,
            question_count=5
        )
        
        prompt = self.generator._build_prompt(request, template)
        
        self.assertIn("5", prompt)
        self.assertIn("technical", prompt)
        self.assertIn("Python Developer at StartupCo", prompt)
    
    def test_build_prompt_with_additional_context(self):
        """Test prompt building with additional context."""
        template = PromptTemplate(
            name="Context Test",
            technique=PromptTechnique.ROLE_BASED,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.SENIOR,
            template="Company: {company_type}, Focus: {focus_areas}",
            variables=["company_type", "focus_areas"],
            metadata={}
        )
        
        request = GenerationRequest(
            job_description="Engineering Manager",
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.SENIOR,
            prompt_technique=PromptTechnique.ROLE_BASED,
            question_count=3
        )
        request.additional_context = {
            "company_type": "FAANG",
            "focus_areas": "leadership and scaling"
        }
        
        prompt = self.generator._build_prompt(request, template)
        
        self.assertIn("FAANG", prompt)
        self.assertIn("leadership and scaling", prompt)
    
    def test_select_prompt_template(self):
        """Test template selection logic."""
        request = GenerationRequest(
            job_description="Test Job",
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.JUNIOR,
            prompt_technique=PromptTechnique.ZERO_SHOT,
            question_count=5
        )
        
        # Test each technique
        techniques = [
            PromptTechnique.FEW_SHOT,
            PromptTechnique.CHAIN_OF_THOUGHT,
            PromptTechnique.ZERO_SHOT,
            PromptTechnique.STRUCTURED_OUTPUT
        ]
        
        for technique in techniques:
            template = self.generator._select_prompt_template(request, technique)
            self.assertIsNotNone(template, f"No template for {technique.value}")
            self.assertEqual(template.technique, technique)
    
    def test_select_role_based_template(self):
        """Test role-based template selection with persona."""
        request = GenerationRequest(
            job_description="Test Job",
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.MID,
            prompt_technique=PromptTechnique.ROLE_BASED,
            question_count=5
        )
        request.additional_context = {"persona": "strict"}
        
        template = self.generator._select_prompt_template(
            request,
            PromptTechnique.ROLE_BASED
        )
        
        self.assertIsNotNone(template)
        self.assertIn("strict", template.template.lower())
    
    def test_generation_result_structure(self):
        """Test GenerationResult dataclass."""
        from models.simple_schemas import CostBreakdown
        
        result = GenerationResult(
            questions=["Q1", "Q2"],
            recommendations=["R1"],
            metadata={"test": "data"},
            cost_breakdown=CostBreakdown(
                input_cost=0.01,
                output_cost=0.02,
                total_cost=0.03,
                input_tokens=100,
                output_tokens=200
            ),
            raw_response="raw text",
            technique_used=PromptTechnique.FEW_SHOT,
            model_used=AIModel.GPT_4O,
            success=True,
            error_message=None
        )
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.questions), 2)
        self.assertEqual(result.cost_breakdown.total_cost, 0.03)
        self.assertEqual(result.technique_used, PromptTechnique.FEW_SHOT)
    
    def test_error_types(self):
        """Test custom error types."""
        # Test error hierarchy
        self.assertTrue(issubclass(APIError, GeneratorError))
        self.assertTrue(issubclass(ParsingError, GeneratorError))
        self.assertTrue(issubclass(RateLimitError, GeneratorError))
        
        # Test error creation
        api_error = APIError("API failed")
        self.assertEqual(str(api_error), "API failed")
        
        parse_error = ParsingError("Invalid JSON")
        self.assertEqual(str(parse_error), "Invalid JSON")
        
        rate_error = RateLimitError("Limit exceeded")
        self.assertEqual(str(rate_error), "Limit exceeded")
    
    def test_get_generation_stats(self):
        """Test statistics retrieval."""
        stats = self.generator.get_generation_stats()
        
        # Check required fields
        self.assertIn("model", stats)
        self.assertIn("total_cost", stats)
        self.assertIn("session_costs", stats)
        self.assertIn("rate_limit_status", stats)
        self.assertIn("rate_limit_stats", stats)
        
        # Check types
        self.assertEqual(stats["model"], "gpt-4o-2024-08-06")
        self.assertIsInstance(stats["total_cost"], float)
        self.assertIsInstance(stats["rate_limit_status"], dict)


if __name__ == "__main__":
    unittest.main(verbosity=2)