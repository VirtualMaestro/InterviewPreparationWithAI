"""
Direct test of data models
"""
import sys
from datetime import datetime
from pathlib import Path

# Import directly from files
exec(open('src/models/enums.py').read())
exec(open('src/models/simple_schemas.py').read())


def test_models():
    """Test all models directly"""
    print("🧪 Testing Data Models Directly\n")

    # Test enums
    print("Testing Enums...")
    assert InterviewType.TECHNICAL.value == "Technical Questions"
    assert ExperienceLevel.SENIOR.value == "Senior (5+ years)"
    assert PromptTechnique.CHAIN_OF_THOUGHT.value == "Chain-of-Thought"
    print("  ✓ Enums work correctly")

    # Test AISettings
    print("Testing AISettings...")
    settings = AISettings()
    assert settings.model == "gpt-4o"
    assert settings.temperature == 0.7

    settings = AISettings(model="gpt-5", temperature=0.5)
    assert settings.model == "gpt-5"
    print("  ✓ AISettings work correctly")

    # Test CostBreakdown
    print("Testing CostBreakdown...")
    cost = CostBreakdown(
        input_cost=0.001,
        output_cost=0.002,
        total_cost=0.003,
        input_tokens=100,
        output_tokens=200
    )
    assert cost.total_cost == 0.003
    print("  ✓ CostBreakdown works correctly")

    # Test GenerationRequest
    print("Testing GenerationRequest...")
    request = GenerationRequest(
        job_description="Senior Python Developer with Django experience",
        interview_type=InterviewType.TECHNICAL,
        experience_level=ExperienceLevel.SENIOR,
        prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT,
        question_count=5
    )
    assert "Python" in request.job_description
    assert request.ai_settings is not None
    print("  ✓ GenerationRequest works correctly")

    # Test InterviewResults
    print("Testing InterviewResults...")
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
    print("  ✓ InterviewResults work correctly")

    # Test InterviewSession
    print("Testing InterviewSession...")
    session = InterviewSession(
        id="session-123",
        timestamp=datetime.now(),
        job_description="Senior Python Developer with Django experience",
        interview_type=InterviewType.TECHNICAL,
        experience_level=ExperienceLevel.SENIOR,
        ai_settings=settings,
        prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT,
        question_count=5
    )
    assert session.id == "session-123"
    print("  ✓ InterviewSession works correctly")

    # Test ApplicationState
    print("Testing ApplicationState...")
    state = ApplicationState()
    assert state.total_api_calls == 0

    session_summary = SessionSummary(
        session_id="test-123",
        timestamp=datetime.now(),
        interview_type=InterviewType.TECHNICAL,
        experience_level=ExperienceLevel.SENIOR,
        question_count=5,
        total_cost=0.05,
        technique_used=PromptTechnique.CHAIN_OF_THOUGHT,
        success=True
    )

    state.add_session(session_summary)
    assert state.total_api_calls == 1
    print("  ✓ ApplicationState works correctly")

    print("\n🎉 All data model tests passed! Models are working correctly.")


if __name__ == "__main__":
    test_models()
