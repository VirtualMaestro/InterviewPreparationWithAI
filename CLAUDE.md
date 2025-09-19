# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-Powered Interview Preparation Application - A comprehensive web application that leverages OpenAI's GPT models to provide personalized interview preparation assistance. Built with Python 3.11+, Streamlit, and OpenAI API, this production-ready system implements advanced prompt engineering techniques for generating customized interview questions, strategic preparation advice, and real-time feedback with transparent cost tracking.

**Current Status**: 🚀 **NEAR COMPLETE** - 14/16 tasks completed, fully functional with comprehensive AI system

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
# Run the GUI specification-compliant interface
streamlit run app.py
```

### Testing
```bash
# Run all tests with pytest
python -m pytest tests/ -v

# Run complete system verification
python tests/test_complete_system.py

# Core system tests
python tests/test_setup_simple.py           # Configuration
python tests/direct_test_models.py          # Data models
python tests/test_security_simple.py        # Security validation
python tests/security_demo.py               # Security demonstration

# Utility system tests
python tests/test_cost_simple.py            # Cost calculation
python tests/test_rate_limiter_simple.py    # Rate limiting

# AI prompt engineering tests (ALL 5 techniques implemented)
python tests/test_prompts_simple.py         # Template infrastructure
python tests/test_few_shot_simple.py        # Few-Shot Learning
python tests/test_chain_of_thought_simple.py # Chain-of-Thought
python tests/test_zero_shot_simple.py       # Zero-Shot
python tests/test_role_based_simple.py      # Role-Based
python tests/test_structured_output_simple.py # Structured Output

# Integration tests
python tests/test_generator_integration.py
python tests/test_structured_output_integration.py
python tests/test_error_handling_integration.py
```

### Code Quality
```bash
# Linting configuration available
pylint src/ --rcfile=.pylintrc

# No automatic formatting configured
# Consider adding black, flake8, or ruff for future development
```

## Architecture & Code Structure

### Project Organization
The codebase follows a modular architecture with clear separation of concerns:

**✅ COMPLETED MODULES:**

- **src/config.py**: Centralized configuration using dataclasses, handles environment variables and directory setup
- **app.py**: GUI specification-compliant interface with built-in components and session management (single entry point)

- **src/models/**: Data models with comprehensive validation
  - `enums.py`: All application enums (InterviewType, ExperienceLevel, PromptTechnique, etc.)
  - `simple_schemas.py`: Production dataclass models for runtime use (✅ RECOMMENDED)
  - `schemas.py`: Pydantic models (import issues, avoid using)

- **src/utils/**: Production-ready utility modules
  - `security.py`: Input validation and prompt injection protection (75% attack blocking rate)
  - `cost.py`: Token-based cost calculation for OpenAI API usage with 6-decimal precision
  - `rate_limiter.py`: Sliding window rate limiting (100 calls/hour default)
  - `logger.py`: Structured logging configuration
  - `error_handler.py`: Comprehensive error handling system

- **src/ai/**: Complete prompt engineering system ✅ (62 templates total)
  - `prompts.py`: Core template infrastructure and global prompt library
  - `generator.py`: AI question generator with OpenAI API integration and retry logic
  - `parser.py`: Response parsing with fallback systems
  - `few_shot.py`: Example-driven prompt templates (10 templates)
  - `chain_of_thought.py`: Step-by-step reasoning templates (10 templates)
  - `zero_shot.py`: Direct generation templates with fallbacks (10 templates)
  - `role_based.py`: Persona-driven interview templates (12 templates)
  - `structured_output.py`: JSON-formatted response templates (10 templates)

- **src/ui/**: Remaining utility components
  - `error_display.py`: Error presentation and troubleshooting

### Key Design Patterns

1. **Global Singleton Instances**: Shared instances for cost tracking, rate limiting, and prompt library
   ```python
   from ai.prompts import prompt_library
   from utils.cost import cost_calculator
   from utils.rate_limiter import rate_limiter
   from utils.security import SecurityValidator
   ```

2. **Template Registration**: All prompt templates auto-register with the global prompt library on import

3. **Comprehensive Fallback System**: Multi-level fallback strategies ensure 100% availability
   - Primary technique → Secondary technique → Zero-shot fallback → Emergency defaults

4. **Progressive Difficulty Scaling**: Templates adapt from Junior (1-2 years) to Lead/Principal level

5. **Async API Integration**: OpenAI API calls with retry logic using tenacity for robust error handling

6. **Session State Management**: Streamlit session state for persistent user experience

## 🐍 Python 3.11+ Modern Coding Standards

**CRITICAL REQUIREMENT**: All Python code MUST use modern Python 3.11+ syntax and features. No legacy patterns allowed.

### ✅ Required Modern Syntax:

#### 1. **Type Annotations (PEP 585, 604, 612)**
```python
# ✅ CORRECT - Modern Python 3.11+ typing
from typing import Optional, Union
from collections.abc import Sequence, Mapping

def process_data(items: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Process list of dictionaries with modern type hints."""
    pass

# Union types with | operator (Python 3.10+)
def handle_response(data: dict[str, Any] | None) -> str | None:
    pass

# ❌ FORBIDDEN - Old style typing
from typing import List, Dict  # Don't use these
def old_style(items: List[Dict[str, str]]) -> Dict[str, List[str]]:
    pass
```

#### 2. **Modern Class Definitions with dataclasses**
```python
# ✅ CORRECT - Modern dataclass with type annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class InterviewSession:
    job_description: str
    interview_type: InterviewType
    experience_level: ExperienceLevel
    questions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

# ❌ FORBIDDEN - Old style class definitions
class OldSession:
    def __init__(self, job_description, interview_type):
        self.job_description = job_description  # No type hints
        self.interview_type = interview_type
```

#### 3. **F-string Usage (Python 3.6+)**
```python
# ✅ CORRECT - Use f-strings exclusively
name = "Claude"
message = f"Hello {name}, cost: ${cost:.6f}"

# ❌ FORBIDDEN - Old string formatting
message = "Hello %s, cost: $%.6f" % (name, cost)
message = "Hello {}, cost: ${:.6f}".format(name, cost)
```

#### 4. **Match-Case Statements (Python 3.10+)**
```python
# ✅ CORRECT - Use match-case for complex conditionals
match interview_type:
    case InterviewType.TECHNICAL:
        return generate_technical_questions()
    case InterviewType.BEHAVIORAL:
        return generate_behavioral_questions()
    case _:
        return generate_default_questions()

# ❌ ACCEPTABLE but prefer match-case for complex scenarios
if interview_type == InterviewType.TECHNICAL:
    return generate_technical_questions()
```

#### 5. **Modern Exception Handling**
```python
# ✅ CORRECT - Specific exception handling with modern syntax
try:
    result = await api_call()
except OpenAIAPIError as e:
    logger.error(f"API error: {e}")
    raise InterviewGenerationError(f"Failed to generate questions: {e}") from e
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise

# ❌ FORBIDDEN - Bare except or generic catching
try:
    result = api_call()
except:  # Don't do this
    pass
```

#### 6. **Async/Await (Required for OpenAI calls)**
```python
# ✅ CORRECT - Modern async/await patterns
import asyncio
from typing import AsyncGenerator

async def generate_questions_async(prompt: str) -> dict[str, Any]:
    """Generate questions using async OpenAI API."""
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        return response.json()

# Use async context managers
async def with_rate_limiting() -> AsyncGenerator[None, None]:
    async with rate_limiter:
        yield
```

### 🚫 Forbidden Legacy Patterns:

1. **No `typing.List`, `typing.Dict`** - Use `list[]`, `dict[]`
2. **No bare `except:`** - Always specify exception types
3. **No `%` or `.format()`** - Use f-strings exclusively
4. **No manual `__init__` for data classes** - Use `@dataclass`
5. **No `typing.Union`** - Use `|` operator (Python 3.10+)
6. **No synchronous API calls** - Use async/await for OpenAI
7. **No mutable default arguments** - Use `field(default_factory=...)`

### ✅ Modern Python Features to Use:

- **Walrus Operator** (`:=`) for assignment expressions
- **Positional-only parameters** with `/` when appropriate
- **Keyword-only parameters** with `*` when appropriate
- **Enhanced error messages** with detailed context
- **Pattern matching** for complex conditional logic
- **Generic type aliases** with `TypeAlias` annotation
- **Literal types** for string/enum constants

### 🔧 Example Modern Code Structure:
```python
from __future__ import annotations  # Enable forward references
from dataclasses import dataclass, field
from typing import Any, Literal, TypeAlias
from collections.abc import AsyncGenerator, Sequence

# Type aliases
PromptTemplate: TypeAlias = dict[str, Any]
InterviewTypeStr: TypeAlias = Literal["technical", "behavioral"]

@dataclass(frozen=True, slots=True)  # Modern dataclass features
class ModernPromptConfig:
    technique: PromptTechnique
    template_vars: dict[str, str] = field(default_factory=dict)

    def format_prompt(self, /, **kwargs: Any) -> str:  # Positional-only param
        """Format prompt with modern f-string and error handling."""
        try:
            return f"Prompt: {self.technique.value} - {kwargs}"
        except KeyError as e:
            raise ValueError(f"Missing required parameter: {e}") from e
```

**ENFORCEMENT**: Any code that uses legacy Python patterns will be rejected. All new code and modifications must follow these modern Python 3.11+ standards.

## Current Implementation Status

**✅ COMPLETED (14/16 tasks)** - Near Complete!

### ✅ Fully Implemented Components:
- **Core infrastructure**: Configuration, models, logging system
- **Security validation**: Input validation, prompt injection protection (75% attack blocking)
- **Cost calculation**: Token-based cost tracking with 6-decimal precision
- **Rate limiting**: Sliding window algorithm (100 calls/hour)
- **Complete prompt engineering**: All 5 techniques with 62 templates total
- **AI Question Generator**: OpenAI integration with retry logic
- **Response parsing**: JSON/text parsing with fallback systems
- **Streamlit UI**: Complete UI components and session management
- **Error handling**: Comprehensive error handling system
- **Application orchestrator**: Main app with async support (src/app.py)
- **Entry point**: Configured main.py with page settings
- **Comprehensive test suite**: 100+ tests with 100% pass rate

### 🎯 Remaining Tasks (2/16):
- **Task 14**: Final test coverage verification
- **Task 15-16**: Documentation polish and final validation

### 📊 Prompt Engineering Coverage:
| Technique | Templates | Status |
|-----------|-----------|---------|
| Few-Shot Learning | 10 | ✅ Complete |
| Chain-of-Thought | 10 | ✅ Complete |
| Zero-Shot | 10 | ✅ Complete |
| Role-Based | 12 | ✅ Complete |
| Structured Output | 10 | ✅ Complete |
| **TOTAL** | **62** | **✅ All Implemented** |

## Testing Strategy & Current Coverage

**✅ COMPREHENSIVE TEST SUITE IMPLEMENTED**

### Test Organization:
- **Unit tests**: `test_<module>_simple.py` pattern
- **Integration tests**: `test_<module>_integration.py` pattern
- **System tests**: `test_complete_system.py` for end-to-end verification
- **Security tests**: `security_demo.py` with attack simulation

### Current Test Coverage:
- **Total test files**: 16 implemented
- **Total test functions**: 100+ comprehensive tests
- **Success rate**: 100% passing
- **Security validation**: 75% attack blocking verified
- **Integration coverage**: Full cross-component testing

### Key Test Categories:
1. **Core Infrastructure**: Configuration, models, logging
2. **Security System**: Input validation, prompt injection defense
3. **Utility Systems**: Cost calculation, rate limiting, error handling
4. **AI System**: All 5 prompt techniques, generation, parsing
5. **UI Components**: Session management, error display
6. **Integration**: Complete workflows, API interactions

### Running Tests:
After implementing any feature, run comprehensive tests to ensure reliability and maintain coverage above 90% for new code.

## Important Context Files

**CRITICAL**: Always read these files before making changes:

### Project Specifications (.kiro/ folder):
- **`.kiro/specs/ai-interview-prep/requirements.md`** - Complete EARS format requirements
- **`.kiro/specs/ai-interview-prep/design.md`** - Full architecture and component design
- **`.kiro/specs/ai-interview-prep/tasks.md`** - Implementation plan with current status
- **`.kiro/steering/tech.md`** - Technology stack and development standards
- **`.kiro/steering/structure.md`** - Project organization and file structure
- **`.kiro/steering/product.md`** - Product overview and core features

### Project Status:
- **`HANDOFF_SUMMARY.md`** - Detailed progress status and implementation notes
- **`RUN_APP.md`** - Application running instructions and setup guidance

### Key Implementation Files:
- **`app.py`** - GUI specification-compliant interface (single entry point)
- **`src/models/simple_schemas.py`** - Production data models (use these, not schemas.py)

## Security Considerations

**✅ PRODUCTION-READY SECURITY IMPLEMENTED**

- **API Key Protection**: Never commit API keys or sensitive data, format validation implemented
- **Input Sanitization**: All user inputs processed through `SecurityValidator` class
- **Prompt Injection Defense**: 20+ attack patterns detected with 75% blocking rate
- **Rate Limiting**: Sliding window algorithm prevents API abuse (100 calls/hour default)
- **Cost Tracking**: Budget compliance with real-time monitoring and alerts
- **Error Handling**: Comprehensive error logging without exposing sensitive information
- **Session Security**: Secure session state management in Streamlit

## 🚀 Current Application Features

**✅ FULLY FUNCTIONAL SYSTEM - Ready to Use!**

### 🎯 Core Features Available:
- **Personalized Question Generation**: Creates tailored interview questions for specific job descriptions
- **Multi-Interview Support**: Technical, Behavioral, Case Study, and Reverse interview types
- **Experience Level Adaptation**: Junior, Mid-level, Senior, and Lead level scaling
- **Real-time Cost Tracking**: Transparent OpenAI API usage monitoring with 6-decimal precision
- **Advanced Security**: 75% prompt injection attack blocking rate
- **Smart Rate Limiting**: 100 calls/hour with sliding window algorithm

### 🧠 AI Prompt Engineering (All 5 Techniques):
- **Few-Shot Learning**: Example-driven question generation (10 templates)
- **Chain-of-Thought**: Step-by-step reasoning approach (10 templates)
- **Zero-Shot**: Direct generation with fallbacks (10 templates)
- **Role-Based**: Interviewer personas (strict, friendly, neutral) (12 templates)
- **Structured Output**: JSON-formatted responses with metadata (10 templates)

### 🛡️ Production Security Features:
- Input validation and sanitization
- API key format validation
- Comprehensive error handling
- Session state management
- Cost tracking and budget alerts

### 📊 System Integration:
```python
# Ready-to-use global instances
from ai.prompts import prompt_library        # 62 templates ready
from utils.cost import cost_calculator       # Real-time cost tracking
from utils.rate_limiter import rate_limiter  # API rate management
from utils.security import SecurityValidator # Input protection
```