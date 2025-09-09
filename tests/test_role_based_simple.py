"""
Simple test suite for Role-Based prompt implementation.
Tests Role-Based templates and persona consistency in generated questions.
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
    from ai.role_based import RoleBasedPrompts
    from models.enums import InterviewType, PromptTechnique
    print("✅ Role-Based imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def test_role_based_template_registration():
    """Test that Role-Based templates are properly registered"""
    print("Testing Role-Based template registration...")

    # Check that templates were registered during import
    role_based_templates = RoleBasedPrompts.get_all_role_based_templates()

    print(f"Found {len(role_based_templates)} Role-Based templates:")
    for template in role_based_templates:
        print(f"  - {template.name} ({template.interview_type.value})")

    # Should have templates for all personas and interview types
    assert len(role_based_templates) > 0, "No Role-Based templates found"

    # Check that we have templates for each persona
    personas_found = set()
    for template in role_based_templates:
        for persona in ["strict", "friendly", "neutral"]:
            if persona in template.name.lower():
                personas_found.add(persona)

    assert len(
        personas_found) > 0, f"No persona templates found. Templates: {[t.name for t in role_based_templates]}"

    print("✅ Role-Based template registration test passed")


def test_persona_definitions():
    """Test that all personas are properly defined"""
    print("Testing persona definitions...")

    personas = RoleBasedPrompts.get_available_personas()

    # Should have the three main personas
    expected_personas = ["strict", "friendly", "neutral"]
    assert set(personas) == set(expected_personas)

    # Each persona should have complete information
    for persona in personas:
        info = RoleBasedPrompts.get_persona_info(persona)

        assert "name" in info
        assert "description" in info
        assert "tone" in info
        assert "focus" in info

        # Check that all fields have content
        for key, value in info.items():
            assert isinstance(value, str)
            assert len(value) > 0

    print("✅ Persona definitions test passed")


def test_company_type_definitions():
    """Test that company types are properly defined"""
    print("Testing company type definitions...")

    company_types = RoleBasedPrompts.get_company_types()

    # Should have multiple company types
    expected_types = ["startup", "enterprise",
                      "tech_giant", "consulting", "finance"]
    assert set(company_types) == set(expected_types)

    # Each company type should have complete information
    for company_type in company_types:
        info = RoleBasedPrompts.get_company_info(company_type)

        assert "culture" in info
        assert "values" in info
        assert "interview_style" in info

        # Check that all fields have content
        for key, value in info.items():
            assert isinstance(value, str)
            assert len(value) > 0

    print("✅ Company type definitions test passed")


def test_persona_template_coverage():
    """Test that all personas have templates for all interview types"""
    print("Testing persona template coverage...")

    personas = RoleBasedPrompts.get_available_personas()
    interview_types = [InterviewType.TECHNICAL, InterviewType.BEHAVIORAL,
                       InterviewType.CASE_STUDY, InterviewType.REVERSE]

    for persona in personas:
        for interview_type in interview_types:
            template = RoleBasedPrompts.get_persona_template(
                persona, interview_type)
            assert template is not None, f"Missing template for {persona} {interview_type.value}"

            # Check that persona is in template name
            assert persona in template.name.lower()

            # Check that template has correct interview type
            assert template.interview_type == interview_type

            # Check that template uses ROLE_BASED technique
            assert template.technique == PromptTechnique.ROLE_BASED

    print("✅ Persona template coverage test passed")


def test_persona_consistency_in_templates():
    """Test that persona characteristics are consistent in templates"""
    print("Testing persona consistency in templates...")

    personas = ["strict", "friendly", "neutral"]

    for persona in personas:
        persona_info = RoleBasedPrompts.get_persona_info(persona)

        # Get a technical template for this persona
        template = RoleBasedPrompts.get_persona_template(
            persona, InterviewType.TECHNICAL)

        # Format template to check content
        sample_vars = template.get_sample_variables()
        sample_vars.update({
            "company_type": "startup",
            "experience_level": "Mid-level"
        })
        formatted = template.format(**sample_vars)

        # Check that persona characteristics appear in the template
        assert persona_info["name"] in formatted
        assert persona_info["tone"] in formatted

        # Check that persona-specific guidance is included
        if persona == "strict":
            assert "precise" in formatted.lower() or "detailed" in formatted.lower()
        elif persona == "friendly":
            assert "encouraging" in formatted.lower() or "supportive" in formatted.lower()
        elif persona == "neutral":
            assert "balanced" in formatted.lower() or "objective" in formatted.lower()

    print("✅ Persona consistency test passed")


def test_company_type_integration():
    """Test that company type context is integrated into templates"""
    print("Testing company type integration...")

    template = RoleBasedPrompts.get_persona_template(
        "neutral", InterviewType.TECHNICAL)

    # Test with different company types
    company_types = ["startup", "enterprise", "tech_giant"]

    for company_type in company_types:
        sample_vars = template.get_sample_variables()
        sample_vars["company_type"] = company_type

        formatted = template.format(**sample_vars)

        # Should contain company type reference
        assert company_type in formatted

        # Should contain company context guidance
        assert "company" in formatted.lower()
        assert "culture" in formatted.lower() or "context" in formatted.lower()

    print("✅ Company type integration test passed")


def test_template_metadata():
    """Test that Role-Based templates have appropriate metadata"""
    print("Testing template metadata...")

    template = RoleBasedPrompts.get_persona_template(
        "strict", InterviewType.BEHAVIORAL)

    # Should have persona-specific metadata
    assert "persona" in template.metadata
    assert template.metadata["persona"] == "strict"

    assert "interviewer_style" in template.metadata
    assert "focus_areas" in template.metadata
    assert "personality_driven" in template.metadata

    # Focus areas should be a list
    focus_areas = template.metadata["focus_areas"]
    assert isinstance(focus_areas, list)
    assert len(focus_areas) > 0

    print("✅ Template metadata test passed")


def test_persona_guidance_differentiation():
    """Test that different personas have different guidance"""
    print("Testing persona guidance differentiation...")

    # Test guidance differentiation through formatted templates
    sample_vars = {
        "question_count": "3",
        "job_description": "Software Engineer",
        "experience_level": "Mid-level",
        "company_type": "startup"
    }

    # Get formatted templates for different personas
    strict_template = RoleBasedPrompts.get_persona_template(
        "strict", InterviewType.TECHNICAL)
    friendly_template = RoleBasedPrompts.get_persona_template(
        "friendly", InterviewType.TECHNICAL)
    neutral_template = RoleBasedPrompts.get_persona_template(
        "neutral", InterviewType.TECHNICAL)

    strict_content = strict_template.format(**sample_vars)
    friendly_content = friendly_template.format(**sample_vars)
    neutral_content = neutral_template.format(**sample_vars)

    # Should be different content
    assert strict_content != friendly_content
    assert friendly_content != neutral_content
    assert strict_content != neutral_content

    # Should contain persona-specific keywords in the formatted content
    assert "strict" in strict_content.lower() or "precise" in strict_content.lower(
    ) or "detailed" in strict_content.lower()
    assert "friendly" in friendly_content.lower() or "encouraging" in friendly_content.lower(
    ) or "supportive" in friendly_content.lower()
    assert "neutral" in neutral_content.lower() or "balanced" in neutral_content.lower(
    ) or "objective" in neutral_content.lower()

    print("✅ Persona guidance differentiation test passed")


def test_persona_company_compatibility():
    """Test persona and company type compatibility recommendations"""
    print("Testing persona company compatibility...")

    compatibility = RoleBasedPrompts.get_persona_company_compatibility()

    # Should have recommendations for all personas
    personas = RoleBasedPrompts.get_available_personas()
    for persona in personas:
        assert persona in compatibility
        assert isinstance(compatibility[persona], list)
        assert len(compatibility[persona]) > 0

    # Test company-specific recommendations
    startup_personas = RoleBasedPrompts.recommend_persona_for_company(
        "startup")
    assert isinstance(startup_personas, list)
    assert len(startup_personas) > 0

    # Should include friendly for startup (typically)
    assert "friendly" in startup_personas or "neutral" in startup_personas

    print("✅ Persona company compatibility test passed")


def test_error_handling():
    """Test error handling for invalid inputs"""
    print("Testing error handling...")

    # Test invalid persona
    try:
        RoleBasedPrompts.get_persona_info("invalid_persona")
        assert False, "Should have raised ValueError for invalid persona"
    except ValueError as e:
        assert "Unknown persona" in str(e)

    # Test invalid company type
    try:
        RoleBasedPrompts.get_company_info("invalid_company")
        assert False, "Should have raised ValueError for invalid company"
    except ValueError as e:
        assert "Unknown company type" in str(e)

    # Test invalid persona in template retrieval
    try:
        RoleBasedPrompts.get_persona_template(
            "invalid", InterviewType.TECHNICAL)
        assert False, "Should have raised ValueError for invalid persona"
    except ValueError as e:
        assert "Unknown persona" in str(e)

    print("✅ Error handling test passed")


def test_template_formatting():
    """Test that Role-Based templates format correctly with all variables"""
    print("Testing template formatting...")

    template = RoleBasedPrompts.get_persona_template(
        "friendly", InterviewType.CASE_STUDY)

    # Test with complete variable set
    variables = {
        "question_count": "4",
        "job_description": "Senior Software Engineer with team leadership responsibilities",
        "experience_level": "Senior",
        "company_type": "tech_giant"
    }

    formatted = template.format(**variables)

    # Should contain all variable values
    assert "4" in formatted
    assert "Senior Software Engineer" in formatted
    assert "Senior" in formatted
    assert "tech_giant" in formatted

    # Should not have unresolved variables
    assert "{" not in formatted or "}" not in formatted

    # Should contain persona-specific content
    assert "friendly" in formatted.lower() or "encouraging" in formatted.lower()

    print("✅ Template formatting test passed")


def test_reverse_interview_persona_awareness():
    """Test that reverse interview templates are persona-aware"""
    print("Testing reverse interview persona awareness...")

    template = RoleBasedPrompts.get_persona_template(
        "strict", InterviewType.REVERSE)

    sample_vars = template.get_sample_variables()
    sample_vars.update({
        "company_type": "finance",
        "experience_level": "Senior"
    })

    formatted = template.format(**sample_vars)

    # Should contain guidance about facing a strict interviewer
    assert "strict" in formatted.lower()

    # Should contain advice specific to strict interviewers
    assert "detailed" in formatted.lower(
    ) or "thorough" in formatted.lower() or "precise" in formatted.lower()

    # Should mention the interviewer's characteristics
    assert "interviewer" in formatted.lower()

    print("✅ Reverse interview persona awareness test passed")


def test_template_uniqueness():
    """Test that Role-Based templates are unique for each persona"""
    print("Testing template uniqueness...")

    # Get all Role-Based templates
    role_based_templates = prompt_library.list_templates(
        technique=PromptTechnique.ROLE_BASED)

    # Check unique names
    names = [t.name for t in role_based_templates]
    assert len(names) == len(set(names)), "Duplicate template names found"

    # Check that different personas have different content
    strict_template = RoleBasedPrompts.get_persona_template(
        "strict", InterviewType.TECHNICAL)
    friendly_template = RoleBasedPrompts.get_persona_template(
        "friendly", InterviewType.TECHNICAL)

    sample_vars = {"question_count": "5", "job_description": "Developer",
                   "experience_level": "Mid", "company_type": "startup"}

    strict_content = strict_template.format(**sample_vars)
    friendly_content = friendly_template.format(**sample_vars)

    # Should have different content
    assert strict_content != friendly_content
    assert len(strict_content) > 100  # Should have substantial content
    assert len(friendly_content) > 100

    print("✅ Template uniqueness test passed")


def test_all_interview_types_coverage():
    """Test that all interview types are covered for each persona"""
    print("Testing all interview types coverage...")

    personas = RoleBasedPrompts.get_available_personas()
    interview_types = [InterviewType.TECHNICAL, InterviewType.BEHAVIORAL,
                       InterviewType.CASE_STUDY, InterviewType.REVERSE]

    for persona in personas:
        for interview_type in interview_types:
            template = RoleBasedPrompts.get_persona_template(
                persona, interview_type)

            assert template is not None, f"Missing {persona} template for {interview_type.value}"

            # Verify template content is appropriate for interview type
            sample_vars = template.get_sample_variables()
            formatted = template.format(**sample_vars)

            if interview_type == InterviewType.TECHNICAL:
                assert "technical" in formatted.lower()
            elif interview_type == InterviewType.BEHAVIORAL:
                assert "behavioral" in formatted.lower()
            elif interview_type == InterviewType.CASE_STUDY:
                assert "case" in formatted.lower() or "scenario" in formatted.lower()
            elif interview_type == InterviewType.REVERSE:
                assert "questions" in formatted.lower() and "ask" in formatted.lower()

    print("✅ All interview types coverage test passed")


def run_all_tests():
    """Run all Role-Based tests"""
    print("🧪 Running Role-Based Tests")
    print("=" * 45)

    try:
        test_role_based_template_registration()
        test_persona_definitions()
        test_company_type_definitions()
        test_persona_template_coverage()
        test_persona_consistency_in_templates()
        test_company_type_integration()
        test_template_metadata()
        test_persona_guidance_differentiation()
        test_persona_company_compatibility()
        test_error_handling()
        test_template_formatting()
        test_reverse_interview_persona_awareness()
        test_template_uniqueness()
        test_all_interview_types_coverage()

        print("=" * 45)
        print("🎉 All Role-Based tests passed!")
        return True

    except Exception as e:  # pylint: disable=broad-except
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
