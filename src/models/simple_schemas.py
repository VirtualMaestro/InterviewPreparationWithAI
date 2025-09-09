"""
Simple data schemas without Pydantic for basic functionality
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# Enums will be imported in the execution context


@dataclass
class AISettings:
    """Configuration settings for AI model parameters"""
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 0.9
    frequency_penalty: float = 0.0

    def __post_init__(self):
        """Validate settings after initialization"""
        if self.model not in ["gpt-4o", "gpt-5"]:
            raise ValueError(f"Invalid model: {self.model}")

        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")

        if not 100 <= self.max_tokens <= 4000:
            raise ValueError("Max tokens must be between 100 and 4000")


@dataclass
class CostBreakdown:
    """Cost breakdown for API usage"""
    input_cost: float
    output_cost: float
    total_cost: float
    input_tokens: int
    output_tokens: int

    def __post_init__(self):
        """Validate cost breakdown"""
        if self.input_cost < 0 or self.output_cost < 0:
            raise ValueError("Costs cannot be negative")

        expected_total = self.input_cost + self.output_cost
        if abs(self.total_cost - expected_total) > 0.000001:
            raise ValueError("Total cost must equal input_cost + output_cost")


@dataclass
class GenerationRequest:
    """Request model for question generation"""
    job_description: str
    interview_type: InterviewType
    experience_level: ExperienceLevel
    prompt_technique: PromptTechnique
    question_count: int = 5
    ai_settings: Optional[AISettings] = None

    def __post_init__(self):
        """Validate request after initialization"""
        if not self.job_description or len(self.job_description.strip()) < 10:
            raise ValueError("Job description must be at least 10 characters")

        if len(self.job_description) > 5000:
            raise ValueError("Job description too long (max 5000 characters)")

        if not 1 <= self.question_count <= 20:
            raise ValueError("Question count must be between 1 and 20")

        # Basic security validation
        dangerous_patterns = ['<script', 'javascript:', 'data:text/html']
        job_lower = self.job_description.lower()
        for pattern in dangerous_patterns:
            if pattern in job_lower:
                raise ValueError(
                    f'Job description contains harmful content: {pattern}')

        if self.ai_settings is None:
            self.ai_settings = AISettings()


@dataclass
class InterviewResults:
    """Results from interview question generation"""
    questions: List[str]
    recommendations: List[str]
    cost_breakdown: CostBreakdown
    response_time: float
    model_used: str
    tokens_used: Dict[str, int]
    technique_used: PromptTechnique
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate results after initialization"""
        if not self.questions:
            raise ValueError("At least one question must be generated")

        if len(self.questions) > 20:
            raise ValueError("Maximum 20 questions allowed")

        if len(self.recommendations) > 10:
            raise ValueError("Maximum 10 recommendations allowed")

        if self.response_time < 0:
            raise ValueError("Response time cannot be negative")

        if self.metadata is None:
            self.metadata = {}


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


@dataclass
class SessionSummary:
    """Summary of a completed interview session"""
    session_id: str
    timestamp: datetime
    interview_type: InterviewType
    experience_level: ExperienceLevel
    question_count: int
    total_cost: float
    technique_used: PromptTechnique
    success: bool

    def __post_init__(self):
        """Validate session summary"""
        if self.total_cost < 0:
            raise ValueError("Total cost cannot be negative")


@dataclass
class ApplicationState:
    """Application state management"""
    current_session: Optional[SessionSummary] = None
    session_history: List[SessionSummary] = None
    total_api_calls: int = 0
    total_cost: float = 0.0
    error_count: int = 0

    def __post_init__(self):
        """Initialize default values"""
        if self.session_history is None:
            self.session_history = []

    def add_session(self, session: SessionSummary) -> None:
        """Add a new session to history"""
        self.session_history.append(session)

        # Keep only the 10 most recent sessions
        if len(self.session_history) > 10:
            self.session_history = self.session_history[-10:]

        self.current_session = session
        self.total_api_calls += 1
        self.total_cost += session.total_cost

    def get_recent_sessions(self, count: int = 5) -> List[SessionSummary]:
        """Get the most recent sessions"""
        return self.session_history[-count:] if self.session_history else []
