# Project Structure & Organization

## Directory Layout

```
InterviewPreparationWithAI/
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore patterns
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
├── main.py                  # Streamlit application entry point
├── docs/                    # Documentation files
│   └── technical-spec-markdown.md
├── exports/                 # Generated content exports
├── logs/                    # Application log files
│   └── app_YYYYMMDD.log
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_*.py           # Individual test modules
│   └── debug_test.py       # Debug and validation scripts
└── src/                    # Main application source code
    ├── __init__.py
    ├── config.py           # Application configuration
    ├── pyproject.toml      # Project metadata
    ├── ai/                 # AI and prompt engineering
    │   └── __init__.py
    ├── models/             # Data models and schemas
    │   ├── __init__.py
    │   ├── schemas.py      # Pydantic models
    │   ├── enums.py        # Enumeration definitions
    │   └── simple_schemas.py
    ├── utils/              # Utility functions
    │   ├── __init__.py
    │   └── logger.py       # Logging configuration
    ├── ui/                 # User interface components
    │   └── __init__.py
    ├── exports/            # Export functionality
    └── logs/               # Log utilities
```

## Module Organization Principles

### Core Application (`src/`)
- **Single source of truth** for all application logic
- Each subdirectory represents a distinct functional area
- All modules must include `__init__.py` for proper Python packaging

### AI Module (`src/ai/`)
- Contains prompt engineering implementations
- Question generation logic
- AI model interaction and response processing
- Should include: `generator.py`, `prompts.py`, `techniques.py`

### Models Module (`src/models/`)
- **Pydantic models** for data validation and serialization
- **Enums** for consistent value definitions across the application
- Type-safe data structures with comprehensive validation
- Current files: `schemas.py`, `enums.py`, `simple_schemas.py`

### Utils Module (`src/utils/`)
- Cross-cutting concerns and helper functions
- Security validation, cost calculation, rate limiting
- Logging setup and configuration
- Should include: `security.py`, `cost.py`, `rate_limiter.py`

### UI Module (`src/ui/`)
- Streamlit component definitions
- User interface logic separated from business logic
- Reusable UI components and layouts
- Should include: `components.py`

## File Naming Conventions

### Python Files
- Use **snake_case** for all Python files and directories
- Descriptive names that indicate functionality
- Test files prefixed with `test_`
- Debug/utility scripts clearly labeled

### Configuration Files
- `.env.example` for environment variable templates
- `config.py` for centralized application configuration
- `pyproject.toml` for project metadata and dependencies

### Generated Content
- **logs/** directory for application logs with date stamps
- **exports/** directory for user-generated content exports
- Automatic directory creation in configuration setup

## Import Structure

### Relative Imports
```python
# Within src/ modules, use relative imports
from .models.schemas import AISettings
from .utils.logger import setup_logging
```

### Absolute Imports
```python
# From external modules or tests
from src.models.enums import InterviewType
from src.config import Config
```

### Third-party Dependencies
```python
# Group imports: standard library, third-party, local
import os
from pathlib import Path

import streamlit as st
from pydantic import BaseModel

from src.models.schemas import Question
```

## Testing Organization

### Test Structure
- Mirror the `src/` directory structure in `tests/`
- One test file per source module
- Integration tests for complete workflows
- Debug scripts for development validation

### Test File Patterns
- `test_models.py` - Data model validation
- `test_config.py` - Configuration testing
- `debug_test.py` - Development debugging
- `validate_models.py` - Schema validation scripts