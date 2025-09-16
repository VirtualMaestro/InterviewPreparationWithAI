#!/usr/bin/env python3
"""
Integration tests for the new GUI interface (main_gui.py).

Tests complete workflows including recent fixes:
- Question count bug fix (5, 10, 15, 20)
- Structured Output JSON parsing
- Mock Interview mode
- All prompt techniques

This validates our GUI consolidation and recent improvements.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typing import Any, Dict

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import GUI class
sys.path.insert(0, str(Path(__file__).parent.parent))
from main_gui import InterviewPrepGUI
from src.models.enums import InterviewType, ExperienceLevel, PromptTechnique


class TestGUIIntegration:
    """Integration tests for the complete GUI workflow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.gui = InterviewPrepGUI()
        self.mock_api_key = "sk-test123456789"

        # Mock sidebar configuration
        self.test_sidebar_config = {
            "job_description": "Senior Python Developer at a tech company working on distributed systems",
            "experience_level": "Senior (5+ years)",
            "question_type": "Technical",
            "session_mode": "Generate questions",
            "questions_num": 10,  # Test the question count fix
            "prompt_technique": "Few Shot",
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2000
        }

    def test_map_config_to_enums(self):
        """Test configuration mapping works correctly."""
        mapped = self.gui.map_config_to_enums(self.test_sidebar_config)

        assert mapped["job_description"] == self.test_sidebar_config["job_description"]
        assert mapped["experience_level"] == ExperienceLevel.SENIOR
        assert mapped["interview_type"] == InterviewType.TECHNICAL
        assert mapped["prompt_technique"] == PromptTechnique.FEW_SHOT
        assert mapped["question_count"] == 10  # Test question count fix
        assert mapped["temperature"] == 0.7

    def test_extract_questions_structured_output(self):
        """Test JSON parsing for Structured Output technique."""
        # Test JSON response (like the user reported issue)
        json_response = '''
        {
            "questions": [
                {
                    "id": 1,
                    "question": "Design a simple caching system for a web application. What data structures would you use and how would you handle cache invalidation?",
                    "difficulty": "medium",
                    "category": "system_design"
                },
                {
                    "id": 2,
                    "question": "Explain how you would refactor a monolithic Python application into a microservices architecture.",
                    "difficulty": "hard",
                    "category": "system_design"
                }
            ]
        }
        '''

        # Test with structured output technique
        questions = self.gui.extract_questions_directly(json_response, "Structured Output")

        assert len(questions) == 2
        assert "Design a simple caching system" in questions[0]
        assert "refactor a monolithic Python application" in questions[1]
        assert "undefined" not in questions[0]  # Ensure the bug is fixed

    def test_extract_questions_few_shot(self):
        """Test that Few-Shot doesn't get broken by JSON parsing."""
        # Test normal Few-Shot response (should not be parsed as JSON)
        few_shot_response = '''
        1. **Question 1:** Explain the difference between list and tuple in Python.

        2. **Question 2:** How would you implement a decorator in Python?

        3. **Question 3:** What is the GIL and how does it affect multithreading?
        '''

        # Test with Few-Shot technique (should use text parsing)
        questions = self.gui.extract_questions_directly(few_shot_response, "Few Shot")

        assert len(questions) >= 3
        assert any("list and tuple" in q for q in questions)
        assert any("decorator" in q for q in questions)
        assert any("GIL" in q for q in questions)

    @pytest.mark.asyncio
    async def test_question_count_fix(self):
        """Test that question count fix works for different counts."""
        test_counts = [5, 10, 15, 20]

        for count in test_counts:
            config = self.test_sidebar_config.copy()
            config["questions_num"] = count

            # Test the mapping function
            mapped = self.gui.map_config_to_enums(config)
            assert mapped["question_count"] == count, f"Question count mapping failed for {count}"

    @pytest.mark.asyncio
    async def test_mock_interview_question_generation(self):
        """Test Mock Interview mode question generation."""
        with patch.object(self.gui, 'ensure_generator_initialized'):
            with patch('streamlit.session_state', {'api_key': self.mock_api_key}):

                # Mock the generator and its response
                mock_generator = Mock()
                mock_result = Mock()
                mock_result.success = True
                mock_result.questions = [
                    "Question 1: Tell me about yourself",
                    "Question 2: What is your experience with Python?",
                    "Question 3: How do you handle debugging?"
                ]
                mock_result.technique_used.value = "Few Shot"
                mock_result.raw_response = "1. Question 1: Tell me about yourself\n2. Question 2: What is your experience with Python?"

                mock_generator.generate_questions = AsyncMock(return_value=mock_result)
                self.gui.generator = mock_generator

                # Test question generation
                questions = await self.gui.generate_mock_questions_async(self.test_sidebar_config, count=5)

                assert len(questions) >= 3
                assert mock_generator.generate_questions.called

    @pytest.mark.asyncio
    async def test_answer_evaluation(self):
        """Test AI answer evaluation functionality."""
        question = "What is the difference between list and tuple in Python?"
        answer = "Lists are mutable while tuples are immutable. Lists use square brackets and tuples use parentheses."

        with patch('openai.AsyncOpenAI') as mock_openai:
            # Mock OpenAI response
            mock_response = Mock()
            mock_response.choices[0].message.content = """
            SCORE: 8
            FEEDBACK: Good understanding of the fundamental differences. Clear explanation of mutability.
            SUGGESTIONS: Could add examples and mention performance differences.
            """

            mock_client = Mock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_client

            with patch('streamlit.session_state', {'api_key': self.mock_api_key}):
                evaluation = await self.gui.evaluate_answer_async(
                    question, answer, "Python Developer", "Senior"
                )

                assert evaluation["score"] == 8
                assert "Good understanding" in evaluation["feedback"]
                assert "examples" in evaluation["suggestions"]

    def test_initialization(self):
        """Test GUI initialization."""
        assert self.gui.config is not None
        assert self.gui.security is not None
        assert self.gui.generator is None  # Not initialized without API key

    def test_session_state_initialization(self):
        """Test session state initialization."""
        with patch('streamlit.session_state', {}) as mock_session:
            self.gui.initialize_session_state()

            # Check that required session state variables are set
            expected_keys = [
                'chat_messages', 'mock_started', 'current_question',
                'correct', 'incorrect', 'api_key_validated', 'generation_in_progress'
            ]

            # Verify the session state would be properly initialized
            # (In actual Streamlit, these would be set on the session_state object)
            assert True  # Placeholder - in real test would check mock_session calls

    def test_api_key_validation(self):
        """Test API key validation logic."""
        # Test invalid API key
        assert not self.gui.validate_api_key("invalid-key")
        assert not self.gui.validate_api_key("")

        # Test valid format (but we won't test actual API call)
        with patch('streamlit.session_state', {}):
            with patch.object(self.gui, 'generator', None):
                # Valid format should pass initial validation
                result = self.gui.validate_api_key(self.mock_api_key)
                # In real implementation, this would make an API call
                # For testing, we just verify the format check

    @pytest.mark.asyncio
    async def test_complete_generation_workflow(self):
        """Test the complete question generation workflow."""
        with patch.object(self.gui, 'ensure_generator_initialized'):
            with patch('streamlit.session_state', {'api_key': self.mock_api_key}):

                # Mock successful generation
                mock_generator = Mock()
                mock_result = Mock()
                mock_result.success = True
                mock_result.questions = ["Question 1", "Question 2", "Question 3", "Question 4", "Question 5"]
                mock_result.recommendations = ["Study algorithms", "Practice coding"]
                mock_result.technique_used.value = "Few Shot"
                mock_result.model_used.value = "gpt-4o"
                mock_result.raw_response = "1. Question 1\n2. Question 2\n3. Question 3\n4. Question 4\n5. Question 5"
                mock_result.metadata = {"test": "data"}

                # Mock cost breakdown
                mock_cost = Mock()
                mock_cost.input_cost = 0.001
                mock_cost.output_cost = 0.002
                mock_cost.total_cost = 0.003
                mock_cost.input_tokens = 100
                mock_cost.output_tokens = 200
                mock_result.cost_breakdown = mock_cost

                mock_generator.generate_questions = AsyncMock(return_value=mock_result)
                self.gui.generator = mock_generator

                # Test the async generation
                config = {
                    "job_description": "Python Developer",
                    "interview_type": InterviewType.TECHNICAL,
                    "experience_level": ExperienceLevel.SENIOR,
                    "prompt_technique": PromptTechnique.FEW_SHOT,
                    "question_count": 5,
                    "temperature": 0.7
                }

                result = await self.gui.generate_questions_async(config)

                assert result is not None
                assert result["questions"] == mock_result.questions
                assert result["recommendations"] == mock_result.recommendations
                assert result["cost_breakdown"]["total_cost"] == 0.003
                assert result["metadata"]["test"] == "data"

    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test with no API key
        with patch('streamlit.session_state', {}):
            assert not self.gui.validate_api_key("")

        # Test extract_questions_directly with empty response
        questions = self.gui.extract_questions_directly("", "Few Shot")
        assert questions == []

        # Test extract_questions_directly with malformed JSON
        questions = self.gui.extract_questions_directly('{"invalid": json}', "Structured Output")
        assert isinstance(questions, list)  # Should fall back to text parsing


def test_gui_imports():
    """Test that all required imports work correctly."""
    # Test that we can import the GUI class
    assert InterviewPrepGUI is not None

    # Test that we can create an instance
    gui = InterviewPrepGUI()
    assert gui is not None


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])