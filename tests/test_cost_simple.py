"""
Simple test suite for cost calculation system.
Tests CostCalculator functionality without pytest dependencies.
"""
import os
import sys
from datetime import datetime

# Add src to path for imports - use absolute path resolution
test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(test_dir)
src_path = os.path.join(project_root, 'src')

print(f"Test dir: {test_dir}")
print(f"Project root: {project_root}")
print(f"Src path: {src_path}")
print(f"Src exists: {os.path.exists(src_path)}")

if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from src.utils.cost import CostCalculator
    print("[SUCCESS] Import successful")
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    print(
        f"Available in utils: {os.listdir(os.path.join(src_path, 'utils')) if os.path.exists(os.path.join(src_path, 'utils')) else 'utils dir not found'}")
    sys.exit(1)


def test_model_pricing_constants():
    """Test that model pricing constants are properly defined"""
    print("Testing model pricing constants...")

    calculator = CostCalculator()

    # Test that both models are defined
    assert "gpt-4o" in calculator.MODEL_PRICING
    assert "gpt-5" in calculator.MODEL_PRICING

    # Test GPT-4o pricing
    gpt4o_pricing = calculator.MODEL_PRICING["gpt-4o"]
    assert gpt4o_pricing.input_cost_per_1k_tokens == 0.0025
    assert gpt4o_pricing.output_cost_per_1k_tokens == 0.010
    assert gpt4o_pricing.model_name == "gpt-4o"

    # Test GPT-5 pricing
    gpt5_pricing = calculator.MODEL_PRICING["gpt-5"]
    assert gpt5_pricing.input_cost_per_1k_tokens == 0.005
    assert gpt5_pricing.output_cost_per_1k_tokens == 0.020
    assert gpt5_pricing.model_name == "gpt-5"

    print("[PASS] Model pricing constants test passed")


def test_basic_cost_calculation():
    """Test basic cost calculation functionality"""
    print("Testing basic cost calculation...")

    calculator = CostCalculator()

    # Test GPT-4o calculation with 1000 input, 500 output tokens
    result = calculator.calculate_cost("gpt-4o", 1000, 500)

    expected_input_cost = (1000 / 1000.0) * 0.0025  # 0.0025
    expected_output_cost = (500 / 1000.0) * 0.010   # 0.005
    expected_total = expected_input_cost + expected_output_cost  # 0.0075

    assert result["input_cost"] == 0.0025
    assert result["output_cost"] == 0.005
    assert result["total_cost"] == 0.0075
    assert result["input_tokens"] == 1000
    assert result["output_tokens"] == 500

    print("[PASS] Basic cost calculation test passed")


def test_gpt5_cost_calculation():
    """Test cost calculation for GPT-5 model"""
    print("Testing GPT-5 cost calculation...")

    calculator = CostCalculator()

    # Test GPT-5 calculation with 2000 input, 1000 output tokens
    result = calculator.calculate_cost("gpt-5", 2000, 1000)

    expected_input_cost = (2000 / 1000.0) * 0.005   # 0.010
    expected_output_cost = (1000 / 1000.0) * 0.020  # 0.020
    expected_total = expected_input_cost + expected_output_cost  # 0.030

    assert result["input_cost"] == 0.010
    assert result["output_cost"] == 0.020
    assert result["total_cost"] == 0.030
    assert result["input_tokens"] == 2000
    assert result["output_tokens"] == 1000

    print("[PASS] GPT-5 cost calculation test passed")


def test_precision_and_rounding():
    """Test cost calculation precision and rounding"""
    print("Testing precision and rounding...")

    calculator = CostCalculator()

    # Test with odd token counts that require rounding
    result = calculator.calculate_cost("gpt-4o", 1337, 2468)

    expected_input_cost = (1337 / 1000.0) * 0.0025   # 0.0033425
    expected_output_cost = (2468 / 1000.0) * 0.010   # 0.02468
    expected_total = expected_input_cost + expected_output_cost  # 0.0280225

    # Should be rounded to 6 decimal places
    assert result["input_cost"] == round(expected_input_cost, 6)
    assert result["output_cost"] == round(expected_output_cost, 6)
    assert result["total_cost"] == round(expected_total, 6)

    print("[PASS] Precision and rounding test passed")


def test_zero_tokens():
    """Test cost calculation with zero tokens"""
    print("Testing zero token scenarios...")

    calculator = CostCalculator()

    # Test with zero input tokens
    result = calculator.calculate_cost("gpt-4o", 0, 1000)
    assert result["input_cost"] == 0.0
    assert result["output_cost"] == 0.010
    assert result["total_cost"] == 0.010

    # Test with zero output tokens
    result = calculator.calculate_cost("gpt-4o", 1000, 0)
    assert result["input_cost"] == 0.0025
    assert result["output_cost"] == 0.0
    assert result["total_cost"] == 0.0025

    # Test with both zero
    result = calculator.calculate_cost("gpt-4o", 0, 0)
    assert result["input_cost"] == 0.0
    assert result["output_cost"] == 0.0
    assert result["total_cost"] == 0.0

    print("[PASS] Zero token scenarios test passed")


def test_error_handling():
    """Test error handling for invalid inputs"""
    print("Testing error handling...")

    calculator = CostCalculator()

    # Test unsupported model
    try:
        calculator.calculate_cost("gpt-3", 1000, 500)
        assert False, "Should have raised ValueError for unsupported model"
    except ValueError as e:
        assert "Unsupported model" in str(e)

    # Test negative input tokens
    try:
        calculator.calculate_cost("gpt-4o", -100, 500)
        assert False, "Should have raised ValueError for negative tokens"
    except ValueError as e:
        assert "Token counts cannot be negative" in str(e)

    # Test negative output tokens
    try:
        calculator.calculate_cost("gpt-4o", 1000, -500)
        assert False, "Should have raised ValueError for negative tokens"
    except ValueError as e:
        assert "Token counts cannot be negative" in str(e)

    print("[PASS] Error handling test passed")


def test_cumulative_tracking():
    """Test cumulative cost tracking functionality"""
    print("Testing cumulative tracking...")

    calculator = CostCalculator()
    calculator.reset_tracking()  # Start fresh

    # Add first usage
    result1 = calculator.add_usage("gpt-4o", 1000, 500)
    assert result1["total_cost"] == 0.0075

    stats = calculator.get_cumulative_stats()
    assert stats["total_cost"] == 0.0075
    assert stats["total_input_tokens"] == 1000
    assert stats["total_output_tokens"] == 500
    assert stats["session_count"] == 1
    assert stats["average_cost_per_session"] == 0.0075

    # Add second usage
    result2 = calculator.add_usage("gpt-5", 2000, 1000)
    assert result2["total_cost"] == 0.030

    stats = calculator.get_cumulative_stats()
    expected_total = 0.0075 + 0.030  # 0.0375
    assert stats["total_cost"] == round(expected_total, 6)
    assert stats["total_input_tokens"] == 3000
    assert stats["total_output_tokens"] == 1500
    assert stats["session_count"] == 2
    assert stats["average_cost_per_session"] == round(expected_total / 2, 6)

    print("[PASS] Cumulative tracking test passed")


def test_reset_tracking():
    """Test tracking reset functionality"""
    print("Testing tracking reset...")

    calculator = CostCalculator()

    # Add some usage
    calculator.add_usage("gpt-4o", 1000, 500)
    calculator.add_usage("gpt-5", 2000, 1000)

    # Verify we have data
    stats_before = calculator.get_cumulative_stats()
    assert stats_before["session_count"] > 0
    assert stats_before["total_cost"] > 0

    # Reset tracking
    reset_time = datetime.now()
    calculator.reset_tracking()

    # Verify reset
    stats_after = calculator.get_cumulative_stats()
    assert stats_after["total_cost"] == 0.0
    assert stats_after["total_input_tokens"] == 0
    assert stats_after["total_output_tokens"] == 0
    assert stats_after["session_count"] == 0
    assert stats_after["average_cost_per_session"] == 0.0
    assert stats_after["last_reset"] >= reset_time

    print("[PASS] Tracking reset test passed")


def test_model_pricing_info():
    """Test model pricing information retrieval"""
    print("Testing model pricing info...")

    calculator = CostCalculator()

    # Test specific model pricing
    gpt4o_info = calculator.get_model_pricing_info("gpt-4o")
    assert gpt4o_info["model"] == "gpt-4o"
    assert gpt4o_info["input_cost_per_1k_tokens"] == 0.0025
    assert gpt4o_info["output_cost_per_1k_tokens"] == 0.010
    assert gpt4o_info["input_cost_per_1m_tokens"] == 2.5
    assert gpt4o_info["output_cost_per_1m_tokens"] == 10.0

    # Test all models pricing
    all_pricing = calculator.get_model_pricing_info()
    assert "gpt-4o" in all_pricing
    assert "gpt-5" in all_pricing
    assert all_pricing["gpt-4o"]["input_cost_per_1k_tokens"] == 0.0025
    assert all_pricing["gpt-5"]["input_cost_per_1k_tokens"] == 0.005

    # Test invalid model
    try:
        calculator.get_model_pricing_info("invalid-model")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unsupported model" in str(e)

    print("[PASS] Model pricing info test passed")


def test_cost_estimation():
    """Test cost estimation without tracking"""
    print("Testing cost estimation...")

    calculator = CostCalculator()
    calculator.reset_tracking()

    # Estimate cost without adding to tracking
    estimate = calculator.estimate_cost("gpt-4o", 1000, 500)
    assert estimate["total_cost"] == 0.0075

    # Verify tracking wasn't updated
    stats = calculator.get_cumulative_stats()
    assert stats["session_count"] == 0
    assert stats["total_cost"] == 0.0

    print("[PASS] Cost estimation test passed")


def test_cost_display_formatting():
    """Test cost display formatting"""
    print("Testing cost display formatting...")

    calculator = CostCalculator()

    cost_breakdown = calculator.calculate_cost("gpt-4o", 1000, 500)
    formatted = calculator.format_cost_display(cost_breakdown)

    expected = (
        "Input: $0.002500 (1,000 tokens) | "
        "Output: $0.005000 (500 tokens) | "
        "Total: $0.007500"
    )

    assert formatted == expected

    print("[PASS] Cost display formatting test passed")


def test_large_token_counts():
    """Test cost calculation with large token counts"""
    print("Testing large token counts...")

    calculator = CostCalculator()

    # Test with very large token counts
    result = calculator.calculate_cost("gpt-4o", 100000, 50000)

    expected_input_cost = (100000 / 1000.0) * 0.0025   # 0.25
    expected_output_cost = (50000 / 1000.0) * 0.010    # 0.50
    expected_total = expected_input_cost + expected_output_cost  # 0.75

    assert result["input_cost"] == 0.25
    assert result["output_cost"] == 0.50
    assert result["total_cost"] == 0.75

    print("[PASS] Large token counts test passed")


def run_all_tests():
    """Run all cost calculator tests"""
    print("[TEST] Running Cost Calculator Tests")
    print("=" * 50)

    try:
        test_model_pricing_constants()
        test_basic_cost_calculation()
        test_gpt5_cost_calculation()
        test_precision_and_rounding()
        test_zero_tokens()
        test_error_handling()
        test_cumulative_tracking()
        test_reset_tracking()
        test_model_pricing_info()
        test_cost_estimation()
        test_cost_display_formatting()
        test_large_token_counts()

        print("=" * 50)
        print("[SUCCESS] All Cost Calculator tests passed!")
        return True

    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
