"""
Role-Based prompt implementation for AI interview question generation.
Implements interviewer persona templates with company type integration.
"""
from typing import Dict, List, Optional

from ai.prompts import PromptTemplate, prompt_library
from models.enums import ExperienceLevel, InterviewType, PromptTechnique


class RoleBasedPromptTemplate(PromptTemplate):
    """
    Extended PromptTemplate for Role-Based prompts with company context integration.
    """

    def __init__(self, persona: str, *args, **kwargs):
        """Initialize with persona information"""
        super().__init__(*args, **kwargs)
        self.persona = persona

    def format(self, **kwargs) -> str:
        """
        Format template with company context integration.

        Args:
            **kwargs: Variable values for substitution

        Returns:
            Formatted prompt string with company context
        """
        # Add company context if company_type is provided
        if 'company_type' in kwargs:
            company_type = kwargs['company_type']
            if company_type in RoleBasedPrompts.COMPANY_TYPES:
                company_info = RoleBasedPrompts.COMPANY_TYPES[company_type]
                kwargs['company_context'] = f"""
Company Type: {company_type}
Culture: {company_info['culture']}
Values: {company_info['values']}
Interview Style: {company_info['interview_style']}"""
            else:
                kwargs['company_context'] = f"Company Type: {company_type}"
        else:
            kwargs['company_context'] = "Company context not specified"

        return super().format(**kwargs)


class RoleBasedPrompts:
    """
    Role-Based prompt engineering implementation.

    Creates interviewer persona templates (strict, friendly, neutral) with
    company type and personality trait integration for context-aware
    role adoption in question generation.
    """

    # Storage for role-based templates
    _role_templates: Dict[str, RoleBasedPromptTemplate] = {}

    # Persona definitions with characteristics
    PERSONAS = {
        "strict": {
            "name": "Strict Interviewer",
            "description": "Detail-oriented, precise, and thorough interviewer who expects comprehensive answers",
            "tone": "formal and demanding",
            "focus": "technical accuracy and depth of knowledge"
        },
        "friendly": {
            "name": "Friendly Interviewer",
            "description": "Supportive, encouraging interviewer who creates a comfortable environment",
            "tone": "warm and encouraging",
            "focus": "candidate potential and collaborative skills"
        },
        "neutral": {
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
                template = cls._create_persona_template(
                    persona, interview_type)
                # Store in our custom storage
                key = f"{persona}_{interview_type.value}"
                cls._role_templates[key] = template
                # Also register with prompt library for general access
                prompt_library.register_template(template)

    @classmethod
    def get_all_role_based_templates(cls) -> List[RoleBasedPromptTemplate]:
        """Get all role-based templates from custom storage"""
        return list(cls._role_templates.values())

    @classmethod
    def get_available_personas(cls) -> List[str]:
        """Get list of available interviewer personas"""
        return list(cls.PERSONAS.keys())

    @classmethod
    def get_persona_info(cls, persona: str) -> Dict[str, str]:
        """Get detailed information about a persona"""
        if persona not in cls.PERSONAS:
            raise ValueError(f"Unknown persona: {persona}")
        return cls.PERSONAS[persona].copy()

    @classmethod
    def get_company_types(cls) -> List[str]:
        """Get list of available company types"""
        return list(cls.COMPANY_TYPES.keys())

    @classmethod
    def get_company_info(cls, company_type: str) -> Dict[str, str]:
        """Get detailed information about a company type"""
        if company_type not in cls.COMPANY_TYPES:
            raise ValueError(f"Unknown company type: {company_type}")
        return cls.COMPANY_TYPES[company_type].copy()

    @classmethod
    def get_persona_template(cls, persona: str, interview_type: InterviewType) -> Optional[RoleBasedPromptTemplate]:
        """Get template for specific persona and interview type"""
        if persona not in cls.PERSONAS:
            raise ValueError(f"Unknown persona: {persona}")

        key = f"{persona}_{interview_type.value}"
        return cls._role_templates.get(key)

    @classmethod
    def get_persona_company_compatibility(cls) -> Dict[str, List[str]]:
        """Get persona-company compatibility recommendations"""
        return cls.PERSONA_COMPANY_COMPATIBILITY.copy()

    @classmethod
    def recommend_persona_for_company(cls, company_type: str) -> List[str]:
        """Recommend personas suitable for a company type"""
        if company_type not in cls.COMPANY_TYPES:
            raise ValueError(f"Unknown company type: {company_type}")

        recommended = []
        for persona, compatible_companies in cls.PERSONA_COMPANY_COMPATIBILITY.items():
            if company_type in compatible_companies:
                recommended.append(persona)

        # Always include neutral as a safe option
        if "neutral" not in recommended:
            recommended.append("neutral")

        return recommended

    @classmethod
    def _create_persona_template(cls, persona: str, interview_type: InterviewType) -> PromptTemplate:
        """Create a Role-Based template for specific persona and interview type"""
        persona_info = cls.PERSONAS[persona]

        # Generate template content based on persona and interview type
        template_content = cls._generate_template_content(
            persona, interview_type)

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
            persona=persona,
            name=template_name,
            technique=PromptTechnique.ROLE_BASED,
            interview_type=interview_type,
            experience_level=None,  # Generic template
            template=template_content,
            metadata=metadata
        )

    @classmethod
    def get_company_context_for_template(cls, company_type: str) -> str:
        """Get company context information for template formatting"""
        if company_type not in cls.COMPANY_TYPES:
            return "Consider the company's unique culture and values in your interview approach."

        company_info = cls.COMPANY_TYPES[company_type]
        return f"""Company Culture: {company_info['culture']}
Company Values: {company_info['values']}
Interview Style: {company_info['interview_style']}"""

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

COMPANY CONTEXT:
{{company_context}}

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

Format your response as a numbered list of questions, followed by preparation recommendations that account for your interviewer style and the company culture."""

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
        elif interview_type == InterviewType.BEHAVIORAL:
            return cls._get_persona_behavioral_guidance(persona)
        elif interview_type == InterviewType.CASE_STUDY:
            return cls._get_persona_case_study_guidance(persona)
        elif interview_type == InterviewType.REVERSE:
            return cls._get_persona_reverse_guidance(persona)
        else:
            return ""

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
    def _get_persona_case_study_guidance(cls, persona: str) -> str:
        """Get persona-specific case study guidance"""
        if persona == "strict":
            return """CASE STUDY APPROACH (Strict):
- Present complex, multi-faceted business scenarios
- Expect thorough analysis with supporting data and reasoning
- Challenge assumptions and ask for alternative solutions
- Focus on analytical rigor and attention to detail
- Require candidates to defend their recommendations"""

        elif persona == "friendly":
            return """CASE STUDY APPROACH (Friendly):
- Present engaging, realistic business scenarios
- Guide candidates through the problem-solving process
- Encourage creative thinking and innovative solutions
- Provide feedback and suggestions during the discussion
- Focus on collaborative problem-solving approach"""

        elif persona == "neutral":
            return """CASE STUDY APPROACH (Neutral):
- Present standard business cases relevant to the role
- Evaluate structured thinking and analytical approach
- Ask clarifying questions to understand reasoning
- Focus on methodology and logical problem-solving
- Maintain objectivity in evaluating proposed solutions"""

        return ""

    @classmethod
    def _get_persona_reverse_guidance(cls, persona: str) -> str:
        """Get persona-specific reverse interview guidance"""
        if persona == "strict":
            return """REVERSE INTERVIEW PREPARATION (Strict Interviewer):
Prepare the candidate to ask questions when facing a strict interviewer:
- Questions should demonstrate thorough research and preparation
- Focus on detailed, specific inquiries about role expectations
- Ask about performance metrics, evaluation criteria, and success measures
- Inquire about challenges, obstacles, and how the company addresses them
- Show seriousness about the role and commitment to excellence"""

        elif persona == "friendly":
            return """REVERSE INTERVIEW PREPARATION (Friendly Interviewer):
Prepare the candidate to ask questions when facing a friendly interviewer:
- Ask about company culture, team dynamics, and work environment
- Inquire about growth opportunities and career development
- Show interest in the interviewer's experience and journey
- Ask about what they enjoy most about working at the company
- Focus on building rapport and demonstrating cultural fit"""

        elif persona == "neutral":
            return """REVERSE INTERVIEW PREPARATION (Neutral Interviewer):
Prepare the candidate to ask questions when facing a neutral interviewer:
- Ask balanced questions about role responsibilities and expectations
- Inquire about team structure, reporting relationships, and processes
- Focus on understanding the business context and strategic priorities
- Ask about typical career progression and advancement opportunities
- Demonstrate professionalism and genuine interest in the position"""

        return ""

    @classmethod
    def _get_interview_type_guidance(cls, interview_type: InterviewType) -> str:
        """Get general guidance for interview type"""
        if interview_type == InterviewType.TECHNICAL:
            return "Focus on technical skills, problem-solving abilities, and relevant experience."
        elif interview_type == InterviewType.BEHAVIORAL:
            return "Focus on past experiences, soft skills, and cultural fit using the STAR method."
        elif interview_type == InterviewType.CASE_STUDY:
            return "Present business scenarios that test analytical thinking and problem-solving."
        elif interview_type == InterviewType.REVERSE:
            return "Generate questions the candidate should ask to demonstrate interest and preparation."
        return ""

    @classmethod
    def _get_persona_focus_areas(cls, persona: str, interview_type: InterviewType) -> List[str]:
        """Get focus areas for persona and interview type combination"""
        base_areas = {
            InterviewType.TECHNICAL: ["technical_skills", "problem_solving", "code_quality"],
            InterviewType.BEHAVIORAL: ["soft_skills", "experience", "cultural_fit"],
            InterviewType.CASE_STUDY: ["analytical_thinking", "business_acumen", "communication"],
            InterviewType.REVERSE: ["preparation",
                                    "interest", "strategic_thinking"]
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
