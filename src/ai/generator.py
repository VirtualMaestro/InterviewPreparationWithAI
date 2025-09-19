"""
AI Question Generator with OpenAI API integration and retry logic.

This module provides the core AI integration for generating interview questions
using various prompt engineering techniques with retry mechanisms and fallback strategies.
"""

import asyncio
import logging
from dataclasses import asdict, dataclass
from typing import Any, final

# from httpx import Response
from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.responses.response import Response
from openai.types.responses.response_output_message import ResponseOutputMessage
from tenacity import (
    after_log,
    before_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.ai.parser import ParsedResponse
from src.utils.error_handler import ErrorContext
from src.utils.rate_limiter import RateLimitStatus

from ..config import Config
from ..models.enums import AIModel, PromptTechnique
from ..models.simple_schemas import SimpleCostBreakdown, SimpleGenerationRequest
from ..utils.cost import cost_calculator
from ..utils.error_handler import APIError as AppAPIError
from ..utils.error_handler import RateLimitError as AppRateLimitError
from ..utils.error_handler import (
    ValidationError,
    global_error_handler,
    handle_async_errors,
)
from ..utils.rate_limiter import rate_limiter
from ..utils.security import SecurityValidator
from .parser import response_parser
from .prompts import PromptTemplate, prompt_library

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
    questions: list[str]
    recommendations: list[str]
    metadata: dict[str, Any]
    cost_breakdown: SimpleCostBreakdown
    raw_response: str
    technique_used: PromptTechnique
    model_used: str
    success: bool
    error_message: str | None = None


@final
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
    
    def __init__(self, api_key: str, config: Config):
        """
        Initialize the generator with API credentials.
        
        Args:
            api_key: OpenAI API key
            model: AI model to use (default: GPT-4o)
        """
        self.api_key = api_key
        self.config = config
        self.client = AsyncOpenAI(api_key=api_key)
        self.security = SecurityValidator()
        
        # Configure retry settings
        self.max_retries = 3
        self.base_wait = 1  # seconds
        self.max_wait = 10  # seconds
        
        logger.info(f"Initialized generator with model: {config.model}")

    #-- Call GPT-5 new API
    #-- Temperature and top_p are not supported in the GPT-5 new API
    async def _call_gpt_5(self, prompt: str, max_output_tokens: int) -> dict[str, Any]: #CoroutineType[Any, Any, Response]:
        response: Response = await self.client.responses.create(
        model=self.config.model,
        input=[
            {"role": "system", "content": "You are an expert interview coach."},
            {"role": "user", "content": prompt}
        ],
        max_output_tokens = max_output_tokens,
        timeout=30)  # 30 second timeout

        target_output: ResponseOutputMessage | None

        for item in response.output:
            if  isinstance(item, ResponseOutputMessage):  
                target_output = item
                break
        
        if target_output is None:
            raise ValueError("No valid object from the OpenAI API call")

        result = {
            "content": target_output.content[0].text,
            "usage": {
                "prompt_tokens": response.usage.input_tokens if response.usage else 0,
                "completion_tokens": response.usage.output_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            },
            "model": self.config.model,
            "finish_reason": target_output.status 
        }

        return result
    
    #--- Call GPT-4 old API
    async def _call_gpt_4(self, prompt: str, temperature: float, top_p: float, max_tokens: int) -> dict[str, Any]: #CoroutineType[Any, Any, Response]:
        response: ChatCompletion = await self.client.chat.completions.create(
        model=self.config.model,
        messages=[
            {"role": "system", "content": "You are an expert interview coach."},
            {"role": "user", "content": prompt}
        ],
        temperature = temperature,
        top_p = top_p,
        max_tokens = max_tokens,
        timeout = 30)  # 30 second timeout
        
        # Extract response data with proper error checking
        if not response.choices or len(response.choices) == 0:
            raise ValueError("API response contains no choices")

        choice = response.choices[0]
        if not hasattr(choice, 'message') or not hasattr(choice.message, 'content'):
            raise ValueError("API response choice missing message content")

        content = choice.message.content
        if content is None:
            raise ValueError("API response content is None")

        result = {
            "content": content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            },
            "model": response.model if hasattr(response, 'model') else self.config.model,
            "finish_reason": choice.finish_reason if hasattr(choice, 'finish_reason') else "unknown"
        }

        return result
    
    
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
        temperature: float,
        top_p: float,
        max_tokens: int
    ) -> dict[str, Any]:
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
            status: RateLimitStatus = rate_limiter.get_rate_limit_status()
            context: ErrorContext = ErrorContext(
                operation="api_call",
                additional_info={
                    "rate_limit_status" : asdict(status),
                    "model": self.config.model
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
            result: dict[str, Any]
            
            if self.config.model == AIModel.GPT_5.value:
                result = await self._call_gpt_5(prompt, max_tokens)
            else:
                result = await self._call_gpt_4(prompt, temperature, top_p, max_tokens)
            
            return result
            
        except asyncio.TimeoutError:
            context = ErrorContext(
                operation="api_call",
                additional_info={"timeout_duration": 30, "model": self.config.model}
            )
            logger.error("API call timed out")
            raise AppAPIError("API call timed out after 30 seconds", context=context)
        except Exception as e:
            context = ErrorContext(
                operation="api_call",
                additional_info={"model": self.config.model, "error_type": type(e).__name__}
            )
            logger.error(f"API call failed: {str(e)}")
            raise AppAPIError(f"API call failed: {str(e)}", context=context, cause=e)
    
    #****************
    def _select_prompt_template(
        self,
        request: SimpleGenerationRequest,
        technique: PromptTechnique
    ) -> PromptTemplate:

        return  prompt_library.get_template(
            technique,
            request.interview_type,
            request.experience_level
        )

    def _build_prompt(
        self,
        request: SimpleGenerationRequest,
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
    
    # def _parse_json_response(self, response: str) -> dict[str, Any]:
    #     """
    #     Parse JSON response from API.
        
    #     Args:
    #         response: Raw response string
            
    #     Returns:
    #         Parsed JSON dictionary
            
    #     Raises:
    #         ParsingError: If parsing fails
    #     """
    #     try:
    #         # Try to extract JSON from response
    #         # Handle cases where response has markdown code blocks
    #         if "```json" in response:
    #             start = response.find("```json") + 7
    #             end = response.find("```", start)
    #             json_str = response[start:end].strip()
    #         elif "```" in response:
    #             start = response.find("```") + 3
    #             end = response.find("```", start)
    #             json_str = response[start:end].strip()
    #         else:
    #             json_str = response.strip()
            
    #         # Parse JSON
    #         data = json.loads(json_str)
    #         return data
            
    #     except json.JSONDecodeError as e:
    #         logger.error(f"JSON parsing failed: {str(e)}")
    #         raise ParsingError(f"Failed to parse JSON response: {str(e)}")
    
    # def _parse_text_response(self, response: str) -> dict[str, Any]:
    #     """
    #     Parse text response to extract questions and recommendations.
        
    #     Args:
    #         response: Raw response string
            
    #     Returns:
    #         Parsed data dictionary
    #     """
    #     lines = response.strip().split('\n')
    #     questions = []
    #     recommendations = []
    #     current_section = None
        
    #     for line in lines:
    #         line = line.strip()
    #         if not line:
    #             continue
                
    #         # Detect sections
    #         if any(word in line.lower() for word in ['question', 'interview']):
    #             current_section = 'questions'
    #             continue
    #         elif any(word in line.lower() for word in ['recommendation', 'tip', 'advice']):
    #             current_section = 'recommendations'
    #             continue
            
    #         # Parse numbered items
    #         if line[0].isdigit() or line.startswith('-') or line.startswith('•'):
    #             # Clean up the line
    #             if line[0].isdigit():
    #                 # Remove number and punctuation
    #                 parts = line.split('.', 1)
    #                 if len(parts) > 1:
    #                     line = parts[1].strip()
    #                 else:
    #                     parts = line.split(')', 1)
    #                     if len(parts) > 1:
    #                         line = parts[1].strip()
    #             else:
    #                 # Remove bullet point
    #                 line = line[1:].strip()
                
    #             # Add to appropriate section
    #             if current_section == 'recommendations' or (
    #                 current_section is None and 
    #                 any(word in line.lower() for word in ['prepare', 'practice', 'review'])
    #             ):
    #                 recommendations.append(line)
    #             else:
    #                 questions.append(line)
        
    #     # Ensure we have at least some questions
    #     if not questions and recommendations:
    #         # Some recommendations might actually be questions
    #         questions = recommendations[:5]
    #         recommendations = recommendations[5:]
        
    #     return {
    #         "questions": questions,
    #         "recommendations": recommendations,
    #         "metadata": {
    #             "parsed_from": "text",
    #             "total_lines": len(lines)
    #         }
    #     }
    
    @handle_async_errors(
        error_handler=global_error_handler,
        attempt_recovery=False,
        reraise=False
    )
    async def generate_questions(
        self,
        request: SimpleGenerationRequest,
        preferred_technique: PromptTechnique
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
                "model": self.config.model,
                "preferred_technique": preferred_technique.value if preferred_technique else None
            }
        )
        
        try:
            # Validate input
            validation = self.security.validate_input(request.job_description, "job_description")

            if not validation.is_valid:
                error_msg = validation.warnings[0] if validation.warnings else "Validation failed"
                
                global_error_handler.handle_error(
                    ValidationError(error_msg, field_name="job_description"),
                    error_context)

                return GenerationResult(
                    questions=[],
                    recommendations=[],
                    metadata={"error": error_msg},
                    cost_breakdown=SimpleCostBreakdown(0, 0, 0, 0, 0),
                    raw_response="",
                    technique_used=PromptTechnique.ZERO_SHOT,
                    model_used=self.config.model,
                    success=False,
                    error_message=error_msg)

        except Exception as e:
            global_error_handler.handle_error(e, error_context)
            return GenerationResult(
                questions=[],
                recommendations=["Unable to validate input. Please try again."],
                metadata={"error": str(e)},
                cost_breakdown=SimpleCostBreakdown(0, 0, 0, 0, 0),
                raw_response="",
                technique_used=PromptTechnique.ZERO_SHOT,
                model_used=self.config.model,
                success=False,
                error_message=str(e)
            )
        
        last_error = None
        
        # Try each technique
        # for technique in techniques_to_try:
        try:
            logger.info(f"Trying technique: {preferred_technique.value}")
            
            # Select template
            template = self._select_prompt_template(request, preferred_technique)
            
            # Build prompt
            prompt = self._build_prompt(request, template)
            
            # Make API call
            api_response: dict[str, Any] = await self._make_api_call(
                prompt,
                temperature = self.config.temperature,
                top_p = self.config.top_p,
                max_tokens = self.config.max_tokens
            )

            # Validate API response structure
            if not isinstance(api_response, dict) or "content" not in api_response:
                raise ValueError(f"Invalid API response structure: {type(api_response)}")

            # Use enhanced parser
            parsed_response: ParsedResponse = response_parser.parse(api_response["content"], request.interview_type, request.experience_level)
            
            # Convert to expected format
            parsed_data: dict[str, list[str] | dict[str, Any]] = {
                "questions": parsed_response.raw_questions,
                "recommendations": parsed_response.recommendations,
                "metadata": parsed_response.metadata
            }
            
            # Calculate costs
            usage = api_response.get("usage", {"prompt_tokens": 0, "completion_tokens": 0})
            cost_data = cost_calculator.calculate_cost(
                self.config.model,
                usage.get("prompt_tokens", 0),
                usage.get("completion_tokens", 0)
            )

            cost_breakdown = SimpleCostBreakdown(
                input_cost = cost_data["input_cost"],
                output_cost = cost_data["output_cost"],
                total_cost = cost_data["total_cost"],
                input_tokens = api_response["usage"]["prompt_tokens"],
                output_tokens = api_response["usage"]["completion_tokens"]
            )
            
            # Track cumulative cost
            cost_calculator.add_usage(
                self.config.model,
                api_response["usage"]["prompt_tokens"],
                api_response["usage"]["completion_tokens"]
            )
            
            # Build result
            questions_list = parsed_data.get("questions", [])
            if isinstance(questions_list, list):
                limited_questions = questions_list[:request.question_count]
            else:
                limited_questions = []

            recommendations_list = parsed_data.get("recommendations", [])
            if isinstance(recommendations_list, list):
                safe_recommendations = recommendations_list
            else:
                safe_recommendations = []

            # Handle metadata safely
            parsed_metadata = parsed_data.get("metadata", {})
            if isinstance(parsed_metadata, dict):
                safe_metadata = parsed_metadata
            else:
                safe_metadata = {}

            return GenerationResult(
                questions=limited_questions,
                recommendations=safe_recommendations,
                metadata={
                    "technique": preferred_technique.value,
                    "template_name": template.name,
                    "tokens_used": usage.get("total_tokens", 0),
                    "finish_reason": api_response.get("finish_reason", "unknown"),
                    **safe_metadata
                },

                cost_breakdown=cost_breakdown,
                raw_response=api_response["content"],
                technique_used=preferred_technique,
                model_used=self.config.model,
                success=True
            )
            
        except (APIError, RateLimitError, ParsingError, AppAPIError, AppRateLimitError) as e:
            logger.error(f"Technique {preferred_technique.value} failed: {str(e)}")
            global_error_handler.handle_error(e, error_context)
            last_error = str(e)
        except Exception as e:
            logger.error(f"Unexpected error with {preferred_technique.value}: {str(e)}")
            global_error_handler.handle_error(e, error_context)
            last_error = str(e)
        
        # All techniques failed
        logger.error("All techniques failed")
        return GenerationResult(
            questions=[],
            recommendations=[
                "Unable to generate questions at this time.",
                "Please try again later or contact support."
            ],
            metadata={"error": "All techniques failed", "last_error": last_error},
            cost_breakdown=SimpleCostBreakdown(0, 0, 0, 0, 0),
            raw_response="",
            technique_used=PromptTechnique.ZERO_SHOT,
            model_used=self.config.model,
            success=False,
            error_message=last_error or "All prompt techniques failed")