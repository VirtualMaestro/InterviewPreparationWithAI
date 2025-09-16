"""
Zero-Shot prompt implementation for interview question generation.
Provides direct, concise prompts for immediate question generation without examples or reasoning.
"""
from typing import Any

from src.models.enums import ExperienceLevel, InterviewType, PromptTechnique

from .prompts import PromptTemplate, prompt_library


class ZeroShotPrompts:
    """
    Zero-Shot prompt templates for direct question generation.

    Provides concise, focused prompts that generate questions immediately
    without examples or step-by-step reasoning. Serves as fallback when
    other techniques fail or when quick generation is needed.
    """

    @staticmethod
    def register_all_templates() -> None:
        """Register all Zero-Shot templates with the prompt library"""

        # Technical Interview Templates
        ZeroShotPrompts._register_technical_templates()

        # Behavioral Interview Templates
        ZeroShotPrompts._register_behavioral_templates()

        # Case Study Interview Templates
        ZeroShotPrompts._register_case_study_templates()

        # Reverse Interview Templates (Questions for Employer)
        ZeroShotPrompts._register_reverse_templates()

    @staticmethod
    def _register_technical_templates() -> None:
        """Register Zero-Shot templates for technical interviews"""

        # Junior Level Technical
        junior_technical = PromptTemplate(
            name="zero_shot_technical_junior",
            technique=PromptTechnique.ZERO_SHOT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.JUNIOR,
            template="""Generate {question_count} technical interview questions for a {experience_level} developer position.

Job Description: {job_description}

Create questions that test fundamental programming concepts, basic problem-solving skills, and practical knowledge of the technologies mentioned. Questions should be appropriate for someone with 1-2 years of experience and focus on core concepts rather than advanced system design.

Questions:""",
            metadata={
                "difficulty": "beginner",
                "approach": "direct_generation",
                "focus": "fundamental_concepts",
                "fallback_priority": "high"
            }
        )

        # Mid-Level Technical
        mid_technical = PromptTemplate(
            name="zero_shot_technical_mid",
            technique=PromptTechnique.ZERO_SHOT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.MID,
            template="""Generate {question_count} technical interview questions for a {experience_level} developer position.

Job Description: {job_description}

Create questions that test intermediate programming skills, system design thinking, performance optimization, and best practices. Questions should be appropriate for someone with 3-5 years of experience and include both technical depth and practical application scenarios.

Questions:""",
            metadata={
                "difficulty": "intermediate",
                "approach": "direct_generation",
                "focus": "system_design_and_optimization",
                "fallback_priority": "high"
            }
        )

        # Senior Level Technical
        senior_technical = PromptTemplate(
            name="zero_shot_technical_senior",
            technique=PromptTechnique.ZERO_SHOT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR,
            template="""Generate {question_count} technical interview questions for a {experience_level} developer position.

Job Description: {job_description}

Create questions that test advanced system architecture, scalability, technical leadership, and strategic decision-making. Questions should be appropriate for someone with 5+ years of experience and include complex problem-solving scenarios that demonstrate senior-level expertise.

Questions:""",
            metadata={
                "difficulty": "advanced",
                "approach": "direct_generation",
                "focus": "architecture_and_leadership",
                "fallback_priority": "high"
            }
        )

        # Lead Level Technical
        lead_technical = PromptTemplate(
            name="zero_shot_technical_lead",
            technique=PromptTechnique.ZERO_SHOT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.LEAD,
            template="""Generate {question_count} technical interview questions for a {experience_level} engineer position.

Job Description: {job_description}

Create questions that test technical vision, organizational impact, strategic planning, and executive-level technical leadership. Questions should be appropriate for principal/staff level positions and focus on transformation, culture building, and industry influence.

Questions:""",
            metadata={
                "difficulty": "expert",
                "approach": "direct_generation",
                "focus": "strategic_leadership",
                "fallback_priority": "high"
            }
        )

        # Register all technical templates
        for template in [junior_technical, mid_technical, senior_technical, lead_technical]:
            prompt_library.register_template(template)

    @staticmethod
    def _register_behavioral_templates() -> None:
        """Register Zero-Shot templates for behavioral interviews"""

        # Junior Level Behavioral
        junior_behavioral = PromptTemplate(
            name="zero_shot_behavioral_junior",
            technique=PromptTechnique.ZERO_SHOT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.JUNIOR,
            template="""Generate {question_count} behavioral interview questions for a {experience_level} position.

            Job Description: {job_description}

            Create behavioral questions that assess learning ability, collaboration skills, communication, and professional growth. Questions should be appropriate for someone with 1-2 years of experience and focus on individual contributor scenarios.

            Questions:""",
            metadata={
                "difficulty": "entry_level",
                "approach": "direct_generation",
                "focus": "learning_and_collaboration",
                "fallback_priority": "high"
            }
        )

        # Mid-Level Behavioral
        mid_behavioral = PromptTemplate(
            name="zero_shot_behavioral_mid",
            technique=PromptTechnique.ZERO_SHOT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.MID,
            template="""Generate {question_count} behavioral interview questions for a {experience_level} position.

Job Description: {job_description}

Create behavioral questions that assess influence, project management, cross-team collaboration, and emerging leadership skills. Questions should be appropriate for someone with 3-5 years of experience and include scenarios involving multiple stakeholders.

Questions:""",
            metadata={
                "difficulty": "intermediate",
                "approach": "direct_generation",
                "focus": "influence_and_project_management",
                "fallback_priority": "high"
            }
        )

        # Senior Level Behavioral
        senior_behavioral = PromptTemplate(
            name="zero_shot_behavioral_senior",
            technique=PromptTechnique.ZERO_SHOT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.SENIOR,
            template="""Generate {question_count} behavioral interview questions for a {experience_level} position.

Job Description: {job_description}

Create behavioral questions that assess strategic thinking, mentoring, organizational impact, and leadership capabilities. Questions should be appropriate for someone with 5+ years of experience and focus on complex stakeholder management and team development.

Questions:""",
            metadata={
                "difficulty": "advanced",
                "approach": "direct_generation",
                "focus": "strategic_leadership_and_mentoring",
                "fallback_priority": "high"
            }
        )

        # Lead Level Behavioral
        lead_behavioral = PromptTemplate(
            name="zero_shot_behavioral_lead",
            technique=PromptTechnique.ZERO_SHOT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.LEAD,
            template="""Generate {question_count} behavioral interview questions for a {experience_level} position.

Job Description: {job_description}

Create behavioral questions that assess organizational transformation, executive communication, culture building, and strategic vision. Questions should be appropriate for principal/staff level positions and focus on large-scale impact and industry influence.

Questions:""",
            metadata={
                "difficulty": "expert",
                "approach": "direct_generation",
                "focus": "organizational_transformation",
                "fallback_priority": "high"
            }
        )

        # Register all behavioral templates
        for template in [junior_behavioral, mid_behavioral, senior_behavioral, lead_behavioral]:
            prompt_library.register_template(template)

    @staticmethod
    def _register_case_study_templates() -> None:
        """Register Zero-Shot templates for case study interviews"""

        # Generic Case Study
        case_study_generic = PromptTemplate(
            name="zero_shot_case_study_generic",
            technique=PromptTechnique.ZERO_SHOT,
            interview_type=InterviewType.CASE_STUDY,
            experience_level=None,  # Generic for all levels
            template="""Generate {question_count} case study interview questions for a {experience_level} position.

Job Description: {job_description}

Create realistic technical scenarios that test problem-solving methodology, analytical thinking, and practical application of skills. Present situations that allow candidates to demonstrate their approach to complex challenges relevant to this role.

Case Studies:""",
            metadata={
                "difficulty": "adaptive",
                "approach": "direct_generation",
                "focus": "problem_solving_scenarios",
                "fallback_priority": "medium"
            }
        )

        prompt_library.register_template(case_study_generic)

    @staticmethod
    def _register_reverse_templates() -> None:
        """Register Zero-Shot templates for reverse interviews"""

        # Generic Reverse Interview
        reverse_generic = PromptTemplate(
            name="zero_shot_reverse_generic",
            technique=PromptTechnique.ZERO_SHOT,
            interview_type=InterviewType.REVERSE,
            experience_level=None,  # Generic for all levels
            template="""Generate {question_count} thoughtful questions that a {experience_level} candidate should ask about this position.

Job Description: {job_description}

Create strategic questions that help the candidate evaluate the role, team, company culture, growth opportunities, and alignment with their career goals. Questions should demonstrate preparation and genuine interest in the position.

Questions for the Employer:""",
            metadata={
                "difficulty": "strategic",
                "approach": "direct_generation",
                "focus": "role_evaluation_and_career_alignment",
                "fallback_priority": "medium"
            }
        )

        prompt_library.register_template(reverse_generic)

    @staticmethod
    def get_fallback_template(interview_type: InterviewType, experience_level: ExperienceLevel) -> PromptTemplate:
        """
        Get Zero-Shot template as fallback when other techniques fail.

        Args:
            interview_type: Type of interview
            experience_level: Experience level (optional)

        Returns:
            Zero-Shot template for fallback use
        """
        template = prompt_library.get_template(
            PromptTechnique.ZERO_SHOT,
            interview_type,
            experience_level
        )

        if template is None:
            # Ultimate fallback - create a basic template on the fly
            template = ZeroShotPrompts.create_emergency_fallback(
                interview_type, experience_level)

        return template

    @staticmethod
    def create_emergency_fallback(interview_type: InterviewType, experience_level: ExperienceLevel) -> PromptTemplate:
        """
        Create an emergency fallback template when no Zero-Shot template exists.

        Args:
            interview_type: Type of interview
            experience_level: Experience level (optional)

        Returns:
            Emergency fallback template
        """
        exp_text = experience_level.value if experience_level else "candidate"

        emergency_template = PromptTemplate(
            name=f"emergency_fallback_{interview_type.value.lower().replace(' ', '_')}",
            technique=PromptTechnique.ZERO_SHOT,
            interview_type=interview_type,
            experience_level=experience_level,
            template=f"""Generate {{question_count}} {interview_type.value.lower()} interview questions for a {exp_text} position.

Job Description: {{job_description}}

Create appropriate questions that assess the candidate's skills and fit for this role.

Questions:""",
            metadata={
                "difficulty": "adaptive",
                "approach": "emergency_fallback",
                "focus": "basic_assessment",
                "fallback_priority": "emergency"
            }
        )

        return emergency_template

    @staticmethod
    def is_fallback_needed(primary_technique: PromptTechnique, interview_type: InterviewType, experience_level: ExperienceLevel ) -> bool:
        """
        Check if Zero-Shot fallback is needed when primary technique fails.

        Args:
            primary_technique: The technique that failed
            interview_type: Type of interview
            experience_level: Experience level (optional)

        Returns:
            True if Zero-Shot fallback should be used
        """
        if primary_technique == PromptTechnique.ZERO_SHOT:
            return False  # Already using Zero-Shot

        # Check if Zero-Shot template exists for this combination
        zero_shot_template = prompt_library.get_template(
            PromptTechnique.ZERO_SHOT,
            interview_type,
            experience_level
        )

        return zero_shot_template is not None

    @staticmethod
    def get_template_comparison_info() -> dict[str, Any]:
        """
        Get information comparing Zero-Shot templates with other techniques.

        Returns:
            Dictionary with comparison information
        """
        zero_shot_templates = prompt_library.list_templates(
            technique=PromptTechnique.ZERO_SHOT)
        all_templates = prompt_library.list_templates()

        # Calculate template lengths for comparison
        zero_shot_lengths = []
        other_technique_lengths = []

        for template in all_templates:
            sample_vars = template.get_sample_variables()
            formatted_length = len(template.format(**sample_vars))

            if template.technique == PromptTechnique.ZERO_SHOT:
                zero_shot_lengths.append(formatted_length)
            else:
                other_technique_lengths.append(formatted_length)

        avg_zero_shot_length = sum(
            zero_shot_lengths) / len(zero_shot_lengths) if zero_shot_lengths else 0
        avg_other_length = sum(other_technique_lengths) / \
            len(other_technique_lengths) if other_technique_lengths else 0

        return {
            "zero_shot_template_count": len(zero_shot_templates),
            "total_template_count": len(all_templates),
            "zero_shot_percentage": (len(zero_shot_templates) / len(all_templates) * 100) if all_templates else 0,
            "avg_zero_shot_length": round(avg_zero_shot_length),
            "avg_other_technique_length": round(avg_other_length),
            "length_ratio": round(avg_zero_shot_length / avg_other_length, 2) if avg_other_length > 0 else 0,
            "fallback_coverage": {
                interview_type.value: ZeroShotPrompts._check_fallback_coverage(
                    interview_type)
                for interview_type in InterviewType
            }
        }

    @staticmethod
    def _check_fallback_coverage(interview_type: InterviewType) -> dict[str, bool]:
        """Check fallback coverage for an interview type"""
        coverage = {}

        for level in ExperienceLevel:
            template = prompt_library.get_template(
                PromptTechnique.ZERO_SHOT,
                interview_type,
                level
            )
            coverage[level.value] = template is not None

        # Check generic template
        generic_template = prompt_library.get_template(
            PromptTechnique.ZERO_SHOT,
            interview_type,
            None
        )
        coverage["generic"] = generic_template is not None

        return coverage


# Initialize Zero-Shot templates when module is imported
ZeroShotPrompts.register_all_templates()
