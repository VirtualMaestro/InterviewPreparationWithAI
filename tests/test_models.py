"""
Test data models and validation schemas
"""
from src.models.simple_schemas import (SimpleAISettings, SimpleApplicationState, SimpleCostBreakdown,
                                SimpleGenerationRequest, SimpleInterviewResults,
                                SimpleInterviewSession, SimpleQuestion, SimpleSessionSummary)
from src.models.enums import (DifficultyLevel, ExperienceLevel, InterviewType,
                              PromptTechnique, QuestionCategory)
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pytest
from pydantic import ValidationError

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))


class TestSimpleAISettings:
    """Test SimpleAISettings model validation"""

    def test_default_values(self):
        """Test default AI settings"""
        settings = SimpleAISettings()
        assert settings.model == "gpt-4o"
        assert settings.temperature == 0.7
        assert settings.max_tokens == 2000
        assert settings.top_p == 0.9
        assert settings.frequency_penalty == 0.0

    def test_valid_settings(self):
        """Test valid AI settings"""
        settings = SimpleAISettings(
            model="gpt-5",
            temperature=0.5,
            max_tokens=1500,
            top_p=0.8,
            frequency_penalty=0.1
        )
        assert settings.model == "gpt-5"
        assert settings.temperature == 0.5

    def test_invalid_temperature(self):
        """Test invalid temperature values"""
        with pytest.raises(ValidationError):
            SimpleAISettings(temperature=-0.1)

        with pytest.raises(ValidationError):
            SimpleAISettings(temperature=2.1)

    def test_invalid_model(self):
        """Test invalid model name"""
        with pytest.raises(ValidationError):
            SimpleAISettings(model="gpt-3")


class TestQuestion:
    """Test Question model validation"""

    def test_valid_question(self):
        """Test valid question creation"""
        question = Question(
            id=1,
            question="What is the difference between list and tuple in Python?",
            difficulty=DifficultyLevel.EASY,
            category=QuestionCategory.CONCEPTUAL,
            time_estimate="3 minutes",
            evaluation_criteria=[
                "Understanding of data structures", "Clear explanation"],
            follow_ups=["When would you use each?"],
            hints=["Think about mutability"]
        )
        assert question.id == 1
        assert "Python" in question.question
        assert question.difficulty == DifficultyLevel.EASY

    def test_question_too_short(self):
        """Test question text too short"""
        with pytest.raises(ValidationError):
            Question(
                id=1,
                question="Short",
                difficulty=DifficultyLevel.EASY,
                category=QuestionCategory.CONCEPTUAL,
                time_estimate="1 minute"
            )

    def test_question_too_long(self):
        """Test question text too long"""
        long_question = "x" * 1001
        with pytest.raises(ValidationError):
            Question(
                id=1,
                question=long_question,
                difficulty=DifficultyLevel.EASY,
                category=QuestionCategory.CONCEPTUAL,
                time_estimate="1 minute"
            )


class TestSimpleCostBreakdown:
    """Test SimpleCostBreakdown model validation"""

    def test_valid_cost_breakdown(self):
        """Test valid cost breakdown"""
        cost = SimpleCostBreakdown(
            input_cost=0.001,
            output_cost=0.002,
            total_cost=0.003,
            input_tokens=100,
            output_tokens=200
        )
        assert cost.input_cost == 0.001
        assert cost.total_cost == 0.003

    def test_invalid_total_cost(self):
        """Test invalid total cost calculation"""
        with pytest.raises(ValidationError):
            SimpleCostBreakdown(
                input_cost=0.001,
                output_cost=0.002,
                total_cost=0.005,  # Should be 0.003
                input_tokens=100,
                output_tokens=200
            )

    def test_negative_costs(self):
        """Test negative cost values"""
        with pytest.raises(ValidationError):
            SimpleCostBreakdown(
                input_cost=-0.001,
                output_cost=0.002,
                total_cost=0.001,
                input_tokens=100,
                output_tokens=200
            )


class TestSimpleInterviewResults:
    """Test SimpleInterviewResults model validation"""

    def test_valid_results(self):
        """Test valid interview results"""
        cost = SimpleCostBreakdown(
            input_cost=0.001,
            output_cost=0.002,
            total_cost=0.003,
            input_tokens=100,
            output_tokens=200
        )

        results = SimpleInterviewResults(
            questions=["Question 1?", "Question 2?"],
            recommendations=["Practice coding", "Review algorithms"],
            cost_breakdown=cost,
            response_time=2.5,
            model_used="gpt-4o",
            tokens_used={"input": 100, "output": 200},
            technique_used=PromptTechnique.CHAIN_OF_THOUGHT
        )

        assert len(results.questions) == 2
        assert len(results.recommendations) == 2
        assert results.response_time == 2.5

    def test_empty_questions(self):
        """Test empty questions list"""
        cost = SimpleCostBreakdown(
            input_cost=0.001,
            output_cost=0.002,
            total_cost=0.003,
            input_tokens=100,
            output_tokens=200
        )

        with pytest.raises(ValidationError):
            SimpleInterviewResults(
                questions=[],  # Empty list should fail
                recommendations=["Practice coding"],
                cost_breakdown=cost,
                response_time=2.5,
                model_used="gpt-4o",
                tokens_used={"input": 100, "output": 200},
                technique_used=PromptTechnique.CHAIN_OF_THOUGHT
            )

    def test_too_many_questions(self):
        """Test too many questions"""
        cost = SimpleCostBreakdown(
            input_cost=0.001,
            output_cost=0.002,
            total_cost=0.003,
            input_tokens=100,
            output_tokens=200
        )

        # 21 questions, max is 20
        questions = [f"Question {i}?" for i in range(21)]

        with pytest.raises(ValidationError):
            SimpleInterviewResults(
                questions=questions,
                recommendations=["Practice coding"],
                cost_breakdown=cost,
                response_time=2.5,
                model_used="gpt-4o",
                tokens_used={"input": 100, "output": 200},
                technique_used=PromptTechnique.CHAIN_OF_THOUGHT
            )


class TestSimpleGenerationRequest:
    """Test SimpleGenerationRequest model validation"""

    def test_valid_request(self):
        """Test valid generation request"""
        request = SimpleGenerationRequest(
            job_description="Senior Python Developer with Django experience",
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR,
            prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT,
            question_count=5
        )

        assert "Python" in request.job_description
        assert request.interview_type == InterviewType.TECHNICAL
        assert request.question_count == 5

    def test_job_description_too_short(self):
        """Test job description too short"""
        with pytest.raises(ValidationError):
            SimpleGenerationRequest(
                job_description="Short",  # Less than 10 characters
                interview_type=InterviewType.TECHNICAL,
                experience_level=ExperienceLevel.SENIOR,
                prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT
            )

    def test_job_description_too_long(self):
        """Test job description too long"""
        long_description = "x" * 5001
        with pytest.raises(ValidationError):
            SimpleGenerationRequest(
                job_description=long_description,
                interview_type=InterviewType.TECHNICAL,
                experience_level=ExperienceLevel.SENIOR,
                prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT
            )

    def test_malicious_job_description(self):
        """Test job description with malicious content"""
        with pytest.raises(ValidationError):
            SimpleGenerationRequest(
                job_description="<script>alert('xss')</script> Python Developer",
                interview_type=InterviewType.TECHNICAL,
                experience_level=ExperienceLevel.SENIOR,
                prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT
            )

    def test_invalid_question_count(self):
        """Test invalid question count"""
        with pytest.raises(ValidationError):
            SimpleGenerationRequest(
                job_description="Senior Python Developer",
                interview_type=InterviewType.TECHNICAL,
                experience_level=ExperienceLevel.SENIOR,
                prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT,
                question_count=0  # Should be >= 1
            )

        with pytest.raises(ValidationError):
            SimpleGenerationRequest(
                job_description="Senior Python Developer",
                interview_type=InterviewType.TECHNICAL,
                experience_level=ExperienceLevel.SENIOR,
                prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT,
                question_count=21  # Should be <= 20
            )


class TestSimpleInterviewSession:
    """Test SimpleInterviewSession dataclass validation"""

    def test_valid_session(self):
        """Test valid interview session"""
        ai_settings = SimpleAISettings()
        session = SimpleInterviewSession(
            id="session-123",
            timestamp=datetime.now(),
            job_description="Senior Python Developer with Django experience",
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR,
            ai_settings=ai_settings,
            prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT,
            question_count=5
        )

        assert session.id == "session-123"
        assert session.interview_type == InterviewType.TECHNICAL
        assert session.question_count == 5

    def test_invalid_job_description(self):
        """Test invalid job description"""
        ai_settings = SimpleAISettings()

        with pytest.raises(ValueError):
            SimpleInterviewSession(
                id="session-123",
                timestamp=datetime.now(),
                job_description="Short",  # Too short
                interview_type=InterviewType.TECHNICAL,
                experience_level=ExperienceLevel.SENIOR,
                ai_settings=ai_settings,
                prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT,
                question_count=5
            )

    def test_invalid_question_count(self):
        """Test invalid question count"""
        ai_settings = SimpleAISettings()

        with pytest.raises(ValueError):
            SimpleInterviewSession(
                id="session-123",
                timestamp=datetime.now(),
                job_description="Senior Python Developer with Django experience",
                interview_type=InterviewType.TECHNICAL,
                experience_level=ExperienceLevel.SENIOR,
                ai_settings=ai_settings,
                prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT,
                question_count=0  # Invalid count
            )


class TestSimpleApplicationState:
    """Test SimpleApplicationState model validation"""

    def test_default_state(self):
        """Test default application state"""
        state = SimpleApplicationState()

        assert state.current_session is None
        assert len(state.session_history) == 0
        assert state.total_api_calls == 0
        assert state.total_cost == 0.0
        assert state.error_count == 0

    def test_add_session(self):
        """Test adding session to state"""
        state = SimpleApplicationState()

        session = SimpleSessionSummary(
            session_id="test-123",
            timestamp=datetime.now(),
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR,
            question_count=5,
            total_cost=0.05,
            technique_used=PromptTechnique.CHAIN_OF_THOUGHT,
            success=True
        )

        state.add_session(session)

        assert state.current_session == session
        assert len(state.session_history) == 1
        assert state.total_api_calls == 1
        assert state.total_cost == 0.05

    def test_session_history_limit(self):
        """Test session history limit enforcement"""
        state = SimpleApplicationState()

        # Add 12 sessions (more than the 10 limit)
        for i in range(12):
            session = SimpleSessionSummary(
                session_id=f"test-{i}",
                timestamp=datetime.now(),
                interview_type=InterviewType.TECHNICAL,
                experience_level=ExperienceLevel.SENIOR,
                question_count=5,
                total_cost=0.05,
                technique_used=PromptTechnique.CHAIN_OF_THOUGHT,
                success=True
            )
            state.add_session(session)

        # Should only keep the last 10 sessions
        assert len(state.session_history) == 10
        # First two should be removed
        assert state.session_history[0].session_id == "test-2"
        assert state.session_history[-1].session_id == "test-11"


if __name__ == "__main__":
    # Run tests manually if pytest is not available
    import traceback

    test_classes = [
        TestSimpleAISettings, TestQuestion, TestSimpleCostBreakdown,
        TestSimpleInterviewResults, TestSimpleGenerationRequest,
        TestSimpleInterviewSession, TestSimpleApplicationState
    ]

    total_tests = 0
    passed_tests = 0

    for test_class in test_classes:
        print(f"\nTesting {test_class.__name__}...")

        test_instance = test_class()
        test_methods = [method for method in dir(
            test_instance) if method.startswith('test_')]

        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                print(f"  ✓ {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"  ✗ {method_name}: {str(e)}")
                traceback.print_exc()

    print(f"\n🎯 Test Results: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🎉 All model tests passed!")
    else:
        print(f"❌ {total_tests - passed_tests} tests failed")
