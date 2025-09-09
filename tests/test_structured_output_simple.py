"""
Simple test suite for Structured Output prompt implementation.
Tests JSON-formatted responses with question metadata and validation.
"""
import json
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
    from ai.structured_output import StructuredOutputPrompts
    from models.enums import ExperienceLevel, InterviewType, PromptTechnique
    print("✅ Structured Output imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def test_structured_output_template_registration():
    """Test that Structured Output templates are properly registered"""
    print("Testing Structured Output template registration...")

    # Get all structured output templates
    structured_templates = prompt_library.list_templates(
        technique=PromptTechnique.STRUCTURED_OUTPUT)

    print(f"Found {len(structured_templates)} Structured Output templates:")
    for template in structured_templates:
        print(f"  - {template.name} ({template.interview_type.value})")

    # Should have templates for all interview types
    assert len(structured_templates) > 0, "No Structured Output templates found"

    # Check coverage for different interview types
    interview_types_found = set()
    for template in structured_templates:
        interview_types_found.add(template.interview_type)

    expected_types = {InterviewType.TECHNICAL, InterviewType.BEHAVIORAL,
                      InterviewType.CASE_STUDY, InterviewType.REVERSE}
    assert interview_types_found == expected_types, f"Missing interview types. Found: {interview_types_found}"

    print("✅ Structured Output template registration test passed")


def test_json_schema_definition():
    """Test that JSON schema is properly defined"""
    print("Testing JSON schema definition...")

    schema = StructuredOutputPrompts.get_json_schema()

    # Should have required top-level properties
    assert "properties" in schema
    assert "required" in schema

    required_props = schema["required"]
    assert "questions" in required_props
    assert "recommendations" in required_props
    assert "metadata" in required_props

    # Check questions schema
    questions_schema = schema["properties"]["questions"]
    assert questions_schema["type"] == "array"
    assert "items" in questions_schema

    question_props = questions_schema["items"]["properties"]
    assert "id" in question_props
    assert "question" in question_props
    assert "difficulty" in question_props
    assert "category" in question_props
    assert "estimated_time_minutes" in question_props

    print("✅ JSON schema definition test passed")


def test_sample_response_creation():
    """Test creation of sample structured responses"""
    print("Testing sample response creation...")

    # Create sample with default count
    sample = StructuredOutputPrompts.create_sample_response()

    # Should have all required keys
    assert "questions" in sample
    assert "recommendations" in sample
    assert "metadata" in sample

    # Questions should be properly structured
    questions = sample["questions"]
    assert isinstance(questions, list)
    assert len(questions) == 3  # Default count

    for i, question in enumerate(questions):
        assert "id" in question
        assert "question" in question
        assert "difficulty" in question
        assert "category" in question
        assert "estimated_time_minutes" in question
        assert question["id"] == i + 1

    # Recommendations should be structured
    recommendations = sample["recommendations"]
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

    for rec in recommendations:
        assert "category" in rec
        assert "recommendation" in rec
        assert "priority" in rec

    # Metadata should be structured
    metadata = sample["metadata"]
    assert "total_questions" in metadata
    assert "estimated_total_time" in metadata
    assert metadata["total_questions"] == 3

    print("✅ Sample response creation test passed")


def test_json_validation_success():
    """Test successful JSON validation"""
    print("Testing JSON validation success...")

    # Create valid sample response
    sample = StructuredOutputPrompts.create_sample_response(2)
    json_string = json.dumps(sample)

    # Should validate successfully
    validated = StructuredOutputPrompts.validate_json_response(json_string)

    assert validated == sample
    assert len(validated["questions"]) == 2
    assert validated["metadata"]["total_questions"] == 2

    print("✅ JSON validation success test passed")


def test_json_validation_failures():
    """Test JSON validation error handling"""
    print("Testing JSON validation failures...")

    # Test invalid JSON
    try:
        StructuredOutputPrompts.validate_json_response("invalid json")
        assert False, "Should have raised ValueError for invalid JSON"
    except ValueError as e:
        assert "Invalid JSON" in str(e)

    # Test missing required keys
    try:
        StructuredOutputPrompts.validate_json_response('{"questions": []}')
        assert False, "Should have raised ValueError for missing keys"
    except ValueError as e:
        assert "Missing required key" in str(e)

    # Test empty questions list
    try:
        invalid_response = {
            "questions": [],
            "recommendations": [],
            "metadata": {"total_questions": 0, "estimated_total_time": 0}
        }
        StructuredOutputPrompts.validate_json_response(
            json.dumps(invalid_response))
        assert False, "Should have raised ValueError for empty questions"
    except ValueError as e:
        assert "non-empty list" in str(e)

    # Test invalid difficulty
    try:
        invalid_response = {
            "questions": [{
                "id": 1,
                "question": "Test?",
                "difficulty": "invalid",
                "category": "test",
                "estimated_time_minutes": 5
            }],
            "recommendations": [{"category": "test", "recommendation": "test", "priority": "high"}],
            "metadata": {"total_questions": 1, "estimated_total_time": 5}
        }
        StructuredOutputPrompts.validate_json_response(
            json.dumps(invalid_response))
        assert False, "Should have raised ValueError for invalid difficulty"
    except ValueError as e:
        assert "Invalid difficulty" in str(e)

    print("✅ JSON validation failures test passed")


def test_technical_template_coverage():
    """Test that technical templates cover all experience levels"""
    print("Testing technical template coverage...")

    experience_levels = [ExperienceLevel.JUNIOR, ExperienceLevel.MID,
                         ExperienceLevel.SENIOR, ExperienceLevel.LEAD]

    for level in experience_levels:
        template = prompt_library.get_template(
            PromptTechnique.STRUCTURED_OUTPUT,
            InterviewType.TECHNICAL,
            level
        )

        assert template is not None, f"Missing technical template for {level.value}"
        assert template.technique == PromptTechnique.STRUCTURED_OUTPUT
        assert template.interview_type == InterviewType.TECHNICAL
        assert template.experience_level == level

        # Check that template contains JSON format requirements
        assert "JSON" in template.template
        assert "valid json" in template.template.lower()

    print("✅ Technical template coverage test passed")


def test_behavioral_template_coverage():
    """Test that behavioral templates cover all experience levels"""
    print("Testing behavioral template coverage...")

    experience_levels = [ExperienceLevel.JUNIOR, ExperienceLevel.MID,
                         ExperienceLevel.SENIOR, ExperienceLevel.LEAD]

    for level in experience_levels:
        template = prompt_library.get_template(
            PromptTechnique.STRUCTURED_OUTPUT,
            InterviewType.BEHAVIORAL,
            level
        )

        assert template is not None, f"Missing behavioral template for {level.value}"
        assert template.technique == PromptTechnique.STRUCTURED_OUTPUT
        assert template.interview_type == InterviewType.BEHAVIORAL
        assert template.experience_level == level

        # Check that template contains JSON format requirements
        assert "JSON" in template.template
        assert "valid json" in template.template.lower()
        assert "behavioral" in template.template.lower()

    print("✅ Behavioral template coverage test passed")


def test_template_json_format_consistency():
    """Test that all templates have consistent JSON format requirements"""
    print("Testing template JSON format consistency...")

    structured_templates = prompt_library.list_templates(
        technique=PromptTechnique.STRUCTURED_OUTPUT)

    for template in structured_templates:
        # Should contain JSON format instructions
        assert "JSON" in template.template
        assert "valid json" in template.template.lower()
        assert "valid json only" in template.template.lower()

        # Should contain example JSON structure
        assert "questions" in template.template
        assert "recommendations" in template.template
        assert "metadata" in template.template

        # Should have structured output metadata
        assert template.metadata.get("json_validated") is True
        assert template.metadata.get("structured_parsing") is True
        assert template.metadata.get("metadata_rich") is True

    print("✅ Template JSON format consistency test passed")


def test_template_formatting_with_variables():
    """Test that Structured Output templates format correctly with variables"""
    print("Testing template formatting with variables...")

    template = prompt_library.get_template(
        PromptTechnique.STRUCTURED_OUTPUT,
        InterviewType.TECHNICAL,
        ExperienceLevel.MID
    )

    # Test with complete variable set
    variables = {
        "question_count": "3",
        "job_description": "Senior Python Developer with Django experience",
        "experience_level": "Mid-level"
    }

    formatted = template.format(**variables)

    # Should contain all variable values
    assert "3" in formatted
    assert "Senior Python Developer" in formatted
    assert "Mid-level" in formatted

    # Should not have unresolved variables
    assert "{question_count}" not in formatted
    assert "{job_description}" not in formatted
    assert "{experience_level}" not in formatted

    # Should contain JSON format requirements
    assert "JSON" in formatted
    assert "valid json" in formatted.lower()

    print("✅ Template formatting with variables test passed")


def test_difficulty_distribution_by_level():
    """Test that difficulty distribution varies by experience level"""
    print("Testing difficulty distribution by experience level...")

    # Check junior level - should be mostly easy
    junior_template = prompt_library.get_template(
        PromptTechnique.STRUCTURED_OUTPUT,
        InterviewType.TECHNICAL,
        ExperienceLevel.JUNIOR
    )
    assert "easy" in junior_template.template
    assert junior_template.metadata["difficulty_focus"] == "easy_medium"

    # Check senior level - should be mostly hard
    senior_template = prompt_library.get_template(
        PromptTechnique.STRUCTURED_OUTPUT,
        InterviewType.TECHNICAL,
        ExperienceLevel.SENIOR
    )
    assert "hard" in senior_template.template
    assert senior_template.metadata["difficulty_focus"] == "hard"

    # Check lead level - should be expert level
    lead_template = prompt_library.get_template(
        PromptTechnique.STRUCTURED_OUTPUT,
        InterviewType.TECHNICAL,
        ExperienceLevel.LEAD
    )
    assert lead_template.metadata["difficulty_focus"] == "expert"

    print("✅ Difficulty distribution by level test passed")


def test_case_study_and_reverse_templates():
    """Test that case study and reverse templates exist and are properly structured"""
    print("Testing case study and reverse templates...")

    # Test case study template
    case_study_template = prompt_library.get_template(
        PromptTechnique.STRUCTURED_OUTPUT,
        InterviewType.CASE_STUDY
    )

    assert case_study_template is not None
    assert case_study_template.interview_type == InterviewType.CASE_STUDY
    assert case_study_template.experience_level is None  # Generic
    assert "case study" in case_study_template.template.lower()
    assert case_study_template.metadata["difficulty_focus"] == "adaptive"

    # Test reverse template
    reverse_template = prompt_library.get_template(
        PromptTechnique.STRUCTURED_OUTPUT,
        InterviewType.REVERSE
    )

    assert reverse_template is not None
    assert reverse_template.interview_type == InterviewType.REVERSE
    assert reverse_template.experience_level is None  # Generic
    assert "questions" in reverse_template.template.lower()
    assert reverse_template.metadata["difficulty_focus"] == "professional"

    print("✅ Case study and reverse templates test passed")


def test_metadata_richness():
    """Test that templates include rich metadata for structured output"""
    print("Testing metadata richness...")

    template = prompt_library.get_template(
        PromptTechnique.STRUCTURED_OUTPUT,
        InterviewType.BEHAVIORAL,
        ExperienceLevel.SENIOR
    )

    # Should have structured output specific metadata
    metadata = template.metadata
    assert metadata["json_validated"] is True
    assert metadata["structured_parsing"] is True
    assert metadata["metadata_rich"] is True

    # Should have difficulty focus
    assert "difficulty_focus" in metadata
    assert metadata["difficulty_focus"] in ["easy", "medium",
                                            "hard", "expert", "easy_medium", "medium_hard"]

    print("✅ Metadata richness test passed")


def test_json_schema_validation_completeness():
    """Test that JSON schema covers all required validation cases"""
    print("Testing JSON schema validation completeness...")

    schema = StructuredOutputPrompts.get_json_schema()

    # Test question validation requirements
    question_schema = schema["properties"]["questions"]["items"]
    question_required = question_schema["required"]

    assert "id" in question_required
    assert "question" in question_required
    assert "difficulty" in question_required
    assert "category" in question_required
    assert "estimated_time_minutes" in question_required

    # Test difficulty enum
    difficulty_enum = question_schema["properties"]["difficulty"]["enum"]
    assert set(difficulty_enum) == {"easy", "medium", "hard"}

    # Test recommendation validation requirements
    rec_schema = schema["properties"]["recommendations"]["items"]
    rec_required = rec_schema["required"]

    assert "category" in rec_required
    assert "recommendation" in rec_required
    assert "priority" in rec_required

    # Test priority enum
    priority_enum = rec_schema["properties"]["priority"]["enum"]
    assert set(priority_enum) == {"high", "medium", "low"}

    print("✅ JSON schema validation completeness test passed")


def test_template_variable_extraction():
    """Test that Structured Output templates correctly extract variables"""
    print("Testing template variable extraction...")

    template = prompt_library.get_template(
        PromptTechnique.STRUCTURED_OUTPUT,
        InterviewType.TECHNICAL,
        ExperienceLevel.JUNIOR
    )

    # Should extract expected variables
    variables = template.variables
    expected_vars = {"question_count", "job_description", "experience_level"}

    assert expected_vars.issubset(
        set(variables)), f"Missing variables. Found: {variables}"

    # Should provide sample variables
    sample_vars = template.get_sample_variables()
    for var in expected_vars:
        assert var in sample_vars
        assert isinstance(sample_vars[var], str)
        assert len(sample_vars[var]) > 0

    print("✅ Template variable extraction test passed")


def test_error_handling_edge_cases():
    """Test error handling for edge cases in validation"""
    print("Testing error handling edge cases...")

    # Test question with missing required field
    try:
        invalid_response = {
            "questions": [{
                "id": 1,
                "question": "Test?",
                # Missing difficulty, category, estimated_time_minutes
            }],
            "recommendations": [{"category": "test", "recommendation": "test", "priority": "high"}],
            "metadata": {"total_questions": 1, "estimated_total_time": 5}
        }
        StructuredOutputPrompts.validate_json_response(
            json.dumps(invalid_response))
        assert False, "Should have raised ValueError for missing question fields"
    except ValueError as e:
        assert "Missing required field" in str(e)

    # Test invalid priority in recommendation
    try:
        invalid_response = {
            "questions": [{
                "id": 1,
                "question": "Test?",
                "difficulty": "easy",
                "category": "test",
                "estimated_time_minutes": 5
            }],
            "recommendations": [{"category": "test", "recommendation": "test", "priority": "invalid"}],
            "metadata": {"total_questions": 1, "estimated_total_time": 5}
        }
        StructuredOutputPrompts.validate_json_response(
            json.dumps(invalid_response))
        assert False, "Should have raised ValueError for invalid priority"
    except ValueError as e:
        assert "Invalid priority" in str(e)

    # Test invalid metadata fields
    try:
        invalid_response = {
            "questions": [{
                "id": 1,
                "question": "Test?",
                "difficulty": "easy",
                "category": "test",
                "estimated_time_minutes": 5
            }],
            "recommendations": [{"category": "test", "recommendation": "test", "priority": "high"}],
            "metadata": {"total_questions": "invalid", "estimated_total_time": 5}
        }
        StructuredOutputPrompts.validate_json_response(
            json.dumps(invalid_response))
        assert False, "Should have raised ValueError for invalid metadata"
    except ValueError as e:
        assert "Invalid total_questions" in str(e)

    print("✅ Error handling edge cases test passed")


def run_all_tests():
    """Run all Structured Output tests"""
    print("🧪 Running Structured Output Tests")
    print("=" * 50)

    try:
        test_structured_output_template_registration()
        test_json_schema_definition()
        test_sample_response_creation()
        test_json_validation_success()
        test_json_validation_failures()
        test_technical_template_coverage()
        test_behavioral_template_coverage()
        test_template_json_format_consistency()
        test_template_formatting_with_variables()
        test_difficulty_distribution_by_level()
        test_case_study_and_reverse_templates()
        test_metadata_richness()
        test_json_schema_validation_completeness()
        test_template_variable_extraction()
        test_error_handling_edge_cases()

        print("=" * 50)
        print("🎉 All Structured Output tests passed!")
        return True

    except Exception as e:  # pylint: disable=broad-except
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
