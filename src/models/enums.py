"""
Enums for the AI Interview Prep Application
"""
from enum import Enum


class InterviewType(Enum):
    """Types of interview preparation available"""
    TECHNICAL = "Technical Questions"
    BEHAVIORAL = "Behavioral Questions"

class ExperienceLevel(Enum):
    """Candidate experience levels"""
    JUNIOR = "Junior (1-2 years)"
    MID = "Mid-level (3-5 years)"
    SENIOR = "Senior (5+ years)"
    LEAD = "Lead/Principal"


class PromptTechnique(Enum):
    """Available prompt engineering techniques"""
    FEW_SHOT = "Few-shot Learning"
    CHAIN_OF_THOUGHT = "Chain-of-Thought"
    ZERO_SHOT = "Zero-shot"
    ROLE_BASED = "Role-based"
    STRUCTURED_OUTPUT = "Structured Output"


class DifficultyLevel(Enum):
    """Question difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionCategory(Enum):
    """Categories for technical questions"""
    ALGORITHMS = "algorithms"
    SYSTEM_DESIGN = "system_design"
    CODING = "coding"
    CONCEPTUAL = "conceptual"
    BEHAVIORAL = "behavioral"

class SessionMode(Enum):
    KEY = "session_mode"
    GENERATE_QUESTIONS = "Generate questions"
    MOCK_INTERVIEW = "Mock Interview"

class InterviewState(Enum):
    """Mock interview session states for BDD compliance"""
    NOT_STARTED = "not_started"
    GENERATING_QUESTION = "generating_question"
    QUESTION_READY = "question_ready"
    EVALUATING_ANSWER = "evaluating_answer"
    SHOWING_EVALUATION = "showing_evaluation"


class AIModel(Enum):
    """Available AI models for generation"""
    GPT_5 = "gpt-5"
    GPT_4O = "gpt-4o"

class PersonaRole(Enum):
    STRICT = "strict"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"


def get_persona_enum(persona: str) -> PersonaRole:
    match persona.lower():
        case "strict": return PersonaRole.STRICT
        case "friendly": return PersonaRole.FRIENDLY
        case "neutral": return PersonaRole.NEUTRAL
        case _: return PersonaRole.NEUTRAL