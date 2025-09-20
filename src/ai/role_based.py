"""
Role-Based prompt implementation for AI interview question generation.
Implements interviewer persona templates with company type integration.
"""
from ..models.enums import ExperienceLevel, InterviewType, PersonaRole, PromptTechnique
from .prompts import PromptTemplate, prompt_library


class RoleBasedPromptTemplate(PromptTemplate):
    """
    Extended PromptTemplate for Role-Based prompts with company context integration.
    """

    def __init__(self, persona: str, *args, **kwargs):
        """Initialize with persona information"""
        super().__init__(*args, **kwargs)
        self.persona = persona

    # def format(self, **kwargs) -> str:
    #     """
    #     Format template with company context integration.

    #     Args:
    #         **kwargs: Variable values for substitution

    #     Returns:
    #         Formatted prompt string with company context
    #     """
    #     # Add company context if company_type is provided
    #     if 'company_type' in kwargs:
    #         company_type = kwargs['company_type']
    #         if company_type in RoleBasedPrompts.COMPANY_TYPES:
    #             company_info = RoleBasedPrompts.COMPANY_TYPES[company_type]
    #             kwargs['company_context'] = f"""
    #                 Company Type: {company_type}
    #                 Culture: {company_info['culture']}
    #                 Values: {company_info['values']}
    #                 Interview Style: {company_info['interview_style']}"""
    #         else:
    #             kwargs['company_context'] = f"Company Type: {company_type}"
    #     else:
    #         kwargs['company_context'] = "Company context not specified"

    #     return super().format(**kwargs)


class RoleBasedPrompts:
    """
    Role-Based prompt engineering implementation.

    Creates interviewer persona templates (strict, friendly, neutral) with
    company type and personality trait integration for context-aware
    role adoption in question generation.
    """

    # Storage for role-based templates
    _role_templates: dict[str, RoleBasedPromptTemplate] = {}

    # Persona definitions with characteristics
    PERSONAS = {
        PersonaRole.STRICT.value: {
            "name": "Strict Interviewer",
            "description": "Detail-oriented, precise, and thorough interviewer who expects comprehensive answers",
            "tone": "formal and demanding",
            "focus": "technical accuracy and depth of knowledge"
        },
        PersonaRole.FRIENDLY.value: {
            "name": "Friendly Interviewer",
            "description": "Supportive, encouraging interviewer who creates a comfortable environment",
            "tone": "warm and encouraging",
            "focus": "candidate potential and collaborative skills"
        },
        PersonaRole.NEUTRAL.value: {
            "name": "Neutral Interviewer",
            "description": "Balanced, objective interviewer who maintains professional distance",
            "tone": "professional and balanced",
            "focus": "fair assessment and structured evaluation"
        }
    }

    # Company type definitions with culture and interview style
    COMPANY_TYPES = {
        "startup": {
            "culture": "fast-paced, innovative, flexible",
            "values": "adaptability, creativity, ownership",
            "interview_style": "informal, problem-solving focused"
        },
        "enterprise": {
            "culture": "structured, process-oriented, stable",
            "values": "reliability, scalability, compliance",
            "interview_style": "formal, methodology focused"
        },
        "tech_giant": {
            "culture": "competitive, data-driven, excellence-focused",
            "values": "innovation, scale, technical excellence",
            "interview_style": "rigorous, algorithm focused"
        },
        "consulting": {
            "culture": "client-focused, analytical, presentation-oriented",
            "values": "problem-solving, communication, business impact",
            "interview_style": "case-study heavy, communication focused"
        },
        "finance": {
            "culture": "risk-aware, detail-oriented, performance-driven",
            "values": "accuracy, compliance, quantitative skills",
            "interview_style": "precise, quantitative focused"
        }
    }

    # Persona-company compatibility recommendations
    PERSONA_COMPANY_COMPATIBILITY = {
        "strict": ["finance", "enterprise", "tech_giant"],
        "friendly": ["startup", "consulting"],
        "neutral": ["enterprise", "tech_giant", "consulting"]
    }

    @classmethod
    def initialize_templates(cls) -> None:
        """Initialize and register all Role-Based templates"""
        for persona in cls.PERSONAS.keys():
            for interview_type in InterviewType:
                template = cls._create_persona_template(persona, interview_type)
                # Store in our custom storage
                key = f"{persona}_{interview_type.value}"
                cls._role_templates[key] = template
                # Also register with prompt library for general access
                prompt_library.register_template(template)

    # @classmethod
    # def get_all_role_based_templates(cls) -> list[RoleBasedPromptTemplate]:
    #     """Get all role-based templates from custom storage"""
    #     return list(cls._role_templates.values())

    # @classmethod
    # def get_available_personas(cls) -> list[str]:
    #     """Get list of available interviewer personas"""
    #     return list(cls.PERSONAS.keys())

    # @classmethod
    # def get_persona_info(cls, persona: str) -> dict[str, str]:
    #     """Get detailed information about a persona"""
    #     if persona not in cls.PERSONAS:
    #         raise ValueError(f"Unknown persona: {persona}")
    #     return cls.PERSONAS[persona].copy()

    # @classmethod
    # def get_company_types(cls) -> list[str]:
    #     """Get list of available company types"""
    #     return list(cls.COMPANY_TYPES.keys())

    # @classmethod
    # def get_company_info(cls, company_type: str) -> dict[str, str]:
    #     """Get detailed information about a company type"""
    #     if company_type not in cls.COMPANY_TYPES:
    #         raise ValueError(f"Unknown company type: {company_type}")
    #     return cls.COMPANY_TYPES[company_type].copy()

    @classmethod
    def get_persona_template(cls, persona: str, interview_type: InterviewType) -> RoleBasedPromptTemplate:
        """Get template for specific persona and interview type"""
        # if persona not in cls.PERSONAS:
            # raise ValueError(f"Unknown persona: {persona}")

        key = f"{persona}_{interview_type.value}"
        return cls._role_templates[key]

    # @classmethod
    # def get_persona_company_compatibility(cls) -> dict[str, list[str]]:
    #     """Get persona-company compatibility recommendations"""
    #     return cls.PERSONA_COMPANY_COMPATIBILITY.copy()

    # @classmethod
    # def recommend_persona_for_company(cls, company_type: str) -> list[str]:
    #     """Recommend personas suitable for a company type"""
    #     if company_type not in cls.COMPANY_TYPES:
    #         raise ValueError(f"Unknown company type: {company_type}")

    #     recommended = []
    #     for persona, compatible_companies in cls.PERSONA_COMPANY_COMPATIBILITY.items():
    #         if company_type in compatible_companies:
    #             recommended.append(persona)

    #     # Always include neutral as a safe option
    #     if "neutral" not in recommended:
    #         recommended.append("neutral")

    #     return recommended

    @classmethod
    def _create_persona_template(cls, persona: str, interview_type: InterviewType) -> RoleBasedPromptTemplate:
        """Create a Role-Based template for specific persona and interview type"""
        persona_info = cls.PERSONAS[persona]

        # Generate template content based on persona and interview type
        template_content = cls._generate_template_content(persona, interview_type)

        # Create template name
        template_name = f"Role-Based {persona_info['name']} - {interview_type.value}"

        # Define metadata
        metadata = {
            "persona": persona,
            "interviewer_style": persona_info["tone"],
            "focus_areas": cls._get_persona_focus_areas(persona, interview_type),
            "personality_driven": True,
            "company_aware": True
        }

        return RoleBasedPromptTemplate(
            persona = persona,
            name = template_name,
            technique = PromptTechnique.ROLE_BASED,
            interview_type = interview_type,
            experience_level = ExperienceLevel.JUNIOR,  # Generic template
            template = template_content,
            metadata = metadata
        )

    # @classmethod
    # def get_company_context_for_template(cls, company_type: str) -> str:
    #     """Get company context information for template formatting"""
    #     if company_type not in cls.COMPANY_TYPES:
    #         return "Consider the company's unique culture and values in your interview approach."

    #     company_info = cls.COMPANY_TYPES[company_type]
    #     return f"""Company Culture: {company_info['culture']}
    #     Company Values: {company_info['values']}
    #     Interview Style: {company_info['interview_style']}"""

    @classmethod
    def _generate_template_content(cls, persona: str, interview_type: InterviewType) -> str:
        """Generate template content for persona and interview type"""
        persona_info = cls.PERSONAS[persona]

        # Base template structure - using regular string formatting to avoid f-string conflicts
        template_text = """You are a {} conducting a {} interview.

            INTERVIEWER PERSONA:
            - Name: {}
            - Style: {}
            - Focus: {}
            - Description: {}

            Adapt your interviewing style to match the company culture and values. Consider how this company type typically conducts interviews and tailor questions to reflect what this type of organization values most.

            CANDIDATE PROFILE:
            - Experience Level: {{experience_level}}
            - Target Role: Based on the job description below
            - Job Description: {{job_description}}

            {}

            INSTRUCTIONS:
            Generate {{question_count}} {} that reflect your {} interviewer persona and the company context. 

            {}

            Remember to maintain your {} interviewer persona throughout:
            {}

            Format your response as a numbered list of questions, followed by preparation recommendations that account for your interviewer style and the company culture.
            Important: Do not include in your response your greetings or other uneeded sentences. Only questions"""

        base_template = template_text.format(
            persona_info['name'],
            interview_type.value.lower(),
            persona_info['name'],
            persona_info['tone'],
            persona_info['focus'],
            persona_info['description'],
            cls._get_persona_specific_guidance(persona, interview_type),
            interview_type.value.lower(),
            persona,
            cls._get_interview_type_guidance(interview_type),
            persona,
            cls._get_persona_behavioral_guidance(persona)
        )

        return base_template

    @classmethod
    def _get_persona_specific_guidance(cls, persona: str, interview_type: InterviewType) -> str:
        """Get persona-specific guidance for question generation"""
        if interview_type == InterviewType.TECHNICAL:
            return cls._get_persona_technical_guidance(persona)
        
        return cls._get_persona_behavioral_guidance(persona)
     

    @classmethod
    def _get_persona_technical_guidance(cls, persona: str) -> str:
        """Get persona-specific technical interview guidance"""
        if persona == "strict":
            return """TECHNICAL APPROACH (Strict):
            - Ask detailed, precise technical questions that require comprehensive answers
            - Focus on edge cases, error handling, and optimization
            - Expect candidates to explain their reasoning step-by-step
            - Include follow-up questions that dig deeper into technical concepts
            - Emphasize best practices, code quality, and scalability considerations"""

        elif persona == "friendly":
            return """TECHNICAL APPROACH (Friendly):
            - Create a supportive environment while still challenging the candidate
            - Ask technical questions that allow candidates to showcase their strengths
            - Provide hints or guidance if candidates seem stuck
            - Focus on problem-solving approach rather than perfect solutions
            - Encourage candidates to think aloud and explain their thought process"""

        elif persona == "neutral":
            return """TECHNICAL APPROACH (Neutral):
            - Ask balanced technical questions that fairly assess competency
            - Maintain objectivity while evaluating technical skills
            - Focus on core competencies relevant to the role
            - Ask standard technical questions without leading the candidate
            - Evaluate both technical knowledge and problem-solving methodology"""

        return ""

    @classmethod
    def _get_persona_behavioral_guidance(cls, persona: str) -> str:
        """Get persona-specific behavioral interview guidance"""
        if persona == "strict":
            return """- Demand specific examples with measurable outcomes
- Press for details about challenges and how they were overcome
- Focus on accountability and ownership of results
- Ask follow-up questions to verify claims and dig deeper"""

        elif persona == "friendly":
            return """- Create a comfortable environment for sharing experiences
- Show genuine interest in the candidate's journey and growth
- Ask about learning experiences and personal development
- Encourage storytelling and provide positive reinforcement"""

        elif persona == "neutral":
            return """- Ask standard behavioral questions using the STAR method
- Maintain professional objectivity while gathering information
- Focus on relevant experiences that demonstrate required competencies
- Evaluate responses fairly without showing bias or preference"""

        return ""

    @classmethod
    def _get_interview_type_guidance(cls, interview_type: InterviewType) -> str:
        """Get general guidance for interview type"""
        if interview_type == InterviewType.TECHNICAL:
            return "Focus on technical skills, problem-solving abilities, and relevant experience."
        
        return "Focus on past experiences, soft skills, and cultural fit using the STAR method."

    @classmethod
    def _get_persona_focus_areas(cls, persona: str, interview_type: InterviewType) -> list[str]:
        """Get focus areas for persona and interview type combination"""
        base_areas = {
            InterviewType.TECHNICAL: ["technical_skills", "problem_solving", "code_quality"],
            InterviewType.BEHAVIORAL: ["soft_skills", "experience", "cultural_fit"]
        }

        persona_modifiers = {
            "strict": ["precision", "depth", "thoroughness"],
            "friendly": ["potential", "growth", "collaboration"],
            "neutral": ["objectivity", "fairness", "standards"]
        }

        areas = base_areas.get(interview_type, [])
        areas.extend(persona_modifiers.get(persona, []))

        return areas


# Initialize templates when module is imported
RoleBasedPrompts.initialize_templates()
