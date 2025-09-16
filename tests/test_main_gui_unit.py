#!/usr/bin/env python3
"""
Unit tests for main_gui.py core functionality.

Tests individual methods and components of the InterviewPrepGUI class.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import GUI class
sys.path.insert(0, str(Path(__file__).parent.parent))
from main_gui import InterviewPrepGUI
from src.models.enums import InterviewType, ExperienceLevel, PromptTechnique


class TestInterviewPrepGUIUnit:
    """Unit tests for InterviewPrepGUI class methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.gui = InterviewPrepGUI()

    def test_initialization(self):
        """Test GUI class initialization."""
        assert self.gui.config is not None
        assert self.gui.security is not None
        assert self.gui.generator is None
        assert hasattr(self.gui, 'debug_mode')

    def test_map_config_to_enums_technical(self):
        """Test configuration mapping for technical interviews."""
        sidebar_config = {
            "job_description": "Python Developer",
            "experience_level": "Mid-level (3-5 years)",
            "question_type": "Technical",
            "prompt_technique": "Chain of Thought",
            "questions_num": 15,
            "temperature": 0.8,
            "top_p": 0.9,
            "max_tokens": 3000
        }

        mapped = self.gui.map_config_to_enums(sidebar_config)

        assert mapped["job_description"] == "Python Developer"
        assert mapped["experience_level"] == ExperienceLevel.MID
        assert mapped["interview_type"] == InterviewType.TECHNICAL
        assert mapped["prompt_technique"] == PromptTechnique.CHAIN_OF_THOUGHT
        assert mapped["question_count"] == 15  # Test question count fix
        assert mapped["temperature"] == 0.8

    def test_map_config_to_enums_behavioral(self):
        """Test configuration mapping for behavioral interviews."""
        sidebar_config = {
            "job_description": "Senior Product Manager",
            "experience_level": "Senior (5+ years)",
            "question_type": "Behavioural",
            "prompt_technique": "Role Based",
            "questions_num": 20,
            "temperature": 0.6,
            "top_p": 0.8,
            "max_tokens": 2500
        }

        mapped = self.gui.map_config_to_enums(sidebar_config)

        assert mapped["experience_level"] == ExperienceLevel.SENIOR
        assert mapped["interview_type"] == InterviewType.BEHAVIORAL
        assert mapped["prompt_technique"] == PromptTechnique.ROLE_BASED
        assert mapped["question_count"] == 20

    def test_map_config_to_enums_lead_level(self):
        """Test configuration mapping for lead/principal level."""
        sidebar_config = {
            "job_description": "Tech Lead",
            "experience_level": "Lead/Principal",
            "question_type": "Technical",
            "prompt_technique": "Structured Output",
            "questions_num": 5,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2000
        }

        mapped = self.gui.map_config_to_enums(sidebar_config)

        assert mapped["experience_level"] == ExperienceLevel.LEAD
        assert mapped["prompt_technique"] == PromptTechnique.STRUCTURED_OUTPUT
        assert mapped["question_count"] == 5

    def test_extract_questions_json_structured_output(self):
        """Test JSON extraction for Structured Output technique."""
        json_response = '''
        {
            "questions": [
                {
                    "id": 1,
                    "question": "How would you design a distributed cache?",
                    "difficulty": "hard"
                },
                {
                    "id": 2,
                    "question": "Explain microservices architecture benefits.",
                    "difficulty": "medium"
                }
            ]
        }
        '''

        questions = self.gui.extract_questions_directly(json_response, "Structured Output")

        assert len(questions) == 2
        assert "distributed cache" in questions[0]
        assert "microservices architecture" in questions[1]

    def test_extract_questions_json_other_technique(self):
        """Test that JSON is NOT parsed for non-structured techniques."""
        json_response = '''
        {
            "questions": [
                {"question": "This should not be parsed as JSON"}
            ]
        }
        '''

        # Should fall back to text parsing for Few Shot
        questions = self.gui.extract_questions_directly(json_response, "Few Shot")

        # Should not extract from JSON structure when not Structured Output
        assert len(questions) == 0 or "This should not be parsed as JSON" not in questions[0]

    def test_extract_questions_text_parsing(self):
        """Test text parsing for regular responses."""
        text_response = '''
        1. **Question 1:** What is polymorphism in Python?
        2. **Question 2:** How do you handle exceptions in Python?
        3. **Question 3:** Explain the difference between shallow and deep copy.
        '''

        questions = self.gui.extract_questions_directly(text_response, "Few Shot")

        assert len(questions) >= 3
        assert any("polymorphism" in q.lower() for q in questions)
        assert any("exceptions" in q.lower() for q in questions)
        assert any("copy" in q.lower() for q in questions)

    def test_extract_questions_empty_response(self):
        """Test handling of empty responses."""
        assert self.gui.extract_questions_directly("", "Few Shot") == []
        assert self.gui.extract_questions_directly(None, "Few Shot") == []

    def test_extract_questions_malformed_json(self):
        """Test handling of malformed JSON for Structured Output."""
        malformed_json = '{"questions": [{"question": "Test"'  # Missing closing brackets

        # Should fall back to text parsing
        questions = self.gui.extract_questions_directly(malformed_json, "Structured Output")
        assert isinstance(questions, list)

    def test_api_key_validation_format(self):
        """Test API key format validation."""
        # Valid format
        assert self.gui.validate_api_key("sk-1234567890") == True

        # Invalid formats
        assert self.gui.validate_api_key("") == False
        assert self.gui.validate_api_key("invalid-key") == False
        assert self.gui.validate_api_key("api-1234567890") == False

    def test_api_key_validation_with_session_state(self):
        """Test API key validation with session state."""
        with patch('streamlit.session_state', {}) as mock_session:
            valid_key = "sk-test123456789"

            # Should return True for valid format and set session state
            result = self.gui.validate_api_key(valid_key)
            assert result == True

    @patch('streamlit.session_state', {})
    def test_ensure_generator_initialized_no_key(self):
        """Test generator initialization when no API key is available."""
        self.gui.ensure_generator_initialized()
        assert self.gui.generator is None

    @patch('streamlit.session_state', {'api_key': 'sk-test123'})
    def test_ensure_generator_initialized_with_key(self):
        """Test generator initialization with API key."""
        with patch('main_gui.InterviewQuestionGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator

            self.gui.ensure_generator_initialized()

            mock_generator_class.assert_called_once()

    def test_question_count_mapping_edge_cases(self):
        """Test question count mapping handles edge cases."""
        # Test with None value
        config_none = {
            "job_description": "Test",
            "experience_level": "Junior (1-2 years)",
            "question_type": "Technical",
            "prompt_technique": "Zero Shot",
            "questions_num": None,  # This happens when not in "Generate questions" mode
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2000
        }

        mapped = self.gui.map_config_to_enums(config_none)
        assert mapped["question_count"] == 5  # Should default to 5

    def test_all_experience_levels(self):
        """Test all experience level mappings."""
        levels = [
            ("Junior (1-2 years)", ExperienceLevel.JUNIOR),
            ("Mid-level (3-5 years)", ExperienceLevel.MID),
            ("Senior (5+ years)", ExperienceLevel.SENIOR),
            ("Lead/Principal", ExperienceLevel.LEAD)
        ]

        for level_str, expected_enum in levels:
            config = {
                "job_description": "Test",
                "experience_level": level_str,
                "question_type": "Technical",
                "prompt_technique": "Few Shot",
                "questions_num": 5,
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000
            }

            mapped = self.gui.map_config_to_enums(config)
            assert mapped["experience_level"] == expected_enum

    def test_all_prompt_techniques(self):
        """Test all prompt technique mappings."""
        techniques = [
            ("Zero Shot", PromptTechnique.ZERO_SHOT),
            ("Few Shot", PromptTechnique.FEW_SHOT),
            ("Chain of Thought", PromptTechnique.CHAIN_OF_THOUGHT),
            ("Role Based", PromptTechnique.ROLE_BASED),
            ("Structured Output", PromptTechnique.STRUCTURED_OUTPUT)
        ]

        for tech_str, expected_enum in techniques:
            config = {
                "job_description": "Test",
                "experience_level": "Senior (5+ years)",
                "question_type": "Technical",
                "prompt_technique": tech_str,
                "questions_num": 5,
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000
            }

            mapped = self.gui.map_config_to_enums(config)
            assert mapped["prompt_technique"] == expected_enum

    def test_question_count_values(self):
        """Test different question count values."""
        counts = [5, 10, 15, 20]

        for count in counts:
            config = {
                "job_description": "Test",
                "experience_level": "Senior (5+ years)",
                "question_type": "Technical",
                "prompt_technique": "Few Shot",
                "questions_num": count,
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000
            }

            mapped = self.gui.map_config_to_enums(config)
            assert mapped["question_count"] == count


if __name__ == "__main__":
    pytest.main([__file__, "-v"])