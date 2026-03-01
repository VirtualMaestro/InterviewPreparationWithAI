# Data Models Specification
# Auto-generated — review for accuracy

## Requirement: Dataclass-Based Models
The system SHALL use dataclass-based models from `src/models/simple_schemas.py` for all production code.

### Scenario: Creating a data model instance
- GIVEN a dataclass model like `SimpleCostBreakdown` or `SimpleGenerationRequest`
- WHEN instantiating with parameters
- THEN all fields SHALL be type-checked
- AND default values SHALL be applied where specified
- AND validation SHALL occur on instantiation

**Implementation:** `src/models/simple_schemas.py` (production), `src/models/enums.py` (enums)

**Note:** Avoid `src/models/schemas.py` (Pydantic models have import issues)

## Requirement: Enum Types for Constants
The system SHALL use enum types for all categorical values (interview types, experience levels, prompt techniques, etc.).

### Scenario: Interview type selection
- GIVEN a user selects an interview type
- WHEN storing the value
- THEN it SHALL use `InterviewType` enum (TECHNICAL, BEHAVIORAL, CASE_STUDY, REVERSE)
- AND invalid values SHALL be rejected at compile time

### Scenario: Experience level selection
- GIVEN a user selects an experience level
- WHEN storing the value
- THEN it SHALL use `ExperienceLevel` enum (JUNIOR, MID_LEVEL, SENIOR, LEAD_PRINCIPAL)
- AND enum values SHALL map to years of experience

**Available Enums (8 total):**
- `InterviewType`: TECHNICAL, BEHAVIORAL, CASE_STUDY, REVERSE
- `ExperienceLevel`: JUNIOR, MID_LEVEL, SENIOR, LEAD_PRINCIPAL
- `PromptTechnique`: FEW_SHOT, CHAIN_OF_THOUGHT, ZERO_SHOT, ROLE_BASED, STRUCTURED_OUTPUT
- `AIModel`: GPT_4O, GPT_4O_MINI, GPT_5
- `PersonaRole`: STRICT, FRIENDLY, NEUTRAL
- `ErrorCategory`: API_ERROR, VALIDATION_ERROR, RATE_LIMIT_ERROR, SECURITY_ERROR, PARSING_ERROR, SYSTEM_ERROR
- `ErrorSeverity`: LOW, MEDIUM, HIGH, CRITICAL
- `ParseStrategy`: JSON_PARSE, NUMBERED_LIST, BULLETED_LIST, PARAGRAPH, FALLBACK, DEFAULT, STRUCTURED_JSON

## Requirement: Type Safety with Modern Python Hints
The system SHALL use modern Python 3.11+ type hints (list[], dict[], |) for all model fields.

### Scenario: Type-safe field definitions
- GIVEN a dataclass field definition
- WHEN declaring the type
- THEN it SHALL use `list[str]` not `List[str]`
- AND it SHALL use `dict[str, Any]` not `Dict[str, Any]`
- AND it SHALL use `str | None` not `Optional[str]`

## Requirement: Immutable Defaults with field()
The system SHALL use `field(default_factory=...)` for mutable default values in dataclasses.

### Scenario: List or dict default value
- GIVEN a dataclass field with a list or dict default
- WHEN defining the field
- THEN it SHALL use `field(default_factory=list)` or `field(default_factory=dict)`
- AND it SHALL NOT use mutable defaults directly (e.g., `questions: list[str] = []`)

## Requirement: Generation Request Model
The system SHALL use `SimpleGenerationRequest` to encapsulate all parameters for question generation.

### Scenario: Creating a generation request
- GIVEN user inputs (job description, interview type, experience level, num questions, technique)
- WHEN creating a request
- THEN all parameters SHALL be validated
- AND the request SHALL be passed to the generator
- AND type safety SHALL be enforced

**Fields:**
- `job_description: str`
- `interview_type: InterviewType`
- `experience_level: ExperienceLevel`
- `num_questions: int`
- `technique: PromptTechnique`
- `model: str`

## Requirement: Cost Breakdown Model
The system SHALL use `SimpleCostBreakdown` to track token usage and costs.

### Scenario: Calculating API call cost
- GIVEN an OpenAI API response with token counts
- WHEN calculating cost
- THEN `SimpleCostBreakdown` SHALL store prompt_tokens, completion_tokens, total_tokens, cost_usd
- AND cost SHALL be calculated with 6-decimal precision

**Fields:**
- `prompt_tokens: int`
- `completion_tokens: int`
- `total_tokens: int`
- `cost_usd: float` (6-decimal precision)

## Requirement: Generation Result Model
The system SHALL use `GenerationResult` to encapsulate generated questions, recommendations, metadata, and cost.

### Scenario: Returning generation results
- GIVEN the generator completes successfully
- WHEN returning results
- THEN `GenerationResult` SHALL contain questions, recommendations, metadata, cost_breakdown, technique_used
- AND all fields SHALL be type-safe

**Current Models:**
- `SimpleCostBreakdown` — Token usage and cost tracking
- `SimpleGenerationRequest` — Question generation parameters
- `GenerationResult` — Generated questions and metadata
- `ParsedResponse` — Structured parsed output
- `ParsedQuestion` — Individual question with metadata
- `ValidationResult` — Security validation results
