"""
Pydantic models and data schemas for the AI Interview Prep Application
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .enums import (DifficultyLevel, ExperienceLevel, InterviewType,
                    PromptTechnique, QuestionCategory)


class AISettings(BaseModel):
    """Configuration settings for AI model parameters"""
    model_config = ConfigDict(str_strip_whitespace=True)

    model: Literal["gpt-4o",
                   "gpt-5"] = Field(default="gpt-4o", description="OpenAI model to use")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Creativity/randomness (0-2)")
    max_tokens: int = Field(default=2000, ge=100, le=4000,
                            description="Maximum response tokens")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0,
                         description="Nucleus sampling parameter")
    frequency_penalty: float = Field(
        default=0.0, ge=-2.0, le=2.0, description="Frequency penalty")

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v


class Question(BaseModel):
    """Individual interview question with metadata"""
    model_config = ConfigDict(str_strip_whitespace=True)

    id: int = Field(description="Question identifier")
    question: str = Field(min_length=10, max_length=1000,
                          description="The interview question text")
    difficulty: DifficultyLevel = Field(
        description="Question difficulty level")
    category: QuestionCategory = Field(description="Question category")
    time_estimate: str = Field(
        description="Estimated time to answer (e.g., '5 minutes')")
    evaluation_criteria: List[str] = Field(
        default_factory=list, description="What to evaluate in the answer")
    follow_ups: List[str] = Field(
        default_factory=list, description="Possible follow-up questions")
    hints: List[str] = Field(default_factory=list,
                             description="Hints if candidate struggles")
    sample_framework: Optional[str] = Field(
        default=None, description="Suggested answer framework")


class CostBreakdown(BaseModel):
    """Cost breakdown for API usage"""
    model_config = ConfigDict(str_strip_whitespace=True)

    input_cost: float = Field(ge=0.0, description="Cost for input tokens")
    output_cost: float = Field(ge=0.0, description="Cost for output tokens")
    total_cost: float = Field(ge=0.0, description="Total cost for the request")
    input_tokens: int = Field(ge=0, description="Number of input tokens used")
    output_tokens: int = Field(
        ge=0, description="Number of output tokens generated")

    @field_validator('total_cost')
    @classmethod
    def validate_total_cost(cls, v, info):
        if info.data:
            input_cost = info.data.get('input_cost', 0)
            output_cost = info.data.get('output_cost', 0)
            expected_total = input_cost + output_cost
            if abs(v - expected_total) > 0.000001:  # Allow for floating point precision
                raise ValueError(
                    'Total cost must equal input_cost + output_cost')
        return v


class InterviewResults(BaseModel):
    """Results from interview question generation"""
    model_config = ConfigDict(str_strip_whitespace=True)

    questions: List[str] = Field(description="Generated interview questions")
    recommendations: List[str] = Field(
        description="Preparation recommendations")
    cost_breakdown: CostBreakdown = Field(description="API usage cost details")
    response_time: float = Field(
        ge=0.0, description="Time taken to generate (seconds)")
    model_used: str = Field(description="AI model that was used")
    tokens_used: Dict[str, int] = Field(description="Token usage details")
    technique_used: PromptTechnique = Field(
        description="Prompt technique that was applied")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata")

    @field_validator('questions')
    @classmethod
    def validate_questions(cls, v):
        if not v:
            raise ValueError('At least one question must be generated')
        if len(v) > 20:
            raise ValueError('Maximum 20 questions allowed')
        return v

    @field_validator('recommendations')
    @classmethod
    def validate_recommendations(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 recommendations allowed')
        return v


@dataclass
class InterviewSession:
    """Session data for interview preparation"""
    id: str
    timestamp: datetime
    job_description: str
    interview_type: InterviewType
    experience_level: ExperienceLevel
    ai_settings: AISettings
    prompt_technique: PromptTechnique
    question_count: int
    results: Optional[InterviewResults] = None

    def __post_init__(self):
        """Validate session data after initialization"""
        if not self.job_description or len(self.job_description.strip()) < 10:
            raise ValueError("Job description must be at least 10 characters")

        if not 1 <= self.question_count <= 20:
            raise ValueError("Question count must be between 1 and 20")


class GenerationRequest(BaseModel):
    """Request model for question generation"""
    model_config = ConfigDict(str_strip_whitespace=True)

    job_description: str = Field(
        min_length=10, max_length=5000, description="Job description text")
    interview_type: InterviewType = Field(
        description="Type of interview questions to generate")
    experience_level: ExperienceLevel = Field(
        description="Candidate experience level")
    prompt_technique: PromptTechnique = Field(
        description="Prompt engineering technique to use")
    question_count: int = Field(
        default=5, ge=1, le=20, description="Number of questions to generate")
    ai_settings: AISettings = Field(
        default_factory=AISettings, description="AI model configuration")

    @field_validator('job_description')
    @classmethod
    def validate_job_description(cls, v):
        # Basic security validation
        dangerous_patterns = ['<script', 'javascript:', 'data:text/html']
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError(
                    f'Job description contains potentially harmful content: {pattern}')
        return v.strip()


class SessionSummary(BaseModel):
    """Summary of a completed interview session"""
    model_config = ConfigDict(str_strip_whitespace=True)

    session_id: str = Field(description="Unique session identifier")
    timestamp: datetime = Field(description="When the session was created")
    interview_type: InterviewType = Field(
        description="Type of interview preparation")
    experience_level: ExperienceLevel = Field(
        description="Target experience level")
    question_count: int = Field(description="Number of questions generated")
    total_cost: float = Field(
        ge=0.0, description="Total API cost for the session")
    technique_used: PromptTechnique = Field(
        description="Prompt technique that was used")
    success: bool = Field(
        description="Whether the session completed successfully")


class ApplicationState(BaseModel):
    """Application state management"""
    model_config = ConfigDict(str_strip_whitespace=True)

    current_session: Optional[SessionSummary] = Field(
        default=None, description="Currently active session")
    session_history: List[SessionSummary] = Field(
        default_factory=list, description="Recent session history")
    total_api_calls: int = Field(
        default=0, ge=0, description="Total API calls made")
    total_cost: float = Field(
        default=0.0, ge=0.0, description="Cumulative cost across all sessions")
    error_count: int = Field(
        default=0, ge=0, description="Number of errors encountered")

    @field_validator('session_history')
    @classmethod
    def validate_session_history(cls, v):
        if len(v) > 10:
            # Keep only the 10 most recent sessions
            return v[-10:]
        return v

    def add_session(self, session: SessionSummary) -> None:
        """Add a new session to history"""
        self.session_history.append(session)
        if len(self.session_history) > 10:
            self.session_history = self.session_history[-10:]

        self.current_session = session
        self.total_api_calls += 1
        self.total_cost += session.total_cost
