"""
Simple test suite for Zero-Shot prompt implementation.
Tests Zero-Shot templates and comparison with other techniques.
"""
import os
import sys
import traceback

# Add src to path for imports
test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(test_dir)
src_path = os.path.join(project_root, 'src')

if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from ai.prompts import prompt_library
    from ai.zero_shot import ZeroShotPrompts
    from models.enums import ExperienceLevel, InterviewType, PromptTechnique
    print("✅ Zero-Shot imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def test_zero_shot_template_registration():
    """Test that Zero-Shot templates are properly registered"""
    print("Testing Zero-Shot template registration...")

    # Check that templates were registered during import
    zero_shot_templates = prompt_library.list_templates(
        technique=PromptTechnique.ZERO_SHOT)

    # Should have templates for all interview types and experience levels
    assert len(zero_shot_templates) > 0

    # Check specific combinations exist
    technical_junior = prompt_library.get_template(
        PromptTechnique.ZERO_SHOT,
        InterviewType.TECHNICAL,
        ExperienceLevel.JUNIOR
    )
    assert technical_junior is not None
    assert technical_junior.name == "zero_shot_technical_junior"

    behavioral_senior = prompt_library.get_template(
        PromptTechnique.ZERO_SHOT,
        InterviewType.BEHAVIORAL,
        ExperienceLevel.SENIOR
    )
    assert behavioral_senior is not None
    assert behavioral_senior.name == "zero_shot_behavioral_senior"

    print("✅ Zero-Shot template registration test passed")


def test_technical_templates_coverage():
    """Test that all technical experience levels have Zero-Shot templates"""
    print("Testing technical templates coverage...")

    experience_levels = [ExperienceLevel.JUNIOR, ExperienceLevel.MID,
                         ExperienceLevel.SENIOR, ExperienceLevel.LEAD]

    for level in experience_levels:
        template = prompt_library.get_template(
            PromptTechnique.ZERO_SHOT,
            InterviewType.TECHNICAL,
            level
        )
        assert template is not None, f"Missing technical template for {level.value}"
        assert PromptTechnique.ZERO_SHOT == template.technique
        assert InterviewType.TECHNICAL == template.interview_type
        assert level == template.experience_level

    print("✅ Technical templates coverage test passed")


def test_behavioral_templates_coverage():
    """Test that all behavioral experience levels have Zero-Shot templates"""
    print("Testing behavioral templates coverage...")

    experience_levels = [ExperienceLevel.JUNIOR, ExperienceLevel.MID,
                         ExperienceLevel.SENIOR, ExperienceLevel.LEAD]

    for level in experience_levels:
        template = prompt_library.get_template(
            PromptTechnique.ZERO_SHOT,
            InterviewType.BEHAVIORAL,
            level
        )
        assert template is not None, f"Missing behavioral template for {level.value}"
        assert PromptTechnique.ZERO_SHOT == template.technique
        assert InterviewType.BEHAVIORAL == template.interview_type
        assert level == template.experience_level

    print("✅ Behavioral templates coverage test passed")


def test_case_study_and_reverse_templates():
    """Test case study and reverse interview templates exist and are generic"""
    print("Testing case study and reverse templates...")

    # Case study template
    case_study = prompt_library.get_template(
        PromptTechnique.ZERO_SHOT,
        InterviewType.CASE_STUDY,
        None
    )
    assert case_study is not None
    assert case_study.name == "zero_shot_case_study_generic"
    assert case_study.experience_level is None

    # Reverse interview template
    reverse = prompt_library.get_template(
        PromptTechnique.ZERO_SHOT,
        InterviewType.REVERSE,
        None
    )
    assert reverse is not None
    assert reverse.name == "zero_shot_reverse_generic"
    assert reverse.experience_level is None

    print("✅ Case study and reverse templates test passed")


def test_direct_generation_approach():
    """Test that Zero-Shot templates use direct generation approach"""
    print("Testing direct generation approach...")

    template = prompt_library.get_template(
        PromptTechnique.ZERO_SHOT,
        InterviewType.TECHNICAL,
        ExperienceLevel.MID
    )

    # Format template to check content
    sample_vars = template.get_sample_variables()
    formatted = template.format(**sample_vars)

    # Should NOT contain step-by-step reasoning
    assert "Step 1:" not in formatted
    assert "Step 2:" not in formatted

    # Should NOT contain examples
    assert "Example 1:" not in formatted
    assert "Example 2:" not in formatted

    # Should be concise and direct
    assert len(
        formatted) < 1000, f"Zero-Shot template too long: {len(formatted)} characters"

    # Should contain direct instruction
    assert "Generate" in formatted or "Create" in formatted

    print("✅ Direct generation approach test passed")


def test_concise_focused_prompts():
    """Test that Zero-Shot prompts are concise and focused"""
    print("Testing concise focused prompts...")

    # Get Zero-Shot template
    zero_shot = prompt_library.get_template(
        PromptTechnique.ZERO_SHOT,
        InterviewType.BEHAVIORAL,
        ExperienceLevel.SENIOR
    )

    # Format template
    sample_vars = {"question_count": "5", "experience_level": "Senior",
                   "job_description": "Engineering Manager"}

    zero_shot_content = zero_shot.format(**sample_vars)

    # Zero-Shot should be concise (less than 1000 characters)
    assert len(
        zero_shot_content) < 1000, f"Zero-Shot too long: {len(zero_shot_content)} characters"

    # Zero-Shot should be focused and direct
    assert zero_shot_content.count(
        '\n') < 10, "Zero-Shot should have fewer line breaks"

    print("✅ Concise focused prompts test passed")


def test_fallback_mechanism():
    """Test fallback mechanism functionality"""
    print("Testing fallback mechanism...")

    # Test getting fallback template
    fallback = ZeroShotPrompts.get_fallback_template(
        InterviewType.TECHNICAL,
        ExperienceLevel.JUNIOR
    )

    assert fallback is not None
    assert fallback.technique == PromptTechnique.ZERO_SHOT
    assert fallback.interview_type == InterviewType.TECHNICAL

    # Test fallback needed check
    needs_fallback = ZeroShotPrompts.is_fallback_needed(
        PromptTechnique.FEW_SHOT,
        InterviewType.TECHNICAL,
        ExperienceLevel.JUNIOR
    )
    assert needs_fallback == True

    # Zero-Shot doesn't need fallback to itself
    no_fallback_needed = ZeroShotPrompts.is_fallback_needed(
        PromptTechnique.ZERO_SHOT,
        InterviewType.TECHNICAL,
        ExperienceLevel.JUNIOR
    )
    assert no_fallback_needed == False

    print("✅ Fallback mechanism test passed")


def test_emergency_fallback_creation():
    """Test emergency fallback template creation"""
    print("Testing emergency fallback creation...")

    # Create emergency fallback
    emergency = ZeroShotPrompts.create_emergency_fallback(
        InterviewType.TECHNICAL,
        ExperienceLevel.MID
    )

    assert emergency is not None
    assert emergency.technique == PromptTechnique.ZERO_SHOT
    assert emergency.interview_type == InterviewType.TECHNICAL
    assert emergency.experience_level == ExperienceLevel.MID
    assert "emergency_fallback" in emergency.name

    # Should be able to format
    sample_vars = emergency.get_sample_variables()
    formatted = emergency.format(**sample_vars)
    assert len(formatted) > 50  # Should have some content

    print("✅ Emergency fallback creation test passed")


def test_fallback_priority_metadata():
    """Test that templates have appropriate fallback priority metadata"""
    print("Testing fallback priority metadata...")

    template = prompt_library.get_template(
        PromptTechnique.ZERO_SHOT,
        InterviewType.TECHNICAL,
        ExperienceLevel.SENIOR
    )

    # Should have fallback priority
    assert "fallback_priority" in template.metadata
    priority = template.metadata["fallback_priority"]
    assert priority in ["high", "medium", "low", "emergency"]

    # Technical and behavioral should have high priority
    assert priority == "high"

    print("✅ Fallback priority metadata test passed")


def test_template_comparison_info():
    """Test template comparison information generation"""
    print("Testing template comparison info...")

    comparison = ZeroShotPrompts.get_template_comparison_info()

    # Should have comparison metrics
    assert "zero_shot_template_count" in comparison
    assert "total_template_count" in comparison
    assert "zero_shot_percentage" in comparison
    assert "avg_zero_shot_length" in comparison
    assert "avg_other_technique_length" in comparison
    assert "length_ratio" in comparison
    assert "fallback_coverage" in comparison

    # Zero-Shot should be shorter on average
    assert comparison["length_ratio"] < 1.0, "Zero-Shot should be shorter than other techniques"

    # Should have coverage information
    coverage = comparison["fallback_coverage"]
    assert "Technical Questions" in coverage
    assert "Behavioral Questions" in coverage

    print("✅ Template comparison info test passed")


def test_approach_metadata():
    """Test that templates have correct approach metadata"""
    print("Testing approach metadata...")

    template = prompt_library.get_template(
        PromptTechnique.ZERO_SHOT,
        InterviewType.BEHAVIORAL,
        ExperienceLevel.MID
    )

    # Should have approach metadata
    assert "approach" in template.metadata
    assert template.metadata["approach"] == "direct_generation"

    # Should have focus metadata
    assert "focus" in template.metadata
    focus = template.metadata["focus"]
    assert isinstance(focus, str)
    assert len(focus) > 0

    print("✅ Approach metadata test passed")


def test_experience_level_appropriateness():
    """Test that Zero-Shot templates are appropriate for experience levels"""
    print("Testing experience level appropriateness...")

    junior_template = prompt_library.get_template(
        PromptTechnique.ZERO_SHOT,
        InterviewType.TECHNICAL,
        ExperienceLevel.JUNIOR
    )

    senior_template = prompt_library.get_template(
        PromptTechnique.ZERO_SHOT,
        InterviewType.TECHNICAL,
        ExperienceLevel.SENIOR
    )

    # Format templates
    sample_vars = {"question_count": "5", "experience_level": "Junior",
                   "job_description": "Python Developer"}
    junior_content = junior_template.format(**sample_vars)

    sample_vars["experience_level"] = "Senior"
    senior_content = senior_template.format(**sample_vars)

    # Junior should mention fundamentals
    assert "fundamental" in junior_content.lower() or "basic" in junior_content.lower()

    # Senior should mention advanced concepts
    assert "advanced" in senior_content.lower() or "strategic" in senior_content.lower()

    print("✅ Experience level appropriateness test passed")


def test_template_formatting_and_variables():
    """Test that Zero-Shot templates format correctly"""
    print("Testing template formatting and variables...")

    template = prompt_library.get_template(
        PromptTechnique.ZERO_SHOT,
        InterviewType.CASE_STUDY,
        None
    )

    # Should have standard variables
    expected_vars = {"question_count", "job_description"}
    actual_vars = set(template.variables)
    assert expected_vars.issubset(actual_vars)

    # Should format correctly
    custom_vars = {
        "question_count": "3",
        "experience_level": "Mid-level",
        "job_description": "Full-stack developer with React and Node.js experience"
    }

    formatted = template.format(**custom_vars)

    # Should contain custom values
    assert "3" in formatted
    assert "React" in formatted

    # Should not have unresolved variables
    assert "{" not in formatted or "}" not in formatted

    print("✅ Template formatting and variables test passed")


def test_template_uniqueness():
    """Test that Zero-Shot templates are unique and properly differentiated"""
    print("Testing template uniqueness...")

    # Get all Zero-Shot templates
    zero_shot_templates = prompt_library.list_templates(
        technique=PromptTechnique.ZERO_SHOT)

    # Check unique names
    names = [t.name for t in zero_shot_templates]
    assert len(names) == len(set(names)), "Duplicate template names found"

    # Check content differentiation
    contents = []
    for template in zero_shot_templates:
        sample_vars = template.get_sample_variables()
        content = template.format(**sample_vars)
        contents.append(content)

    # Should have different content
    content_hashes = [hash(c) for c in contents]
    assert len(set(content_hashes)) == len(
        content_hashes), "Duplicate template content found"

    print("✅ Template uniqueness test passed")


def run_all_tests():
    """Run all Zero-Shot tests"""
    print("🧪 Running Zero-Shot Tests")
    print("=" * 40)

    try:
        test_zero_shot_template_registration()
        test_technical_templates_coverage()
        test_behavioral_templates_coverage()
        test_case_study_and_reverse_templates()
        test_direct_generation_approach()
        test_concise_focused_prompts()
        test_fallback_mechanism()
        test_emergency_fallback_creation()
        test_fallback_priority_metadata()
        test_template_comparison_info()
        test_approach_metadata()
        test_experience_level_appropriateness()
        test_template_formatting_and_variables()
        test_template_uniqueness()

        print("=" * 40)
        print("🎉 All Zero-Shot tests passed!")
        return True

    except Exception as e:  # pylint: disable=broad-except
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
