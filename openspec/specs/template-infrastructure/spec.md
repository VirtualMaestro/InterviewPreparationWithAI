# Template Infrastructure Specification
# Auto-generated — review for accuracy

## Requirement: Central Prompt Template Registry
The system SHALL maintain a global PromptLibrary singleton that manages all prompt templates with automatic registration.

### Scenario: Template registration on import
- GIVEN a prompt technique module is imported
- WHEN the module loads
- THEN all templates SHALL automatically register with the global `prompt_library`
- AND templates SHALL be indexed by technique, interview type, and experience level

**Implementation:** `src/ai/prompts.py`

## Requirement: Template Variable Substitution
The system SHALL support dynamic variable substitution in prompt templates.

### Scenario: Formatting a template with variables
- GIVEN a template with placeholders like `{job_description}`, `{experience_level}`, `{num_questions}`
- WHEN `format_prompt()` is called with variable values
- THEN all placeholders SHALL be replaced with actual values
- AND missing variables SHALL raise a clear error

## Requirement: Template Selection by Criteria
The system SHALL retrieve templates based on technique, interview type, and experience level.

### Scenario: Retrieving a specific template
- GIVEN a request for Few-Shot technique, Technical interview, Senior level
- WHEN `get_template()` is called with these criteria
- THEN the matching template SHALL be returned
- AND if no exact match exists, a fallback template SHALL be provided

## Requirement: Progressive Difficulty Scaling
The system SHALL provide templates that scale in difficulty from Junior to Lead/Principal level.

### Scenario: Junior level template
- GIVEN experience level is Junior (1-2 years)
- WHEN retrieving a template
- THEN questions SHALL focus on fundamental concepts
- AND complexity SHALL be appropriate for entry-level candidates

### Scenario: Lead/Principal level template
- GIVEN experience level is Lead or Principal
- WHEN retrieving a template
- THEN questions SHALL focus on system design, architecture, and leadership
- AND complexity SHALL be appropriate for senior technical leaders

## Requirement: Template Metadata
The system SHALL store metadata for each template including technique, interview type, experience level, and description.

### Scenario: Querying template metadata
- GIVEN a registered template
- WHEN accessing its metadata
- THEN technique, interview_type, experience_level, and description SHALL be available
- AND metadata SHALL be used for template selection and logging

**Current State:** 62 templates registered across 5 techniques (Few-Shot: 10, Chain-of-Thought: 10, Zero-Shot: 10, Role-Based: 12, Structured Output: 10)
