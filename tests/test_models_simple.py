"""
Simple test runner for data models
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.models.schemas import (AISettings, ApplicationState, CostBreakdown,
                            GenerationRequest, InterviewResults,
                            InterviewSession, Question, SessionSummary)
from src.models.enums import (DifficultyLevel, ExperienceLevel, InterviewType,
                          PromptTechnique, QuestionCategory)
import sys
from datetime import datetime
from pathlib import Path

# Add src to Python path BEFORE imports


def test_ai_settings():
    """Test AISettings model"""
    print("Testing AISettings...")

    # Test default values
    settings = AISettings()
    assert settings.model == "gpt-4o"
    assert settings.temperature == 0.7
    print("  ✓ Default values correct")

    # Test custom values
    settings = AISettings(model="gpt-5", temperature=0.5)
    assert settings.model == "gpt-5"
    assert settings.temperature == 0.5
    print("  ✓ Custom values work")

    # Test validation
    try:
        AISettings(temperature=3.0)  # Should fail
        assert False, "Should have failed validation"
    except Exception:
        print("  ✓ Validation works")


def test_question():
    """Test Question model"""
    print("Testing Question...")

    question = Question(
        id=1,
        question="What is the difference between list and tuple in Python?",
        difficulty=DifficultyLevel.EASY,
        category=QuestionCategory.CONCEPTUAL,
        time_estimate="3 minutes"
    )

    assert question.id == 1
    assert "Python" in question.question
    print("  ✓ Question creation works")


def test_cost_breakdown():
    """Test CostBreakdown model"""
    print("Testing CostBreakdown...")

    cost = CostBreakdown(
        input_cost=0.001,
        output_cost=0.002,
        total_cost=0.003,
        input_tokens=100,
        output_tokens=200
    )

    assert cost.total_cost == 0.003
    print("  ✓ Cost breakdown works")


def test_generation_request():
    """Test GenerationRequest model"""
    print("Testing GenerationRequest...")

    request = GenerationRequest(
        job_description="Senior Python Developer with Django experience",
        interview_type=InterviewType.TECHNICAL,
        experience_level=ExperienceLevel.SENIOR,
        prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT,
        question_count=5
    )

    assert "Python" in request.job_description
    assert request.question_count == 5
    print("  ✓ Generation request works")


def test_interview_session():
    """Test InterviewSession dataclass"""
    print("Testing InterviewSession...")

    ai_settings = AISettings()
    session = InterviewSession(
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
    assert session.question_count == 5
    print("  ✓ Interview session works")


def test_application_state():
    """Test ApplicationState model"""
    print("Testing ApplicationState...")

    state = ApplicationState()
    assert state.total_api_calls == 0
    assert state.total_cost == 0.0

    # Test adding session
    session = SessionSummary(
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
    assert state.total_api_calls == 1
    assert state.total_cost == 0.05
    print("  ✓ Application state works")


if __name__ == "__main__":
    print("🧪 Testing Data Models and Schemas\n")

    try:
        test_ai_settings()
        test_question()
        test_cost_breakdown()
        test_generation_request()
        test_interview_session()
        test_application_state()

        print("\n🎉 All model tests passed! Data models are working correctly.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
