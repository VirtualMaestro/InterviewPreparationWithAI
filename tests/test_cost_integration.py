"""
Integration test for cost calculator with existing data models.
Tests that CostCalculator works properly with SimpleCostBreakdown model.
"""
import os
import sys
from datetime import datetime

# Add src to path for imports
test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(test_dir)
src_path = os.path.join(project_root, 'src')

if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from models.enums import ExperienceLevel, InterviewType, PromptTechnique
    from models.simple_schemas import SimpleCostBreakdown
    from utils.cost import CostCalculator
    print("PASS All imports successful")
except ImportError as e:
    print(f"FAIL Import failed: {e}")
    sys.exit(1)


def test_cost_calculator_with_cost_breakdown_model():
    """Test that CostCalculator output works with SimpleCostBreakdown model"""
    print("Testing CostCalculator integration with SimpleCostBreakdown model...")

    calculator = CostCalculator()

    # Calculate cost using calculator
    cost_data = calculator.calculate_cost("gpt-4o", 1000, 500)

    # Create SimpleCostBreakdown model from calculator output
    cost_breakdown = SimpleCostBreakdown(
        input_cost=cost_data["input_cost"],
        output_cost=cost_data["output_cost"],
        total_cost=cost_data["total_cost"],
        input_tokens=cost_data["input_tokens"],
        output_tokens=cost_data["output_tokens"]
    )

    # Verify the model was created successfully
    assert cost_breakdown.input_cost == 0.0025
    assert cost_breakdown.output_cost == 0.005
    assert cost_breakdown.total_cost == 0.0075
    assert cost_breakdown.input_tokens == 1000
    assert cost_breakdown.output_tokens == 500

    print("PASS CostCalculator integrates properly with SimpleCostBreakdown model")


def test_cost_breakdown_validation():
    """Test that SimpleCostBreakdown model validation works correctly"""
    print("Testing SimpleCostBreakdown model validation...")

    # Test valid cost breakdown
    valid_breakdown = SimpleCostBreakdown(
        input_cost=0.001,
        output_cost=0.002,
        total_cost=0.003,
        input_tokens=100,
        output_tokens=200
    )
    assert valid_breakdown.total_cost == 0.003

    # Test negative cost validation
    try:
        SimpleCostBreakdown(
            input_cost=-0.001,
            output_cost=0.002,
            total_cost=0.001,
            input_tokens=100,
            output_tokens=200
        )
        assert False, "Should have raised ValueError for negative input cost"
    except ValueError as e:
        assert "Costs cannot be negative" in str(e)

    # Test total cost validation
    try:
        SimpleCostBreakdown(
            input_cost=0.001,
            output_cost=0.002,
            total_cost=0.005,  # Wrong total
            input_tokens=100,
            output_tokens=200
        )
        assert False, "Should have raised ValueError for incorrect total"
    except ValueError as e:
        assert "Total cost must equal input_cost + output_cost" in str(e)

    print("PASS SimpleCostBreakdown model validation works correctly")


def test_multiple_model_calculations():
    """Test cost calculations for different models"""
    print("Testing multiple model calculations...")

    calculator = CostCalculator()

    # Test GPT-4o
    gpt4o_cost = calculator.calculate_cost("gpt-4o", 1000, 1000)
    gpt4o_breakdown = SimpleCostBreakdown(
        input_cost=gpt4o_cost["input_cost"],
        output_cost=gpt4o_cost["output_cost"],
        total_cost=gpt4o_cost["total_cost"],
        input_tokens=gpt4o_cost["input_tokens"],
        output_tokens=gpt4o_cost["output_tokens"]
    )

    # Test GPT-5
    gpt5_cost = calculator.calculate_cost("gpt-5", 1000, 1000)
    gpt5_breakdown = SimpleCostBreakdown(
        input_cost=gpt5_cost["input_cost"],
        output_cost=gpt5_cost["output_cost"],
        total_cost=gpt5_cost["total_cost"],
        input_tokens=gpt5_cost["input_tokens"],
        output_tokens=gpt5_cost["output_tokens"]
    )

    # Verify GPT-5 is more expensive than GPT-4o
    assert gpt5_breakdown.total_cost > gpt4o_breakdown.total_cost
    assert gpt5_breakdown.input_cost > gpt4o_breakdown.input_cost
    assert gpt5_breakdown.output_cost > gpt4o_breakdown.output_cost

    print("PASS Multiple model calculations work correctly")


def test_cumulative_tracking_integration():
    """Test cumulative tracking with multiple sessions"""
    print("Testing cumulative tracking integration...")

    calculator = CostCalculator()
    calculator.reset_tracking()

    # Simulate multiple API calls
    sessions = [
        ("gpt-4o", 1000, 500),
        ("gpt-4o", 1500, 750),
        ("gpt-5", 800, 400),
    ]

    total_expected_cost = 0.0
    breakdowns = []

    for model, input_tokens, output_tokens in sessions:
        cost_data = calculator.add_usage(model, input_tokens, output_tokens)
        breakdown = SimpleCostBreakdown(
            input_cost=cost_data["input_cost"],
            output_cost=cost_data["output_cost"],
            total_cost=cost_data["total_cost"],
            input_tokens=cost_data["input_tokens"],
            output_tokens=cost_data["output_tokens"]
        )
        breakdowns.append(breakdown)
        total_expected_cost += breakdown.total_cost

    # Verify cumulative stats
    stats = calculator.get_cumulative_stats()
    assert abs(stats["total_cost"] - total_expected_cost) < 0.000001
    assert stats["session_count"] == 3
    assert stats["total_input_tokens"] == 3300
    assert stats["total_output_tokens"] == 1650

    print("PASS Cumulative tracking integration works correctly")


def run_integration_tests():
    """Run all integration tests"""
    print("TEST Running Cost Calculator Integration Tests")
    print("=" * 60)

    try:
        test_cost_calculator_with_cost_breakdown_model()
        test_cost_breakdown_validation()
        test_multiple_model_calculations()
        test_cumulative_tracking_integration()

        print("=" * 60)
        print("SUCCESS All Cost Calculator integration tests passed!")
        return True

    except Exception as e:
        print(f"FAIL Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
