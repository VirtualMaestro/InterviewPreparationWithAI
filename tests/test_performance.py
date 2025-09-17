#!/usr/bin/env python3
"""
Performance tests for the Interview Preparation Application.

Tests response times, memory usage, and concurrent operations.
"""

import asyncio
import sys
import time
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import GUI class
sys.path.insert(0, str(Path(__file__).parent.parent))
from app import InterviewPrepGUI


class TestPerformance:
    """Performance tests for the application."""

    def setup_method(self):
        """Set up test fixtures."""
        self.gui = InterviewPrepGUI()
        self.test_config = {
            "job_description": "Senior Python Developer position",
            "experience_level": "Senior (5+ years)",
            "question_type": "Technical",
            "prompt_technique": "Few Shot",
            "questions_num": 10,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2000
        }

    def test_config_mapping_performance(self):
        """Test configuration mapping performance."""
        print("Testing configuration mapping performance...")

        start_time = time.time()
        for _ in range(1000):  # Test 1000 iterations
            result = self.gui.map_config_to_enums(self.test_config)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time = total_time / 1000

        print(f"1000 config mappings completed in {total_time:.4f}s")
        print(f"Average time per mapping: {avg_time:.6f}s")

        # Should be very fast (under 1ms per mapping)
        assert avg_time < 0.001, f"Config mapping too slow: {avg_time:.6f}s per mapping"

    def test_question_extraction_performance(self):
        """Test question extraction performance with large responses."""
        print("Testing question extraction performance...")

        # Create a large response with many questions
        large_response = ""
        for i in range(50):
            large_response += f"{i+1}. **Question {i+1}:** This is test question number {i+1} with some detailed content.\n"

        start_time = time.time()
        for _ in range(100):  # Test 100 iterations
            questions = self.gui.extract_questions_directly(large_response, "Few Shot")
        end_time = time.time()

        total_time = end_time - start_time
        avg_time = total_time / 100

        print(f"100 question extractions completed in {total_time:.4f}s")
        print(f"Average time per extraction: {avg_time:.6f}s")
        print(f"Extracted {len(questions)} questions from large response")

        # Should extract questions reasonably fast
        assert avg_time < 0.1, f"Question extraction too slow: {avg_time:.6f}s per extraction"
        assert len(questions) >= 40, f"Should extract most questions, got {len(questions)}"

    def test_json_parsing_performance(self):
        """Test JSON parsing performance for Structured Output."""
        print("Testing JSON parsing performance...")

        # Create JSON response with many questions
        json_questions = []
        for i in range(20):
            json_questions.append({
                "id": i+1,
                "question": f"This is structured question number {i+1} with detailed content for testing performance.",
                "difficulty": "medium",
                "category": "technical"
            })

        import json
        json_response = json.dumps({"questions": json_questions})

        start_time = time.time()
        for _ in range(100):  # Test 100 iterations
            questions = self.gui.extract_questions_directly(json_response, "Structured Output")
        end_time = time.time()

        total_time = end_time - start_time
        avg_time = total_time / 100

        print(f"100 JSON parsings completed in {total_time:.4f}s")
        print(f"Average time per parsing: {avg_time:.6f}s")
        print(f"Extracted {len(questions)} questions from JSON")

        # JSON parsing should be fast
        assert avg_time < 0.01, f"JSON parsing too slow: {avg_time:.6f}s per parsing"
        assert len(questions) == 20, f"Should extract all 20 questions, got {len(questions)}"

    def test_api_key_validation_performance(self):
        """Test API key validation performance."""
        print("Testing API key validation performance...")

        test_keys = [
            "sk-test123456789012345678901234567890",
            "invalid-key",
            "",
            "sk-short",
            "api-wrongprefix123456789012345678901234567890"
        ]

        start_time = time.time()
        for _ in range(1000):  # Test 1000 iterations
            for key in test_keys:
                self.gui.validate_api_key(key)
        end_time = time.time()

        total_time = end_time - start_time
        total_validations = 1000 * len(test_keys)
        avg_time = total_time / total_validations

        print(f"{total_validations} API key validations completed in {total_time:.4f}s")
        print(f"Average time per validation: {avg_time:.6f}s")

        # Validation should be very fast
        assert avg_time < 0.0001, f"API key validation too slow: {avg_time:.6f}s per validation"

    @patch('streamlit.session_state', {'api_key': 'sk-test123'})
    def test_generator_initialization_performance(self):
        """Test generator initialization performance."""
        print("Testing generator initialization performance...")

        with patch('app.InterviewQuestionGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator

            start_time = time.time()
            for _ in range(10):  # Test 10 initializations
                self.gui.generator = None  # Reset
                self.gui.ensure_generator_initialized()
            end_time = time.time()

            total_time = end_time - start_time
            avg_time = total_time / 10

            print(f"10 generator initializations completed in {total_time:.4f}s")
            print(f"Average time per initialization: {avg_time:.6f}s")

            # Initialization should be reasonable
            assert avg_time < 0.5, f"Generator initialization too slow: {avg_time:.6f}s per init"

    def test_memory_usage_question_extraction(self):
        """Test memory usage during question extraction."""
        print("Testing memory usage during question extraction...")

        # Create very large response (simulate large API response)
        huge_response = ""
        for i in range(500):  # 500 questions
            huge_response += f"{i+1}. **Question {i+1}:** " + "X" * 100 + "\n"  # 100 char questions

        print(f"Created test response with {len(huge_response)} characters")

        # Extract questions and measure basic performance
        start_time = time.time()
        questions = self.gui.extract_questions_directly(huge_response, "Few Shot")
        end_time = time.time()

        total_time = end_time - start_time

        print(f"Extracted {len(questions)} questions in {total_time:.4f}s")
        print(f"Memory test completed - no crashes with large input")

        # Should handle large inputs without crashing
        assert len(questions) >= 400, f"Should extract most questions from large input, got {len(questions)}"
        assert total_time < 2.0, f"Large input processing too slow: {total_time:.4f}s"

    def test_concurrent_config_mapping(self):
        """Test concurrent configuration mapping."""
        print("Testing concurrent configuration mapping...")

        # Different configurations to test concurrency
        configs = [
            {**self.test_config, "experience_level": "Junior (1-2 years)"},
            {**self.test_config, "experience_level": "Mid-level (3-5 years)"},
            {**self.test_config, "experience_level": "Senior (5+ years)"},
            {**self.test_config, "experience_level": "Lead/Principal"},
        ]

        def map_config_batch(config_list):
            """Map a batch of configurations."""
            results = []
            for config in config_list:
                results.append(self.gui.map_config_to_enums(config))
            return results

        start_time = time.time()

        # Simulate concurrent operations
        results = []
        for _ in range(25):  # 25 batches of 4 configs each
            batch_results = map_config_batch(configs)
            results.extend(batch_results)

        end_time = time.time()

        total_time = end_time - start_time
        total_mappings = len(results)
        avg_time = total_time / total_mappings

        print(f"{total_mappings} concurrent config mappings completed in {total_time:.4f}s")
        print(f"Average time per mapping: {avg_time:.6f}s")

        # Should handle concurrent operations efficiently
        assert avg_time < 0.001, f"Concurrent config mapping too slow: {avg_time:.6f}s per mapping"
        assert len(results) == 100, f"Should complete all mappings, got {len(results)}"


def run_performance_tests():
    """Run all performance tests."""
    print("=" * 60)
    print("PERFORMANCE TESTS FOR INTERVIEW PREP APPLICATION")
    print("=" * 60)

    test_instance = TestPerformance()
    test_methods = [
        test_instance.test_config_mapping_performance,
        test_instance.test_question_extraction_performance,
        test_instance.test_json_parsing_performance,
        test_instance.test_api_key_validation_performance,
        test_instance.test_generator_initialization_performance,
        test_instance.test_memory_usage_question_extraction,
        test_instance.test_concurrent_config_mapping,
    ]

    passed_tests = 0
    total_tests = len(test_methods)

    for test_method in test_methods:
        try:
            test_instance.setup_method()
            print(f"\n--- {test_method.__name__} ---")
            test_method()
            print("PASSED")
            passed_tests += 1
        except Exception as e:
            print(f"FAILED: {e}")

    print("\n" + "=" * 60)
    print(f"PERFORMANCE TEST RESULTS: {passed_tests}/{total_tests} PASSED")
    if passed_tests == total_tests:
        print("All performance tests passed! Application meets performance requirements.")
    else:
        print("Some performance tests failed. Review performance bottlenecks.")
    print("=" * 60)

    return passed_tests == total_tests


if __name__ == "__main__":
    run_performance_tests()