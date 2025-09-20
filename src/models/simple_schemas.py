"""
Simple data schemas without Pydantic for basic functionality
"""
from dataclasses import dataclass

from .enums import ExperienceLevel, InterviewType, PersonaRole, PromptTechnique


@dataclass
class SimpleCostBreakdown:
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
class SimpleGenerationRequest:
    """Request model for question generation"""
    job_description: str
    interview_type: InterviewType
    experience_level: ExperienceLevel
    prompt_technique: PromptTechnique
    question_count: int
    persona: PersonaRole
    