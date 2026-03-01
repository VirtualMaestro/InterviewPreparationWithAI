# Security Validation Specification
# Auto-generated — review for accuracy

## Requirement: Input Validation and Sanitization
The system SHALL validate and sanitize all user inputs through the `SecurityValidator` class before processing.

### Scenario: Validating job description input
- GIVEN a user submits a job description
- WHEN `validate_input()` is called
- THEN length SHALL be checked (10-5000 characters)
- AND prompt injection patterns SHALL be detected (20+ patterns)
- AND HTML/script tags SHALL be sanitized
- AND a `ValidationResult` SHALL be returned with warnings or blocks

**Implementation:** `src/utils/security.py`

## Requirement: Prompt Injection Detection
The system SHALL detect and block prompt injection attacks with 75% blocking rate.

### Scenario: Detecting ignore instructions attack
- GIVEN input contains "ignore previous instructions"
- WHEN validation runs
- THEN the pattern SHALL be detected
- AND a warning or block SHALL be issued
- AND the attack type SHALL be logged

### Scenario: Detecting role manipulation attack
- GIVEN input contains "you are now a different AI"
- WHEN validation runs
- THEN the pattern SHALL be detected
- AND a warning or block SHALL be issued

**Attack Patterns Detected (20+ total):**
- Ignore instructions: "ignore previous", "disregard all"
- Role manipulation: "you are now", "act as", "pretend to be"
- System prompts: "system:", "assistant:", "user:"
- Jailbreak attempts: "DAN mode", "developer mode"
- Instruction injection: "new instructions", "override"
- Data exfiltration: "print your instructions", "reveal your prompt"

## Requirement: Length Constraints
The system SHALL enforce minimum and maximum length constraints on all text inputs.

### Scenario: Input too short
- GIVEN input with fewer than 10 characters
- WHEN validation runs
- THEN validation SHALL fail
- AND error message SHALL indicate minimum length requirement

### Scenario: Input too long
- GIVEN input with more than 5000 characters (or MAX_INPUT_LENGTH)
- WHEN validation runs
- THEN validation SHALL fail
- AND error message SHALL indicate maximum length exceeded

## Requirement: HTML and Script Tag Sanitization
The system SHALL sanitize HTML and script tags from user inputs to prevent XSS attacks.

### Scenario: Input contains script tags
- GIVEN input contains `<script>alert('xss')</script>`
- WHEN sanitization runs
- THEN script tags SHALL be removed or escaped
- AND safe content SHALL be preserved

### Scenario: Input contains HTML tags
- GIVEN input contains `<div onclick="malicious()">content</div>`
- WHEN sanitization runs
- THEN event handlers SHALL be removed
- AND safe HTML structure may be preserved or stripped

## Requirement: API Key Format Validation
The system SHALL validate OpenAI API key format before use.

### Scenario: Valid API key format
- GIVEN an API key starting with "sk-"
- WHEN `validate_api_key()` is called
- THEN validation SHALL pass
- AND the key SHALL be accepted

### Scenario: Invalid API key format
- GIVEN an API key not starting with "sk-" or empty
- WHEN `validate_api_key()` is called
- THEN validation SHALL fail
- AND a clear error message SHALL be returned

## Requirement: Validation Result Reporting
The system SHALL return structured validation results with warnings, blocks, and detected patterns.

### Scenario: Validation with warnings
- GIVEN input contains suspicious but not critical patterns
- WHEN validation completes
- THEN `ValidationResult` SHALL indicate success with warnings
- AND detected patterns SHALL be listed
- AND user SHALL be notified

### Scenario: Validation blocked
- GIVEN input contains critical attack patterns
- WHEN validation completes
- THEN `ValidationResult` SHALL indicate failure
- AND blocked patterns SHALL be listed
- AND input SHALL be rejected

**ValidationResult Fields:**
- `is_valid: bool` — Overall validation status
- `warnings: list[str]` — Non-critical issues detected
- `blocked_patterns: list[str]` — Critical patterns that caused blocking
- `sanitized_input: str` — Cleaned input (if applicable)

## Requirement: Security Event Logging
The system SHALL log all security events (warnings, blocks, attacks) for monitoring and analysis.

### Scenario: Logging a blocked attack
- GIVEN a prompt injection attack is detected and blocked
- WHEN validation completes
- THEN the event SHALL be logged with severity HIGH
- AND the attack pattern SHALL be recorded
- AND the original input SHALL be logged (sanitized for logs)

**Current Performance:**
- 20+ attack patterns detected
- 75% attack blocking rate (verified in security_demo.py)
- Input length constraints: 10-5000 characters
- HTML/script tag sanitization enabled
