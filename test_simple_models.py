"""
Test simple data models without Pydantic
"""
from models.simple_schemas import (AISettings, ApplicationState, CostBreakdown,
                                   GenerationRequest, InterviewResults,
                                   InterviewSession, SessionSummary)
from models.enums import ExperienceLevel, InterviewType, PromptTechnique
import sys
from datetime import datetime
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_ai_settings():
    """Test AISettings dataclass"""
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
    except ValueError:
        print("  ✓ Temperature validation works")

    try:
        AISettings(model="invalid-model")  # Should fail
        assert False, "Should have failed validation"
    except ValueError:
        print("  ✓ Model validation works")


def test_cost_breakdown():
    """Test CostBreakdown dataclass"""
    print("Testing CostBreakdown...")

    cost = CostBreakdown(
        input_cost=0.001,
        output_cost=0.002,
        total_cost=0.003,
        input_tokens=100,
        output_tokens=200
    )

    assert cost.total_cost == 0.003
    print("  ✓ Cost breakdown creation works")

    # Test validation
    try:
        CostBreakdown(
            input_cost=0.001,
            output_cost=0.002,
            total_cost=0.005,  # Wrong total
            input_tokens=100,
            output_tokens=200
        )
        assert False, "Should have failed validation"
    except ValueError:
        print("  ✓ Cost validation works")


def test_generation_request():
    """Test GenerationRequest dataclass"""
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
    assert request.ai_settings is not None  # Should be auto-created
    print("  ✓ Generation request works")

    # Test validation
    try:
        GenerationRequest(
            job_description="Short",  # Too short
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR,
            prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT
        )
        assert False, "Should have failed validation"
    except ValueError:
        print("  ✓ Job description validation works")


def test_interview_results():
    """Test InterviewResults dataclass"""
    print("Testing InterviewResults...")

    cost = CostBreakdown(
        input_cost=0.001,
        output_cost=0.002,
        total_cost=0.003,
        input_tokens=100,
        output_tokens=200
    )

    results = InterviewResults(
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
    assert results.metadata is not None  # Should be auto-created
    print("  ✓ Interview results work")


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
    """Test ApplicationState dataclass"""
    print("Testing ApplicationState...")

    state = ApplicationState()
    assert state.total_api_calls == 0
    assert state.total_cost == 0.0
    assert state.session_history is not None
    print("  ✓ Default state works")

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
    assert len(state.session_history) == 1
    print("  ✓ Session management works")


if __name__ == "__main__":
    print("🧪 Testing Simple Data Models\n")

    try:
        test_ai_settings()
        test_cost_breakdown()
        test_generation_request()
        test_interview_results()
        test_interview_session()
        test_application_state()

        print("\n🎉 All simple model tests passed! Data models are working correctly.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
