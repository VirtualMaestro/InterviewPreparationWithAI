"""
Structured Output prompt implementation for AI interview question generation.
Provides JSON-formatted response templates with question metadata for consistent parsing.
"""
import json
from typing import Any, Dict, List, Optional

from models.enums import (DifficultyLevel, ExperienceLevel, InterviewType,
                          PromptTechnique, QuestionCategory)

from .prompts import PromptTemplate, prompt_library


class StructuredOutputPrompts:
    """
    Structured Output prompt engineering implementation.

    Creates JSON-formatted response templates with question metadata including
    difficulty, category, time estimates, hints, and structured parsing support.
    """

    # JSON schema for structured responses
    JSON_SCHEMA = {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "question": {"type": "string"},
                        "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
                        "category": {"type": "string"},
                        "estimated_time_minutes": {"type": "integer"},
                        "hints": {"type": "array", "items": {"type": "string"}},
                        "follow_up_questions": {"type": "array", "items": {"type": "string"}},
                        "evaluation_criteria": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["id", "question", "difficulty", "category", "estimated_time_minutes"]
                }
            },
            "recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "recommendation": {"type": "string"},
                        "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                        "resources": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["category", "recommendation", "priority"]
                }
            },
            "metadata": {
                "type": "object",
                "properties": {
                    "total_questions": {"type": "integer"},
                    "difficulty_distribution": {"type": "object"},
                    "estimated_total_time": {"type": "integer"},
                    "focus_areas": {"type": "array", "items": {"type": "string"}},
                    "preparation_level": {"type": "string"}
                },
                "required": ["total_questions", "estimated_total_time"]
            }
        },
        "required": ["questions", "recommendations", "metadata"]
    }

    @staticmethod
    def register_all_templates() -> None:
        """Register all Structured Output templates with the prompt library"""

        # Technical Interview Templates
        StructuredOutputPrompts._register_technical_templates()

        # Behavioral Interview Templates
        StructuredOutputPrompts._register_behavioral_templates()

        # Case Study Interview Templates
        StructuredOutputPrompts._register_case_study_templates()

        # Reverse Interview Templates
        StructuredOutputPrompts._register_reverse_templates()

    @staticmethod
    def _register_technical_templates() -> None:
        """Register Structured Output templates for technical interviews"""

        # Junior Level Technical
        junior_technical = PromptTemplate(
            name="structured_output_technical_junior",
            technique=PromptTechnique.STRUCTURED_OUTPUT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.JUNIOR,
            template="""Generate {question_count} technical interview questions for a {experience_level} position based on this job description: {job_description}

You MUST respond with valid JSON in the exact format specified below. Do not include any text before or after the JSON.

JSON Format Required:
{{
  "questions": [
    {{
      "id": 1,
      "question": "What is the difference between a list and a tuple in Python?",
      "difficulty": "easy",
      "category": "conceptual",
      "estimated_time_minutes": 5,
      "hints": ["Think about mutability", "Consider use cases for each"],
      "follow_up_questions": ["When would you use each one?", "Can you give examples?"],
      "evaluation_criteria": ["Understands mutability concept", "Can explain practical differences", "Provides clear examples"]
    }}
  ],
  "recommendations": [
    {{
      "category": "preparation",
      "recommendation": "Review basic Python data structures and their properties",
      "priority": "high",
      "resources": ["Python documentation", "Practice coding exercises"]
    }}
  ],
  "metadata": {{
    "total_questions": {question_count},
    "difficulty_distribution": {{"easy": 60, "medium": 30, "hard": 10}},
    "estimated_total_time": 25,
    "focus_areas": ["basic_concepts", "fundamental_skills", "practical_application"],
    "preparation_level": "entry_level"
  }}
}}

Generate questions appropriate for {experience_level} level (1-2 years experience):
- Focus on fundamental programming concepts
- Test basic implementation and understanding
- Avoid complex system design or advanced algorithms
- Include practical, hands-on scenarios
- Difficulty should be mostly "easy" with some "medium"
- Categories should include: "conceptual", "coding", "algorithms"
- Time estimates: 3-8 minutes per question
- Provide helpful hints and clear evaluation criteria

Job Description: {job_description}

Respond with valid JSON only:""",
            metadata={
                "difficulty_focus": "easy_medium",
                "json_validated": True,
                "structured_parsing": True,
                "metadata_rich": True
            }
        )

        # Mid-Level Technical
        mid_technical = PromptTemplate(
            name="structured_output_technical_mid",
            technique=PromptTechnique.STRUCTURED_OUTPUT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.MID,
            template="""Generate {question_count} technical interview questions for a {experience_level} position based on this job description: {job_description}

You MUST respond with valid JSON in the exact format specified below. Do not include any text before or after the JSON.

JSON Format Required:
{{
  "questions": [
    {{
      "id": 1,
      "question": "Design a simple caching system for a web application. What data structures would you use and how would you handle cache invalidation?",
      "difficulty": "medium",
      "category": "system_design",
      "estimated_time_minutes": 12,
      "hints": ["Consider different cache strategies", "Think about memory constraints", "Consider cache hit/miss scenarios"],
      "follow_up_questions": ["How would you handle cache eviction?", "What about distributed caching?"],
      "evaluation_criteria": ["Understands caching concepts", "Can design appropriate data structures", "Considers edge cases and performance"]
    }}
  ],
  "recommendations": [
    {{
      "category": "system_design",
      "recommendation": "Practice designing scalable systems with caching layers",
      "priority": "high",
      "resources": ["System design interviews", "Redis documentation", "Caching patterns"]
    }}
  ],
  "metadata": {{
    "total_questions": {question_count},
    "difficulty_distribution": {{"easy": 20, "medium": 60, "hard": 20}},
    "estimated_total_time": 45,
    "focus_areas": ["system_design", "optimization", "decision_making", "best_practices"],
    "preparation_level": "intermediate"
  }}
}}

Generate questions appropriate for {experience_level} level (3-5 years experience):
- Test intermediate programming and system concepts
- Include some system design elements
- Require analysis and decision-making
- Cover optimization and best practices
- Balance theory with practical implementation
- Difficulty should be mostly "medium" with some "easy" and "hard"
- Categories should include: "system_design", "coding", "algorithms", "conceptual"
- Time estimates: 8-15 minutes per question
- Include challenging follow-up questions

Job Description: {job_description}

Respond with valid JSON only:""",
            metadata={
                "difficulty_focus": "medium_hard",
                "json_validated": True,
                "structured_parsing": True,
                "metadata_rich": True
            }
        )

        # Senior Level Technical
        senior_technical = PromptTemplate(
            name="structured_output_technical_senior",
            technique=PromptTechnique.STRUCTURED_OUTPUT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR,
            template="""Generate {question_count} technical interview questions for a {experience_level} position based on this job description: {job_description}

You MUST respond with valid JSON in the exact format specified below. Do not include any text before or after the JSON.

JSON Format Required:
{{
  "questions": [
    {{
      "id": 1,
      "question": "Design a distributed system for handling 1 million concurrent users. How would you handle load balancing, data consistency, and fault tolerance?",
      "difficulty": "hard",
      "category": "system_design",
      "estimated_time_minutes": 20,
      "hints": ["Consider microservices architecture", "Think about CAP theorem", "Consider monitoring and observability"],
      "follow_up_questions": ["How would you handle database sharding?", "What about cross-region replication?", "How would you monitor system health?"],
      "evaluation_criteria": ["Demonstrates advanced system design skills", "Understands distributed systems concepts", "Can handle complex trade-offs", "Shows leadership thinking"]
    }}
  ],
  "recommendations": [
    {{
      "category": "architecture",
      "recommendation": "Study distributed systems patterns and real-world case studies",
      "priority": "high",
      "resources": ["Designing Data-Intensive Applications", "System design case studies", "Cloud architecture patterns"]
    }}
  ],
  "metadata": {{
    "total_questions": {question_count},
    "difficulty_distribution": {{"easy": 10, "medium": 40, "hard": 50}},
    "estimated_total_time": 75,
    "focus_areas": ["system_architecture", "scalability", "leadership", "strategic_thinking"],
    "preparation_level": "advanced"
  }}
}}

Generate questions appropriate for {experience_level} level (5+ years experience):
- Test advanced system design and architecture
- Include complex problem-solving scenarios
- Require strategic thinking and trade-off analysis
- Cover scalability, reliability, and performance
- Demonstrate leadership and mentoring capabilities
- Difficulty should be mostly "hard" with some "medium"
- Categories should include: "system_design", "algorithms", "conceptual"
- Time estimates: 15-25 minutes per question
- Include deep technical follow-up questions

Job Description: {job_description}

Respond with valid JSON only:""",
            metadata={
                "difficulty_focus": "hard",
                "json_validated": True,
                "structured_parsing": True,
                "metadata_rich": True
            }
        )

        # Lead Level Technical
        lead_technical = PromptTemplate(
            name="structured_output_technical_lead",
            technique=PromptTechnique.STRUCTURED_OUTPUT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.LEAD,
            template="""Generate {question_count} technical interview questions for a {experience_level} position based on this job description: {job_description}

You MUST respond with valid JSON in the exact format specified below. Do not include any text before or after the JSON.

JSON Format Required:
{{
  "questions": [
    {{
      "id": 1,
      "question": "As a technical lead, how would you evaluate and choose between different architectural patterns for a new product? Walk me through your decision framework.",
      "difficulty": "hard",
      "category": "system_design",
      "estimated_time_minutes": 25,
      "hints": ["Consider business requirements", "Think about team capabilities", "Evaluate long-term maintainability", "Consider technical debt implications"],
      "follow_up_questions": ["How would you get buy-in from stakeholders?", "What if the team disagrees with your choice?", "How would you measure success?"],
      "evaluation_criteria": ["Shows strategic technical thinking", "Demonstrates leadership skills", "Can balance technical and business concerns", "Shows experience with organizational challenges"]
    }}
  ],
  "recommendations": [
    {{
      "category": "leadership",
      "recommendation": "Develop skills in technical strategy and organizational influence",
      "priority": "high",
      "resources": ["Technical leadership books", "Architecture decision records", "Engineering management resources"]
    }}
  ],
  "metadata": {{
    "total_questions": {question_count},
    "difficulty_distribution": {{"easy": 0, "medium": 30, "hard": 70}},
    "estimated_total_time": 100,
    "focus_areas": ["technical_leadership", "strategy", "team_management", "organizational_scaling"],
    "preparation_level": "expert"
  }}
}}

Generate questions appropriate for {experience_level} level (Lead/Principal positions):
- Test technical leadership and strategic thinking
- Include organizational and team management aspects
- Require long-term planning and vision
- Cover mentoring, architecture decisions, and process improvement
- Demonstrate ability to influence and guide technical direction
- Difficulty should be mostly "hard"
- Categories should include: "system_design", "conceptual"
- Time estimates: 20-30 minutes per question
- Include strategic and leadership follow-up questions

Job Description: {job_description}

Respond with valid JSON only:""",
            metadata={
                "difficulty_focus": "expert",
                "json_validated": True,
                "structured_parsing": True,
                "metadata_rich": True
            }
        )

        # Register all technical templates
        for template in [junior_technical, mid_technical, senior_technical, lead_technical]:
            prompt_library.register_template(template)

    @staticmethod
    def _register_behavioral_templates() -> None:
        """Register Structured Output templates for behavioral interviews"""

        # Junior Level Behavioral
        junior_behavioral = PromptTemplate(
            name="structured_output_behavioral_junior",
            technique=PromptTechnique.STRUCTURED_OUTPUT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.JUNIOR,
            template="""Generate {question_count} behavioral interview questions for a {experience_level} position based on this job description: {job_description}

You MUST respond with valid JSON in the exact format specified below. Do not include any text before or after the JSON.

JSON Format Required:
{{
  "questions": [
    {{
      "id": 1,
      "question": "Tell me about a time when you had to learn a new technology or programming language quickly. How did you approach it?",
      "difficulty": "easy",
      "category": "behavioral",
      "estimated_time_minutes": 8,
      "hints": ["Use STAR method (Situation, Task, Action, Result)", "Focus on learning process", "Mention specific resources used"],
      "follow_up_questions": ["What challenges did you face?", "How do you stay updated with new technologies?"],
      "evaluation_criteria": ["Shows learning agility", "Demonstrates proactive approach", "Can articulate learning process", "Shows growth mindset"]
    }}
  ],
  "recommendations": [
    {{
      "category": "interview_preparation",
      "recommendation": "Prepare STAR method examples from your recent experiences",
      "priority": "high",
      "resources": ["STAR method guide", "Behavioral interview examples", "Personal experience reflection"]
    }}
  ],
  "metadata": {{
    "total_questions": {question_count},
    "difficulty_distribution": {{"easy": 70, "medium": 30, "hard": 0}},
    "estimated_total_time": 35,
    "focus_areas": ["learning", "collaboration", "communication", "growth_mindset"],
    "preparation_level": "entry_level"
  }}
}}

Generate questions appropriate for {experience_level} level (1-2 years experience):
- Focus on learning, growth, and basic professional skills
- Emphasize collaboration and communication
- Test adaptability and problem-solving approach
- Avoid complex leadership or management scenarios
- Difficulty should be mostly "easy" with some "medium"
- Category should be "behavioral"
- Time estimates: 5-10 minutes per question
- Focus on individual contributor experiences

Job Description: {job_description}

Respond with valid JSON only:""",
            metadata={
                "difficulty_focus": "easy",
                "json_validated": True,
                "structured_parsing": True,
                "metadata_rich": True
            }
        )

        # Mid-Level Behavioral
        mid_behavioral = PromptTemplate(
            name="structured_output_behavioral_mid",
            technique=PromptTechnique.STRUCTURED_OUTPUT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.MID,
            template="""Generate {question_count} behavioral interview questions for a {experience_level} position based on this job description: {job_description}

You MUST respond with valid JSON in the exact format specified below. Do not include any text before or after the JSON.

JSON Format Required:
{{
  "questions": [
    {{
      "id": 1,
      "question": "Tell me about a time when you had to convince your team to adopt a new approach or technology. How did you handle resistance?",
      "difficulty": "medium",
      "category": "behavioral",
      "estimated_time_minutes": 10,
      "hints": ["Use STAR method", "Focus on influence and persuasion", "Describe specific actions taken", "Mention outcomes and lessons learned"],
      "follow_up_questions": ["What would you do differently?", "How did you measure success?", "What was the long-term impact?"],
      "evaluation_criteria": ["Shows influence skills", "Demonstrates change management", "Can handle resistance", "Shows collaborative leadership"]
    }}
  ],
  "recommendations": [
    {{
      "category": "leadership_skills",
      "recommendation": "Develop examples of influence and cross-team collaboration",
      "priority": "high",
      "resources": ["Leadership scenarios", "Influence techniques", "Change management examples"]
    }}
  ],
  "metadata": {{
    "total_questions": {question_count},
    "difficulty_distribution": {{"easy": 30, "medium": 60, "hard": 10}},
    "estimated_total_time": 45,
    "focus_areas": ["influence", "project_management", "proactive_thinking", "cross_team_collaboration"],
    "preparation_level": "intermediate"
  }}
}}

Generate questions appropriate for {experience_level} level (3-5 years experience):
- Include some leadership and influence scenarios
- Test project management and prioritization skills
- Emphasize proactive problem-solving
- Cover cross-team collaboration and communication
- Difficulty should be mostly "medium" with some "easy"
- Category should be "behavioral"
- Time estimates: 8-12 minutes per question
- Focus on senior contributor experiences

Job Description: {job_description}

Respond with valid JSON only:""",
            metadata={
                "difficulty_focus": "medium",
                "json_validated": True,
                "structured_parsing": True,
                "metadata_rich": True
            }
        )

        # Senior Level Behavioral
        senior_behavioral = PromptTemplate(
            name="structured_output_behavioral_senior",
            technique=PromptTechnique.STRUCTURED_OUTPUT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.SENIOR,
            template="""Generate {question_count} behavioral interview questions for a {experience_level} position based on this job description: {job_description}

You MUST respond with valid JSON in the exact format specified below. Do not include any text before or after the JSON.

JSON Format Required:
{{
  "questions": [
    {{
      "id": 1,
      "question": "Tell me about a time when you had to make a difficult technical decision that affected multiple teams. How did you gather input and communicate the decision?",
      "difficulty": "hard",
      "category": "behavioral",
      "estimated_time_minutes": 15,
      "hints": ["Use STAR method", "Focus on stakeholder management", "Describe decision-making process", "Emphasize communication strategy"],
      "follow_up_questions": ["How did you handle disagreement?", "What was the long-term impact?", "How did you measure success?"],
      "evaluation_criteria": ["Shows strategic decision-making", "Demonstrates stakeholder management", "Can handle complex situations", "Shows leadership impact"]
    }}
  ],
  "recommendations": [
    {{
      "category": "senior_leadership",
      "recommendation": "Prepare examples of cross-organizational impact and strategic decisions",
      "priority": "high",
      "resources": ["Leadership case studies", "Stakeholder management techniques", "Strategic decision frameworks"]
    }}
  ],
  "metadata": {{
    "total_questions": {question_count},
    "difficulty_distribution": {{"easy": 10, "medium": 40, "hard": 50}},
    "estimated_total_time": 60,
    "focus_areas": ["leadership", "mentoring", "strategic_thinking", "stakeholder_management"],
    "preparation_level": "advanced"
  }}
}}

Generate questions appropriate for {experience_level} level (5+ years experience):
- Include leadership and mentoring scenarios
- Test strategic thinking and organizational impact
- Emphasize stakeholder management and communication
- Cover conflict resolution and difficult decisions
- Difficulty should be mostly "hard" with some "medium"
- Category should be "behavioral"
- Time estimates: 12-18 minutes per question
- Focus on technical leadership experiences

Job Description: {job_description}

Respond with valid JSON only:""",
            metadata={
                "difficulty_focus": "hard",
                "json_validated": True,
                "structured_parsing": True,
                "metadata_rich": True
            }
        )

        # Lead Level Behavioral
        lead_behavioral = PromptTemplate(
            name="structured_output_behavioral_lead",
            technique=PromptTechnique.STRUCTURED_OUTPUT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.LEAD,
            template="""Generate {question_count} behavioral interview questions for a {experience_level} position based on this job description: {job_description}

You MUST respond with valid JSON in the exact format specified below. Do not include any text before or after the JSON.

JSON Format Required:
{{
  "questions": [
    {{
      "id": 1,
      "question": "Tell me about a time when you had to transform the technical culture of an organization. What was your strategy and how did you measure success?",
      "difficulty": "hard",
      "category": "behavioral",
      "estimated_time_minutes": 20,
      "hints": ["Use STAR method", "Focus on organizational change", "Describe culture transformation strategy", "Emphasize measurement and outcomes"],
      "follow_up_questions": ["How did you handle resistance to change?", "What metrics did you use?", "How did you sustain the changes?"],
      "evaluation_criteria": ["Shows organizational transformation skills", "Demonstrates strategic leadership", "Can drive culture change", "Shows executive-level thinking"]
    }}
  ],
  "recommendations": [
    {{
      "category": "executive_leadership",
      "recommendation": "Develop examples of organizational transformation and strategic initiatives",
      "priority": "high",
      "resources": ["Organizational change management", "Culture transformation case studies", "Executive leadership frameworks"]
    }}
  ],
  "metadata": {{
    "total_questions": {question_count},
    "difficulty_distribution": {{"easy": 0, "medium": 20, "hard": 80}},
    "estimated_total_time": 80,
    "focus_areas": ["organizational_transformation", "executive_communication", "strategic_business_thinking", "culture_change"],
    "preparation_level": "expert"
  }}
}}

Generate questions appropriate for {experience_level} level (Lead/Principal positions):
- Include organizational transformation scenarios
- Test executive communication and influence
- Emphasize strategic business thinking
- Cover culture change and team building at scale
- Difficulty should be mostly "hard"
- Category should be "behavioral"
- Time estimates: 15-25 minutes per question
- Focus on senior leadership experiences

Job Description: {job_description}

Respond with valid JSON only:""",
            metadata={
                "difficulty_focus": "expert",
                "json_validated": True,
                "structured_parsing": True,
                "metadata_rich": True
            }
        )

        # Register all behavioral templates
        for template in [junior_behavioral, mid_behavioral, senior_behavioral, lead_behavioral]:
            prompt_library.register_template(template)

    @staticmethod
    def _register_case_study_templates() -> None:
        """Register Structured Output templates for case study interviews"""

        # Generic Case Study (all levels can adapt)
        case_study_generic = PromptTemplate(
            name="structured_output_case_study_generic",
            technique=PromptTechnique.STRUCTURED_OUTPUT,
            interview_type=InterviewType.CASE_STUDY,
            experience_level=None,  # Generic for all levels
            template="""Generate {question_count} case study questions for a {experience_level} position based on this job description: {job_description}

You MUST respond with valid JSON in the exact format specified below. Do not include any text before or after the JSON.

JSON Format Required:
{{
  "questions": [
    {{
      "id": 1,
      "question": "Our e-commerce platform is experiencing slow page load times during peak hours. Walk me through how you would investigate and solve this problem.",
      "difficulty": "medium",
      "category": "case_study",
      "estimated_time_minutes": 15,
      "hints": ["Consider multiple potential causes", "Think about monitoring and metrics", "Prioritize solutions by impact", "Consider both short-term and long-term fixes"],
      "follow_up_questions": ["How would you prioritize different solutions?", "What metrics would you track?", "How would you prevent this in the future?"],
      "evaluation_criteria": ["Shows systematic problem-solving", "Considers multiple solutions", "Can prioritize effectively", "Demonstrates technical depth appropriate for level"]
    }}
  ],
  "recommendations": [
    {{
      "category": "problem_solving",
      "recommendation": "Practice systematic debugging and problem-solving methodologies",
      "priority": "high",
      "resources": ["System troubleshooting guides", "Performance optimization techniques", "Case study examples"]
    }}
  ],
  "metadata": {{
    "total_questions": {question_count},
    "difficulty_distribution": {{"easy": 20, "medium": 60, "hard": 20}},
    "estimated_total_time": 50,
    "focus_areas": ["problem_solving", "analytical_thinking", "system_understanding", "methodology"],
    "preparation_level": "adaptive"
  }}
}}

Generate case study questions that:
- Present realistic technical scenarios relevant to the role
- Allow candidates to demonstrate their problem-solving process
- Can be adapted for different experience levels
- Test both technical skills and analytical thinking
- Include scenarios related to the job description
- Encourage candidates to ask clarifying questions
- Focus on methodology as much as the final solution
- Difficulty should adapt to experience level
- Category should be "case_study"
- Time estimates: 10-20 minutes per question

Job Description: {job_description}

Respond with valid JSON only:""",
            metadata={
                "difficulty_focus": "adaptive",
                "json_validated": True,
                "structured_parsing": True,
                "metadata_rich": True
            }
        )

        prompt_library.register_template(case_study_generic)

    @staticmethod
    def _register_reverse_templates() -> None:
        """Register Structured Output templates for reverse interviews (questions for employer)"""

        # Generic Reverse Interview
        reverse_generic = PromptTemplate(
            name="structured_output_reverse_generic",
            technique=PromptTechnique.STRUCTURED_OUTPUT,
            interview_type=InterviewType.REVERSE,
            experience_level=None,  # Generic for all levels
            template="""Generate {question_count} thoughtful questions a candidate should ask about this role: {job_description}

You MUST respond with valid JSON in the exact format specified below. Do not include any text before or after the JSON.

JSON Format Required:
{{
  "questions": [
    {{
      "id": 1,
      "question": "What does success look like in this role after 6 months and 1 year?",
      "difficulty": "medium",
      "category": "behavioral",
      "estimated_time_minutes": 5,
      "hints": ["Shows goal-oriented thinking", "Demonstrates interest in performance expectations", "Helps understand role trajectory"],
      "follow_up_questions": ["How is performance measured?", "What are the key milestones?"],
      "evaluation_criteria": ["Shows strategic thinking", "Demonstrates preparation", "Indicates genuine interest", "Professional approach"]
    }}
  ],
  "recommendations": [
    {{
      "category": "interview_strategy",
      "recommendation": "Research the company and role thoroughly before asking questions",
      "priority": "high",
      "resources": ["Company website", "Recent news", "Employee reviews", "Industry reports"]
    }}
  ],
  "metadata": {{
    "total_questions": {question_count},
    "difficulty_distribution": {{"easy": 40, "medium": 50, "hard": 10}},
    "estimated_total_time": 20,
    "focus_areas": ["role_understanding", "career_growth", "team_dynamics", "company_culture"],
    "preparation_level": "professional"
  }}
}}

Generate thoughtful questions that:
- Demonstrate genuine interest in the role and company
- Show strategic thinking about career growth
- Help the candidate evaluate if the role is a good fit
- Cover technical, cultural, and growth aspects
- Are specific enough to provide valuable insights
- Relate to the position described in the job description
- Avoid questions easily answered by basic research
- Show professionalism and preparation
- Difficulty should be mostly "medium"
- Categories should include: "behavioral", "conceptual"
- Time estimates: 3-8 minutes per question

Job Description: {job_description}

Respond with valid JSON only:""",
            metadata={
                "difficulty_focus": "professional",
                "json_validated": True,
                "structured_parsing": True,
                "metadata_rich": True
            }
        )

        prompt_library.register_template(reverse_generic)

    @staticmethod
    def validate_json_response(response: str) -> Dict[str, Any]:
        """
        Validate and parse JSON response from structured output.

        Args:
            response: Raw response string from AI

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If JSON is invalid or doesn't match schema
        """
        try:
            # Parse JSON
            data = json.loads(response.strip())
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")

        # Validate required top-level keys
        required_keys = ["questions", "recommendations", "metadata"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")

        # Validate questions structure
        if not isinstance(data["questions"], list) or len(data["questions"]) == 0:
            raise ValueError("Questions must be a non-empty list")

        for i, question in enumerate(data["questions"]):
            StructuredOutputPrompts._validate_question_structure(question, i)

        # Validate recommendations structure
        if not isinstance(data["recommendations"], list):
            raise ValueError("Recommendations must be a list")

        for i, rec in enumerate(data["recommendations"]):
            StructuredOutputPrompts._validate_recommendation_structure(rec, i)

        # Validate metadata structure
        StructuredOutputPrompts._validate_metadata_structure(data["metadata"])

        return data

    @staticmethod
    def _validate_question_structure(question: Dict[str, Any], index: int) -> None:
        """Validate individual question structure"""
        required_fields = ["id", "question", "difficulty",
                           "category", "estimated_time_minutes"]

        for field in required_fields:
            if field not in question:
                raise ValueError(
                    f"Question {index}: Missing required field '{field}'")

        # Validate difficulty
        if question["difficulty"] not in ["easy", "medium", "hard"]:
            raise ValueError(
                f"Question {index}: Invalid difficulty '{question['difficulty']}'")

        # Validate estimated time
        if not isinstance(question["estimated_time_minutes"], int) or question["estimated_time_minutes"] <= 0:
            raise ValueError(
                f"Question {index}: Invalid estimated_time_minutes")

        # Validate optional fields if present
        if "hints" in question and not isinstance(question["hints"], list):
            raise ValueError(f"Question {index}: Hints must be a list")

        if "follow_up_questions" in question and not isinstance(question["follow_up_questions"], list):
            raise ValueError(
                f"Question {index}: Follow-up questions must be a list")

        if "evaluation_criteria" in question and not isinstance(question["evaluation_criteria"], list):
            raise ValueError(
                f"Question {index}: Evaluation criteria must be a list")

    @staticmethod
    def _validate_recommendation_structure(recommendation: Dict[str, Any], index: int) -> None:
        """Validate individual recommendation structure"""
        required_fields = ["category", "recommendation", "priority"]

        for field in required_fields:
            if field not in recommendation:
                raise ValueError(
                    f"Recommendation {index}: Missing required field '{field}'")

        # Validate priority
        if recommendation["priority"] not in ["high", "medium", "low"]:
            raise ValueError(
                f"Recommendation {index}: Invalid priority '{recommendation['priority']}'")

        # Validate optional fields if present
        if "resources" in recommendation and not isinstance(recommendation["resources"], list):
            raise ValueError(
                f"Recommendation {index}: Resources must be a list")

    @staticmethod
    def _validate_metadata_structure(metadata: Dict[str, Any]) -> None:
        """Validate metadata structure"""
        required_fields = ["total_questions", "estimated_total_time"]

        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"Metadata: Missing required field '{field}'")

        # Validate total_questions
        if not isinstance(metadata["total_questions"], int) or metadata["total_questions"] <= 0:
            raise ValueError("Metadata: Invalid total_questions")

        # Validate estimated_total_time
        if not isinstance(metadata["estimated_total_time"], int) or metadata["estimated_total_time"] <= 0:
            raise ValueError("Metadata: Invalid estimated_total_time")

        # Validate optional fields if present
        if "difficulty_distribution" in metadata and not isinstance(metadata["difficulty_distribution"], dict):
            raise ValueError(
                "Metadata: Difficulty distribution must be a dictionary")

        if "focus_areas" in metadata and not isinstance(metadata["focus_areas"], list):
            raise ValueError("Metadata: Focus areas must be a list")

    @staticmethod
    def get_json_schema() -> Dict[str, Any]:
        """Get the JSON schema for structured output validation"""
        return StructuredOutputPrompts.JSON_SCHEMA.copy()

    @staticmethod
    def create_sample_response(question_count: int = 3) -> Dict[str, Any]:
        """
        Create a sample structured response for testing.

        Args:
            question_count: Number of questions to include

        Returns:
            Sample structured response dictionary
        """
        return {
            "questions": [
                {
                    "id": i + 1,
                    "question": f"Sample technical question {i + 1}?",
                    "difficulty": ["easy", "medium", "hard"][i % 3],
                    "category": "conceptual",
                    "estimated_time_minutes": 5 + (i * 3),
                    "hints": [f"Hint {i + 1}a", f"Hint {i + 1}b"],
                    "follow_up_questions": [f"Follow-up {i + 1}?"],
                    "evaluation_criteria": [f"Criteria {i + 1}"]
                }
                for i in range(question_count)
            ],
            "recommendations": [
                {
                    "category": "preparation",
                    "recommendation": "Study fundamental concepts",
                    "priority": "high",
                    "resources": ["Documentation", "Practice problems"]
                }
            ],
            "metadata": {
                "total_questions": question_count,
                "difficulty_distribution": {"easy": 33, "medium": 33, "hard": 34},
                "estimated_total_time": question_count * 8,
                "focus_areas": ["concepts", "implementation"],
                "preparation_level": "intermediate"
            }
        }


# Initialize Structured Output templates when module is imported
StructuredOutputPrompts.register_all_templates()
