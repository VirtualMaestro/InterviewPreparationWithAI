"""
Enums for the AI Interview Prep Application
"""
from enum import Enum


class InterviewType(Enum):
    """Types of interview preparation available"""
    TECHNICAL = "Technical Questions"
    BEHAVIORAL = "Behavioral Questions"
    CASE_STUDY = "Case Studies"
    REVERSE = "Questions for Employer"


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
    CASE_STUDY = "case_study"


class AIModel(Enum):
    """Available AI models for generation"""
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
