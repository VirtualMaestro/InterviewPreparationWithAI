"""
Chain-of-Thought prompt implementation for interview question generation.
Provides step-by-step reasoning process for systematic question creation.
"""

from src.models.enums import ExperienceLevel, InterviewType, PromptTechnique

from .prompts import PromptTemplate, prompt_library


class ChainOfThoughtPrompts:
    """
    Chain-of-Thought prompt templates with structured reasoning processes.

    Implements step-by-step thinking for job analysis and question generation,
    with progressive complexity building for different experience levels.
    """

    @staticmethod
    def register_all_templates() -> None:
        """Register all Chain-of-Thought templates with the prompt library"""

        # Technical Interview Templates
        ChainOfThoughtPrompts._register_technical_templates()

        # Behavioral Interview Templates
        ChainOfThoughtPrompts._register_behavioral_templates()

        # Case Study Interview Templates
        ChainOfThoughtPrompts._register_case_study_templates()

        # Reverse Interview Templates (Questions for Employer)
        ChainOfThoughtPrompts._register_reverse_templates()

    @staticmethod
    def _register_technical_templates() -> None:
        """Register Chain-of-Thought templates for technical interviews"""

        # Junior Level Technical
        junior_technical = PromptTemplate(
            name="chain_of_thought_technical_junior",
            technique=PromptTechnique.CHAIN_OF_THOUGHT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.JUNIOR,
            template="""You are an experienced technical interviewer. I need you to generate {question_count} technical interview questions for a {experience_level} position. Let me walk through my reasoning process step by step.

**Step 1: Analyze the Job Description**
Job Description: {job_description}

Let me break down what this role requires:
- What are the core technologies mentioned? (programming languages, frameworks, databases)
- What level of complexity is expected for a {experience_level} role?
- What practical skills should they demonstrate?
- What foundational concepts are most important?

**Step 2: Determine Appropriate Difficulty Level**
For a {experience_level} developer (1-2 years experience), I should focus on:
- Fundamental programming concepts and syntax
- Basic problem-solving with simple algorithms
- Understanding of core development tools and practices
- Practical application of technologies mentioned in the job description
- Avoid: Complex system design, advanced algorithms, or architectural decisions

**Step 3: Identify Key Assessment Areas**
Based on the job description analysis, I should test:
- Core language/framework knowledge from the job requirements
- Basic debugging and problem-solving skills
- Understanding of development fundamentals (version control, testing, etc.)
- Practical coding ability with simple, real-world scenarios
- Communication of technical concepts at an appropriate level

**Step 4: Structure Question Progression**
I'll create questions that build in complexity:
1. Start with fundamental concept questions
2. Move to practical application questions
3. Include simple problem-solving scenarios
4. End with basic best practices or tool usage

**Step 5: Generate Questions**
Now I'll create {question_count} questions following this reasoning:

[Generate the questions here, ensuring each aligns with the analysis above and is appropriate for {experience_level} level]""",
            metadata={
                "difficulty": "beginner",
                "reasoning_steps": 5,
                "focus_areas": ["fundamental_concepts", "practical_application", "basic_problem_solving"],
                "complexity_building": "linear_progression"
            }
        )

        # Mid-Level Technical
        mid_technical = PromptTemplate(
            name="chain_of_thought_technical_mid",
            technique=PromptTechnique.CHAIN_OF_THOUGHT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.MID,
            template="""You are an experienced technical interviewer. I need you to generate {question_count} technical interview questions for a {experience_level} position. Let me walk through my reasoning process step by step.

**Step 1: Analyze the Job Description and Role Expectations**
Job Description: {job_description}

For a {experience_level} role, I need to assess:
- What advanced technologies and frameworks are required?
- What level of system thinking is expected?
- What problem-solving complexity should they handle?
- What leadership or mentoring aspects might be relevant?

**Step 2: Determine Appropriate Complexity Level**
For a {experience_level} developer (3-5 years experience), I should focus on:
- Intermediate to advanced programming concepts
- System design thinking at moderate scale
- Performance optimization and debugging skills
- Best practices and architectural decision-making
- Some cross-team collaboration and technical communication

**Step 3: Identify Advanced Assessment Areas**
Based on the analysis, I should test:
- Deep knowledge of technologies mentioned in the job description
- System design and architecture thinking
- Performance optimization and scalability considerations
- Code quality, testing, and maintainability practices
- Technical decision-making and trade-off analysis

**Step 4: Structure Progressive Complexity**
I'll create questions with increasing sophistication:
1. Start with advanced technical concepts
2. Move to system design and architecture questions
3. Include optimization and performance scenarios
4. Add decision-making and trade-off analysis
5. End with cross-functional or leadership elements

**Step 5: Consider Real-World Application**
Each question should reflect realistic scenarios they'd encounter:
- Problems that require analysis and multiple solution approaches
- Situations requiring technical judgment and justification
- Scenarios involving system constraints and trade-offs
- Cross-team technical communication challenges

**Step 6: Generate Questions**
Now I'll create {question_count} questions following this reasoning:

[Generate the questions here, ensuring each builds on the previous analysis and demonstrates {experience_level} complexity]""",
            metadata={
                "difficulty": "intermediate",
                "reasoning_steps": 6,
                "focus_areas": ["system_design", "optimization", "decision_making", "technical_leadership"],
                "complexity_building": "progressive_sophistication"
            }
        )

        # Senior Level Technical
        senior_technical = PromptTemplate(
            name="chain_of_thought_technical_senior",
            technique=PromptTechnique.CHAIN_OF_THOUGHT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR,
            template="""You are an experienced technical interviewer. I need you to generate {question_count} technical interview questions for a {experience_level} position. Let me walk through my reasoning process step by step.

**Step 1: Analyze Strategic Technical Requirements**
Job Description: {job_description}

For a {experience_level} role, I must evaluate:
- What complex systems and architectural challenges exist?
- What level of technical leadership is required?
- What cross-organizational impact is expected?
- What strategic technical decisions will they make?

**Step 2: Assess Advanced Competency Requirements**
For a {experience_level} developer (5+ years experience), I should focus on:
- Advanced system architecture and design patterns
- Scalability, reliability, and performance at enterprise scale
- Technical leadership and mentoring capabilities
- Strategic thinking and long-term technical planning
- Cross-functional collaboration and stakeholder management

**Step 3: Identify Strategic Assessment Areas**
Based on the role analysis, I should test:
- Complex system design and architectural decision-making
- Scalability and reliability engineering expertise
- Technical leadership and team development skills
- Strategic planning and technical roadmap creation
- Risk assessment and mitigation in technical decisions

**Step 4: Structure Multi-Dimensional Complexity**
I'll create questions that assess multiple competencies:
1. Complex technical problems requiring architectural thinking
2. Leadership scenarios involving technical decision-making
3. Strategic planning and long-term technical vision
4. Cross-organizational influence and communication
5. Mentoring and team development capabilities

**Step 5: Consider Organizational Impact**
Each question should reflect senior-level responsibilities:
- Decisions that affect multiple teams and systems
- Long-term technical strategy and planning
- Risk management and technical debt considerations
- Mentoring and developing other engineers
- Balancing technical excellence with business needs

**Step 6: Evaluate Cross-Functional Leadership**
Senior roles require assessment of:
- Communication with non-technical stakeholders
- Technical advocacy and influence across the organization
- Conflict resolution in technical disagreements
- Building consensus on technical direction

**Step 7: Generate Questions**
Now I'll create {question_count} questions following this comprehensive reasoning:

[Generate the questions here, ensuring each reflects senior-level strategic thinking and technical leadership]""",
            metadata={
                "difficulty": "advanced",
                "reasoning_steps": 7,
                "focus_areas": ["strategic_architecture", "technical_leadership", "organizational_impact", "mentoring"],
                "complexity_building": "multi_dimensional"
            }
        )

        # Lead Level Technical
        lead_technical = PromptTemplate(
            name="chain_of_thought_technical_lead",
            technique=PromptTechnique.CHAIN_OF_THOUGHT,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.LEAD,
            template="""You are an experienced technical interviewer. I need you to generate {question_count} technical interview questions for a {experience_level} position. Let me walk through my reasoning process step by step.

**Step 1: Analyze Executive Technical Leadership Requirements**
Job Description: {job_description}

For a {experience_level} role, I must evaluate:
- What organizational transformation capabilities are needed?
- What level of technical vision and strategy is required?
- What executive communication and influence is expected?
- What large-scale technical program management is involved?

**Step 2: Assess Principal/Staff Level Competencies**
For a {experience_level} engineer (principal/staff level), I should focus on:
- Organizational technical strategy and vision
- Large-scale system transformation and modernization
- Executive-level communication and stakeholder management
- Technical culture development and organizational scaling
- Industry expertise and thought leadership

**Step 3: Identify Organizational Assessment Areas**
Based on the leadership analysis, I should test:
- Technical vision and long-term strategic planning
- Organizational transformation and change management
- Executive communication and cross-functional leadership
- Technical culture development and scaling practices
- Industry expertise and external thought leadership

**Step 4: Structure Organizational Complexity**
I'll create questions that assess executive-level capabilities:
1. Organizational technical strategy and vision setting
2. Large-scale transformation and change management
3. Executive stakeholder management and communication
4. Technical culture and organizational development
5. Industry leadership and external influence

**Step 5: Consider Enterprise-Scale Impact**
Each question should reflect principal/staff responsibilities:
- Decisions affecting entire engineering organizations
- Technical strategy spanning multiple years and products
- Cultural transformation and organizational scaling
- External industry influence and thought leadership
- Executive-level business and technical alignment

**Step 6: Evaluate Transformation Leadership**
Principal/staff roles require assessment of:
- Leading technical transformation across large organizations
- Building consensus among senior technical leaders
- Communicating technical strategy to executive leadership
- Developing and scaling technical culture and practices

**Step 7: Assess Industry Influence**
At this level, candidates should demonstrate:
- Thought leadership and industry expertise
- External speaking, writing, or open source contributions
- Influence on technical standards and best practices
- Ability to attract and develop top technical talent

**Step 8: Generate Questions**
Now I'll create {question_count} questions following this executive-level reasoning:

[Generate the questions here, ensuring each reflects principal/staff-level organizational leadership and technical vision]""",
            metadata={
                "difficulty": "expert",
                "reasoning_steps": 8,
                "focus_areas": ["organizational_strategy", "transformation_leadership", "executive_communication", "industry_influence"],
                "complexity_building": "organizational_scale"
            }
        )

        # Register all technical templates
        for template in [junior_technical, mid_technical, senior_technical, lead_technical]:
            prompt_library.register_template(template)

    @staticmethod
    def _register_behavioral_templates() -> None:
        """Register Chain-of-Thought templates for behavioral interviews"""

        # Junior Level Behavioral
        junior_behavioral = PromptTemplate(
            name="chain_of_thought_behavioral_junior",
            technique=PromptTechnique.CHAIN_OF_THOUGHT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.JUNIOR,
            template="""You are an experienced behavioral interviewer. I need you to generate {question_count} behavioral interview questions for a {experience_level} position. Let me walk through my reasoning process step by step.

**Step 1: Analyze Role and Experience Expectations**
Job Description: {job_description}

For a {experience_level} role, I need to assess:
- What foundational professional skills are required?
- What learning and growth mindset indicators should I look for?
- What collaboration and communication abilities are needed?
- What basic problem-solving approaches are expected?

**Step 2: Identify Key Behavioral Competencies**
For a {experience_level} professional (1-2 years experience), I should focus on:
- Learning agility and adaptability to new situations
- Basic collaboration and teamwork skills
- Communication and help-seeking behaviors
- Accountability and ownership of mistakes
- Growth mindset and receptiveness to feedback

**Step 3: Structure Appropriate Scenario Complexity**
I'll focus on scenarios that a junior professional would encounter:
- Learning new technologies or processes quickly
- Working with team members and asking for help
- Handling mistakes and learning from feedback
- Adapting to changing requirements or priorities
- Taking ownership of individual tasks and deliverables

**Step 4: Design Questions for Growth Assessment**
Each question should evaluate:
- How they approach learning and skill development
- Their ability to collaborate effectively with others
- Their response to challenges and setbacks
- Their communication style and help-seeking behavior
- Their accountability and professional maturity

**Step 5: Generate Questions**
Now I'll create {question_count} behavioral questions following this reasoning:

[Generate the questions here, focusing on learning, collaboration, and professional development appropriate for {experience_level} level]""",
            metadata={
                "difficulty": "entry_level",
                "reasoning_steps": 5,
                "focus_areas": ["learning_agility", "collaboration", "accountability", "growth_mindset"],
                "scenario_complexity": "individual_contributor"
            }
        )

        # Mid-Level Behavioral
        mid_behavioral = PromptTemplate(
            name="chain_of_thought_behavioral_mid",
            technique=PromptTechnique.CHAIN_OF_THOUGHT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.MID,
            template="""You are an experienced behavioral interviewer. I need you to generate {question_count} behavioral interview questions for a {experience_level} position. Let me walk through my reasoning process step by step.

**Step 1: Analyze Intermediate Leadership Requirements**
Job Description: {job_description}

For a {experience_level} role, I need to assess:
- What influence and persuasion capabilities are needed?
- What project management and prioritization skills are required?
- What cross-team collaboration abilities are expected?
- What proactive problem-solving approaches are needed?

**Step 2: Identify Advanced Behavioral Competencies**
For a {experience_level} professional (3-5 years experience), I should focus on:
- Influence and persuasion without formal authority
- Project management and competing priority handling
- Cross-functional collaboration and communication
- Proactive problem identification and resolution
- Beginning leadership and mentoring capabilities

**Step 3: Structure Intermediate Scenario Complexity**
I'll focus on scenarios involving:
- Leading initiatives or convincing others of new approaches
- Managing multiple projects with competing deadlines
- Working across teams with different priorities
- Identifying and solving problems before they escalate
- Beginning to mentor or guide junior team members

**Step 4: Design Questions for Leadership Potential**
Each question should evaluate:
- Their ability to influence and persuade others
- Their approach to managing complexity and priorities
- Their cross-functional collaboration skills
- Their proactive thinking and problem-solving
- Their emerging leadership and mentoring abilities

**Step 5: Assess Strategic Thinking Development**
Questions should also explore:
- How they balance short-term and long-term considerations
- Their ability to see broader organizational context
- Their approach to stakeholder management
- Their conflict resolution and negotiation skills

**Step 6: Generate Questions**
Now I'll create {question_count} behavioral questions following this reasoning:

[Generate the questions here, focusing on influence, project management, and emerging leadership appropriate for {experience_level} level]""",
            metadata={
                "difficulty": "intermediate",
                "reasoning_steps": 6,
                "focus_areas": ["influence", "project_management", "cross_team_collaboration", "emerging_leadership"],
                "scenario_complexity": "multi_stakeholder"
            }
        )

        # Senior Level Behavioral
        senior_behavioral = PromptTemplate(
            name="chain_of_thought_behavioral_senior",
            technique=PromptTechnique.CHAIN_OF_THOUGHT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.SENIOR,
            template="""You are an experienced behavioral interviewer. I need you to generate {question_count} behavioral interview questions for a {experience_level} position. Let me walk through my reasoning process step by step.

**Step 1: Analyze Senior Leadership Requirements**
Job Description: {job_description}

For a {experience_level} role, I need to assess:
- What strategic decision-making capabilities are required?
- What people development and mentoring skills are needed?
- What organizational influence and change management abilities are expected?
- What conflict resolution and stakeholder management skills are necessary?

**Step 2: Identify Senior Leadership Competencies**
For a {experience_level} professional (5+ years experience), I should focus on:
- Strategic thinking and long-term planning
- People development, mentoring, and team building
- Organizational influence and change leadership
- Complex stakeholder management and conflict resolution
- Cultural development and process improvement

**Step 3: Structure Complex Organizational Scenarios**
I'll focus on scenarios involving:
- Making difficult decisions with organizational impact
- Developing and mentoring team members through challenges
- Leading change initiatives across multiple teams
- Managing conflicts between senior stakeholders
- Building consensus on strategic direction

**Step 4: Design Questions for Strategic Leadership**
Each question should evaluate:
- Their strategic thinking and decision-making process
- Their approach to developing and mentoring others
- Their ability to influence and lead organizational change
- Their stakeholder management and conflict resolution skills
- Their cultural and process improvement capabilities

**Step 5: Assess Organizational Impact**
Questions should explore:
- How they drive results through others
- Their approach to building high-performing teams
- Their ability to navigate organizational politics
- Their methods for scaling processes and culture

**Step 6: Evaluate Change Leadership**
Senior roles require assessment of:
- Leading transformation initiatives
- Building buy-in for strategic changes
- Managing resistance and overcoming obstacles
- Measuring and communicating impact

**Step 7: Generate Questions**
Now I'll create {question_count} behavioral questions following this reasoning:

[Generate the questions here, focusing on strategic leadership, mentoring, and organizational impact appropriate for {experience_level} level]""",
            metadata={
                "difficulty": "advanced",
                "reasoning_steps": 7,
                "focus_areas": ["strategic_leadership", "mentoring", "organizational_change", "stakeholder_management"],
                "scenario_complexity": "organizational_impact"
            }
        )

        # Lead Level Behavioral
        lead_behavioral = PromptTemplate(
            name="chain_of_thought_behavioral_lead",
            technique=PromptTechnique.CHAIN_OF_THOUGHT,
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.LEAD,
            template="""You are an experienced behavioral interviewer. I need you to generate {question_count} behavioral interview questions for a {experience_level} position. Let me walk through my reasoning process step by step.

**Step 1: Analyze Executive Leadership Requirements**
Job Description: {job_description}

For a {experience_level} role, I need to assess:
- What organizational transformation capabilities are needed?
- What executive communication and influence skills are required?
- What strategic vision and culture development abilities are expected?
- What large-scale change management and scaling expertise is necessary?

**Step 2: Identify Executive Leadership Competencies**
For a {experience_level} professional (principal/staff level), I should focus on:
- Organizational transformation and culture change
- Executive communication and senior stakeholder influence
- Strategic vision setting and long-term planning
- Large-scale change management and organizational scaling
- Industry leadership and external influence

**Step 3: Structure Enterprise-Scale Scenarios**
I'll focus on scenarios involving:
- Transforming organizational culture and practices
- Communicating with and influencing executive leadership
- Setting strategic vision across large organizations
- Managing complex, multi-year transformation initiatives
- Building external industry influence and partnerships

**Step 4: Design Questions for Transformation Leadership**
Each question should evaluate:
- Their organizational transformation and culture change experience
- Their executive communication and influence capabilities
- Their strategic vision setting and planning abilities
- Their large-scale change management and scaling expertise
- Their industry leadership and external influence

**Step 5: Assess Cultural and Strategic Impact**
Questions should explore:
- How they drive cultural transformation at scale
- Their approach to building organizational consensus
- Their methods for scaling practices across large organizations
- Their ability to balance competing executive priorities

**Step 6: Evaluate External Influence**
Principal/staff roles require assessment of:
- Building industry partnerships and influence
- Representing the organization in external forums
- Contributing to industry standards and best practices
- Attracting and developing top talent

**Step 7: Assess Long-term Vision**
Questions should examine:
- Their ability to set and communicate long-term vision
- Their approach to multi-year strategic planning
- Their methods for maintaining momentum through long initiatives
- Their ability to adapt strategy based on changing conditions

**Step 8: Generate Questions**
Now I'll create {question_count} behavioral questions following this reasoning:

[Generate the questions here, focusing on organizational transformation, executive influence, and strategic vision appropriate for {experience_level} level]""",
            metadata={
                "difficulty": "expert",
                "reasoning_steps": 8,
                "focus_areas": ["organizational_transformation", "executive_influence", "strategic_vision", "culture_change"],
                "scenario_complexity": "enterprise_scale"
            }
        )

        # Register all behavioral templates
        for template in [junior_behavioral, mid_behavioral, senior_behavioral, lead_behavioral]:
            prompt_library.register_template(template)

    @staticmethod
    def _register_case_study_templates() -> None:
        """Register Chain-of-Thought templates for case study interviews"""

        # Generic Case Study with reasoning process
        case_study_generic = PromptTemplate(
            name="chain_of_thought_case_study_generic",
            technique=PromptTechnique.CHAIN_OF_THOUGHT,
            interview_type=InterviewType.CASE_STUDY,
            experience_level=None,  # Generic for all levels
            template="""You are an experienced interviewer conducting case study interviews. I need you to generate {question_count} case study questions for a {experience_level} position. Let me walk through my reasoning process step by step.

**Step 1: Analyze the Role and Technical Context**
Job Description: {job_description}

I need to understand:
- What technical domains and challenges are most relevant?
- What level of system complexity should the scenarios involve?
- What problem-solving approaches should I assess?
- What real-world constraints and trade-offs are important?

**Step 2: Determine Appropriate Scenario Complexity**
Based on the {experience_level} level, I should create scenarios that:
- Match the complexity they'd encounter in this role
- Test relevant technical and analytical skills
- Allow for multiple valid solution approaches
- Include realistic constraints and trade-offs

**Step 3: Structure Problem-Solving Assessment**
Each case study should evaluate:
- Their systematic approach to problem analysis
- Their ability to ask clarifying questions
- Their consideration of multiple solution options
- Their evaluation of trade-offs and constraints
- Their communication of reasoning and decisions

**Step 4: Design Realistic Technical Scenarios**
I'll create scenarios that:
- Reflect actual challenges mentioned in the job description
- Include ambiguity that requires clarification
- Have multiple valid solution paths
- Test both technical knowledge and judgment
- Allow assessment of their thought process

**Step 5: Build in Progressive Complexity**
Each scenario should:
- Start with clear problem definition
- Include layers of complexity that can be explored
- Allow for follow-up questions based on their approach
- Test both breadth and depth of thinking

**Step 6: Generate Case Studies**
Now I'll create {question_count} case study scenarios following this reasoning:

[Generate the case studies here, ensuring each provides a realistic technical scenario with appropriate complexity for {experience_level} level, focusing on areas mentioned in the job description]""",
            metadata={
                "difficulty": "adaptive",
                "reasoning_steps": 6,
                "focus_areas": ["systematic_analysis", "problem_solving", "technical_judgment", "communication"],
                "scenario_type": "realistic_technical_challenges"
            }
        )

        prompt_library.register_template(case_study_generic)

    @staticmethod
    def _register_reverse_templates() -> None:
        """Register Chain-of-Thought templates for reverse interviews"""

        # Generic Reverse Interview with reasoning
        reverse_generic = PromptTemplate(
            name="chain_of_thought_reverse_generic",
            technique=PromptTechnique.CHAIN_OF_THOUGHT,
            interview_type=InterviewType.REVERSE,
            experience_level=None,  # Generic for all levels
            template="""You are helping a candidate prepare thoughtful questions to ask their potential employer. I need to generate {question_count} strategic questions for a {experience_level} position. Let me walk through my reasoning process step by step.

**Step 1: Analyze the Role and Candidate Priorities**
Job Description: {job_description}

I need to consider:
- What aspects of this role would be most important to evaluate?
- What information would help the candidate make an informed decision?
- What concerns or priorities would someone at {experience_level} level have?
- What strategic questions would demonstrate their thoughtfulness and preparation?

**Step 2: Identify Key Evaluation Areas**
A candidate should assess:
- Role expectations and success metrics
- Team dynamics and collaboration patterns
- Growth opportunities and career development
- Company culture and values alignment
- Technical challenges and learning opportunities

**Step 3: Structure Questions by Strategic Value**
I'll create questions that:
- Demonstrate genuine interest and preparation
- Provide valuable decision-making information
- Show strategic thinking about their career
- Help evaluate cultural and role fit
- Cannot be easily answered through basic research

**Step 4: Consider Experience Level Appropriateness**
For a {experience_level} candidate, questions should:
- Reflect their career stage and priorities
- Show appropriate level of strategic thinking
- Demonstrate understanding of their potential impact
- Address concerns relevant to their experience level

**Step 5: Balance Different Question Types**
I'll include questions about:
- Role-specific expectations and challenges
- Team structure and collaboration
- Growth and development opportunities
- Company culture and values
- Strategic direction and future plans

**Step 6: Generate Strategic Questions**
Now I'll create {question_count} thoughtful questions following this reasoning:

[Generate the questions here, ensuring each provides strategic value for evaluating the role and demonstrates thoughtful preparation appropriate for {experience_level} level]""",
            metadata={
                "difficulty": "strategic",
                "reasoning_steps": 6,
                "focus_areas": ["role_evaluation", "strategic_thinking", "career_planning", "cultural_assessment"],
                "question_type": "mutual_evaluation"
            }
        )

        prompt_library.register_template(reverse_generic)


# Initialize Chain-of-Thought templates when module is imported
ChainOfThoughtPrompts.register_all_templates()
