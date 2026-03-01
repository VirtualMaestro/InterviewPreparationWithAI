# Prompt Engineering Specification
# Auto-generated — review for accuracy

## Requirement: Five Prompt Engineering Techniques
The system SHALL implement all 5 advanced prompt engineering techniques with comprehensive template coverage.

### Scenario: Few-Shot Learning technique
- GIVEN user selects Few-Shot technique
- WHEN generating questions
- THEN the system SHALL use example-driven prompts with 2-3 sample questions
- AND examples SHALL be relevant to the interview type and experience level
- AND the AI SHALL learn from the examples to generate similar questions

### Scenario: Chain-of-Thought technique
- GIVEN user selects Chain-of-Thought technique
- WHEN generating questions
- THEN the system SHALL use step-by-step reasoning prompts
- AND the prompt SHALL guide the AI through: understanding job requirements → identifying key skills → formulating questions → ensuring relevance
- AND questions SHALL demonstrate logical progression

### Scenario: Zero-Shot technique
- GIVEN user selects Zero-Shot technique
- WHEN generating questions
- THEN the system SHALL use direct generation prompts without examples
- AND the prompt SHALL be clear and specific
- AND the AI SHALL generate questions based solely on the instructions

### Scenario: Role-Based technique
- GIVEN user selects Role-Based technique
- WHEN generating questions
- THEN the system SHALL adopt an interviewer persona (Strict, Friendly, Neutral)
- AND questions SHALL reflect the persona's style
- AND the prompt SHALL include persona-specific instructions

### Scenario: Structured Output technique
- GIVEN user selects Structured Output technique
- WHEN generating questions
- THEN the system SHALL request JSON-formatted responses
- AND response SHALL include question, difficulty, topic, follow_up fields
- AND the AI SHALL return structured data for easy parsing

**Implementation:** `src/ai/few_shot.py`, `src/ai/chain_of_thought.py`, `src/ai/zero_shot.py`, `src/ai/role_based.py`, `src/ai/structured_output.py`

## Requirement: Comprehensive Template Coverage
The system SHALL provide 62 total templates covering all combinations of techniques, interview types, and experience levels.

### Scenario: Template availability for all combinations
- GIVEN any combination of technique, interview type, and experience level
- WHEN requesting a template
- THEN a matching template SHALL be available
- AND if no exact match exists, a fallback template SHALL be provided

**Template Distribution:**
- Few-Shot Learning: 10 templates
- Chain-of-Thought: 10 templates
- Zero-Shot: 10 templates
- Role-Based: 12 templates (3 personas × 4 interview types)
- Structured Output: 10 templates
- **Total: 62 templates**

## Requirement: Progressive Difficulty Scaling
The system SHALL scale question difficulty based on experience level from Junior to Lead/Principal.

### Scenario: Junior level questions (1-2 years)
- GIVEN experience level is Junior
- WHEN generating questions
- THEN questions SHALL focus on fundamental concepts
- AND complexity SHALL be appropriate for entry-level (basic syntax, simple algorithms, common patterns)
- AND questions SHALL avoid advanced architecture or system design

### Scenario: Mid-level questions (3-5 years)
- GIVEN experience level is Mid-level
- WHEN generating questions
- THEN questions SHALL focus on practical application and problem-solving
- AND complexity SHALL include design patterns, optimization, debugging
- AND questions SHALL require deeper understanding than Junior level

### Scenario: Senior level questions (6-10 years)
- GIVEN experience level is Senior
- WHEN generating questions
- THEN questions SHALL focus on architecture, scalability, and best practices
- AND complexity SHALL include system design, performance optimization, trade-offs
- AND questions SHALL require broad technical knowledge

### Scenario: Lead/Principal level questions (10+ years)
- GIVEN experience level is Lead or Principal
- WHEN generating questions
- THEN questions SHALL focus on strategic thinking, leadership, and complex systems
- AND complexity SHALL include distributed systems, organizational impact, technical vision
- AND questions SHALL require expert-level knowledge and experience

## Requirement: Interview Type Specialization
The system SHALL provide specialized templates for each interview type (Technical, Behavioral, Case Study, Reverse).

### Scenario: Technical interview questions
- GIVEN interview type is Technical
- WHEN generating questions
- THEN questions SHALL focus on coding, algorithms, data structures, system design
- AND questions SHALL be specific to the job description's technical requirements

### Scenario: Behavioral interview questions
- GIVEN interview type is Behavioral
- WHEN generating questions
- THEN questions SHALL focus on past experiences, teamwork, conflict resolution, leadership
- AND questions SHALL use STAR format (Situation, Task, Action, Result)

### Scenario: Case Study interview questions
- GIVEN interview type is Case Study
- WHEN generating questions
- THEN questions SHALL present real-world scenarios requiring analysis and solutions
- AND questions SHALL assess problem-solving approach and decision-making

### Scenario: Reverse interview questions
- GIVEN interview type is Reverse
- WHEN generating questions
- THEN questions SHALL be what the candidate should ask the interviewer
- AND questions SHALL help assess company culture, role expectations, team dynamics

## Requirement: Company-Aware Role Adoption
The system SHALL adapt interviewer personas based on company type (Startup, Enterprise, Tech Giant, Consulting, Academia).

### Scenario: Startup interviewer persona
- GIVEN company type is Startup
- WHEN using Role-Based technique
- THEN questions SHALL emphasize adaptability, ownership, rapid learning
- AND tone SHALL be informal and fast-paced

### Scenario: Enterprise interviewer persona
- GIVEN company type is Enterprise
- WHEN using Role-Based technique
- THEN questions SHALL emphasize process, compliance, scalability
- AND tone SHALL be formal and structured

## Requirement: Interviewer Persona Styles
The system SHALL support 3 interviewer persona styles (Strict, Friendly, Neutral) for Role-Based technique.

### Scenario: Strict persona
- GIVEN persona is Strict
- WHEN generating questions
- THEN questions SHALL be direct and challenging
- AND tone SHALL be formal and demanding
- AND follow-up questions SHALL probe deeply

### Scenario: Friendly persona
- GIVEN persona is Friendly
- WHEN generating questions
- THEN questions SHALL be conversational and encouraging
- AND tone SHALL be warm and supportive
- AND follow-up questions SHALL guide the candidate

### Scenario: Neutral persona
- GIVEN persona is Neutral
- WHEN generating questions
- THEN questions SHALL be balanced and professional
- AND tone SHALL be objective and fair
- AND follow-up questions SHALL clarify understanding

## Requirement: Fallback Strategy Integration
The system SHALL integrate with the multi-level fallback system to ensure 100% availability.

### Scenario: Primary technique failure
- GIVEN the selected technique fails to generate questions
- WHEN fallback is triggered
- THEN the system SHALL attempt a secondary technique
- AND if all techniques fail, Zero-Shot SHALL be used as final fallback
- AND emergency default questions SHALL be provided if all else fails

**Current State:**
- 62 templates fully implemented and tested
- All 5 techniques operational
- Progressive difficulty scaling from Junior to Lead/Principal
- 4 interview types supported
- 3 interviewer personas for Role-Based
- 5 company types for context adaptation
- Comprehensive fallback system ensuring 100% reliability
