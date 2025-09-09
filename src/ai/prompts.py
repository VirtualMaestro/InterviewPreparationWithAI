"""
Prompt template infrastructure for AI interview question generation.
Provides template management, variable substitution, and technique selection.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from models.enums import ExperienceLevel, InterviewType, PromptTechnique


@dataclass
class PromptTemplate:
    """
    Template for AI prompts with variable substitution support.

    Supports dynamic variable replacement and technique-specific formatting.
    """
    name: str
    technique: PromptTechnique
    interview_type: InterviewType
    experience_level: Optional[ExperienceLevel]
    template: str
    variables: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Extract variables from template after initialization"""
        if not self.variables:
            self.variables = self._extract_variables()

    def _extract_variables(self) -> List[str]:
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

    def format(self, **kwargs) -> str:
        """
        Format template with provided variables.

        Args:
            **kwargs: Variable values for substitution

        Returns:
            Formatted prompt string

        Raises:
            ValueError: If required variables are missing
        """
        missing_vars = [var for var in self.variables if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")

        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Template formatting error: {e}")

    def validate_variables(self, variables: Dict[str, Any]) -> bool:
        """
        Validate that all required variables are provided.

        Args:
            variables: Dictionary of variable values

        Returns:
            True if all variables are present, False otherwise
        """
        return all(var in variables for var in self.variables)

    def get_sample_variables(self) -> Dict[str, str]:
        """
        Get sample variable values for testing.

        Returns:
            Dictionary with sample values for all variables
        """
        samples = {
            'job_description': 'Senior Python Developer with Django and REST API experience',
            'interview_type': 'Technical',
            'experience_level': 'Senior',
            'question_count': '5',
            'company_name': 'TechCorp',
            'role_title': 'Senior Software Engineer',
            'specific_skills': 'Python, Django, PostgreSQL, REST APIs',
            'years_experience': '5-7',
            'interviewer_persona': 'friendly',
            'difficulty_level': 'advanced'
        }

        return {var: samples.get(var, f'sample_{var}') for var in self.variables}


class PromptLibrary:
    """
    Central library for managing prompt templates.

    Provides template selection, registration, and retrieval based on
    interview type, experience level, and prompt technique.
    """

    def __init__(self):
        """Initialize empty prompt library"""
        self.templates: Dict[str, PromptTemplate] = {}
        self._initialize_default_templates()

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
        experience_level: Optional[ExperienceLevel] = None
    ) -> Optional[PromptTemplate]:
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
        if key in self.templates:
            return self.templates[key]

        # Try without experience level (generic template)
        generic_key = self._generate_key(technique, interview_type, None)
        if generic_key in self.templates:
            return self.templates[generic_key]

        return None

    def list_templates(
        self,
        technique: Optional[PromptTechnique] = None,
        interview_type: Optional[InterviewType] = None
    ) -> List[PromptTemplate]:
        """
        List templates matching optional filters.

        Args:
            technique: Filter by technique (optional)
            interview_type: Filter by interview type (optional)

        Returns:
            List of matching templates
        """
        templates = list(self.templates.values())

        if technique:
            templates = [t for t in templates if t.technique == technique]

        if interview_type:
            templates = [
                t for t in templates if t.interview_type == interview_type]

        return templates

    def get_available_techniques(self, interview_type: InterviewType) -> List[PromptTechnique]:
        """
        Get available prompt techniques for an interview type.

        Args:
            interview_type: Interview type to check

        Returns:
            List of available techniques
        """
        techniques = set()
        for template in self.templates.values():
            if template.interview_type == interview_type:
                techniques.add(template.technique)

        return list(techniques)

    def _generate_key(
        self,
        technique: PromptTechnique,
        interview_type: InterviewType,
        experience_level: Optional[ExperienceLevel]
    ) -> str:
        """Generate unique key for template storage"""
        exp_level = experience_level.value if experience_level else "generic"
        return f"{technique.value}_{interview_type.value}_{exp_level}"

    def _initialize_default_templates(self) -> None:
        """Initialize library with default prompt templates"""
        # This will be populated by individual technique implementations
        # in subsequent tasks (6.2 through 6.6)
        pass

    def get_template_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about all templates.

        Returns:
            Dictionary with template statistics and information
        """
        total_templates = len(self.templates)
        techniques_count = {}
        interview_types_count = {}

        for template in self.templates.values():
            # Count by technique
            tech = template.technique.value
            techniques_count[tech] = techniques_count.get(tech, 0) + 1

            # Count by interview type
            int_type = template.interview_type.value
            interview_types_count[int_type] = interview_types_count.get(
                int_type, 0) + 1

        return {
            "total_templates": total_templates,
            "techniques": techniques_count,
            "interview_types": interview_types_count,
            "template_keys": list(self.templates.keys())
        }

    def validate_template_coverage(self) -> Dict[str, Any]:
        """
        Validate that all required combinations have templates.

        Returns:
            Dictionary with coverage analysis
        """
        required_combinations = []
        missing_combinations = []

        # Generate all required combinations
        for technique in PromptTechnique:
            for interview_type in InterviewType:
                combo = (technique, interview_type)
                required_combinations.append(combo)

                # Check if template exists
                template = self.get_template(technique, interview_type)
                if not template:
                    missing_combinations.append(combo)

        coverage_percent = (
            (len(required_combinations) - len(missing_combinations)) /
            len(required_combinations) * 100
        )

        return {
            "total_combinations": len(required_combinations),
            "covered_combinations": len(required_combinations) - len(missing_combinations),
            "missing_combinations": [
                f"{tech.value}_{int_type.value}"
                for tech, int_type in missing_combinations
            ],
            "coverage_percent": round(coverage_percent, 2)
        }


# Global prompt library instance
prompt_library = PromptLibrary()
