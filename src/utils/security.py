"""
Security validation system for AI Interview Prep Application
Provides input validation, sanitization, and prompt injection protection
"""
import html
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of security validation"""
    is_valid: bool
    cleaned_text: str
    warnings: List[str]
    blocked_patterns: List[str]

    def __post_init__(self):
        """Ensure warnings and blocked_patterns are lists"""
        if self.warnings is None:
            self.warnings = []
        if self.blocked_patterns is None:
            self.blocked_patterns = []


class SecurityValidator:
    """
    Comprehensive security validator for user inputs
    Handles length validation, content sanitization, and prompt injection prevention
    """

    # Configuration constants
    MAX_INPUT_LENGTH = 5000
    MIN_INPUT_LENGTH = 10

    # Prompt injection patterns (case-insensitive)
    PROMPT_INJECTION_PATTERNS = [
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
    HTML_SCRIPT_PATTERNS = [
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
    SUSPICIOUS_PATTERNS = [
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
        warnings = []
        blocked_patterns = []

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
    def validate_job_description(cls, job_description: str) -> ValidationResult:
        """
        Specialized validation for job descriptions

        Args:
            job_description: Job description text

        Returns:
            ValidationResult for job description
        """
        result = cls.validate_input(job_description, "Job description")

        if result.is_valid:
            # Additional job description specific checks
            if len(result.cleaned_text.split()) < 5:
                result.warnings.append(
                    "Job description seems very short. Consider adding more details.")

            # Check for common job description elements
            job_keywords = ['experience', 'skills',
                            'requirements', 'responsibilities', 'qualifications']
            if not any(keyword in result.cleaned_text.lower() for keyword in job_keywords):
                result.warnings.append(
                    "Job description might be missing key elements (requirements, skills, etc.)")

        return result

    @classmethod
    def validate_api_key(cls, api_key: str) -> ValidationResult:
        """
        Validate OpenAI API key format

        Args:
            api_key: API key to validate

        Returns:
            ValidationResult for API key
        """
        warnings = []

        if not api_key:
            return ValidationResult(
                is_valid=False,
                cleaned_text="",
                warnings=["API key is required"],
                blocked_patterns=[]
            )

        # Check format
        if not api_key.startswith("sk-"):
            return ValidationResult(
                is_valid=False,
                cleaned_text="",
                warnings=[
                    "Invalid API key format. OpenAI keys should start with 'sk-'"],
                blocked_patterns=[]
            )

        # Check length (OpenAI keys are typically 51 characters)
        if len(api_key) < 40:
            warnings.append("API key seems unusually short")
        elif len(api_key) > 60:
            warnings.append("API key seems unusually long")

        # Check for placeholder values
        placeholder_patterns = [
            "your_api_key_here",
            "your_openai_api_key",
            "sk-your-actual-api-key",
            "sk-test",
            "sk-fake",
            "sk-placeholder"
        ]

        for pattern in placeholder_patterns:
            if pattern in api_key.lower():
                return ValidationResult(
                    is_valid=False,
                    cleaned_text="",
                    warnings=[
                        "Please replace placeholder API key with your actual OpenAI API key"],
                    blocked_patterns=[pattern]
                )

        return ValidationResult(
            is_valid=True,
            cleaned_text=api_key.strip(),
            warnings=warnings,
            blocked_patterns=[]
        )

    @classmethod
    def get_security_report(cls, validation_results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Generate a security report from multiple validation results

        Args:
            validation_results: List of validation results

        Returns:
            Security report dictionary
        """
        total_validations = len(validation_results)
        valid_inputs = sum(
            1 for result in validation_results if result.is_valid)
        total_warnings = sum(len(result.warnings)
                             for result in validation_results)
        total_blocks = sum(len(result.blocked_patterns)
                           for result in validation_results)

        # Collect all blocked patterns
        all_blocked_patterns = []
        for result in validation_results:
            all_blocked_patterns.extend(result.blocked_patterns)

        # Count pattern frequencies
        pattern_counts = {}
        for pattern in all_blocked_patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        return {
            "total_validations": total_validations,
            "valid_inputs": valid_inputs,
            "invalid_inputs": total_validations - valid_inputs,
            "success_rate": (valid_inputs / total_validations * 100) if total_validations > 0 else 0,
            "total_warnings": total_warnings,
            "total_blocks": total_blocks,
            "blocked_patterns": pattern_counts,
            "security_level": cls._calculate_security_level(total_blocks, total_warnings, total_validations)
        }

    @classmethod
    def _calculate_security_level(cls, blocks: int, warnings: int, total: int) -> str:
        """Calculate overall security level"""
        if total == 0:
            return "unknown"

        threat_ratio = (blocks + warnings * 0.5) / total

        if threat_ratio == 0:
            return "secure"
        elif threat_ratio < 0.1:
            return "low_risk"
        elif threat_ratio < 0.3:
            return "medium_risk"
        else:
            return "high_risk"
