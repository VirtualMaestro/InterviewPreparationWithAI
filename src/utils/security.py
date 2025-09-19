"""
Security validation system for AI Interview Prep Application
Provides input validation, sanitization, and prompt injection protection
"""
import html
import logging
import re
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of security validation"""
    is_valid: bool
    cleaned_text: str
    warnings: list[str]
    blocked_patterns: list[str]

class SecurityValidator:
    """
    Comprehensive security validator for user inputs
    Handles length validation, content sanitization, and prompt injection prevention
    """

    # Configuration constants
    MAX_INPUT_LENGTH = 5000
    MIN_INPUT_LENGTH = 10

    # Prompt injection patterns (case-insensitive)
    PROMPT_INJECTION_PATTERNS: list[str] = [
        # Direct instruction attempts
        r"ignore\s+previous\s+instructions?",
        r"ignore\s+all\s+previous\s+instructions?",
        r"forget\s+previous\s+instructions?",
        r"disregard\s+previous\s+instructions?",

        # System override attempts
        r"system\s*:\s*you\s+are\s+now",
        r"system\s*:\s*act\s+as",
        r"system\s*:\s*pretend\s+to\s+be",
        r"you\s+are\s+no\s+longer",
        r"new\s+instructions?\s*:",

        # Role manipulation
        r"act\s+as\s+if\s+you\s+are",
        r"pretend\s+you\s+are",
        r"roleplay\s+as",
        r"simulate\s+being",

        # Output manipulation
        r"output\s+only",
        r"respond\s+with\s+only",
        r"say\s+nothing\s+but",
        r"print\s+only",

        # Jailbreak attempts
        r"jailbreak",
        r"dan\s+mode",
        r"developer\s+mode",
        r"god\s+mode",

        # Encoding attempts
        r"base64",
        r"rot13",
        r"hex\s+encoded?",

        # Template injection
        r"\{\{\s*.*\s*\}\}",
        r"\$\{.*\}",

        # Code execution attempts
        r"exec\s*\(",
        r"eval\s*\(",
        r"__import__",
        r"subprocess",
        r"os\.system",
    ]

    # HTML/Script injection patterns
    HTML_SCRIPT_PATTERNS: list[str] = [
        r"<script[^>]*>.*?</script>",
        r"<iframe[^>]*>.*?</iframe>",
        r"javascript\s*:",
        r"data\s*:\s*text/html",
        r"vbscript\s*:",
        r"on\w+\s*=",  # Event handlers like onclick, onload
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>",
        r"<form[^>]*>.*?</form>",
    ]

    # Suspicious content patterns
    SUSPICIOUS_PATTERNS: list[str] = [
        r"password",
        r"credit\s+card",
        r"social\s+security",
        r"ssn",
        r"api\s+key",
        r"secret\s+key",
        r"private\s+key",
        r"token",
        r"bearer\s+",
    ]

    # Check for placeholder values
    PLACEHOLDER_PATTERNS: list[str] = [
        "your_api_key_here",
        "your_openai_api_key",
        "sk-your-actual-api-key",
        "sk-test",
        "sk-fake",
        "sk-placeholder"
    ]

    @classmethod
    def validate_input(cls, text: str, field_name: str = "input") -> ValidationResult:
        """
        Comprehensive input validation and sanitization

        Args:
            text: Input text to validate
            field_name: Name of the field being validated (for error messages)

        Returns:
            ValidationResult with validation status and cleaned text
        """
        warnings: list[Any] = []
        blocked_patterns: list[Any] = []

        # Basic validation
        if not text or not isinstance(text, str):
            return ValidationResult(
                is_valid=False,
                cleaned_text="",
                warnings=[f"{field_name} cannot be empty"],
                blocked_patterns=[]
            )

        # Strip whitespace
        text = text.strip()

        # Length validation
        if len(text) < cls.MIN_INPUT_LENGTH:
            return ValidationResult(
                is_valid=False,
                cleaned_text=text,
                warnings=[
                    f"{field_name} must be at least {cls.MIN_INPUT_LENGTH} characters"],
                blocked_patterns=[]
            )

        if len(text) > cls.MAX_INPUT_LENGTH:
            return ValidationResult(
                is_valid=False,
                cleaned_text=text[:cls.MAX_INPUT_LENGTH],
                warnings=[
                    f"{field_name} too long. Maximum {cls.MAX_INPUT_LENGTH} characters"],
                blocked_patterns=[]
            )

        # Check for prompt injection patterns
        text_lower = text.lower()
        for pattern in cls.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE):
                blocked_patterns.append(pattern)
                logger.warning(f"Prompt injection attempt detected: {pattern}")

        # Check for HTML/Script injection
        for pattern in cls.HTML_SCRIPT_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL):
                blocked_patterns.append(pattern)
                logger.warning(
                    f"HTML/Script injection attempt detected: {pattern}")

        # Check for suspicious content (warnings, not blocks)
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                warnings.append(
                    f"Potentially sensitive content detected: {pattern}")

        # If any blocking patterns found, reject input
        if blocked_patterns:
            return ValidationResult(
                is_valid=False,
                cleaned_text="",
                warnings=[f"Input contains potentially harmful content"],
                blocked_patterns=blocked_patterns
            )

        # Sanitize the text
        cleaned_text = cls._sanitize_text(text)

        return ValidationResult(
            is_valid=True,
            cleaned_text=cleaned_text,
            warnings=warnings,
            blocked_patterns=[]
        )

    @classmethod
    def _sanitize_text(cls, text: str) -> str:
        """
        Sanitize text by removing/escaping potentially harmful content

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        # HTML escape
        text = html.escape(text)

        # Remove HTML tags (after escaping to handle nested tags)
        text = re.sub(r'<[^>]+>', '', text)

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove null bytes and control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

        # Normalize unicode
        text = text.encode('utf-8', errors='ignore').decode('utf-8')

        return text.strip()

    @classmethod
    def validate_api_key(cls, api_key: str) -> ValidationResult:
        """
        Validate OpenAI API key format

        Args:
            api_key: API key to validate

        Returns:
            ValidationResult for API key
        """
        result: ValidationResult = ValidationResult(False, "", [], [])

        if not api_key:
            result.warnings.append("API key is required")
            return result

        # Check format
        if not api_key.startswith("sk-"):
            result.warnings.append("Invalid API key format. OpenAI keys should start with 'sk-'")
            return result

        # Check length (OpenAI keys are typically 51 characters)
        api_len = len(api_key)
        too_short: bool = api_len < 48
        too_long: bool = api_len > 164

        if too_short or too_long:
            too_much: str = "short" if too_short else "long"
            result.warnings.append(F"API key seems unusually {too_much}")
            return result

        for pattern in cls.PLACEHOLDER_PATTERNS:
            if pattern in api_key.lower():
                result.warnings.append("Please replace placeholder API key with your actual OpenAI API key")
                result.blocked_patterns=[pattern]
                return result

        result.is_valid = True
        result.cleaned_text = api_key.strip()

        return result
