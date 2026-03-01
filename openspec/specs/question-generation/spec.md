# Question Generation Specification
# Auto-generated — review for accuracy

## Requirement: Personalized Question Generation
The system SHALL generate personalized interview questions based on job description, interview type, experience level, and selected prompt technique.

### Scenario: Generating questions for a specific role
- GIVEN a job description for "Senior Python Developer"
- AND interview type is Technical
- AND experience level is Senior
- AND technique is Few-Shot
- WHEN generating questions
- THEN questions SHALL be tailored to Python development
- AND difficulty SHALL match Senior level (6-10 years)
- AND questions SHALL use Few-Shot technique with examples
- AND 1-20 questions SHALL be generated (default 5)

**Implementation:** `src/ai/generator.py`

## Requirement: OpenAI API Integration with Async Support
The system SHALL integrate with OpenAI API using async/await patterns for non-blocking operations.

### Scenario: Async API call
- GIVEN a question generation request
- WHEN calling OpenAI API
- THEN the call SHALL use `async def` and `await`
- AND the call SHALL use `AsyncOpenAI` client
- AND the UI SHALL remain responsive during generation
- AND progress indicators SHALL be displayed

## Requirement: Retry Logic with Exponential Backoff
The system SHALL implement retry logic using tenacity library for resilient API calls.

### Scenario: Transient API failure
- GIVEN an API call fails with a transient error (timeout, rate limit)
- WHEN the error occurs
- THEN the system SHALL retry up to 3 times
- AND retry delays SHALL use exponential backoff (1s, 2s, 4s)
- AND user SHALL be notified of retry attempts
- AND if all retries fail, a clear error message SHALL be displayed

## Requirement: Multi-Model Support
The system SHALL support multiple OpenAI models (GPT-4o, GPT-4o-mini, GPT-5) with model-specific API handling.

### Scenario: GPT-4o API call
- GIVEN model is GPT-4o
- WHEN making API call
- THEN the system SHALL use `client.chat.completions.create()` endpoint
- AND model parameter SHALL be "gpt-4o"
- AND response SHALL be parsed from ChatCompletion format

### Scenario: GPT-5 API call
- GIVEN model is GPT-5
- WHEN making API call
- THEN the system SHALL use `client.responses.create()` endpoint (new API)
- AND model parameter SHALL be "gpt-5"
- AND response SHALL be parsed from Response format

**Known Issue:** GPT-5 support currently disabled in UI due to bugs (commit a5330c3)

## Requirement: Template Selection and Formatting
The system SHALL select appropriate templates from the prompt library and format them with request parameters.

### Scenario: Template selection
- GIVEN a generation request with technique, interview type, experience level
- WHEN selecting a template
- THEN the system SHALL query `prompt_library.get_template()`
- AND the best matching template SHALL be retrieved
- AND template variables SHALL be substituted with actual values
- AND formatted prompt SHALL be sent to OpenAI API

## Requirement: Response Parsing Integration
The system SHALL integrate with ResponseParser to parse API responses into structured questions.

### Scenario: Parsing API response
- GIVEN OpenAI API returns a response
- WHEN parsing
- THEN the system SHALL use `ResponseParser.parse()`
- AND multiple parsing strategies SHALL be attempted
- AND parsed questions SHALL be extracted
- AND parsing strategy used SHALL be recorded

## Requirement: Cost Tracking Integration
The system SHALL track costs for every API call using the global cost_calculator.

### Scenario: Recording API call cost
- GIVEN an API call completes successfully
- WHEN processing the response
- THEN token counts SHALL be extracted (prompt_tokens, completion_tokens)
- AND cost SHALL be calculated via `cost_calculator.calculate_cost()`
- AND cost breakdown SHALL be included in GenerationResult
- AND cumulative cost SHALL be updated

## Requirement: Rate Limiting Integration
The system SHALL check rate limits before every API call using the global rate_limiter.

### Scenario: Rate limit check before call
- GIVEN a generation request is received
- WHEN preparing to call OpenAI API
- THEN the system SHALL call `rate_limiter.check_rate_limit()`
- AND if rate limit is exceeded, the call SHALL be blocked
- AND user SHALL be notified with wait time
- AND if rate limit is OK, the call SHALL proceed

## Requirement: Security Validation Integration
The system SHALL validate all inputs through SecurityValidator before processing.

### Scenario: Validating job description
- GIVEN a user submits a job description
- WHEN processing the request
- THEN the system SHALL call `SecurityValidator.validate_input()`
- AND if validation fails, generation SHALL be blocked
- AND user SHALL be notified of security issues
- AND if validation passes, generation SHALL proceed

## Requirement: Comprehensive Error Handling
The system SHALL handle all error types gracefully with user-friendly messages.

### Scenario: API authentication error
- GIVEN API key is invalid or missing
- WHEN calling OpenAI API
- THEN authentication error SHALL be caught
- AND user SHALL be prompted to check API key
- AND error SHALL be logged with category API_ERROR

### Scenario: API timeout error
- GIVEN API call times out
- WHEN timeout occurs
- THEN timeout error SHALL be caught
- AND retry logic SHALL be triggered
- AND user SHALL be notified of retry attempts

### Scenario: Parsing error
- GIVEN API response cannot be parsed
- WHEN parsing fails
- THEN parsing error SHALL be caught
- AND fallback parsing strategies SHALL be attempted
- AND default questions SHALL be provided if all parsing fails

## Requirement: Generation Result Model
The system SHALL return a comprehensive GenerationResult containing questions, recommendations, metadata, cost, and technique used.

### Scenario: Returning generation results
- GIVEN generation completes successfully
- WHEN returning results
- THEN GenerationResult SHALL contain:
  - `questions: list[str]` — Generated interview questions
  - `recommendations: list[str]` — Preparation advice
  - `metadata: dict[str, Any]` — Additional context
  - `cost_breakdown: SimpleCostBreakdown` — Token usage and cost
  - `technique_used: PromptTechnique` — Which technique was used
- AND all fields SHALL be populated
- AND result SHALL be displayed to user

## Requirement: Mock Interview Mode Support
The system SHALL support mock interview mode with answer evaluation and feedback.

### Scenario: Evaluating candidate answer
- GIVEN a mock interview question is asked
- AND candidate provides an answer
- WHEN evaluating the answer
- THEN the system SHALL generate evaluation using OpenAI API
- AND evaluation SHALL include strengths, weaknesses, suggestions
- AND evaluation SHALL be displayed to candidate
- AND cost SHALL be tracked for evaluation call

## Requirement: Fallback Strategy Execution
The system SHALL execute multi-level fallback strategies when primary technique fails.

### Scenario: Primary technique failure with fallback
- GIVEN Few-Shot technique fails to generate questions
- WHEN fallback is triggered
- THEN the system SHALL attempt Chain-of-Thought as secondary
- AND if secondary fails, Zero-Shot SHALL be attempted
- AND if all techniques fail, emergency default questions SHALL be provided
- AND user SHALL always receive questions
- AND technique used SHALL be recorded in results

**Current State:**
- Async OpenAI API integration with AsyncOpenAI client
- Retry logic with tenacity (3 attempts, exponential backoff)
- Multi-model support (GPT-4o, GPT-4o-mini, GPT-5)
- Template selection from 62 templates
- Response parsing with 7 strategies
- Cost tracking with 6-decimal precision
- Rate limiting with sliding window
- Security validation with 75% attack blocking
- Comprehensive error handling
- Mock interview mode with answer evaluation
- Multi-level fallback system ensuring 100% availability
