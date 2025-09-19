#!/usr/bin/env python3
"""
Simple test script to verify question generation works independently.
This will help isolate any issues with the AI generation system.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from src.ai.generator import InterviewQuestionGenerator
    from src.models.enums import (AIModel, ExperienceLevel, InterviewType,
                                  PromptTechnique)
    from src.models.simple_schemas import SimpleGenerationRequest, SimpleAISettings
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


async def test_generation():
    """Test question generation with a simple example."""
    print("Testing Question Generation System")
    print("=" * 50)

    # Get API key from user
    api_key = input("Enter your OpenAI API key (sk-...): ").strip()

    if not api_key.startswith("sk-"):
        print("Invalid API key format")
        return

    try:
        # Initialize generator
        print("Initializing generator...")
        generator = InterviewQuestionGenerator(api_key, AIModel.GPT_4O)
        print("Generator initialized successfully")

        # Create a simple request
        request = SimpleGenerationRequest(
            job_description="Senior Python Developer position at a tech company",
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR,
            prompt_technique=PromptTechnique.FEW_SHOT,
            question_count=3
        )

        request.ai_settings = SimpleAISettings()
        request.ai_settings.temperature = 0.7

        print("Making API call...")
        print(f"   - Job: {request.job_description}")
        print(f"   - Type: {request.interview_type.value}")
        print(f"   - Level: {request.experience_level.value}")
        print(f"   - Count: {request.question_count}")

        # Generate questions
        result = await generator.generate_questions(request, preferred_technique=PromptTechnique.FEW_SHOT)

        print("\n📋 RESULTS:")
        print(f"   Success: {result.success}")

        if result.success:
            print(f"   Questions received: {len(result.questions)}")
            print(f"   Model used: {result.model_used.value}")
            print(f"   Technique used: {result.technique_used.value}")

            print("\nGENERATED QUESTIONS:")
            for i, question in enumerate(result.questions, 1):
                print(f"{i}. {question}")
                if not question.strip():
                    print("   WARNING: Empty question detected!")

            if result.cost_breakdown:
                print(f"\nCost: ${result.cost_breakdown.total_cost:.6f}")
        else:
            print(f"   Error: {result.error_message}")

    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")



if __name__ == "__main__":
    asyncio.run(test_generation())