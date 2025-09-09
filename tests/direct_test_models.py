"""
Direct test of data models
"""
from datetime import datetime
from pathlib import Path

# Import directly from files using absolute path
project_root = Path(__file__).parent.parent
exec(open(project_root / 'src/models/enums.py').read())
exec(open(project_root / 'src/models/simple_schemas.py').read())

# The following variables are defined by exec() above:
# InterviewType, ExperienceLevel, PromptTechnique, AISettings, etc.


def test_models():
    """Test all models directly"""
    print("🧪 Testing Data Models Directly\n")

    # Test enums
    print("Testing Enums...")
    assert InterviewType.TECHNICAL.value == "Technical Questions"  # type: ignore
    assert ExperienceLevel.SENIOR.value == "Senior (5+ years)"  # type: ignore
    assert PromptTechnique.CHAIN_OF_THOUGHT.value == "Chain-of-Thought"  # type: ignore
    print("  ✓ Enums work correctly")

    # Test AISettings
    print("Testing AISettings...")
    settings = AISettings()  # type: ignore
    assert settings.model == "gpt-4o"
    assert settings.temperature == 0.7

    settings = AISettings(model="gpt-5", temperature=0.5)  # type: ignore
    assert settings.model == "gpt-5"
    print("  ✓ AISettings work correctly")

    # Test CostBreakdown
    print("Testing CostBreakdown...")
    cost = CostBreakdown(  # type: ignore
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
    request = GenerationRequest(  # type: ignore
        job_description="Senior Python Developer with Django experience",
        interview_type=InterviewType.TECHNICAL,  # type: ignore
        experience_level=ExperienceLevel.SENIOR,  # type: ignore
        prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT,  # type: ignore
        question_count=5
    )
    assert "Python" in request.job_description
    assert request.ai_settings is not None
    print("  ✓ GenerationRequest works correctly")

    # Test InterviewResults
    print("Testing InterviewResults...")
    results = InterviewResults(  # type: ignore
        questions=["Question 1?", "Question 2?"],
        recommendations=["Practice coding", "Review algorithms"],
        cost_breakdown=cost,
        response_time=2.5,
        model_used="gpt-4o",
        tokens_used={"input": 100, "output": 200},
        technique_used=PromptTechnique.CHAIN_OF_THOUGHT  # type: ignore
    )
    assert len(results.questions) == 2
    print("  ✓ InterviewResults work correctly")

    # Test InterviewSession
    print("Testing InterviewSession...")
    session = InterviewSession(  # type: ignore
        id="session-123",
        timestamp=datetime.now(),
        job_description="Senior Python Developer with Django experience",
        interview_type=InterviewType.TECHNICAL,  # type: ignore
        experience_level=ExperienceLevel.SENIOR,  # type: ignore
        ai_settings=settings,
        prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT,  # type: ignore
        question_count=5
    )
    assert session.id == "session-123"
    print("  ✓ InterviewSession works correctly")

    # Test ApplicationState
    print("Testing ApplicationState...")
    state = ApplicationState()  # type: ignore
    assert state.total_api_calls == 0

    session_summary = SessionSummary(  # type: ignore
        session_id="test-123",
        timestamp=datetime.now(),
        interview_type=InterviewType.TECHNICAL,  # type: ignore
        experience_level=ExperienceLevel.SENIOR,  # type: ignore
        question_count=5,
        total_cost=0.05,
        technique_used=PromptTechnique.CHAIN_OF_THOUGHT,  # type: ignore
        success=True
    )

    state.add_session(session_summary)
    assert state.total_api_calls == 1
    print("  ✓ ApplicationState works correctly")

    print("\n🎉 All data model tests passed! Models are working correctly.")


if __name__ == "__main__":
    test_models()
