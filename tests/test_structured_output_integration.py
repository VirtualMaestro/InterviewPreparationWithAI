"""
Integration tests for Structured Output prompt implementation.
Tests complete workflow from template selection to JSON validation.
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
    print("✅ Structured Output integration imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def test_complete_structured_output_workflow():
    """Test complete workflow from template selection to JSON validation"""
    print("Testing complete structured output workflow...")

    # Test data
    job_description = "Senior Python Developer with Django, REST APIs, and PostgreSQL experience"
    question_count = 3
    experience_level = ExperienceLevel.SENIOR

    # 1. Get template
    template = prompt_library.get_template(
        PromptTechnique.STRUCTURED_OUTPUT,
        InterviewType.TECHNICAL,
        experience_level
    )

    assert template is not None, "Template should be found"
    assert template.technique == PromptTechnique.STRUCTURED_OUTPUT

    # 2. Format template with variables
    formatted_prompt = template.format(
        question_count=str(question_count),
        job_description=job_description,
        experience_level=experience_level.value
    )

    # 3. Verify formatted prompt contains required elements
    assert "JSON" in formatted_prompt
    assert job_description in formatted_prompt
    assert str(question_count) in formatted_prompt
    assert experience_level.value in formatted_prompt

    # 4. Create sample response (simulating AI response)
    sample_response = StructuredOutputPrompts.create_sample_response(
        question_count)

    # 5. Validate the response structure
    json_string = json.dumps(sample_response)
    validated_response = StructuredOutputPrompts.validate_json_response(
        json_string)

    # 6. Verify all required fields are present and valid
    assert "questions" in validated_response
    assert "recommendations" in validated_response
    assert "metadata" in validated_response

    # Verify questions structure
    questions = validated_response["questions"]
    assert len(questions) == question_count

    for i, question in enumerate(questions):
        assert question["id"] == i + 1
        assert isinstance(question["question"], str)
        assert len(question["question"]) > 0
        assert question["difficulty"] in ["easy", "medium", "hard"]
        assert isinstance(question["category"], str)
        assert isinstance(question["estimated_time_minutes"], int)
        assert question["estimated_time_minutes"] > 0

    # Verify recommendations structure
    recommendations = validated_response["recommendations"]
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0

    for rec in recommendations:
        assert isinstance(rec["category"], str)
        assert isinstance(rec["recommendation"], str)
        assert rec["priority"] in ["high", "medium", "low"]

    # Verify metadata structure
    metadata = validated_response["metadata"]
    assert metadata["total_questions"] == question_count
    assert isinstance(metadata["estimated_total_time"], int)
    assert metadata["estimated_total_time"] > 0

    print("✅ Complete structured output workflow test passed")


def test_all_interview_types_structured_output():
    """Test structured output for all interview types"""
    print("Testing structured output for all interview types...")

    job_description = "Product Manager for e-commerce platform with team leadership experience"
    question_count = 2

    for interview_type in InterviewType:
        print(f"  Testing {interview_type.value}...")

        # Get appropriate template (some are generic, some have experience levels)
        if interview_type in [InterviewType.CASE_STUDY, InterviewType.REVERSE]:
            template = prompt_library.get_template(
                PromptTechnique.STRUCTURED_OUTPUT,
                interview_type,
                None  # Generic templates
            )
            experience_level_value = "Mid-level"
        else:
            template = prompt_library.get_template(
                PromptTechnique.STRUCTURED_OUTPUT,
                interview_type,
                ExperienceLevel.MID
            )
            experience_level_value = ExperienceLevel.MID.value

        assert template is not None, f"Template not found for {interview_type.value}"

        # Format template
        formatted_prompt = template.format(
            question_count=str(question_count),
            job_description=job_description,
            experience_level=experience_level_value
        )

        # Verify formatted prompt
        assert "JSON" in formatted_prompt
        assert job_description in formatted_prompt
        assert str(question_count) in formatted_prompt

        # Verify template metadata
        assert template.metadata["json_validated"] is True
        assert template.metadata["structured_parsing"] is True
        assert template.metadata["metadata_rich"] is True

    print("✅ All interview types structured output test passed")


def test_json_schema_compliance():
    """Test that generated responses comply with the defined JSON schema"""
    print("Testing JSON schema compliance...")

    schema = StructuredOutputPrompts.get_json_schema()

    # Test with different question counts
    for count in [1, 3, 5]:
        sample_response = StructuredOutputPrompts.create_sample_response(count)

        # Validate against schema structure
        assert "questions" in sample_response

        # Verify schema defines the expected structure
        assert "questions" in schema["properties"], "Schema should define questions structure"
        assert "recommendations" in schema["properties"], "Schema should define recommendations structure"
        assert "metadata" in schema["properties"], "Schema should define metadata structure"
        assert "recommendations" in sample_response
        assert "metadata" in sample_response

        # Validate questions array
        questions = sample_response["questions"]
        assert isinstance(questions, list)
        assert len(questions) == count

        for question in questions:
            # Check required fields
            required_fields = ["id", "question", "difficulty",
                               "category", "estimated_time_minutes"]
            for field in required_fields:
                assert field in question, f"Missing required field: {field}"

            # Check field types and values
            assert isinstance(question["id"], int)
            assert isinstance(question["question"], str)
            assert question["difficulty"] in ["easy", "medium", "hard"]
            assert isinstance(question["category"], str)
            assert isinstance(question["estimated_time_minutes"], int)
            assert question["estimated_time_minutes"] > 0

            # Check optional fields if present
            if "hints" in question:
                assert isinstance(question["hints"], list)
            if "follow_up_questions" in question:
                assert isinstance(question["follow_up_questions"], list)
            if "evaluation_criteria" in question:
                assert isinstance(question["evaluation_criteria"], list)

        # Validate recommendations array
        recommendations = sample_response["recommendations"]
        assert isinstance(recommendations, list)

        for rec in recommendations:
            required_fields = ["category", "recommendation", "priority"]
            for field in required_fields:
                assert field in rec, f"Missing required field: {field}"

            assert isinstance(rec["category"], str)
            assert isinstance(rec["recommendation"], str)
            assert rec["priority"] in ["high", "medium", "low"]

            if "resources" in rec:
                assert isinstance(rec["resources"], list)

        # Validate metadata
        metadata = sample_response["metadata"]
        required_fields = ["total_questions", "estimated_total_time"]
        for field in required_fields:
            assert field in metadata, f"Missing required field: {field}"

        assert isinstance(metadata["total_questions"], int)
        assert metadata["total_questions"] == count
        assert isinstance(metadata["estimated_total_time"], int)
        assert metadata["estimated_total_time"] > 0

        # Check optional metadata fields
        if "difficulty_distribution" in metadata:
            assert isinstance(metadata["difficulty_distribution"], dict)
        if "focus_areas" in metadata:
            assert isinstance(metadata["focus_areas"], list)

    print("✅ JSON schema compliance test passed")


def test_data_completeness_validation():
    """Test that all structured data fields are properly validated"""
    print("Testing data completeness validation...")

    # Test complete valid response
    complete_response = {
        "questions": [{
            "id": 1,
            "question": "What is the difference between a list and a tuple in Python?",
            "difficulty": "easy",
            "category": "conceptual",
            "estimated_time_minutes": 5,
            "hints": ["Think about mutability", "Consider use cases"],
            "follow_up_questions": ["When would you use each?"],
            "evaluation_criteria": ["Understands mutability", "Provides examples"]
        }],
        "recommendations": [{
            "category": "preparation",
            "recommendation": "Review Python data structures",
            "priority": "high",
            "resources": ["Python docs", "Practice exercises"]
        }],
        "metadata": {
            "total_questions": 1,
            "difficulty_distribution": {"easy": 100},
            "estimated_total_time": 5,
            "focus_areas": ["basic_concepts"],
            "preparation_level": "entry_level"
        }
    }

    # Should validate successfully
    json_string = json.dumps(complete_response)
    validated = StructuredOutputPrompts.validate_json_response(json_string)
    assert validated == complete_response

    # Test with minimal required fields only
    minimal_response = {
        "questions": [{
            "id": 1,
            "question": "Test question?",
            "difficulty": "medium",
            "category": "test",
            "estimated_time_minutes": 10
        }],
        "recommendations": [{
            "category": "test",
            "recommendation": "Test recommendation",
            "priority": "medium"
        }],
        "metadata": {
            "total_questions": 1,
            "estimated_total_time": 10
        }
    }

    # Should also validate successfully
    json_string = json.dumps(minimal_response)
    validated = StructuredOutputPrompts.validate_json_response(json_string)
    assert validated == minimal_response

    print("✅ Data completeness validation test passed")


def test_error_handling_comprehensive():
    """Test comprehensive error handling for malformed structured responses"""
    print("Testing comprehensive error handling...")

    # Test various malformed responses
    test_cases = [
        # Missing top-level keys
        ('{"questions": []}', "Missing required key"),
        ('{"recommendations": []}', "Missing required key"),
        ('{"metadata": {}}', "Missing required key"),

        # Invalid question structure
        ('{"questions": [{"id": "invalid"}], "recommendations": [], "metadata": {"total_questions": 1, "estimated_total_time": 5}}', "Missing required field"),

        # Invalid difficulty
        ('{"questions": [{"id": 1, "question": "Test?", "difficulty": "invalid", "category": "test", "estimated_time_minutes": 5}], "recommendations": [], "metadata": {"total_questions": 1, "estimated_total_time": 5}}', "Invalid difficulty"),

        # Invalid time estimate
        ('{"questions": [{"id": 1, "question": "Test?", "difficulty": "easy", "category": "test", "estimated_time_minutes": "invalid"}], "recommendations": [], "metadata": {"total_questions": 1, "estimated_total_time": 5}}', "Invalid estimated_time_minutes"),

        # Invalid priority
        ('{"questions": [{"id": 1, "question": "Test?", "difficulty": "easy", "category": "test", "estimated_time_minutes": 5}], "recommendations": [{"category": "test", "recommendation": "test", "priority": "invalid"}], "metadata": {"total_questions": 1, "estimated_total_time": 5}}', "Invalid priority"),

        # Invalid metadata
        ('{"questions": [{"id": 1, "question": "Test?", "difficulty": "easy", "category": "test", "estimated_time_minutes": 5}], "recommendations": [], "metadata": {"total_questions": "invalid", "estimated_total_time": 5}}', "Invalid total_questions"),
    ]

    for invalid_json, expected_error in test_cases:
        try:
            StructuredOutputPrompts.validate_json_response(invalid_json)
            assert False, f"Should have raised ValueError for: {invalid_json[:50]}..."
        except ValueError as e:
            assert expected_error.lower() in str(e).lower(
            ), f"Expected '{expected_error}' in error message: {e}"

    print("✅ Comprehensive error handling test passed")


def test_template_consistency_across_levels():
    """Test that templates maintain consistency across experience levels"""
    print("Testing template consistency across experience levels...")

    for interview_type in [InterviewType.TECHNICAL, InterviewType.BEHAVIORAL]:
        templates = []
        for level in [ExperienceLevel.JUNIOR, ExperienceLevel.MID, ExperienceLevel.SENIOR, ExperienceLevel.LEAD]:
            template = prompt_library.get_template(
                PromptTechnique.STRUCTURED_OUTPUT,
                interview_type,
                level
            )
            templates.append(template)

        # All templates should exist
        assert all(
            t is not None for t in templates), f"Missing templates for {interview_type.value}"

        # All should have consistent structure
        for template in templates:
            assert template.technique == PromptTechnique.STRUCTURED_OUTPUT
            assert template.interview_type == interview_type
            assert "JSON" in template.template
            assert "valid json" in template.template.lower()
            assert template.metadata["json_validated"] is True
            assert template.metadata["structured_parsing"] is True
            assert template.metadata["metadata_rich"] is True

        # Difficulty focus should progress appropriately
        difficulty_progression = [
            t.metadata["difficulty_focus"] for t in templates]

        # Junior should be easier, Lead should be hardest
        # Junior
        assert "easy" in difficulty_progression[0] or difficulty_progression[0] == "easy_medium"
        assert difficulty_progression[-1] in ["expert", "hard"]  # Lead

    print("✅ Template consistency across levels test passed")


def run_all_integration_tests():
    """Run all structured output integration tests"""
    print("🧪 Running Structured Output Integration Tests")
    print("=" * 60)

    try:
        test_complete_structured_output_workflow()
        test_all_interview_types_structured_output()
        test_json_schema_compliance()
        test_data_completeness_validation()
        test_error_handling_comprehensive()
        test_template_consistency_across_levels()

        print("=" * 60)
        print("🎉 All Structured Output integration tests passed!")
        return True

    except Exception as e:  # pylint: disable=broad-except
        print(f"❌ Integration test failed: {e}")
        traceback.print_exc()
        return False


def run_all_tests():
    """Compatibility function for complete system test"""
    return run_all_integration_tests()


if __name__ == "__main__":
    success = run_all_integration_tests()
    sys.exit(0 if success else 1)
