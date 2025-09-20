"""
Prompt template infrastructure for AI interview question generation.
Provides template management, variable substitution, and technique selection.
"""
from dataclasses import dataclass, field
from typing import Any

from src.models.enums import ExperienceLevel, InterviewType, PromptTechnique


@dataclass
class PromptTemplate:
    """
    Template for AI prompts with variable substitution support.
    Supports dynamic variable replacement and technique-specific formatting.
    """
    name: str
    technique: PromptTechnique
    interview_type: InterviewType
    experience_level: ExperienceLevel
    template: str
    variables: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Extract variables from template after initialization"""
        if not self.variables:
            self.variables = self._extract_variables()

    def _extract_variables(self) -> list[str]:
        """Extract variable names from template string"""
        import re

        # Find all {variable_name} patterns, but exclude double braces {{}} used in JSON examples
        # First, temporarily replace double braces to avoid matching them
        temp_template = self.template.replace(
            '{{', '__DOUBLE_OPEN__').replace('}}', '__DOUBLE_CLOSE__')

        # Find all {variable_name} patterns
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, temp_template)

        # Filter out any matches that are part of JSON structure or contain newlines/complex content
        variables = []
        for match in matches:
            # Only include simple variable names (alphanumeric, underscore, no spaces or special chars)
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', match.strip()):
                variables.append(match.strip())

        return list(set(variables))  # Remove duplicates

class PromptLibrary:
    """
    Central library for managing prompt templates.

    Provides template selection, registration, and retrieval based on
    interview type, experience level, and prompt technique.
    """

    def __init__(self):
        """Initialize empty prompt library"""
        self.templates: dict[str, PromptTemplate] = {}

    def register_template(self, template: PromptTemplate) -> None:
        """
        Register a new prompt template.

        Args:
            template: PromptTemplate to register
        """
        key = self._generate_key(
            template.technique,
            template.interview_type,
            template.experience_level
        )
        self.templates[key] = template

    def get_template(
        self,
        technique: PromptTechnique,
        interview_type: InterviewType,
        experience_level: ExperienceLevel
    ) -> PromptTemplate:
        """
        Get template by technique, interview type, and experience level.

        Args:
            technique: Prompt engineering technique
            interview_type: Type of interview
            experience_level: Experience level (optional)

        Returns:
            PromptTemplate if found, None otherwise
        """
        # Try exact match first
        key = self._generate_key(technique, interview_type, experience_level)
        return self.templates[key]

    #*********
    def _generate_key(
        self,
        technique: PromptTechnique,
        interview_type: InterviewType,
        experience_level: ExperienceLevel) -> str:
    
        """Generate unique key for template storage"""
        return f"{technique.value}_{interview_type.value}_{experience_level.value}"


# Global prompt library instance
prompt_library = PromptLibrary()
