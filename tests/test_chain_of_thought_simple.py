"""
Simple test suite for Chain-of-Thought prompt implementation.
Tests Chain-of-Thought templates and reasoning chain presence in outputs.
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
    from ai.chain_of_thought import ChainOfThoughtPrompts
    from ai.prompts import prompt_library
    from models.enums import ExperienceLevel, InterviewType, PromptTechnique
    print("✅ Chain-of-Thought imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def test_chain_of_thought_template_registration():
    """Test that Chain-of-Thought templates are properly registered"""
    print("Testing Chain-of-Thought template registration...")

    # Check that templates were registered during import
    cot_templates = prompt_library.list_templates(
        technique=PromptTechnique.CHAIN_OF_THOUGHT)

    # Should have templates for all interview types and experience levels
    assert len(cot_templates) > 0

    # Check specific combinations exist
    technical_junior = prompt_library.get_template(
        PromptTechnique.CHAIN_OF_THOUGHT,
        InterviewType.TECHNICAL,
        ExperienceLevel.JUNIOR
    )
    assert technical_junior is not None
    assert technical_junior.name == "chain_of_thought_technical_junior"

    behavioral_senior = prompt_library.get_template(
        PromptTechnique.CHAIN_OF_THOUGHT,
        InterviewType.BEHAVIORAL,
        ExperienceLevel.SENIOR
    )
    assert behavioral_senior is not None
    assert behavioral_senior.name == "chain_of_thought_behavioral_senior"

    print("✅ Chain-of-Thought template registration test passed")


def test_technical_templates_coverage():
    """Test that all technical experience levels have Chain-of-Thought templates"""
    print("Testing technical templates coverage...")

    experience_levels = [ExperienceLevel.JUNIOR, ExperienceLevel.MID,
                         ExperienceLevel.SENIOR, ExperienceLevel.LEAD]

    for level in experience_levels:
        template = prompt_library.get_template(
            PromptTechnique.CHAIN_OF_THOUGHT,
            InterviewType.TECHNICAL,
            level
        )
        assert template is not None, f"Missing technical template for {level.value}"
        assert PromptTechnique.CHAIN_OF_THOUGHT == template.technique
        assert InterviewType.TECHNICAL == template.interview_type
        assert level == template.experience_level

    print("✅ Technical templates coverage test passed")


def test_behavioral_templates_coverage():
    """Test that all behavioral experience levels have Chain-of-Thought templates"""
    print("Testing behavioral templates coverage...")

    experience_levels = [ExperienceLevel.JUNIOR, ExperienceLevel.MID,
                         ExperienceLevel.SENIOR, ExperienceLevel.LEAD]

    for level in experience_levels:
        template = prompt_library.get_template(
            PromptTechnique.CHAIN_OF_THOUGHT,
            InterviewType.BEHAVIORAL,
            level
        )
        assert template is not None, f"Missing behavioral template for {level.value}"
        assert PromptTechnique.CHAIN_OF_THOUGHT == template.technique
        assert InterviewType.BEHAVIORAL == template.interview_type
        assert level == template.experience_level

    print("✅ Behavioral templates coverage test passed")


def test_case_study_template():
    """Test case study template exists and is generic"""
    print("Testing case study template...")

    template = prompt_library.get_template(
        PromptTechnique.CHAIN_OF_THOUGHT,
        InterviewType.CASE_STUDY,
        None  # Should be generic
    )

    assert template is not None
    assert template.name == "chain_of_thought_case_study_generic"
    assert template.experience_level is None  # Generic template
    assert PromptTechnique.CHAIN_OF_THOUGHT == template.technique
    assert InterviewType.CASE_STUDY == template.interview_type

    print("✅ Case study template test passed")


def test_reverse_template():
    """Test reverse interview template exists and is generic"""
    print("Testing reverse interview template...")

    template = prompt_library.get_template(
        PromptTechnique.CHAIN_OF_THOUGHT,
        InterviewType.REVERSE,
        None  # Should be generic
    )

    assert template is not None
    assert template.name == "chain_of_thought_reverse_generic"
    assert template.experience_level is None  # Generic template
    assert PromptTechnique.CHAIN_OF_THOUGHT == template.technique
    assert InterviewType.REVERSE == template.interview_type

    print("✅ Reverse interview template test passed")


def test_reasoning_chain_structure():
    """Test that templates contain proper step-by-step reasoning structure"""
    print("Testing reasoning chain structure...")

    template = prompt_library.get_template(
        PromptTechnique.CHAIN_OF_THOUGHT,
        InterviewType.TECHNICAL,
        ExperienceLevel.MID
    )

    # Format template to check content
    sample_vars = template.get_sample_variables()
    formatted = template.format(**sample_vars)

    # Should contain step-by-step structure
    assert "Step 1:" in formatted
    assert "Step 2:" in formatted
    assert "Step 3:" in formatted

    # Should have multiple reasoning steps
    step_count = formatted.count("Step ")
    assert step_count >= 5, f"Expected at least 5 reasoning steps, found {step_count}"

    # Should contain analysis and reasoning keywords
    reasoning_keywords = ["analyze", "assess",
                          "consider", "evaluate", "reasoning"]
    found_keywords = [
        kw for kw in reasoning_keywords if kw.lower() in formatted.lower()]
    assert len(
        found_keywords) >= 3, f"Expected reasoning keywords, found: {found_keywords}"

    print("✅ Reasoning chain structure test passed")


def test_progressive_complexity_in_steps():
    """Test that reasoning steps show progressive complexity across experience levels"""
    print("Testing progressive complexity in reasoning steps...")

    junior_template = prompt_library.get_template(
        PromptTechnique.CHAIN_OF_THOUGHT,
        InterviewType.TECHNICAL,
        ExperienceLevel.JUNIOR
    )

    senior_template = prompt_library.get_template(
        PromptTechnique.CHAIN_OF_THOUGHT,
        InterviewType.TECHNICAL,
        ExperienceLevel.SENIOR
    )

    # Format templates
    sample_vars = {"question_count": "5", "experience_level": "Junior",
                   "job_description": "Python Developer"}
    junior_content = junior_template.format(**sample_vars)

    sample_vars["experience_level"] = "Senior"
    senior_content = senior_template.format(**sample_vars)

    # Junior should focus on fundamentals
    junior_lower = junior_content.lower()
    assert any(word in junior_lower for word in [
               "fundamental", "basic", "simple", "foundational"])

    # Senior should focus on advanced concepts
    senior_lower = senior_content.lower()
    assert any(word in senior_lower for word in [
               "strategic", "advanced", "complex", "organizational"])

    # Senior should have more reasoning steps
    junior_steps = junior_content.count("Step ")
    senior_steps = senior_content.count("Step ")
    assert senior_steps >= junior_steps, f"Senior should have >= steps than junior: {senior_steps} vs {junior_steps}"

    print("✅ Progressive complexity test passed")


def test_metadata_reasoning_steps():
    """Test that templates have correct reasoning steps metadata"""
    print("Testing metadata reasoning steps...")

    templates = [
        (ExperienceLevel.JUNIOR, 5),
        (ExperienceLevel.MID, 6),
        (ExperienceLevel.SENIOR, 7),
        (ExperienceLevel.LEAD, 8)
    ]

    for level, expected_steps in templates:
        template = prompt_library.get_template(
            PromptTechnique.CHAIN_OF_THOUGHT,
            InterviewType.TECHNICAL,
            level
        )

        assert "reasoning_steps" in template.metadata
        actual_steps = template.metadata["reasoning_steps"]
        assert actual_steps == expected_steps, f"{level.value}: expected {expected_steps} steps, got {actual_steps}"

    print("✅ Metadata reasoning steps test passed")


def test_complexity_building_metadata():
    """Test that templates have appropriate complexity building metadata"""
    print("Testing complexity building metadata...")

    junior_template = prompt_library.get_template(
        PromptTechnique.CHAIN_OF_THOUGHT,
        InterviewType.TECHNICAL,
        ExperienceLevel.JUNIOR
    )

    lead_template = prompt_library.get_template(
        PromptTechnique.CHAIN_OF_THOUGHT,
        InterviewType.TECHNICAL,
        ExperienceLevel.LEAD
    )

    # Check complexity building metadata
    assert "complexity_building" in junior_template.metadata
    assert "complexity_building" in lead_template.metadata

    junior_complexity = junior_template.metadata["complexity_building"]
    lead_complexity = lead_template.metadata["complexity_building"]

    # Should have different complexity approaches
    assert junior_complexity != lead_complexity
    assert "linear" in junior_complexity or "progression" in junior_complexity
    assert "organizational" in lead_complexity or "scale" in lead_complexity

    print("✅ Complexity building metadata test passed")


def test_behavioral_reasoning_quality():
    """Test that behavioral templates contain appropriate reasoning for people scenarios"""
    print("Testing behavioral reasoning quality...")

    template = prompt_library.get_template(
        PromptTechnique.CHAIN_OF_THOUGHT,
        InterviewType.BEHAVIORAL,
        ExperienceLevel.MID
    )

    # Format template
    sample_vars = template.get_sample_variables()
    formatted = template.format(**sample_vars)

    # Should contain behavioral-specific reasoning
    behavioral_keywords = ["leadership", "collaboration",
                           "communication", "influence", "team"]
    found_keywords = [
        kw for kw in behavioral_keywords if kw.lower() in formatted.lower()]
    assert len(
        found_keywords) >= 3, f"Expected behavioral keywords, found: {found_keywords}"

    # Should have step-by-step behavioral analysis
    assert "competencies" in formatted.lower() or "behavioral" in formatted.lower()
    assert "scenarios" in formatted.lower() or "situations" in formatted.lower()

    print("✅ Behavioral reasoning quality test passed")


def test_case_study_reasoning_structure():
    """Test that case study template has appropriate problem-solving reasoning"""
    print("Testing case study reasoning structure...")

    template = prompt_library.get_template(
        PromptTechnique.CHAIN_OF_THOUGHT,
        InterviewType.CASE_STUDY,
        None
    )

    # Format template
    sample_vars = template.get_sample_variables()
    formatted = template.format(**sample_vars)

    # Should contain problem-solving reasoning
    problem_solving_keywords = [
        "problem", "analysis", "solution", "approach", "methodology"]
    found_keywords = [
        kw for kw in problem_solving_keywords if kw.lower() in formatted.lower()]
    assert len(
        found_keywords) >= 4, f"Expected problem-solving keywords, found: {found_keywords}"

    # Should mention realistic scenarios
    assert "realistic" in formatted.lower() or "scenario" in formatted.lower()
    assert "complexity" in formatted.lower()

    print("✅ Case study reasoning structure test passed")


def test_reverse_interview_reasoning():
    """Test that reverse interview template has strategic question reasoning"""
    print("Testing reverse interview reasoning...")

    template = prompt_library.get_template(
        PromptTechnique.CHAIN_OF_THOUGHT,
        InterviewType.REVERSE,
        None
    )

    # Format template
    sample_vars = template.get_sample_variables()
    formatted = template.format(**sample_vars)

    # Should contain strategic reasoning for question selection
    strategic_keywords = ["strategic", "evaluate",
                          "assess", "decision", "priorities"]
    found_keywords = [
        kw for kw in strategic_keywords if kw.lower() in formatted.lower()]
    assert len(
        found_keywords) >= 3, f"Expected strategic keywords, found: {found_keywords}"

    # Should mention candidate evaluation and preparation
    assert "candidate" in formatted.lower()
    assert "preparation" in formatted.lower() or "thoughtful" in formatted.lower()

    print("✅ Reverse interview reasoning test passed")


def test_template_formatting_with_reasoning():
    """Test that templates format correctly and maintain reasoning structure"""
    print("Testing template formatting with reasoning...")

    template = prompt_library.get_template(
        PromptTechnique.CHAIN_OF_THOUGHT,
        InterviewType.BEHAVIORAL,
        ExperienceLevel.SENIOR
    )

    # Test formatting with custom variables
    custom_vars = {
        "question_count": "7",
        "experience_level": "Senior",
        "job_description": "Engineering Manager role with team leadership and technical strategy responsibilities"
    }

    formatted = template.format(**custom_vars)

    # Should contain the custom values
    assert "7" in formatted
    assert "Senior" in formatted
    assert "Engineering Manager" in formatted

    # Should maintain reasoning structure
    assert "Step 1:" in formatted
    assert "reasoning" in formatted.lower()

    # Should not have unresolved variables
    assert "{" not in formatted or "}" not in formatted

    print("✅ Template formatting with reasoning test passed")


def test_template_uniqueness_and_differentiation():
    """Test that Chain-of-Thought templates are unique and properly differentiated"""
    print("Testing template uniqueness and differentiation...")

    # Get all Chain-of-Thought templates
    cot_templates = prompt_library.list_templates(
        technique=PromptTechnique.CHAIN_OF_THOUGHT)

    # Check that all templates have unique names
    names = [t.name for t in cot_templates]
    assert len(names) == len(set(names)), "Duplicate template names found"

    # Check that templates have different reasoning step counts
    step_counts = []
    for template in cot_templates:
        if "reasoning_steps" in template.metadata:
            step_counts.append(template.metadata["reasoning_steps"])

    # Should have variety in step counts
    assert len(set(step_counts)
               ) > 1, "All templates have same number of reasoning steps"

    # Check content differentiation
    contents = []
    for template in cot_templates:
        sample_vars = template.get_sample_variables()
        content = template.format(**sample_vars)
        contents.append(len(content))

    # Should have different content lengths
    assert len(set(contents)) > 1, "All templates have identical content length"

    print("✅ Template uniqueness and differentiation test passed")


def run_all_tests():
    """Run all Chain-of-Thought tests"""
    print("🧪 Running Chain-of-Thought Tests")
    print("=" * 50)

    try:
        test_chain_of_thought_template_registration()
        test_technical_templates_coverage()
        test_behavioral_templates_coverage()
        test_case_study_template()
        test_reverse_template()
        test_reasoning_chain_structure()
        test_progressive_complexity_in_steps()
        test_metadata_reasoning_steps()
        test_complexity_building_metadata()
        test_behavioral_reasoning_quality()
        test_case_study_reasoning_structure()
        test_reverse_interview_reasoning()
        test_template_formatting_with_reasoning()
        test_template_uniqueness_and_differentiation()

        print("=" * 50)
        print("🎉 All Chain-of-Thought tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
