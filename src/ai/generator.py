"""
AI Question Generator with OpenAI API integration and retry logic.

This module provides the core AI integration for generating interview questions
using various prompt engineering techniques with retry mechanisms and fallback strategies.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from openai import AsyncOpenAI, OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_log,
    after_log
)

from models.enums import (
    InterviewType,
    ExperienceLevel,
    PromptTechnique,
    AIModel
)
from models.simple_schemas import (
    InterviewSession,
    InterviewResults,
    GenerationRequest,
    CostBreakdown
)
from utils.cost import cost_calculator
from utils.rate_limiter import rate_limiter
from utils.security import SecurityValidator
from utils.error_handler import (
    global_error_handler, 
    handle_async_errors, 
    ErrorContext,
    APIError as AppAPIError,
    RateLimitError as AppRateLimitError,
    ValidationError,
    ErrorCategory
)
from ai.prompts import prompt_library, PromptTemplate
from ai.few_shot import FewShotPrompts
from ai.chain_of_thought import ChainOfThoughtPrompts
from ai.zero_shot import ZeroShotPrompts
from ai.role_based import RoleBasedPrompts
from ai.structured_output import StructuredOutputPrompts
from ai.parser import response_parser, ParseStrategy

logger = logging.getLogger(__name__)


class GeneratorError(Exception):
    """Base exception for generator errors."""
    pass


class APIError(GeneratorError):
    """API-related errors."""
    pass


class ParsingError(GeneratorError):
    """Response parsing errors."""
    pass


class RateLimitError(GeneratorError):
    """Rate limit exceeded errors."""
    pass


@dataclass
class GenerationResult:
    """Result of question generation."""
    questions: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]
    cost_breakdown: CostBreakdown
    raw_response: str
    technique_used: PromptTechnique
    model_used: AIModel
    success: bool
    error_message: Optional[str] = None


class InterviewQuestionGenerator:
    """
    Main AI question generator with OpenAI API integration.
    
    Features:
    - Multiple prompt techniques with automatic fallback
    - Retry logic with exponential backoff
    - Cost tracking and rate limiting
    - Security validation and sanitization
    - Structured and text response parsing
    """
    
    def __init__(self, api_key: str, model: AIModel = AIModel.GPT_4O):
        """
        Initialize the generator with API credentials.
        
        Args:
            api_key: OpenAI API key
            model: AI model to use (default: GPT-4o)
        """
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)
        self.sync_client = OpenAI(api_key=api_key)
        self.security = SecurityValidator()
        
        # Configure retry settings
        self.max_retries = 3
        self.base_wait = 1  # seconds
        self.max_wait = 10  # seconds
        
        logger.info(f"Initialized generator with model: {model.value}")
    
    @handle_async_errors(
        error_handler=global_error_handler,
        attempt_recovery=True,
        reraise=True
    )
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((APIError, asyncio.TimeoutError)),
        before=before_log(logger, logging.DEBUG),
        after=after_log(logger, logging.DEBUG)
    )
    async def _make_api_call(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Make API call with retry logic.
        
        Args:
            prompt: The prompt to send
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            API response dictionary
            
        Raises:
            APIError: On API failures
            RateLimitError: When rate limit exceeded
        """
        # Check rate limit
        if not rate_limiter.can_make_call():
            status = rate_limiter.get_rate_limit_status()
            context = ErrorContext(
                operation="api_call",
                additional_info={
                    "rate_limit_status": status._asdict() if hasattr(status, '_asdict') else str(status),
                    "model": self.model.value
                }
            )
            raise AppRateLimitError(
                f"Rate limit exceeded. Reset in {status.time_until_reset.total_seconds():.0f} seconds",
                retry_after=int(status.time_until_reset.total_seconds()),
                context=context
            )
        
        try:
            # Record the API call
            rate_limiter.record_call()
            
            # Make the API call
            response = await self.client.chat.completions.create(
                model=self.model.value,
                messages=[
                    {"role": "system", "content": "You are an expert interview coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=30  # 30 second timeout
            )
            
            # Extract response data
            result = {
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }
            
            logger.debug(f"API call successful: {result['usage']['total_tokens']} tokens")
            return result
            
        except asyncio.TimeoutError:
            context = ErrorContext(
                operation="api_call",
                additional_info={"timeout_duration": 30, "model": self.model.value}
            )
            logger.error("API call timed out")
            raise AppAPIError("API call timed out after 30 seconds", context=context)
        except Exception as e:
            context = ErrorContext(
                operation="api_call",
                additional_info={"model": self.model.value, "error_type": type(e).__name__}
            )
            logger.error(f"API call failed: {str(e)}")
            raise AppAPIError(f"API call failed: {str(e)}", context=context, cause=e)
    
    def _select_prompt_template(
        self,
        request: GenerationRequest,
        technique: PromptTechnique
    ) -> Optional[PromptTemplate]:
        """
        Select appropriate prompt template.
        
        Args:
            request: Generation request
            technique: Prompt technique to use
            
        Returns:
            Selected template or None
        """
        try:
            # Try to get template from prompt library
            template = prompt_library.get_template(
                technique,
                request.interview_type,
                request.experience_level
            )
            
            if template:
                return template
            
            # Fallback to technique-specific methods
            if technique == PromptTechnique.FEW_SHOT:
                return FewShotPrompts.get_template(
                    request.interview_type,
                    request.experience_level
                )
            elif technique == PromptTechnique.CHAIN_OF_THOUGHT:
                return ChainOfThoughtPrompts.get_template(
                    request.interview_type,
                    request.experience_level
                )
            elif technique == PromptTechnique.ZERO_SHOT:
                return ZeroShotPrompts.get_template(
                    request.interview_type,
                    request.experience_level
                )
            elif technique == PromptTechnique.ROLE_BASED:
                persona = getattr(request, 'additional_context', {}).get("persona", "neutral")
                return RoleBasedPrompts.get_persona_template(
                    persona,
                    request.interview_type
                )
            elif technique == PromptTechnique.STRUCTURED_OUTPUT:
                return StructuredOutputPrompts.get_template(
                    request.interview_type,
                    request.experience_level
                )
                
        except Exception as e:
            logger.error(f"Error selecting template: {str(e)}")
            
        return None
    
    def _build_prompt(
        self,
        request: GenerationRequest,
        template: PromptTemplate
    ) -> str:
        """
        Build final prompt from template and request.
        
        Args:
            request: Generation request
            template: Prompt template
            
        Returns:
            Final prompt string
        """
        # Prepare variables for substitution
        variables = {
            "job_description": request.job_description,
            "experience_level": request.experience_level.value,
            "interview_type": request.interview_type.value,
            "num_questions": request.question_count,
            "company_type": getattr(request, 'additional_context', {}).get("company_type", "general"),
            "focus_areas": getattr(request, 'additional_context', {}).get("focus_areas", "general skills")
        }
        
        # Get prompt content
        prompt_content = template.template
        
        # Substitute variables
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt_content:
                prompt_content = prompt_content.replace(placeholder, str(value))
        
        return prompt_content
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from API.
        
        Args:
            response: Raw response string
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            ParsingError: If parsing fails
        """
        try:
            # Try to extract JSON from response
            # Handle cases where response has markdown code blocks
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()
            
            # Parse JSON
            data = json.loads(json_str)
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            raise ParsingError(f"Failed to parse JSON response: {str(e)}")
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """
        Parse text response to extract questions and recommendations.
        
        Args:
            response: Raw response string
            
        Returns:
            Parsed data dictionary
        """
        lines = response.strip().split('\n')
        questions = []
        recommendations = []
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect sections
            if any(word in line.lower() for word in ['question', 'interview']):
                current_section = 'questions'
                continue
            elif any(word in line.lower() for word in ['recommendation', 'tip', 'advice']):
                current_section = 'recommendations'
                continue
            
            # Parse numbered items
            if line[0].isdigit() or line.startswith('-') or line.startswith('•'):
                # Clean up the line
                if line[0].isdigit():
                    # Remove number and punctuation
                    parts = line.split('.', 1)
                    if len(parts) > 1:
                        line = parts[1].strip()
                    else:
                        parts = line.split(')', 1)
                        if len(parts) > 1:
                            line = parts[1].strip()
                else:
                    # Remove bullet point
                    line = line[1:].strip()
                
                # Add to appropriate section
                if current_section == 'recommendations' or (
                    current_section is None and 
                    any(word in line.lower() for word in ['prepare', 'practice', 'review'])
                ):
                    recommendations.append(line)
                else:
                    questions.append(line)
        
        # Ensure we have at least some questions
        if not questions and recommendations:
            # Some recommendations might actually be questions
            questions = recommendations[:5]
            recommendations = recommendations[5:]
        
        return {
            "questions": questions,
            "recommendations": recommendations,
            "metadata": {
                "parsed_from": "text",
                "total_lines": len(lines)
            }
        }
    
    @handle_async_errors(
        error_handler=global_error_handler,
        attempt_recovery=False,
        reraise=False
    )
    async def generate_questions(
        self,
        request: GenerationRequest,
        preferred_technique: Optional[PromptTechnique] = None
    ) -> GenerationResult:
        """
        Generate interview questions based on request.
        
        Args:
            request: Generation request with job details
            preferred_technique: Preferred prompt technique (optional)
            
        Returns:
            Generation result with questions and metadata
        """
        # Create error context for this operation
        error_context = ErrorContext(
            operation="generate_questions",
            additional_info={
                "interview_type": request.interview_type.value,
                "experience_level": request.experience_level.value,
                "question_count": request.question_count,
                "model": self.model.value,
                "preferred_technique": preferred_technique.value if preferred_technique else None
            }
        )
        
        try:
            # Validate input
            validation = self.security.validate_input(
                request.job_description,
                field_name="job_description"
            )
            if not validation.is_valid:
                error_msg = validation.warnings[0] if validation.warnings else "Validation failed"
                global_error_handler.handle_error(
                    ValidationError(error_msg, field_name="job_description"),
                    error_context
                )
                return GenerationResult(
                    questions=[],
                    recommendations=[],
                    metadata={"error": error_msg},
                    cost_breakdown=CostBreakdown(0, 0, 0, 0, 0),
                    raw_response="",
                    technique_used=PromptTechnique.ZERO_SHOT,
                    model_used=self.model,
                    success=False,
                    error_message=error_msg
                )
        except Exception as e:
            global_error_handler.handle_error(e, error_context)
            return GenerationResult(
                questions=[],
                recommendations=["Unable to validate input. Please try again."],
                metadata={"error": str(e)},
                cost_breakdown=CostBreakdown(0, 0, 0, 0, 0),
                raw_response="",
                technique_used=PromptTechnique.ZERO_SHOT,
                model_used=self.model,
                success=False,
                error_message=str(e)
            )
        
        # Determine techniques to try
        if preferred_technique:
            techniques_to_try = [preferred_technique, PromptTechnique.ZERO_SHOT]
        else:
            # Try structured output first, then others
            techniques_to_try = [
                PromptTechnique.STRUCTURED_OUTPUT,
                PromptTechnique.FEW_SHOT,
                PromptTechnique.CHAIN_OF_THOUGHT,
                PromptTechnique.ZERO_SHOT
            ]
        
        last_error = None
        
        # Try each technique
        for technique in techniques_to_try:
            try:
                logger.info(f"Trying technique: {technique.value}")
                
                # Select template
                template = self._select_prompt_template(request, technique)
                if not template:
                    logger.warning(f"No template found for {technique.value}")
                    continue
                
                # Build prompt
                prompt = self._build_prompt(request, template)
                
                # Make API call
                api_response = await self._make_api_call(
                    prompt,
                    temperature=getattr(request, 'temperature', 0.7),
                    max_tokens=2000
                )
                
                # Use enhanced parser
                parsed_response = response_parser.parse(
                    api_response["content"],
                    request.interview_type,
                    request.experience_level
                )
                
                # Check if parsing was successful
                if not parsed_response.success and not parsed_response.questions:
                    logger.warning(f"Parsing failed for {technique.value}: {parsed_response.error_message}")
                    continue
                
                # Convert to expected format
                parsed_data = {
                    "questions": parsed_response.raw_questions,
                    "recommendations": parsed_response.recommendations,
                    "metadata": parsed_response.metadata
                }
                
                # Calculate costs
                cost_data = cost_calculator.calculate_cost(
                    self.model.value,
                    api_response["usage"]["prompt_tokens"],
                    api_response["usage"]["completion_tokens"]
                )
                cost_breakdown = CostBreakdown(
                    input_cost=cost_data["input_cost"],
                    output_cost=cost_data["output_cost"],
                    total_cost=cost_data["total_cost"],
                    input_tokens=api_response["usage"]["prompt_tokens"],
                    output_tokens=api_response["usage"]["completion_tokens"]
                )
                
                # Track cumulative cost
                cost_calculator.add_usage(
                    self.model.value,
                    api_response["usage"]["prompt_tokens"],
                    api_response["usage"]["completion_tokens"]
                )
                
                # Build result
                return GenerationResult(
                    questions=parsed_data.get("questions", [])[:request.question_count],
                    recommendations=parsed_data.get("recommendations", []),
                    metadata={
                        "technique": technique.value,
                        "template_name": template.name,
                        "tokens_used": api_response["usage"]["total_tokens"],
                        "finish_reason": api_response["finish_reason"],
                        **parsed_data.get("metadata", {})
                    },
                    cost_breakdown=cost_breakdown,
                    raw_response=api_response["content"],
                    technique_used=technique,
                    model_used=self.model,
                    success=True
                )
                
            except (APIError, RateLimitError, ParsingError, AppAPIError, AppRateLimitError) as e:
                logger.error(f"Technique {technique.value} failed: {str(e)}")
                global_error_handler.handle_error(e, error_context)
                last_error = str(e)
                continue
            except Exception as e:
                logger.error(f"Unexpected error with {technique.value}: {str(e)}")
                global_error_handler.handle_error(e, error_context)
                last_error = str(e)
                continue
        
        # All techniques failed
        logger.error("All techniques failed")
        return GenerationResult(
            questions=[],
            recommendations=[
                "Unable to generate questions at this time.",
                "Please try again later or contact support."
            ],
            metadata={"error": "All techniques failed", "last_error": last_error},
            cost_breakdown=CostBreakdown(0, 0, 0, 0, 0),
            raw_response="",
            technique_used=PromptTechnique.ZERO_SHOT,
            model_used=self.model,
            success=False,
            error_message=last_error or "All prompt techniques failed"
        )
    
    def generate_questions_sync(
        self,
        request: GenerationRequest,
        preferred_technique: Optional[PromptTechnique] = None
    ) -> GenerationResult:
        """
        Synchronous wrapper for generate_questions.
        
        Args:
            request: Generation request
            preferred_technique: Preferred prompt technique
            
        Returns:
            Generation result
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.generate_questions(request, preferred_technique)
            )
        finally:
            loop.close()
    
    async def validate_api_key(self) -> bool:
        """
        Validate the API key by making a test call.
        
        Returns:
            True if API key is valid
        """
        try:
            response = await self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            return False
    
    def parse_response(
        self,
        response: str,
        interview_type: Optional[InterviewType] = None,
        experience_level: Optional[ExperienceLevel] = None
    ) -> Dict[str, Any]:
        """
        Parse AI response using enhanced parser.
        
        Args:
            response: Raw AI response
            interview_type: Type of interview
            experience_level: Experience level
            
        Returns:
            Parsed response dictionary
        """
        parsed = response_parser.parse(response, interview_type, experience_level)
        return {
            "questions": parsed.raw_questions,
            "recommendations": parsed.recommendations,
            "strategy_used": parsed.strategy_used.value,
            "success": parsed.success,
            "metadata": parsed.metadata
        }
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """
        Get generation statistics.
        
        Returns:
            Statistics dictionary
        """
        cumulative_stats = cost_calculator.get_cumulative_stats()
        return {
            "model": self.model.value,
            "total_cost": cumulative_stats.get("total_cost", 0.0),
            "session_costs": cumulative_stats.get("session_costs", []),
            "rate_limit_status": rate_limiter.get_rate_limit_status(),
            "rate_limit_stats": rate_limiter.get_statistics()
        }