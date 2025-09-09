"""
Simple test suite for Few-Shot Learning prompt implementation.
Tests Few-Shot templates and example-driven output quality.
"""
import os
import sys

# Add src to path for imports
test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(test_dir)
src_path = os.path.join(project_root, 'src')

if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from ai.few_shot import FewShotPrompts
    from ai.prompts import prompt_library
    from models.enums import ExperienceLevel, InterviewType, PromptTechnique
    print("✅ Few-Shot Learning imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def test_few_shot_template_registration():
    """Test that Few-Shot templates are properly registered"""
    print("Testing Few-Shot template registration...")

    # Check that templates were registered during import
    few_shot_templates = prompt_library.list_templates(
        technique=PromptTechnique.FEW_SHOT)

    # Should have templates for all interview types and experience levels
    assert len(few_shot_templates) > 0

    # Check specific combinations exist
    technical_junior = prompt_library.get_template(
        PromptTechnique.FEW_SHOT,
        InterviewType.TECHNICAL,
        ExperienceLevel.JUNIOR
    )
    assert technical_junior is not None
    assert technical_junior.name == "few_shot_technical_junior"

    behavioral_senior = prompt_library.get_template(
        PromptTechnique.FEW_SHOT,
        InterviewType.BEHAVIORAL,
        ExperienceLevel.SENIOR
    )
    assert behavioral_senior is not None
    assert behavioral_senior.name == "few_shot_behavioral_senior"

    print("✅ Few-Shot template registration test passed")


def test_technical_templates_coverage():
    """Test that all technical experience levels have Few-Shot templates"""
    print("Testing technical templates coverage...")

    experience_levels = [ExperienceLevel.JUNIOR, ExperienceLevel.MID,
                         ExperienceLevel.SENIOR, ExperienceLevel.LEAD]

    for level in experience_levels:
        template = prompt_library.get_template(
            PromptTechnique.FEW_SHOT,
            InterviewType.TECHNICAL,
            level
        )
        assert template is not None, f"Missing technical template for {level.value}"
        assert PromptTechnique.FEW_SHOT == template.technique
        assert InterviewType.TECHNICAL == template.interview_type
        assert level == template.experience_level

    print("✅ Technical templates coverage test passed")


def test_behavioral_templates_coverage():
    """Test that all behavioral experience levels have Few-Shot templates"""
    print("Testing behavioral templates coverage...")

    experience_levels = [ExperienceLevel.JUNIOR, ExperienceLevel.MID,
                         ExperienceLevel.SENIOR, ExperienceLevel.LEAD]

    for level in experience_levels:
        template = prompt_library.get_template(
            PromptTechnique.FEW_SHOT,
            InterviewType.BEHAVIORAL,
            level
        )
        assert template is not None, f"Missing behavioral template for {level.value}"
        assert PromptTechnique.FEW_SHOT == template.technique
        assert InterviewType.BEHAVIORAL == template.interview_type
        assert level == template.experience_level

    print("✅ Behavioral templates coverage test passed")


def test_case_study_template():
    """Test case study template exists and is generic"""
    print("Testing case study template...")

    template = prompt_library.get_template(
        PromptTechnique.FEW_SHOT,
        InterviewType.CASE_STUDY,
        None  # Should be generic
    )

    assert template is not None
    assert template.name == "few_shot_case_study_generic"
    assert template.experience_level is None  # Generic template
    assert PromptTechnique.FEW_SHOT == template.technique
    assert InterviewType.CASE_STUDY == template.interview_type

    print("✅ Case study template test passed")


def test_reverse_template():
    """Test reverse interview template exists and is generic"""
    print("Testing reverse interview template...")

    template = prompt_library.get_template(
        PromptTechnique.FEW_SHOT,
        InterviewType.REVERSE,
        None  # Should be generic
    )

    assert template is not None
    assert template.name == "few_shot_reverse_generic"
    assert template.experience_level is None  # Generic template
    assert PromptTechnique.FEW_SHOT == template.technique
    assert InterviewType.REVERSE == template.interview_type

    print("✅ Reverse interview template test passed")


def test_template_variable_extraction():
    """Test that templates have correct variables extracted"""
    print("Testing template variable extraction...")

    template = prompt_library.get_template(
        PromptTechnique.FEW_SHOT,
        InterviewType.TECHNICAL,
        ExperienceLevel.JUNIOR
    )

    # Should have standard variables
    expected_vars = {"question_count", "experience_level", "job_description"}
    actual_vars = set(template.variables)

    assert expected_vars.issubset(
        actual_vars), f"Missing variables: {expected_vars - actual_vars}"

    print("✅ Template variable extraction test passed")


def test_template_formatting():
    """Test that templates can be formatted with sample data"""
    print("Testing template formatting...")

    template = prompt_library.get_template(
        PromptTechnique.FEW_SHOT,
        InterviewType.TECHNICAL,
        ExperienceLevel.MID
    )

    # Test formatting with sample variables
    sample_vars = template.get_sample_variables()
    formatted = template.format(**sample_vars)

    # Should be a non-empty string
    assert isinstance(formatted, str)
    assert len(formatted) > 100  # Should be substantial content

    # Should not contain unresolved variables
    assert "{" not in formatted or "}" not in formatted

    # Should contain examples (key characteristic of Few-Shot)
    assert "Example" in formatted

    print("✅ Template formatting test passed")


def test_example_quality_technical():
    """Test that technical templates contain appropriate examples"""
    print("Testing technical example quality...")

    junior_template = prompt_library.get_template(
        PromptTechnique.FEW_SHOT,
        InterviewType.TECHNICAL,
        ExperienceLevel.JUNIOR
    )

    senior_template = prompt_library.get_template(
        PromptTechnique.FEW_SHOT,
        InterviewType.TECHNICAL,
        ExperienceLevel.SENIOR
    )

    # Format templates to check content
    sample_vars = {"question_count": "5", "experience_level": "Junior",
                   "job_description": "Python Developer"}
    junior_content = junior_template.format(**sample_vars)

    sample_vars["experience_level"] = "Senior"
    senior_content = senior_template.format(**sample_vars)

    # Junior should focus on basics
    assert "fundamental" in junior_content.lower() or "basic" in junior_content.lower()
    assert "1-2 years" in junior_content

    # Senior should focus on advanced topics
    assert "advanced" in senior_content.lower(
    ) or "system design" in senior_content.lower()
    assert "5+" in senior_content

    # Both should have multiple examples
    assert junior_content.count("Example") >= 3
    assert senior_content.count("Example") >= 3

    print("✅ Technical example quality test passed")


def test_example_quality_behavioral():
    """Test that behavioral templates contain appropriate examples"""
    print("Testing behavioral example quality...")

    junior_template = prompt_library.get_template(
        PromptTechnique.FEW_SHOT,
        InterviewType.BEHAVIORAL,
        ExperienceLevel.JUNIOR
    )

    lead_template = prompt_library.get_template(
        PromptTechnique.FEW_SHOT,
        InterviewType.BEHAVIORAL,
        ExperienceLevel.LEAD
    )

    # Format templates to check content
    sample_vars = {"question_count": "5", "experience_level": "Junior",
                   "job_description": "Software Developer"}
    junior_content = junior_template.format(**sample_vars)

    sample_vars["experience_level"] = "Lead"
    lead_content = lead_template.format(**sample_vars)

    # Junior should focus on learning and collaboration
    assert "learn" in junior_content.lower() or "collaboration" in junior_content.lower()

    # Lead should focus on leadership and strategy
    assert "leadership" in lead_content.lower() or "strategy" in lead_content.lower()

    # Both should have behavioral question examples
    assert "Tell me about a time" in junior_content or "Describe a situation" in junior_content
    assert "Tell me about a time" in lead_content or "Describe a situation" in lead_content

    print("✅ Behavioral example quality test passed")


def test_metadata_presence():
    """Test that templates have appropriate metadata"""
    print("Testing template metadata...")

    template = prompt_library.get_template(
        PromptTechnique.FEW_SHOT,
        InterviewType.TECHNICAL,
        ExperienceLevel.SENIOR
    )

    # Should have metadata
    assert template.metadata is not None
    assert len(template.metadata) > 0

    # Should have difficulty level
    assert "difficulty" in template.metadata

    # Should have focus areas
    assert "focus_areas" in template.metadata
    assert isinstance(template.metadata["focus_areas"], list)
    assert len(template.metadata["focus_areas"]) > 0

    print("✅ Template metadata test passed")


def test_difficulty_progression():
    """Test that difficulty progresses appropriately across experience levels"""
    print("Testing difficulty progression...")

    templates = {}
    for level in [ExperienceLevel.JUNIOR, ExperienceLevel.MID, ExperienceLevel.SENIOR, ExperienceLevel.LEAD]:
        template = prompt_library.get_template(
            PromptTechnique.FEW_SHOT,
            InterviewType.TECHNICAL,
            level
        )
        templates[level] = template

    # Check difficulty progression in metadata
    difficulties = {
        ExperienceLevel.JUNIOR: "beginner",
        ExperienceLevel.MID: "intermediate",
        ExperienceLevel.SENIOR: "advanced",
        ExperienceLevel.LEAD: "expert"
    }

    for level, expected_difficulty in difficulties.items():
        template = templates[level]
        actual_difficulty = template.metadata.get("difficulty", "").lower()
        assert expected_difficulty in actual_difficulty, f"Wrong difficulty for {level.value}: expected {expected_difficulty}, got {actual_difficulty}"

    print("✅ Difficulty progression test passed")


def test_template_uniqueness():
    """Test that each template is unique and properly differentiated"""
    print("Testing template uniqueness...")

    # Get all Few-Shot templates
    few_shot_templates = prompt_library.list_templates(
        technique=PromptTechnique.FEW_SHOT)

    # Check that all templates have unique names
    names = [t.name for t in few_shot_templates]
    assert len(names) == len(set(names)), "Duplicate template names found"

    # Check that templates have different content
    contents = []
    for template in few_shot_templates:
        sample_vars = template.get_sample_variables()
        content = template.format(**sample_vars)
        contents.append(content)

    # Should have unique content (at least different lengths)
    content_lengths = [len(c) for c in contents]
    assert len(set(content_lengths)) > 1, "All templates have identical length"

    print("✅ Template uniqueness test passed")


def test_fallback_behavior():
    """Test fallback behavior for missing experience levels"""
    print("Testing fallback behavior...")

    # Case study and reverse should work for any experience level (fallback to generic)
    for level in [ExperienceLevel.JUNIOR, ExperienceLevel.SENIOR]:
        case_study = prompt_library.get_template(
            PromptTechnique.FEW_SHOT,
            InterviewType.CASE_STUDY,
            level
        )
        assert case_study is not None
        assert case_study.experience_level is None  # Should be generic template

        reverse = prompt_library.get_template(
            PromptTechnique.FEW_SHOT,
            InterviewType.REVERSE,
            level
        )
        assert reverse is not None
        assert reverse.experience_level is None  # Should be generic template

    print("✅ Fallback behavior test passed")


def run_all_tests():
    """Run all Few-Shot Learning tests"""
    print("🧪 Running Few-Shot Learning Tests")
    print("=" * 50)

    try:
        test_few_shot_template_registration()
        test_technical_templates_coverage()
        test_behavioral_templates_coverage()
        test_case_study_template()
        test_reverse_template()
        test_template_variable_extraction()
        test_template_formatting()
        test_example_quality_technical()
        test_example_quality_behavioral()
        test_metadata_presence()
        test_difficulty_progression()
        test_template_uniqueness()
        test_fallback_behavior()

        print("=" * 50)
        print("🎉 All Few-Shot Learning tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
