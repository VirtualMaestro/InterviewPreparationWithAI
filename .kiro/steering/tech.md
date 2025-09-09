# Technology Stack & Development Guide

## Core Technologies

### Backend & Frontend
- **Python 3.11+** - Primary development language
- **Streamlit 1.49.1+** - Web application framework for rapid UI development
- **Pydantic 2.11.7+** - Data validation and settings management using Python type annotations

### AI Integration
- **OpenAI API 1.106.1+** - GPT-4o and GPT-5 model access
- **Tenacity 9.1.2+** - Retry logic and error handling for API calls
- **AsyncIO** - Asynchronous programming for improved performance

### Development & Testing
- **pytest 8.4.2+** - Testing framework
- **pytest-asyncio 1.1.0+** - Async testing support
- **python-dotenv 1.1.1+** - Environment variable management

## Project Architecture

### Configuration Management
- Centralized configuration in `src/config.py` using dataclasses
- Environment-based settings with `.env` files
- Validation and directory auto-creation in `__post_init__`

### Data Models
- **Pydantic models** in `src/models/schemas.py` for type safety and validation
- **Enums** in `src/models/enums.py` for consistent value definitions
- Comprehensive field validation with custom validators

### Security & Performance
- Input sanitization and prompt injection protection
- Rate limiting (100 calls/hour default)
- Cost tracking and token usage monitoring
- Structured logging with file and console handlers

## Common Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env with your OpenAI API key
```

### Development
```bash
# Run the application
streamlit run main.py

# Run tests
pytest tests/

# Run specific test file
pytest tests/test_models.py -v

# Check code formatting (if using black)
black src/ tests/
```

### Project Structure Commands
```bash
# View project structure
tree /f

# Create new module directories
mkdir src\new_module
echo. > src\new_module\__init__.py
```

## Development Standards

### Code Organization
- Use `src/` directory structure for all application code
- Separate concerns: `ai/`, `models/`, `utils/`, `ui/`
- Always include `__init__.py` files in Python packages

### Error Handling
- Use custom exceptions (e.g., `InterviewGenerationError`)
- Implement retry logic with exponential backoff using `tenacity`
- Comprehensive logging for debugging and monitoring

### Data Validation
- Use Pydantic models for all data structures
- Implement field validators for business logic
- Sanitize user inputs to prevent security issues