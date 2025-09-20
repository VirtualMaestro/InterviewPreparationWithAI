"""
Few-Shot Learning prompt implementation for interview question generation.
Provides example-based guidance for consistent, high-quality question generation.
"""
from src.models.enums import ExperienceLevel, InterviewType, PromptTechnique

from .prompts import PromptTemplate, prompt_library


class FewShotPrompts:
    """
    Few-Shot Learning prompt templates with examples for different scenarios.

    Provides example-driven prompts that guide AI responses with appropriate
    difficulty patterns and question styles for various experience levels.
    """

    @staticmethod
    def register_all_templates() -> None:
        """Register all Few-Shot Learning templates with the prompt library"""

        # Technical Interview Templates
        FewShotPrompts._register_technical_templates()

        # Behavioral Interview Templates
        FewShotPrompts._register_behavioral_templates()

    @staticmethod
    def _register_technical_templates() -> None:
        """Register Few-Shot templates for technical interviews"""

        # Junior Level Technical
        junior_technical = PromptTemplate(
            name="few_shot_technical_junior",
            technique=PromptTechnique.FEW_SHOT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.JUNIOR,
            template="""You are an experienced technical interviewer. Generate {question_count} technical interview questions for a {experience_level} position based on this job description: {job_description}

                Here are examples of appropriate {experience_level} technical questions:

                Example 1: "What is the difference between a list and a tuple in Python? When would you use each one?"
                - This tests basic data structure knowledge
                - Appropriate for someone with 1-2 years experience
                - Focuses on fundamental concepts

                Example 2: "Can you explain what a REST API is and how you would make a GET request in Python?"
                - Tests basic API knowledge and practical skills
                - Suitable for junior developers
                - Combines theory with simple implementation

                Example 3: "What is version control and why is Git useful for developers?"
                - Tests understanding of development tools
                - Appropriate for entry-level positions
                - Focuses on collaborative development basics

                Now generate {question_count} similar technical questions that:
                - Test fundamental programming concepts
                - Are appropriate for 1-2 years of experience
                - Focus on basic implementation and understanding
                - Avoid complex system design or advanced algorithms
                - Include practical, hands-on scenarios

                Questions should cover areas mentioned in the job description: {job_description}
                Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",

            metadata={
                "difficulty": "beginner",
                "focus_areas": ["basic_concepts", "fundamental_skills", "practical_application"],
                "avoid": ["system_design", "advanced_algorithms", "complex_architecture"]
            }
        )

        # Mid-Level Technical
        mid_technical = PromptTemplate(
            name="few_shot_technical_mid",
            technique=PromptTechnique.FEW_SHOT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.MID,
            template="""You are an experienced technical interviewer. Generate {question_count} technical interview questions for a {experience_level} position based on this job description: {job_description}

                Here are examples of appropriate {experience_level} technical questions:

                Example 1: "Design a simple caching system for a web application. What data structures would you use and how would you handle cache invalidation?"
                - Tests system design thinking at intermediate level
                - Appropriate for 3-5 years experience
                - Combines data structures with practical architecture

                Example 2: "Explain the difference between SQL and NoSQL databases. Given a scenario with user profiles and social media posts, which would you choose and why?"
                - Tests database knowledge and decision-making
                - Suitable for mid-level developers
                - Requires analysis and justification

                Example 3: "How would you optimize a slow database query? Walk me through your debugging process."
                - Tests performance optimization skills
                - Appropriate for experienced developers
                - Focuses on problem-solving methodology

                Now generate {question_count} similar technical questions that:
                - Test intermediate programming and system concepts
                - Are appropriate for 3-5 years of experience
                - Include some system design elements
                - Require analysis and decision-making
                - Cover optimization and best practices
                - Balance theory with practical implementation

                Questions should cover areas mentioned in the job description: {job_description}
                Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",

            metadata={
                "difficulty": "intermediate",
                "focus_areas": ["system_design", "optimization", "decision_making", "best_practices"],
                "complexity": "moderate"
            }
        )

        # Senior Level Technical
        senior_technical = PromptTemplate(
            name="few_shot_technical_senior",
            technique=PromptTechnique.FEW_SHOT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR,
            template="""You are an experienced technical interviewer. Generate {question_count} technical interview questions for a {experience_level} position based on this job description: {job_description}

                Here are examples of appropriate {experience_level} technical questions:

                Example 1: "Design a distributed system for handling 1 million concurrent users. How would you handle load balancing, data consistency, and fault tolerance?"
                - Tests advanced system design skills
                - Appropriate for 5+ years experience
                - Requires deep architectural thinking

                Example 2: "You notice that your microservices architecture is experiencing cascading failures. How would you design a circuit breaker pattern and implement monitoring?"
                - Tests advanced problem-solving and patterns
                - Suitable for senior developers
                - Combines architecture with operational concerns

                Example 3: "Explain how you would migrate a monolithic application to microservices while maintaining zero downtime. What are the key challenges and mitigation strategies?"
                - Tests migration strategy and risk management
                - Appropriate for senior/lead positions
                - Requires strategic thinking and experience

                Now generate {question_count} similar technical questions that:
                - Test advanced system design and architecture
                - Are appropriate for 5+ years of experience
                - Include complex problem-solving scenarios
                - Require strategic thinking and trade-off analysis
                - Cover scalability, reliability, and performance
                - Demonstrate leadership and mentoring capabilities

                Questions should cover areas mentioned in the job description: {job_description}
                Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",
            metadata={
                "difficulty": "advanced",
                "focus_areas": ["system_architecture", "scalability", "leadership", "strategic_thinking"],
                "complexity": "high"
            }
        )

        # Lead Level Technical
        lead_technical = PromptTemplate(
            name="few_shot_technical_lead",
            technique=PromptTechnique.FEW_SHOT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.LEAD,
            template="""You are an experienced technical interviewer. Generate {question_count} technical interview questions for a {experience_level} position based on this job description: {job_description}

                Here are examples of appropriate {experience_level} technical questions:

                Example 1: "As a technical lead, how would you evaluate and choose between different architectural patterns for a new product? Walk me through your decision framework."
                - Tests technical leadership and decision-making
                - Appropriate for lead/principal positions
                - Requires strategic evaluation skills

                Example 2: "Your team is struggling with technical debt and delivery pressure. How would you balance refactoring with feature development while maintaining team morale?"
                - Tests leadership and project management
                - Suitable for senior leadership roles
                - Combines technical and people management

                Example 3: "Design the technical strategy for scaling your engineering organization from 10 to 100 developers. What processes, tools, and architectural changes would you implement?"
                - Tests organizational scaling and strategy
                - Appropriate for principal/staff positions
                - Requires broad technical and leadership experience

                Now generate {question_count} similar technical questions that:
                - Test technical leadership and strategic thinking
                - Are appropriate for lead/principal positions
                - Include organizational and team management aspects
                - Require long-term planning and vision
                - Cover mentoring, architecture decisions, and process improvement
                - Demonstrate ability to influence and guide technical direction

                Questions should cover areas mentioned in the job description: {job_description}
                Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",
            metadata={
                "difficulty": "expert",
                "focus_areas": ["technical_leadership", "strategy", "team_management", "organizational_scaling"],
                "complexity": "very_high"
            }
        )

        # Register all technical templates
        for template in [junior_technical, mid_technical, senior_technical, lead_technical]:
            prompt_library.register_template(template)

    @staticmethod
    def _register_behavioral_templates() -> None:
        """Register Few-Shot templates for behavioral interviews"""

        # Junior Level Behavioral
        junior_behavioral = PromptTemplate(
            name="few_shot_behavioral_junior",
            technique=PromptTechnique.FEW_SHOT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.JUNIOR,
            template="""You are an experienced behavioral interviewer. Generate {question_count} behavioral interview questions for a {experience_level} position based on this job description: {job_description}

                Here are examples of appropriate {experience_level} behavioral questions:

                Example 1: "Tell me about a time when you had to learn a new technology or programming language quickly. How did you approach it?"
                - Tests learning ability and adaptability
                - Appropriate for junior developers
                - Focuses on growth mindset

                Example 2: "Describe a situation where you made a mistake in your code. How did you handle it and what did you learn?"
                - Tests accountability and learning from errors
                - Suitable for entry-level positions
                - Emphasizes professional development

                Example 3: "Give me an example of when you had to ask for help on a project. How did you approach it?"
                - Tests collaboration and communication
                - Appropriate for junior roles
                - Focuses on teamwork and humility

                Now generate {question_count} similar behavioral questions that:
                - Are appropriate for 1-2 years of experience
                - Focus on learning, growth, and basic professional skills
                - Emphasize collaboration and communication
                - Test adaptability and problem-solving approach
                - Avoid complex leadership or management scenarios
                - Relate to the role described in: {job_description}
                Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",
            metadata={
                "difficulty": "entry_level",
                "focus_areas": ["learning", "collaboration", "communication", "growth_mindset"],
                "experience_scope": "individual_contributor"
            }
        )

        # Mid-Level Behavioral
        mid_behavioral = PromptTemplate(
            name="few_shot_behavioral_mid",
            technique=PromptTechnique.FEW_SHOT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.MID,
            template="""You are an experienced behavioral interviewer. Generate {question_count} behavioral interview questions for a {experience_level} position based on this job description: {job_description}

                Here are examples of appropriate {experience_level} behavioral questions:

                Example 1: "Tell me about a time when you had to convince your team to adopt a new approach or technology. How did you handle resistance?"
                - Tests influence and persuasion skills
                - Appropriate for mid-level developers
                - Focuses on technical leadership

                Example 2: "Describe a situation where you had to balance competing priorities on multiple projects. How did you manage your time and communicate with stakeholders?"
                - Tests project management and communication
                - Suitable for experienced developers
                - Emphasizes organizational skills

                Example 3: "Give me an example of when you identified a significant technical problem before it became critical. How did you handle it?"
                - Tests proactive thinking and problem-solving
                - Appropriate for 3-5 years experience
                - Focuses on technical judgment

                Now generate {question_count} similar behavioral questions that:
                - Are appropriate for 3-5 years of experience
                - Include some leadership and influence scenarios
                - Test project management and prioritization skills
                - Emphasize proactive problem-solving
                - Cover cross-team collaboration and communication
                - Relate to the role described in: {job_description}
                Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",
            metadata={
                "difficulty": "intermediate",
                "focus_areas": ["influence", "project_management", "proactive_thinking", "cross_team_collaboration"],
                "experience_scope": "senior_contributor"
            }
        )

        # Senior Level Behavioral
        senior_behavioral = PromptTemplate(
            name="few_shot_behavioral_senior",
            technique=PromptTechnique.FEW_SHOT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.SENIOR,
            template="""You are an experienced behavioral interviewer. Generate {question_count} behavioral interview questions for a {experience_level} position based on this job description: {job_description}

                Here are examples of appropriate {experience_level} behavioral questions:

                Example 1: "Tell me about a time when you had to make a difficult technical decision that affected multiple teams. How did you gather input and communicate the decision?"
                - Tests decision-making and stakeholder management
                - Appropriate for senior developers
                - Focuses on cross-organizational impact

                Example 2: "Describe a situation where you had to mentor a struggling team member. What was your approach and what was the outcome?"
                - Tests mentoring and people development
                - Suitable for senior positions
                - Emphasizes leadership and empathy

                Example 3: "Give me an example of when you had to drive a major technical initiative across the organization. What challenges did you face and how did you overcome them?"
                - Tests strategic thinking and execution
                - Appropriate for senior/lead roles
                - Focuses on organizational influence

                Now generate {question_count} similar behavioral questions that:
                - Are appropriate for 5+ years of experience
                - Include leadership and mentoring scenarios
                - Test strategic thinking and organizational impact
                - Emphasize stakeholder management and communication
                - Cover conflict resolution and difficult decisions
                - Relate to the role described in: {job_description}
                Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",
            metadata={
                "difficulty": "advanced",
                "focus_areas": ["leadership", "mentoring", "strategic_thinking", "stakeholder_management"],
                "experience_scope": "technical_leader"
            }
        )

        # Lead Level Behavioral
        lead_behavioral = PromptTemplate(
            name="few_shot_behavioral_lead",
            technique=PromptTechnique.FEW_SHOT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.LEAD,
            template="""You are an experienced behavioral interviewer. Generate {question_count} behavioral interview questions for a {experience_level} position based on this job description: {job_description}

                Here are examples of appropriate {experience_level} behavioral questions:

                Example 1: "Tell me about a time when you had to transform the technical culture of an organization. What was your strategy and how did you measure success?"
                - Tests organizational transformation and culture change
                - Appropriate for principal/staff positions
                - Focuses on strategic leadership

                Example 2: "Describe a situation where you had to make a decision that balanced technical excellence with business constraints. How did you approach this trade-off?"
                - Tests business acumen and technical judgment
                - Suitable for senior leadership roles
                - Emphasizes strategic decision-making

                Example 3: "Give me an example of when you had to build consensus among senior stakeholders with conflicting priorities. What was your approach?"
                - Tests executive communication and influence
                - Appropriate for principal/director positions
                - Focuses on senior stakeholder management

                Now generate {question_count} similar behavioral questions that:
                - Are appropriate for lead/principal positions
                - Include organizational transformation scenarios
                - Test executive communication and influence
                - Emphasize strategic business thinking
                - Cover culture change and team building at scale
                - Relate to the role described in: {job_description}
                Important: Do not include in your response your greetings or other uneeded sentences. Only questions""",
            metadata={
                "difficulty": "expert",
                "focus_areas": ["organizational_transformation", "executive_communication", "strategic_business_thinking", "culture_change"],
                "experience_scope": "senior_leader"
            }
        )

        # Register all behavioral templates
        for template in [junior_behavioral, mid_behavioral, senior_behavioral, lead_behavioral]:
            prompt_library.register_template(template)


# Initialize Few-Shot templates when module is imported
FewShotPrompts.register_all_templates()
