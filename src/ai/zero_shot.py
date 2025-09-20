"""
Zero-Shot prompt implementation for interview question generation.
Provides direct, concise prompts for immediate question generation without examples or reasoning.
"""
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

                Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",
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
                Create questions that test intermediate programming skills, system design thinking, performance optimization, and best practices. 
                Questions should be appropriate for someone with 3-5 years of experience and include both technical depth and practical application scenarios.
                Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",
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

Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",
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

Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",
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

            Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",
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

                Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",

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

                Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",

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

                Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",

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


# Initialize Zero-Shot templates when module is imported
ZeroShotPrompts.register_all_templates()
