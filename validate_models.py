"""
Validate data models work correctly
"""
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Now import the models
try:
    from models.enums import ExperienceLevel, InterviewType, PromptTechnique
    print("✓ Enums imported successfully")

    from models.schemas import AISettings, GenerationRequest
    print("✓ Schemas imported successfully")

    # Test basic functionality
    settings = AISettings()
    print(
        f"✓ AISettings created: {settings.model}, temp={settings.temperature}")

    # Test enum values
    print(f"✓ Interview types: {[t.value for t in InterviewType]}")
    print(f"✓ Experience levels: {[e.value for e in ExperienceLevel]}")
    print(f"✓ Prompt techniques: {[p.value for p in PromptTechnique]}")

    # Test validation
    request = GenerationRequest(
        job_description="Senior Python Developer with Django experience",
        interview_type=InterviewType.TECHNICAL,
        experience_level=ExperienceLevel.SENIOR,
        prompt_technique=PromptTechnique.CHAIN_OF_THOUGHT,
        question_count=5
    )
    print(f"✓ GenerationRequest created: {request.interview_type.value}")

    print("\n🎉 All data models are working correctly!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
