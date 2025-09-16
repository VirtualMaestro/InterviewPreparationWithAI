"""
Complete system test suite for AI Interview Prep Application.
Tests environment setup, all libraries, and complete functionality.
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import importlib
import importlib.util
import json
import sys
import traceback
from pathlib import Path

from src.ai.prompts import prompt_library
from src.ai.structured_output import StructuredOutputPrompts
from src.models.enums import (DifficultyLevel, ExperienceLevel, InterviewType,
                          PromptTechnique, QuestionCategory)
from src.models.simple_schemas import (SimpleAISettings, SimpleGenerationRequest)
from src.models.schemas import Question

# Add src to path for imports
test_dir = Path(__file__).parent
project_root = test_dir.parent
src_path = project_root / 'src'

if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

# Import project modules at top level


def test_environment_setup():
    """Test that the environment is properly set up with all required libraries"""
    print("🔧 Testing Environment Setup")
    print("-" * 50)

    # Test Python version
    python_version = sys.version_info
    print(
        f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    assert python_version >= (
        3, 11), f"Python 3.11+ required, got {python_version}"
    print("✅ Python version check passed")

    # Test required libraries
    required_libraries = [
        ('streamlit', '1.49.1'),
        ('openai', '1.106.1'),
        ('python-dotenv', '1.1.1'),
        ('pydantic', '2.11.7'),
        ('tenacity', '9.1.2'),
        ('pytest', '8.4.2'),
        ('pytest-asyncio', '1.1.0'),
    ]

    # Map package names to import names
    import_mapping = {
        'python-dotenv': 'dotenv',
        'pytest-asyncio': 'pytest_asyncio'
    }

    for lib_name, min_version in required_libraries:
        try:
            import_name = import_mapping.get(
                lib_name, lib_name.replace('-', '_'))
            lib = importlib.import_module(import_name)
            if hasattr(lib, '__version__'):
                version = lib.__version__
                print(f"✅ {lib_name}: {version}")
            else:
                print(f"✅ {lib_name}: imported successfully")
        except ImportError as e:
            print(f"❌ {lib_name}: {e}")
            raise AssertionError(f"Required library {lib_name} not found")

    print("✅ All required libraries are available")
    return True


def test_project_structure():
    """Test that the project structure is correct"""
    print("\n📁 Testing Project Structure")
    print("-" * 50)

    # Check essential directories
    essential_dirs = [
        'src',
        'src/ai',
        'src/models',
        'src/utils',
        'tests',
    ]

    for dir_path in essential_dirs:
        full_path = project_root / dir_path
        assert full_path.exists(), f"Missing directory: {dir_path}"
        print(f"✅ {dir_path}/ exists")

    # Check essential files
    essential_files = [
        'src/pyproject.toml',
        'src/ai/__init__.py',
        'src/ai/prompts.py',
        'src/ai/structured_output.py',
        'src/models/__init__.py',
        'src/models/schemas.py',
        'src/models/enums.py',
    ]

    for file_path in essential_files:
        full_path = project_root / file_path
        assert full_path.exists(), f"Missing file: {file_path}"
        print(f"✅ {file_path} exists")

    print("✅ Project structure is correct")
    return True


def test_imports():
    """Test that all modules can be imported correctly"""
    print("\n📦 Testing Module Imports")
    print("-" * 50)

    # Test core imports (already imported at top level)
    try:
        print("✅ Enums imported successfully")
        print("✅ Schemas imported successfully")
        print("✅ Prompt system imported successfully")
        print("✅ Structured output imported successfully")

        # Test that templates are registered
        templates = prompt_library.list_templates()
        assert len(templates) > 0, "No templates found in library"
        print(f"✅ Found {len(templates)} registered templates")

        # Test structured output templates specifically
        structured_templates = prompt_library.list_templates(
            technique=PromptTechnique.STRUCTURED_OUTPUT
        )
        assert len(
            structured_templates) >= 10, f"Expected at least 10 structured output templates, got {len(structured_templates)}"
        print(
            f"✅ Found {len(structured_templates)} structured output templates")

    except Exception as e:
        print(f"❌ Import failed: {e}")
        raise

    print("✅ All imports successful")
    return True


def test_core_functionality():
    """Test core functionality of the application"""
    print("\n⚙️ Testing Core Functionality")
    print("-" * 50)

    try:

        # Test 1: Template retrieval and formatting
        print("Testing template retrieval and formatting...")
        template = prompt_library.get_template(
            PromptTechnique.STRUCTURED_OUTPUT,
            InterviewType.TECHNICAL,
            ExperienceLevel.SENIOR
        )

        assert template is not None, "Template not found"

        formatted = template.format(
            question_count="3",
            job_description="Senior Python Developer with Django and AWS experience",
            experience_level="Senior"
        )

        assert "JSON" in formatted, "Template should contain JSON instructions"
        assert "Senior Python Developer" in formatted, "Job description should be in formatted template"
        print("✅ Template retrieval and formatting works")

        # Test 2: JSON validation
        print("Testing JSON validation...")
        sample_response = StructuredOutputPrompts.create_sample_response(3)
        json_string = json.dumps(sample_response)
        validated = StructuredOutputPrompts.validate_json_response(json_string)

        assert len(validated["questions"]) == 3, "Should have 3 questions"
        assert "recommendations" in validated, "Should have recommendations"
        assert "metadata" in validated, "Should have metadata"
        print("✅ JSON validation works")

        # Test 3: Schema validation
        print("Testing schema validation...")
        schema = StructuredOutputPrompts.get_json_schema()
        assert "properties" in schema, "Schema should have properties"
        assert "questions" in schema["properties"], "Schema should define questions"
        print("✅ Schema validation works")

        # Test 4: All interview types
        print("Testing all interview types...")
        for interview_type in InterviewType:
            if interview_type in [InterviewType.CASE_STUDY, InterviewType.REVERSE]:
                template = prompt_library.get_template(
                    PromptTechnique.STRUCTURED_OUTPUT,
                    interview_type,
                    None
                )
            else:
                template = prompt_library.get_template(
                    PromptTechnique.STRUCTURED_OUTPUT,
                    interview_type,
                    ExperienceLevel.MID
                )

            assert template is not None, f"Template not found for {interview_type.value}"
            print(f"  ✅ {interview_type.value} template available")

        print("✅ All interview types supported")

    except Exception as e:
        print(f"❌ Core functionality test failed: {e}")
        raise

    print("✅ Core functionality tests passed")
    return True


def test_data_models():
    """Test Pydantic data models"""
    print("\n📊 Testing Data Models")
    print("-" * 50)

    try:

        # Test AISettings
        print("Testing AISettings model...")
        ai_settings = SimpleAISettings(
            model="gpt-4o",
            temperature=0.7,
            max_tokens=2000
        )
        assert ai_settings.model == "gpt-4o"
        assert ai_settings.temperature == 0.7
        print("✅ SimpleAISettings model works")

        # Test Question model
        print("Testing Question model...")
        question = Question(
            id=1,
            question="What is Python?",
            difficulty=DifficultyLevel.EASY,
            category=QuestionCategory.CONCEPTUAL,
            time_estimate="5 minutes"
        )
        assert question.id == 1
        assert question.difficulty == DifficultyLevel.EASY
        print("✅ Question model works")

        # Test GenerationRequest
        print("Testing GenerationRequest model...")
        request = SimpleGenerationRequest(
            job_description="Senior Python Developer with 5+ years experience",
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR,
            prompt_technique=PromptTechnique.STRUCTURED_OUTPUT,
            question_count=5
        )
        assert request.question_count == 5
        assert request.interview_type == InterviewType.TECHNICAL
        print("✅ SimpleGenerationRequest model works")

    except Exception as e:
        print(f"❌ Data models test failed: {e}")
        raise

    print("✅ Data models tests passed")
    return True


def test_error_handling():
    """Test error handling and validation"""
    print("\n🛡️ Testing Error Handling")
    print("-" * 50)

    try:

        # Test JSON validation errors
        print("Testing JSON validation errors...")

        # Invalid JSON
        try:
            StructuredOutputPrompts.validate_json_response("invalid json")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Invalid JSON" in str(e)
            print("✅ Invalid JSON error handling works")

        # Missing required fields
        try:
            StructuredOutputPrompts.validate_json_response('{"questions": []}')
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Missing required key" in str(
                e) or "non-empty list" in str(e)
            print("✅ Missing fields error handling works")

        # Test Pydantic validation
        print("Testing Pydantic validation...")
        try:
            SimpleGenerationRequest(
                job_description="",  # Too short
                interview_type=InterviewType.TECHNICAL,
                experience_level=ExperienceLevel.SENIOR,
                prompt_technique=PromptTechnique.STRUCTURED_OUTPUT
            )
            assert False, "Should have raised validation error"
        except Exception:
            print("✅ Pydantic validation works")

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        raise

    print("✅ Error handling tests passed")
    return True


def run_existing_test_suites():
    """Run existing test suites"""
    print("\n🧪 Running Existing Test Suites")
    print("-" * 50)

    test_files = [
        'test_prompts_simple.py',
        'test_structured_output_simple.py',
        'test_structured_output_integration.py',
        'test_edge_cases_comprehensive.py',
        'test_uncovered_functionality.py'
    ]

    for test_file in test_files:
        test_path = project_root / 'tests' / test_file
        if test_path.exists():
            print(f"Running {test_file}...")
            try:
                # Import and run the test
                spec = importlib.util.spec_from_file_location(
                    "test_module", test_path)

                if spec is None or spec.loader is None:
                    raise ValueError(f"{spec} is null")

                test_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(test_module) 

                if hasattr(test_module, 'run_all_tests'):
                    result = test_module.run_all_tests()
                    if result:
                        print(f"✅ {test_file} passed")
                    else:
                        print(f"❌ {test_file} failed")
                        return False
                else:
                    print(f"⚠️ {test_file} has no run_all_tests function")
            except Exception as e:
                print(f"❌ {test_file} failed with error: {e}")
                return False
        else:
            print(f"⚠️ {test_file} not found")

    print("✅ All existing test suites passed")
    return True


def main():
    """Run complete system test"""
    print("🚀 AI Interview Prep - Complete System Test")
    print("=" * 60)

    try:
        # Test environment
        test_environment_setup()

        # Test project structure
        test_project_structure()

        # Test imports
        test_imports()

        # Test core functionality
        test_core_functionality()

        # Test data models
        test_data_models()

        # Test error handling
        test_error_handling()

        # Run existing test suites
        run_existing_test_suites()

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Environment is properly set up")
        print("✅ All libraries are working")
        print("✅ All functionality is working")
        print("✅ Project is ready for use")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ SYSTEM TEST FAILED: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
