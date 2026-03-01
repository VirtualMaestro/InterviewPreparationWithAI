# Rate Limiting Specification
# Auto-generated — review for accuracy

## Requirement: Sliding Window Rate Limiting
The system SHALL implement sliding window rate limiting algorithm to prevent API abuse.

### Scenario: Rate limit check before API call
- GIVEN rate limit is 100 calls per hour
- WHEN checking if a new call is allowed
- THEN the system SHALL count calls in the last 60 minutes
- AND if count < 100, the call SHALL be allowed
- AND if count >= 100, the call SHALL be blocked

**Implementation:** `src/utils/rate_limiter.py`

## Requirement: Configurable Rate Limit
The system SHALL support configurable rate limits via environment variable or configuration.

### Scenario: Default rate limit
- GIVEN no `RATE_LIMIT_CALLS` environment variable is set
- WHEN rate limiter initializes
- THEN rate limit SHALL default to 100 calls per hour

### Scenario: Custom rate limit
- GIVEN `RATE_LIMIT_CALLS=50` in environment
- WHEN rate limiter initializes
- THEN rate limit SHALL be set to 50 calls per hour

## Requirement: Call History Tracking
The system SHALL maintain a history of API call timestamps for rate limit calculation.

### Scenario: Recording an API call
- GIVEN an API call is made
- WHEN recording the call
- THEN current timestamp SHALL be added to call history
- AND old timestamps (>60 minutes) SHALL be removed
- AND call history SHALL be used for rate limit checks

## Requirement: Rate Limit Exceeded Handling
The system SHALL provide clear error messages when rate limit is exceeded.

### Scenario: Rate limit exceeded
- GIVEN 100 calls have been made in the last hour
- WHEN attempting a new call
- THEN rate limit check SHALL fail
- AND error message SHALL indicate rate limit exceeded
- AND time until reset SHALL be calculated and displayed
- AND user SHALL be advised to wait

## Requirement: Reset Time Calculation
The system SHALL calculate and display the time until rate limit resets.

### Scenario: Calculating reset time
- GIVEN rate limit is exceeded
- WHEN calculating reset time
- THEN the system SHALL find the oldest call timestamp
- AND calculate time until that call is 60 minutes old
- AND display remaining minutes to user

## Requirement: Global Singleton Rate Limiter
The system SHALL use a global singleton `rate_limiter` instance shared across all modules.

### Scenario: Accessing rate limiter
- GIVEN any module needs to check rate limits
- WHEN importing
- THEN it SHALL use `from utils.rate_limiter import rate_limiter`
- AND all modules SHALL share the same instance
- AND call history SHALL be consistent across modules

## Requirement: Graceful Degradation
The system SHALL handle rate limit errors gracefully without crashing the application.

### Scenario: Rate limit error during generation
- GIVEN rate limit is exceeded during question generation
- WHEN the error occurs
- THEN the application SHALL NOT crash
- AND a user-friendly error message SHALL be displayed
- AND the user SHALL be able to retry after waiting

**Current Configuration:**
- Default rate limit: 100 calls per hour
- Window: 60 minutes (sliding)
- Algorithm: Sliding window with timestamp tracking
- Configurable via: RATE_LIMIT_CALLS environment variable
