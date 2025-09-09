"""
Simple test suite for prompt template infrastructure.
Tests PromptTemplate and PromptLibrary functionality without pytest dependencies.
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
    from ai.prompts import PromptLibrary, PromptTemplate, prompt_library
    from models.enums import ExperienceLevel, InterviewType, PromptTechnique
    print("✅ Prompt template imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def test_prompt_template_creation():
    """Test basic PromptTemplate creation and initialization"""
    print("Testing PromptTemplate creation...")

    template = PromptTemplate(
        name="test_template",
        technique=PromptTechnique.ZERO_SHOT,
        interview_type=InterviewType.TECHNICAL,
        experience_level=ExperienceLevel.SENIOR,
        template="Generate {question_count} questions for {job_description}"
    )

    assert template.name == "test_template"
    assert template.technique == PromptTechnique.ZERO_SHOT
    assert template.interview_type == InterviewType.TECHNICAL
    assert template.experience_level == ExperienceLevel.SENIOR
    assert "question_count" in template.variables
    assert "job_description" in template.variables
    assert len(template.variables) == 2

    print("✅ PromptTemplate creation test passed")


def test_variable_extraction():
    """Test automatic variable extraction from template"""
    print("Testing variable extraction...")

    template = PromptTemplate(
        name="complex_template",
        technique=PromptTechnique.FEW_SHOT,
        interview_type=InterviewType.BEHAVIORAL,
        experience_level=None,
        template="Create {question_count} {interview_type} questions for a {experience_level} {role_title} at {company_name}"
    )

    expected_vars = {"question_count", "interview_type",
                     "experience_level", "role_title", "company_name"}
    actual_vars = set(template.variables)

    assert actual_vars == expected_vars
    assert len(template.variables) == 5

    print("✅ Variable extraction test passed")


def test_template_formatting():
    """Test template formatting with variable substitution"""
    print("Testing template formatting...")

    template = PromptTemplate(
        name="format_test",
        technique=PromptTechnique.CHAIN_OF_THOUGHT,
        interview_type=InterviewType.TECHNICAL,
        experience_level=ExperienceLevel.MID,
        template="Generate {question_count} {interview_type} questions for {job_description}"
    )

    # Test successful formatting
    formatted = template.format(
        question_count="5",
        interview_type="technical",
        job_description="Python developer role"
    )

    expected = "Generate 5 technical questions for Python developer role"
    assert formatted == expected

    # Test missing variable error
    try:
        template.format(question_count="5")  # Missing other variables
        assert False, "Should have raised ValueError for missing variables"
    except ValueError as e:
        assert "Missing required variables" in str(e)

    print("✅ Template formatting test passed")


def test_variable_validation():
    """Test variable validation functionality"""
    print("Testing variable validation...")

    template = PromptTemplate(
        name="validation_test",
        technique=PromptTechnique.ROLE_BASED,
        interview_type=InterviewType.CASE_STUDY,
        experience_level=ExperienceLevel.JUNIOR,
        template="Create questions for {role} with {skills}"
    )

    # Test valid variables
    valid_vars = {"role": "developer", "skills": "Python"}
    assert template.validate_variables(valid_vars) == True

    # Test missing variables
    invalid_vars = {"role": "developer"}  # Missing 'skills'
    assert template.validate_variables(invalid_vars) == False

    # Test extra variables (should still be valid)
    extra_vars = {"role": "developer", "skills": "Python", "extra": "value"}
    assert template.validate_variables(extra_vars) == True

    print("✅ Variable validation test passed")


def test_sample_variables():
    """Test sample variable generation"""
    print("Testing sample variables...")

    template = PromptTemplate(
        name="sample_test",
        technique=PromptTechnique.STRUCTURED_OUTPUT,
        interview_type=InterviewType.REVERSE,
        experience_level=ExperienceLevel.LEAD,
        template="Questions about {company_name} for {role_title} with {years_experience} experience"
    )

    samples = template.get_sample_variables()

    # Check that all variables have sample values
    for var in template.variables:
        assert var in samples
        assert samples[var] is not None
        assert len(samples[var]) > 0

    # Check specific sample values
    assert samples["company_name"] == "TechCorp"
    assert samples["role_title"] == "Senior Software Engineer"
    assert samples["years_experience"] == "5-7"

    print("✅ Sample variables test passed")


def test_prompt_library_initialization():
    """Test PromptLibrary initialization"""
    print("Testing PromptLibrary initialization...")

    library = PromptLibrary()

    assert isinstance(library.templates, dict)
    assert len(library.templates) == 0  # Should be empty initially

    print("✅ PromptLibrary initialization test passed")


def test_template_registration():
    """Test template registration in library"""
    print("Testing template registration...")

    library = PromptLibrary()

    template = PromptTemplate(
        name="registration_test",
        technique=PromptTechnique.FEW_SHOT,
        interview_type=InterviewType.TECHNICAL,
        experience_level=ExperienceLevel.SENIOR,
        template="Test template for {job_description}"
    )

    library.register_template(template)

    assert len(library.templates) == 1

    # Test retrieval
    retrieved = library.get_template(
        PromptTechnique.FEW_SHOT,
        InterviewType.TECHNICAL,
        ExperienceLevel.SENIOR
    )

    assert retrieved is not None
    assert retrieved.name == "registration_test"
    assert retrieved.template == "Test template for {job_description}"

    print("✅ Template registration test passed")


def test_template_retrieval():
    """Test template retrieval with fallbacks"""
    print("Testing template retrieval...")

    library = PromptLibrary()

    # Register specific template
    specific_template = PromptTemplate(
        name="specific",
        technique=PromptTechnique.ZERO_SHOT,
        interview_type=InterviewType.BEHAVIORAL,
        experience_level=ExperienceLevel.MID,
        template="Specific template"
    )

    # Register generic template (no experience level)
    generic_template = PromptTemplate(
        name="generic",
        technique=PromptTechnique.ZERO_SHOT,
        interview_type=InterviewType.BEHAVIORAL,
        experience_level=None,
        template="Generic template"
    )

    library.register_template(specific_template)
    library.register_template(generic_template)

    # Test exact match
    exact_match = library.get_template(
        PromptTechnique.ZERO_SHOT,
        InterviewType.BEHAVIORAL,
        ExperienceLevel.MID
    )
    assert exact_match.name == "specific"

    # Test fallback to generic
    fallback = library.get_template(
        PromptTechnique.ZERO_SHOT,
        InterviewType.BEHAVIORAL,
        ExperienceLevel.JUNIOR  # Not registered, should fallback
    )
    assert fallback.name == "generic"

    # Test no match
    no_match = library.get_template(
        PromptTechnique.CHAIN_OF_THOUGHT,  # Different technique
        InterviewType.BEHAVIORAL,
        ExperienceLevel.MID
    )
    assert no_match is None

    print("✅ Template retrieval test passed")


def test_template_listing():
    """Test template listing with filters"""
    print("Testing template listing...")

    library = PromptLibrary()

    # Register multiple templates
    templates = [
        PromptTemplate("t1", PromptTechnique.FEW_SHOT,
                       InterviewType.TECHNICAL, ExperienceLevel.JUNIOR, "template1"),
        PromptTemplate("t2", PromptTechnique.FEW_SHOT,
                       InterviewType.BEHAVIORAL, ExperienceLevel.SENIOR, "template2"),
        PromptTemplate("t3", PromptTechnique.ZERO_SHOT,
                       InterviewType.TECHNICAL, ExperienceLevel.MID, "template3"),
    ]

    for template in templates:
        library.register_template(template)

    # Test list all
    all_templates = library.list_templates()
    assert len(all_templates) == 3

    # Test filter by technique
    few_shot_templates = library.list_templates(
        technique=PromptTechnique.FEW_SHOT)
    assert len(few_shot_templates) == 2

    # Test filter by interview type
    technical_templates = library.list_templates(
        interview_type=InterviewType.TECHNICAL)
    assert len(technical_templates) == 2

    # Test filter by both
    specific_templates = library.list_templates(
        technique=PromptTechnique.FEW_SHOT,
        interview_type=InterviewType.TECHNICAL
    )
    assert len(specific_templates) == 1
    assert specific_templates[0].name == "t1"

    print("✅ Template listing test passed")


def test_available_techniques():
    """Test getting available techniques for interview type"""
    print("Testing available techniques...")

    library = PromptLibrary()

    # Register templates for different combinations
    library.register_template(PromptTemplate(
        "t1", PromptTechnique.FEW_SHOT, InterviewType.TECHNICAL, None, "template1"))
    library.register_template(PromptTemplate(
        "t2", PromptTechnique.ZERO_SHOT, InterviewType.TECHNICAL, None, "template2"))
    library.register_template(PromptTemplate(
        "t3", PromptTechnique.FEW_SHOT, InterviewType.BEHAVIORAL, None, "template3"))

    # Test technical interview techniques
    technical_techniques = library.get_available_techniques(
        InterviewType.TECHNICAL)
    assert len(technical_techniques) == 2
    assert PromptTechnique.FEW_SHOT in technical_techniques
    assert PromptTechnique.ZERO_SHOT in technical_techniques

    # Test behavioral interview techniques
    behavioral_techniques = library.get_available_techniques(
        InterviewType.BEHAVIORAL)
    assert len(behavioral_techniques) == 1
    assert PromptTechnique.FEW_SHOT in behavioral_techniques

    # Test interview type with no templates
    case_study_techniques = library.get_available_techniques(
        InterviewType.CASE_STUDY)
    assert len(case_study_techniques) == 0

    print("✅ Available techniques test passed")


def test_template_info():
    """Test template information gathering"""
    print("Testing template information...")

    library = PromptLibrary()

    # Register diverse templates
    templates = [
        PromptTemplate("t1", PromptTechnique.FEW_SHOT,
                       InterviewType.TECHNICAL, ExperienceLevel.JUNIOR, "template1"),
        PromptTemplate("t2", PromptTechnique.FEW_SHOT,
                       InterviewType.BEHAVIORAL, ExperienceLevel.SENIOR, "template2"),
        PromptTemplate("t3", PromptTechnique.ZERO_SHOT,
                       InterviewType.TECHNICAL, ExperienceLevel.MID, "template3"),
        PromptTemplate("t4", PromptTechnique.CHAIN_OF_THOUGHT,
                       InterviewType.CASE_STUDY, None, "template4"),
    ]

    for template in templates:
        library.register_template(template)

    info = library.get_template_info()

    assert info["total_templates"] == 4
    assert info["techniques"]["Few-shot Learning"] == 2
    assert info["techniques"]["Zero-shot"] == 1
    assert info["techniques"]["Chain-of-Thought"] == 1
    assert info["interview_types"]["Technical Questions"] == 2
    assert info["interview_types"]["Behavioral Questions"] == 1
    assert info["interview_types"]["Case Studies"] == 1
    assert len(info["template_keys"]) == 4

    print("✅ Template information test passed")


def test_coverage_validation():
    """Test template coverage validation"""
    print("Testing coverage validation...")

    library = PromptLibrary()

    # Register only a few templates (incomplete coverage)
    library.register_template(PromptTemplate(
        "t1", PromptTechnique.FEW_SHOT, InterviewType.TECHNICAL, None, "template1"))
    library.register_template(PromptTemplate(
        "t2", PromptTechnique.ZERO_SHOT, InterviewType.BEHAVIORAL, None, "template2"))

    coverage = library.validate_template_coverage()

    # Should have some coverage but not 100%
    assert coverage["total_combinations"] > 0
    assert coverage["covered_combinations"] == 2
    assert coverage["coverage_percent"] < 100
    assert len(coverage["missing_combinations"]) > 0

    # Check specific missing combinations
    missing = coverage["missing_combinations"]
    assert "Few-shot Learning_Behavioral Questions" in missing
    assert "Zero-shot_Technical Questions" in missing

    print("✅ Coverage validation test passed")


def test_global_library_instance():
    """Test global prompt library instance"""
    print("Testing global library instance...")

    # Test that global instance exists and is PromptLibrary
    assert prompt_library is not None
    assert isinstance(prompt_library, PromptLibrary)

    # Test that it's the same instance
    from ai.prompts import prompt_library as lib2
    assert prompt_library is lib2

    print("✅ Global library instance test passed")


def run_all_tests():
    """Run all prompt template tests"""
    print("🧪 Running Prompt Template Infrastructure Tests")
    print("=" * 60)

    try:
        test_prompt_template_creation()
        test_variable_extraction()
        test_template_formatting()
        test_variable_validation()
        test_sample_variables()
        test_prompt_library_initialization()
        test_template_registration()
        test_template_retrieval()
        test_template_listing()
        test_available_techniques()
        test_template_info()
        test_coverage_validation()
        test_global_library_instance()

        print("=" * 60)
        print("🎉 All Prompt Template Infrastructure tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
