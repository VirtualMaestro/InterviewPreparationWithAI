"""
Cost calculation and tracking system for OpenAI API usage.
Provides model-specific pricing, token-based cost breakdown, and cumulative tracking.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Any


@dataclass
class ModelPricing:
    """Pricing information for a specific model"""
    input_cost_per_1k_tokens: float
    output_cost_per_1k_tokens: float
    model_name: str


class CostCalculator:
    """
    Calculates and tracks API costs for OpenAI models.

    Supports model-specific pricing with token-based cost breakdown
    and cumulative cost tracking across sessions.
    """

    # Model pricing as of January 2025 (in USD per 1K tokens)
    MODEL_PRICING = {
        "gpt-4o": ModelPricing(
            input_cost_per_1k_tokens=0.0025,   # $2.50 per 1M tokens
            output_cost_per_1k_tokens=0.010,   # $10.00 per 1M tokens
            model_name="gpt-4o"
        ),
        "gpt-4o-mini": ModelPricing(
            input_cost_per_1k_tokens=0.00015,  # $0.15 per 1M tokens
            output_cost_per_1k_tokens=0.0006,  # $0.60 per 1M tokens
            model_name="gpt-4o-mini"
        ),
        "gpt-5": ModelPricing(
            # $5.00 per 1M tokens (estimated)
            input_cost_per_1k_tokens=0.005,
            # $20.00 per 1M tokens (estimated)
            output_cost_per_1k_tokens=0.020,
            model_name="gpt-5"
        )
    }

    def __init__(self):
        """Initialize cost calculator with tracking variables"""
        self.cumulative_cost = 0.0
        self.cumulative_input_tokens = 0
        self.cumulative_output_tokens = 0
        self.session_count = 0
        self.last_reset = datetime.now()

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> Dict[str, float]:
        """
        Calculate cost breakdown for a specific API call.

        Args:
            model: Model name (e.g., "gpt-4o", "gpt-5")
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated

        Returns:
            Dictionary with cost breakdown:
            - input_cost: Cost for input tokens
            - output_cost: Cost for output tokens  
            - total_cost: Combined cost
            - input_tokens: Input token count
            - output_tokens: Output token count

        Raises:
            ValueError: If model is not supported or token counts are invalid
        """
        if model not in self.MODEL_PRICING:
            raise ValueError(
                f"Unsupported model: {model}. Supported models: {list(self.MODEL_PRICING.keys())}")

        if input_tokens < 0 or output_tokens < 0:
            raise ValueError("Token counts cannot be negative")

        pricing = self.MODEL_PRICING[model]

        # Calculate costs (pricing is per 1K tokens)
        input_cost = (input_tokens / 1000.0) * pricing.input_cost_per_1k_tokens
        output_cost = (output_tokens / 1000.0) * \
            pricing.output_cost_per_1k_tokens

        # Round to 6 decimal places for precision
        input_cost = round(input_cost, 6)
        output_cost = round(output_cost, 6)
        # Calculate total from rounded components to ensure consistency
        total_cost = round(input_cost + output_cost, 6)

        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }

    def add_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> Dict[str, float]:
        """
        Calculate cost and add to cumulative tracking.

        Args:
            model: Model name used
            input_tokens: Input tokens for this call
            output_tokens: Output tokens for this call

        Returns:
            Cost breakdown dictionary (same as calculate_cost)
        """
        cost_breakdown = self.calculate_cost(
            model, input_tokens, output_tokens)

        # Update cumulative tracking
        self.cumulative_cost += cost_breakdown["total_cost"]
        self.cumulative_input_tokens += input_tokens
        self.cumulative_output_tokens += output_tokens
        self.session_count += 1

        return cost_breakdown

    def get_cumulative_stats(self) -> Dict[str, Any]:
        """
        Get cumulative usage statistics.

        Returns:
            Dictionary with cumulative statistics:
            - total_cost: Total cost across all sessions
            - total_input_tokens: Total input tokens used
            - total_output_tokens: Total output tokens generated
            - session_count: Number of API calls made
            - average_cost_per_session: Average cost per API call
            - last_reset: When tracking was last reset
        """
        average_cost = (
            self.cumulative_cost / self.session_count
            if self.session_count > 0
            else 0.0
        )

        return {
            "total_cost": round(self.cumulative_cost, 6),
            "total_input_tokens": self.cumulative_input_tokens,
            "total_output_tokens": self.cumulative_output_tokens,
            "session_count": self.session_count,
            "average_cost_per_session": round(average_cost, 6),
            "last_reset": self.last_reset
        }

    def reset_tracking(self) -> None:
        """Reset all cumulative tracking to zero"""
        self.cumulative_cost = 0.0
        self.cumulative_input_tokens = 0
        self.cumulative_output_tokens = 0
        self.session_count = 0
        self.last_reset = datetime.now()

    def get_model_pricing_info(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Get pricing information for models.

        Args:
            model: Specific model to get pricing for, or None for all models

        Returns:
            Dictionary with pricing information
        """
        if model:
            if model not in self.MODEL_PRICING:
                raise ValueError(f"Unsupported model: {model}")

            pricing = self.MODEL_PRICING[model]
            return {
                "model": model,
                "input_cost_per_1k_tokens": pricing.input_cost_per_1k_tokens,
                "output_cost_per_1k_tokens": pricing.output_cost_per_1k_tokens,
                "input_cost_per_1m_tokens": pricing.input_cost_per_1k_tokens * 1000,
                "output_cost_per_1m_tokens": pricing.output_cost_per_1k_tokens * 1000
            }
        else:
            # Return all model pricing
            return {
                model_name: {
                    "input_cost_per_1k_tokens": pricing.input_cost_per_1k_tokens,
                    "output_cost_per_1k_tokens": pricing.output_cost_per_1k_tokens,
                    "input_cost_per_1m_tokens": pricing.input_cost_per_1k_tokens * 1000,
                    "output_cost_per_1m_tokens": pricing.output_cost_per_1k_tokens * 1000
                }
                for model_name, pricing in self.MODEL_PRICING.items()
            }

    def estimate_cost(
        self,
        model: str,
        estimated_input_tokens: int,
        estimated_output_tokens: int
    ) -> Dict[str, float]:
        """
        Estimate cost for a planned API call without adding to cumulative tracking.

        Args:
            model: Model name to use
            estimated_input_tokens: Estimated input tokens
            estimated_output_tokens: Estimated output tokens

        Returns:
            Cost breakdown dictionary (same format as calculate_cost)
        """
        return self.calculate_cost(model, estimated_input_tokens, estimated_output_tokens)

    def format_cost_display(self, cost_breakdown: Dict[str, float]) -> str:
        """
        Format cost breakdown for user-friendly display.

        Args:
            cost_breakdown: Cost breakdown dictionary from calculate_cost

        Returns:
            Formatted string for display
        """
        return (
            f"Input: ${cost_breakdown['input_cost']:.6f} "
            f"({cost_breakdown['input_tokens']:,} tokens) | "
            f"Output: ${cost_breakdown['output_cost']:.6f} "
            f"({cost_breakdown['output_tokens']:,} tokens) | "
            f"Total: ${cost_breakdown['total_cost']:.6f}"
        )


# Global cost calculator instance for application-wide tracking
cost_calculator = CostCalculator()
