# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered Interview Preparation Application built with Python 3.11+, Streamlit, and OpenAI API. The project implements advanced prompt engineering techniques for generating personalized interview questions based on job requirements and user experience level.

## Common Commands

### Environment Setup & Dependencies
```bash
# Create and activate virtual environment (Windows)
python -m venv .venv
.venv\Scripts\activate

# Install dependencies from pyproject.toml
pip install -e src/

# Setup environment variables
copy .env.example .env
# Add your OPENAI_API_KEY to .env file
```

### Running the Application
```bash
# Run Streamlit application (when main.py is implemented)
streamlit run main.py
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_complete_system.py

# Run tests for specific modules
python tests/test_prompts_simple.py
python tests/test_security_simple.py
python tests/test_cost_simple.py
python tests/test_rate_limiter_simple.py

# Run integration tests
python tests/test_cost_integration.py
python tests/test_rate_limiter_integration.py
python tests/test_structured_output_integration.py
```

### Code Quality
```bash
# No linting or formatting tools are currently configured
# Consider adding black, flake8, or ruff for future development
```

## Architecture & Code Structure

### Project Organization
The codebase follows a modular architecture with clear separation of concerns:

- **src/config.py**: Centralized configuration using dataclasses, handles environment variables and directory setup
- **src/models/**: Data models with enums and Pydantic schemas for type safety
  - `enums.py`: All application enums (InterviewType, ExperienceLevel, etc.)
  - `simple_schemas.py`: Dataclass models for runtime use
  - `schemas.py`: Pydantic models (has import issues, use simple_schemas.py)

- **src/utils/**: Utility modules for cross-cutting concerns
  - `security.py`: Input validation and prompt injection protection (75% attack blocking)
  - `cost.py`: Token-based cost calculation for OpenAI API usage
  - `rate_limiter.py`: Sliding window rate limiting (100 calls/hour)
  - `logger.py`: Structured logging configuration

- **src/ai/**: Complete prompt engineering system (62 templates total)
  - `prompts.py`: Core template infrastructure and prompt library
  - `few_shot.py`: Example-driven prompt templates
  - `chain_of_thought.py`: Step-by-step reasoning templates
  - `zero_shot.py`: Direct generation templates with fallbacks
  - `role_based.py`: Persona-driven interview templates
  - `structured_output.py`: JSON-formatted response templates

### Key Design Patterns

1. **Global Singleton Instances**: Shared instances for cost tracking, rate limiting, and prompt library
   ```python
   from ai.prompts import prompt_library
   from utils.cost import cost_calculator
   from utils.rate_limiter import rate_limiter
   ```

2. **Template Registration**: All prompt templates auto-register with the global prompt library on import

3. **Comprehensive Fallback System**: Multi-level fallback strategies ensure 100% availability

4. **Progressive Difficulty Scaling**: Templates adapt from Junior (1-2 years) to Lead/Principal level

## Current Implementation Status

**Completed (11/16 tasks):**
- Core infrastructure (config, models, logging)
- Security validation system
- Cost calculation and tracking
- Rate limiting with sliding window
- Complete prompt engineering system (all 5 techniques)
- Comprehensive test suite (100+ tests)

**Remaining (5/16 tasks):**
- Task 7: AI Question Generator with OpenAI integration
- Task 8: Response parsing and fallback systems
- Task 9-11: Streamlit UI components and session management
- Task 12-16: Error handling, entry point, and final testing

## Testing Strategy

After implementing any feature:
1. Write comprehensive unit tests covering edge cases
2. Include both positive and negative test paths
3. Create integration tests for cross-component interactions
4. Maintain test coverage above 90% for new code

Test files follow the pattern `test_<module>_simple.py` for unit tests and `test_<module>_integration.py` for integration tests.

## Important Context Files

Before making significant changes, review:
- `.kiro/specs/ai-interview-prep/` - Complete requirements, design, and task breakdown
- `.kiro/steering/` - Technology stack, structure, and product overview
- `HANDOFF_SUMMARY.md` - Detailed progress status and implementation notes

## Security Considerations

- Never commit API keys or sensitive data
- All user inputs are sanitized through `SecurityValidator`
- Prompt injection protection with 20+ attack patterns
- Rate limiting prevents API abuse
- Cost tracking ensures budget compliance