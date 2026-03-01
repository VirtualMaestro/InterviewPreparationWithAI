# Cost Tracking Specification
# Auto-generated — review for accuracy

## Requirement: Real-Time Token-Based Cost Calculation
The system SHALL calculate OpenAI API costs in real-time based on token usage with 6-decimal precision.

### Scenario: Calculating cost for GPT-4o API call
- GIVEN an API response with prompt_tokens=100, completion_tokens=50
- WHEN `calculate_cost()` is called with model="gpt-4o"
- THEN cost SHALL be calculated using GPT-4o pricing
- AND result SHALL have 6-decimal precision (e.g., $0.001500)
- AND a `SimpleCostBreakdown` SHALL be returned

**Implementation:** `src/utils/cost.py`

## Requirement: Model-Specific Pricing
The system SHALL maintain accurate pricing for all supported OpenAI models.

### Scenario: GPT-4o pricing
- GIVEN model is GPT-4o
- WHEN calculating cost
- THEN prompt tokens SHALL be priced at $0.0025 per 1K tokens
- AND completion tokens SHALL be priced at $0.010 per 1K tokens

### Scenario: GPT-4o-mini pricing
- GIVEN model is GPT-4o-mini
- WHEN calculating cost
- THEN prompt tokens SHALL be priced at $0.00015 per 1K tokens
- AND completion tokens SHALL be priced at $0.0006 per 1K tokens

### Scenario: GPT-5 pricing
- GIVEN model is GPT-5
- WHEN calculating cost
- THEN prompt tokens SHALL be priced at $0.005 per 1K tokens
- AND completion tokens SHALL be priced at $0.015 per 1K tokens

## Requirement: Cumulative Cost Tracking
The system SHALL track cumulative costs across multiple API calls within a session.

### Scenario: Multiple API calls in session
- GIVEN 3 API calls with costs $0.001500, $0.002300, $0.001800
- WHEN tracking cumulative cost
- THEN total SHALL be $0.005600
- AND cumulative cost SHALL be displayed to user
- AND cost history SHALL be maintained

## Requirement: Cost Breakdown Display
The system SHALL display detailed cost breakdowns including prompt tokens, completion tokens, total tokens, and USD cost.

### Scenario: Displaying cost to user
- GIVEN a completed API call
- WHEN showing results
- THEN prompt_tokens count SHALL be displayed
- AND completion_tokens count SHALL be displayed
- AND total_tokens count SHALL be displayed
- AND cost_usd SHALL be displayed with 6-decimal precision
- AND cost SHALL be formatted as "$0.XXXXXX"

## Requirement: Global Singleton Cost Calculator
The system SHALL use a global singleton `cost_calculator` instance shared across all modules.

### Scenario: Accessing cost calculator
- GIVEN any module needs to calculate costs
- WHEN importing
- THEN it SHALL use `from utils.cost import cost_calculator`
- AND all modules SHALL share the same instance
- AND cumulative costs SHALL be consistent across modules

## Requirement: Zero-Cost Fallback Handling
The system SHALL handle cases where API calls fail and no cost is incurred.

### Scenario: API call failure before token usage
- GIVEN an API call fails before processing
- WHEN calculating cost
- THEN cost SHALL be $0.000000
- AND cost breakdown SHALL indicate zero tokens used

**Current Pricing (as of implementation):**
- GPT-4o: $0.0025/1K prompt, $0.010/1K completion
- GPT-4o-mini: $0.00015/1K prompt, $0.0006/1K completion
- GPT-5: $0.005/1K prompt, $0.015/1K completion

**Precision:** 6-decimal places for USD amounts
