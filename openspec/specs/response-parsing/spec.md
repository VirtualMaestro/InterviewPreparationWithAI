# Response Parsing Specification
# Auto-generated — review for accuracy

## Requirement: Multi-Strategy Response Parsing
The system SHALL parse OpenAI API responses using multiple fallback strategies to ensure 100% success rate.

### Scenario: Parsing JSON response
- GIVEN API returns a valid JSON response
- WHEN parsing with `ResponseParser`
- THEN JSON strategy SHALL be attempted first
- AND response SHALL be parsed into `ParsedResponse` with `ParsedQuestion` objects
- AND parsing strategy used SHALL be recorded

**Implementation:** `src/ai/parser.py`

## Requirement: Parsing Strategy Fallback Chain
The system SHALL attempt multiple parsing strategies in order until one succeeds.

### Scenario: JSON parsing fails, fallback to numbered list
- GIVEN API returns non-JSON response with numbered questions
- WHEN JSON parsing fails
- THEN numbered list strategy SHALL be attempted
- AND questions SHALL be extracted by pattern matching (1., 2., 3., etc.)
- AND parsing SHALL succeed

### Scenario: All strategies fail, use default
- GIVEN API returns unparseable response
- WHEN all parsing strategies fail
- THEN default strategy SHALL provide generic questions
- AND user SHALL be notified of parsing issue
- AND system SHALL NOT crash

**Parsing Strategies (7 total):**
1. JSON_PARSE: Parse structured JSON response
2. NUMBERED_LIST: Extract numbered questions (1., 2., 3.)
3. BULLETED_LIST: Extract bulleted questions (-, *, •)
4. PARAGRAPH: Extract questions from paragraph format
5. FALLBACK: Generic fallback parsing
6. DEFAULT: Emergency default questions
7. STRUCTURED_JSON: Parse JSON with metadata

## Requirement: Structured Question Extraction
The system SHALL extract questions with metadata (difficulty, topic, follow-up questions) when available.

### Scenario: Parsing structured JSON with metadata
- GIVEN API returns JSON with question, difficulty, topic, follow_up fields
- WHEN parsing
- THEN each field SHALL be extracted into `ParsedQuestion`
- AND metadata SHALL be preserved
- AND missing fields SHALL use defaults

**ParsedQuestion Fields:**
- `question: str` — The interview question
- `difficulty: str | None` — Difficulty level (if provided)
- `topic: str | None` — Topic/category (if provided)
- `follow_up: list[str]` — Follow-up questions (if provided)

## Requirement: Parsing Strategy Logging
The system SHALL log which parsing strategy succeeded for debugging and monitoring.

### Scenario: Successful parsing with strategy
- GIVEN a response is successfully parsed
- WHEN parsing completes
- THEN the strategy used SHALL be logged
- AND strategy SHALL be included in `ParsedResponse`
- AND debug output SHALL show "Successfully parsed with strategy: JSON_PARSE"

## Requirement: Graceful Parsing Failure Handling
The system SHALL handle parsing failures gracefully without crashing the application.

### Scenario: Parsing failure with recovery
- GIVEN all parsing strategies fail
- WHEN handling the failure
- THEN default questions SHALL be provided
- AND user SHALL be notified with a clear message
- AND error SHALL be logged for investigation
- AND application SHALL continue functioning

## Requirement: Question Count Validation
The system SHALL validate that the parsed number of questions matches the requested count.

### Scenario: Fewer questions than requested
- GIVEN user requests 5 questions but API returns 3
- WHEN parsing completes
- THEN the system SHALL accept the 3 questions
- AND user SHALL be notified that fewer questions were generated
- AND no error SHALL be raised

### Scenario: More questions than requested
- GIVEN user requests 5 questions but API returns 7
- WHEN parsing completes
- THEN the system SHALL return all 7 questions
- AND user SHALL receive the extra questions as a bonus

## Requirement: ParsedResponse Model
The system SHALL return a structured `ParsedResponse` object containing all parsed questions and metadata.

### Scenario: Returning parsed response
- GIVEN parsing succeeds
- WHEN returning results
- THEN `ParsedResponse` SHALL contain list of `ParsedQuestion` objects
- AND strategy used SHALL be included
- AND total question count SHALL be included
- AND any parsing warnings SHALL be included

**ParsedResponse Fields:**
- `questions: list[ParsedQuestion]` — Parsed questions with metadata
- `strategy_used: ParseStrategy` — Which strategy succeeded
- `total_count: int` — Number of questions parsed
- `warnings: list[str]` — Any parsing warnings

**Current Implementation:**
- 7 parsing strategies with fallback chain
- JSON, numbered list, bulleted list, paragraph, fallback, default, structured JSON
- Comprehensive error handling
- Strategy logging for debugging
- 100% success rate (always returns questions, even if defaults)
