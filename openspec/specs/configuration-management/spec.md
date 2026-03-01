# Configuration Management Specification
# Auto-generated — review for accuracy

## Requirement: Centralized Configuration Dataclass
The system SHALL use a centralized `Config` dataclass in `src/config.py` for all application settings.

### Scenario: Loading configuration on startup
- GIVEN the application starts
- WHEN `Config` is instantiated
- THEN all settings SHALL be loaded from environment variables or defaults
- AND API key SHALL be validated for format
- AND directories (logs, exports) SHALL be created if missing

**Implementation:** `src/config.py`

## Requirement: Environment Variable Support
The system SHALL support environment variable overrides for all configuration parameters.

### Scenario: Overriding API key via environment
- GIVEN `OPENAI_API_KEY` is set in environment or `.env` file
- WHEN configuration loads
- THEN the API key SHALL be read from the environment
- AND it SHALL override any default value

### Scenario: Overriding rate limit via environment
- GIVEN `RATE_LIMIT_CALLS` is set to "50"
- WHEN configuration loads
- THEN rate limit SHALL be set to 50 calls per hour
- AND it SHALL override the default of 100

## Requirement: API Key Validation
The system SHALL validate OpenAI API key format on configuration load.

### Scenario: Valid API key format
- GIVEN an API key starting with "sk-"
- WHEN configuration loads
- THEN validation SHALL pass
- AND the key SHALL be stored securely

### Scenario: Invalid API key format
- GIVEN an API key not starting with "sk-"
- WHEN configuration loads
- THEN validation SHALL fail
- AND a clear error message SHALL be displayed

## Requirement: Model Selection Configuration
The system SHALL support configuration of OpenAI model selection (GPT-4o, GPT-4o-mini, GPT-5).

### Scenario: Default model selection
- GIVEN no model is specified
- WHEN configuration loads
- THEN model SHALL default to GPT_5 (as per config.py:18)
- AND model SHALL be available to the generator

**Known Issue:** Config defaults to GPT_5 but app.py overrides to GPT_4O due to GPT-5 bugs

## Requirement: Input Constraints Configuration
The system SHALL configure input length constraints and validation rules.

### Scenario: Maximum input length
- GIVEN `MAX_INPUT_LENGTH` environment variable
- WHEN configuration loads
- THEN input validation SHALL enforce this maximum
- AND default SHALL be 5000 characters if not specified

## Requirement: Directory Management
The system SHALL automatically create required directories for logs and exports.

### Scenario: Missing directories on startup
- GIVEN logs/ or exports/ directories do not exist
- WHEN configuration loads
- THEN directories SHALL be created automatically
- AND appropriate permissions SHALL be set

## Requirement: Debug Mode Configuration
The system SHALL support debug mode via `DEBUG` environment variable.

### Scenario: Debug mode enabled
- GIVEN `DEBUG=true` in environment
- WHEN configuration loads
- THEN debug logging SHALL be enabled
- AND verbose output SHALL be displayed

**Current Settings:**
- API Key: From environment (OPENAI_API_KEY)
- Model: GPT_5 (default), GPT_4O (app.py override)
- Rate Limit: 100 calls/hour (default)
- Max Input Length: 5000 characters
- Directories: logs/, exports/
