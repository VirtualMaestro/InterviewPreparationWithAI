"""
Response Parser with Advanced Fallback Systems.

This module provides robust parsing capabilities for AI-generated responses
with multiple fallback strategies and default recommendation generation.
"""

import json
import re
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum

from models.enums import (
    InterviewType,
    ExperienceLevel,
    DifficultyLevel,
    QuestionCategory
)

logger = logging.getLogger(__name__)


class ParseStrategy(Enum):
    """Parsing strategies for different response formats."""
    JSON_STRUCTURED = "json_structured"
    JSON_SIMPLE = "json_simple"
    TEXT_NUMBERED = "text_numbered"
    TEXT_BULLETED = "text_bulleted"
    TEXT_PARAGRAPH = "text_paragraph"
    FALLBACK_BASIC = "fallback_basic"
    DEFAULT = "default"


@dataclass
class ParsedQuestion:
    """Structured representation of a parsed question."""
    question: str
    difficulty: Optional[DifficultyLevel] = None
    category: Optional[QuestionCategory] = None
    time_estimate: Optional[int] = None
    hints: List[str] = field(default_factory=list)
    follow_ups: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedResponse:
    """Complete parsed response with questions and recommendations."""
    questions: List[ParsedQuestion]
    recommendations: List[str]
    raw_questions: List[str]  # Simple string list for compatibility
    strategy_used: ParseStrategy
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResponseParser:
    """
    Advanced response parser with multiple fallback strategies.
    
    Features:
    - Multi-strategy parsing with automatic fallback
    - Robust error handling and recovery
    - Default recommendation generation
    - Question quality validation
    - Metadata extraction and enrichment
    """
    
    def __init__(self):
        """Initialize the response parser."""
        self.min_question_length = 10
        self.max_question_length = 500
        self.default_time_estimate = 10  # minutes
        
        # Patterns for text parsing
        self.question_patterns = [
            r'^\d+[\.\)]\s*(.+)$',  # 1. or 1) format
            r'^[•\-\*]\s*(.+)$',     # Bullet points
            r'^Q\d*[:.]?\s*(.+)$',   # Q1: or Q: format
            r'^Question\s*\d*[:.]?\s*(.+)$',  # Question 1: format
            r'^\*\*Question\s*\d*[:.]\*\*\s*(.+)$',  # **Question 1:** format
            r'^\*\*Question:\*\*\s*(.+)$',  # **Question:** format
            r'^\*\*Question\s*\d+:\s*([^*]+)\*\*',  # **Question 1: Title**
        ]
        
        # Keywords for section detection
        self.question_keywords = [
            'question', 'interview', 'ask', 'queries', 'topics'
        ]
        self.recommendation_keywords = [
            'recommend', 'suggest', 'tip', 'advice', 'prepare',
            'practice', 'review', 'study', 'focus', 'consider'
        ]
    
    def parse(
        self,
        response: str,
        interview_type: Optional[InterviewType] = None,
        experience_level: Optional[ExperienceLevel] = None
    ) -> ParsedResponse:
        """
        Parse AI response with automatic strategy selection and fallback.
        
        Args:
            response: Raw AI response text
            interview_type: Type of interview for context
            experience_level: Experience level for context
            
        Returns:
            ParsedResponse with questions and recommendations
        """
        if not response or not response.strip():
            return self._generate_default_response(interview_type, experience_level)
        
        # Try parsing strategies in order of preference
        strategies = [
            (ParseStrategy.JSON_STRUCTURED, self._parse_json_structured),
            (ParseStrategy.JSON_SIMPLE, self._parse_json_simple),
            (ParseStrategy.TEXT_NUMBERED, self._parse_markdown_questions),  # Try markdown format first
            (ParseStrategy.TEXT_NUMBERED, self._parse_text_numbered),
            (ParseStrategy.TEXT_BULLETED, self._parse_text_bulleted),
            (ParseStrategy.TEXT_PARAGRAPH, self._parse_text_paragraph),
            (ParseStrategy.FALLBACK_BASIC, self._parse_fallback_basic)
        ]
        
        last_error = None
        
        for strategy, parser_func in strategies:
            try:
                logger.debug(f"Trying parsing strategy: {strategy.value}")
                result = parser_func(response)
                
                # Validate result
                if self._validate_parsed_result(result):
                    result.strategy_used = strategy
                    result.success = True
                    
                    # Enrich with context if available
                    if interview_type or experience_level:
                        result = self._enrich_with_context(
                            result, interview_type, experience_level
                        )
                    
                    logger.info(f"Successfully parsed with strategy: {strategy.value}")
                    return result
                    
            except Exception as e:
                logger.debug(f"Strategy {strategy.value} failed: {str(e)}")
                last_error = str(e)
                continue
        
        # All strategies failed, generate default
        logger.warning("All parsing strategies failed, generating default response")
        return self._generate_default_response(
            interview_type, experience_level, last_error
        )
    
    def _parse_json_structured(self, response: str) -> ParsedResponse:
        """
        Parse structured JSON response with full metadata.
        
        Expected format:
        {
            "questions": [
                {
                    "question": "...",
                    "difficulty": "...",
                    "category": "...",
                    "time_estimate": ...,
                    "hints": [...],
                    "follow_ups": [...]
                }
            ],
            "recommendations": [...]
        }
        """
        json_str = self._extract_json(response)
        data = json.loads(json_str)
        
        questions = []
        raw_questions = []
        
        for q_data in data.get("questions", []):
            if isinstance(q_data, dict):
                question_text = q_data.get("question", "")
                if question_text:
                    # Parse difficulty
                    difficulty = None
                    if "difficulty" in q_data:
                        try:
                            difficulty = DifficultyLevel(q_data["difficulty"].lower())
                        except (ValueError, AttributeError):
                            pass
                    
                    # Parse category
                    category = None
                    if "category" in q_data:
                        try:
                            category = QuestionCategory(q_data["category"].lower())
                        except (ValueError, AttributeError):
                            pass
                    
                    parsed_q = ParsedQuestion(
                        question=question_text,
                        difficulty=difficulty,
                        category=category,
                        time_estimate=q_data.get("time_estimate", self.default_time_estimate),
                        hints=q_data.get("hints", []),
                        follow_ups=q_data.get("follow_ups", []),
                        metadata=q_data.get("metadata", {})
                    )
                    questions.append(parsed_q)
                    raw_questions.append(question_text)
            elif isinstance(q_data, str):
                # Simple string question
                questions.append(ParsedQuestion(question=q_data))
                raw_questions.append(q_data)
        
        recommendations = data.get("recommendations", [])
        if not isinstance(recommendations, list):
            recommendations = []
        
        return ParsedResponse(
            questions=questions,
            recommendations=recommendations,
            raw_questions=raw_questions,
            strategy_used=ParseStrategy.JSON_STRUCTURED,
            success=True,
            metadata=data.get("metadata", {})
        )
    
    def _parse_json_simple(self, response: str) -> ParsedResponse:
        """
        Parse simple JSON response with just questions and recommendations.
        
        Expected format:
        {
            "questions": ["...", "..."],
            "recommendations": ["...", "..."]
        }
        """
        json_str = self._extract_json(response)
        data = json.loads(json_str)
        
        questions = []
        raw_questions = data.get("questions", [])
        
        for q_text in raw_questions:
            if isinstance(q_text, str) and q_text.strip():
                questions.append(ParsedQuestion(question=q_text.strip()))
        
        recommendations = data.get("recommendations", [])
        if not isinstance(recommendations, list):
            recommendations = []
        
        return ParsedResponse(
            questions=questions,
            recommendations=recommendations,
            raw_questions=raw_questions,
            strategy_used=ParseStrategy.JSON_SIMPLE,
            success=True,
            metadata={}
        )
    
    def _parse_text_numbered(self, response: str) -> ParsedResponse:
        """Parse numbered list format (1. 2. 3. or 1) 2) 3))."""
        lines = response.strip().split('\n')
        questions = []
        raw_questions = []
        recommendations = []
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            if self._is_section_header(line):
                if any(kw in line.lower() for kw in self.question_keywords):
                    current_section = 'questions'
                elif any(kw in line.lower() for kw in self.recommendation_keywords):
                    current_section = 'recommendations'
                continue
            
            # Try to match numbered format
            numbered_match = re.match(r'^\d+[\.\)]\s*(.+)$', line)
            if numbered_match:
                content = numbered_match.group(1).strip()
                if current_section == 'recommendations' or self._is_recommendation(content):
                    recommendations.append(content)
                else:
                    questions.append(ParsedQuestion(question=content))
                    raw_questions.append(content)
        
        # If no questions found, try to extract from full text
        if not questions:
            questions, raw_questions = self._extract_questions_from_text(response)
        
        return ParsedResponse(
            questions=questions,
            recommendations=recommendations,
            raw_questions=raw_questions,
            strategy_used=ParseStrategy.TEXT_NUMBERED,
            success=True,
            metadata={}
        )
    
    def _parse_text_bulleted(self, response: str) -> ParsedResponse:
        """Parse bullet point format (-, *, •)."""
        lines = response.strip().split('\n')
        questions = []
        raw_questions = []
        recommendations = []
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            if self._is_section_header(line):
                if any(kw in line.lower() for kw in self.question_keywords):
                    current_section = 'questions'
                elif any(kw in line.lower() for kw in self.recommendation_keywords):
                    current_section = 'recommendations'
                continue
            
            # Try to match bullet format
            bullet_match = re.match(r'^[•\-\*]\s*(.+)$', line)
            if bullet_match:
                content = bullet_match.group(1).strip()
                if current_section == 'recommendations' or self._is_recommendation(content):
                    recommendations.append(content)
                else:
                    questions.append(ParsedQuestion(question=content))
                    raw_questions.append(content)
        
        return ParsedResponse(
            questions=questions,
            recommendations=recommendations,
            raw_questions=raw_questions,
            strategy_used=ParseStrategy.TEXT_BULLETED,
            success=True,
            metadata={}
        )
    
    def _parse_text_paragraph(self, response: str) -> ParsedResponse:
        """Parse paragraph format using sentence detection."""
        # Split into sentences
        sentences = re.split(r'[.!?]+', response)
        
        questions = []
        raw_questions = []
        recommendations = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if it looks like a question
            if self._looks_like_question(sentence):
                # Add question mark if missing
                if not sentence.endswith('?'):
                    sentence += '?'
                questions.append(ParsedQuestion(question=sentence))
                raw_questions.append(sentence)
            elif self._is_recommendation(sentence):
                recommendations.append(sentence)
        
        # If no questions found, extract key sentences
        if not questions:
            questions, raw_questions = self._extract_questions_from_text(response)
        
        return ParsedResponse(
            questions=questions,
            recommendations=recommendations,
            raw_questions=raw_questions,
            strategy_used=ParseStrategy.TEXT_PARAGRAPH,
            success=True,
            metadata={}
        )
    
    def _parse_fallback_basic(self, response: str) -> ParsedResponse:
        """Basic fallback parser that extracts any reasonable content."""
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        
        questions = []
        raw_questions = []
        recommendations = []
        
        for line in lines:
            # Skip very short lines
            if len(line) < self.min_question_length:
                continue
            
            # Skip lines that are clearly headers or metadata
            if line.startswith('#') or line.startswith('===') or line.startswith('---'):
                continue
            
            # Try to categorize the line
            if self._looks_like_question(line) or '?' in line:
                if not line.endswith('?'):
                    line += '?'
                questions.append(ParsedQuestion(question=line))
                raw_questions.append(line)
            elif self._is_recommendation(line):
                recommendations.append(line)
            elif len(questions) < 5:  # Take first 5 substantial lines as questions
                questions.append(ParsedQuestion(question=line))
                raw_questions.append(line)
        
        return ParsedResponse(
            questions=questions,
            recommendations=recommendations,
            raw_questions=raw_questions,
            strategy_used=ParseStrategy.FALLBACK_BASIC,
            success=True,
            metadata={}
        )
    
    def _extract_json(self, response: str) -> str:
        """Extract JSON from response, handling markdown code blocks."""
        # Try to find JSON in code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                json_candidate = response[start:end].strip()
                # Check if it looks like JSON
                if json_candidate.startswith('{') or json_candidate.startswith('['):
                    return json_candidate
        
        # Try to extract JSON directly
        # Look for outermost braces or brackets
        brace_start = response.find('{')
        bracket_start = response.find('[')
        
        if brace_start >= 0 and (bracket_start < 0 or brace_start < bracket_start):
            # Find matching closing brace
            brace_count = 0
            for i in range(brace_start, len(response)):
                if response[i] == '{':
                    brace_count += 1
                elif response[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return response[brace_start:i+1]
        elif bracket_start >= 0:
            # Find matching closing bracket
            bracket_count = 0
            for i in range(bracket_start, len(response)):
                if response[i] == '[':
                    bracket_count += 1
                elif response[i] == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        return response[bracket_start:i+1]
        
        # Return as-is and hope for the best
        return response.strip()
    
    def _is_section_header(self, line: str) -> bool:
        """Check if a line appears to be a section header."""
        line = line.lower()
        return (
            line.endswith(':') or
            line.startswith('#') or
            len(line) < 30 and (
                any(kw in line for kw in self.question_keywords) or
                any(kw in line for kw in self.recommendation_keywords)
            )
        )
    
    def _is_recommendation(self, text: str) -> bool:
        """Check if text appears to be a recommendation."""
        text_lower = text.lower()
        return any(kw in text_lower for kw in self.recommendation_keywords)
    
    def _looks_like_question(self, text: str) -> bool:
        """Check if text appears to be a question."""
        text_lower = text.lower()
        question_starters = [
            'what', 'how', 'why', 'when', 'where', 'who', 'which',
            'can you', 'could you', 'would you', 'have you', 'do you',
            'is there', 'are there', 'describe', 'explain', 'tell me'
        ]
        return any(text_lower.startswith(starter) for starter in question_starters)
    
    def _extract_questions_from_text(self, text: str) -> Tuple[List[ParsedQuestion], List[str]]:
        """Extract potential questions from unstructured text."""
        questions = []
        raw_questions = []
        
        # Try various patterns
        for pattern in self.question_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                if isinstance(match, str) and len(match) >= self.min_question_length:
                    questions.append(ParsedQuestion(question=match))
                    raw_questions.append(match)
        
        # If still no questions, take sentences that look like questions
        if not questions:
            sentences = re.split(r'[.!?]+', text)
            for sentence in sentences:
                sentence = sentence.strip()
                if self._looks_like_question(sentence) and len(sentence) >= self.min_question_length:
                    if not sentence.endswith('?'):
                        sentence += '?'
                    questions.append(ParsedQuestion(question=sentence))
                    raw_questions.append(sentence)
        
        return questions, raw_questions
    
    def _validate_parsed_result(self, result: ParsedResponse) -> bool:
        """Validate that parsed result contains meaningful content."""
        if not result.questions:
            return False
        
        # Check that questions are valid
        for question in result.questions:
            if not question.question or len(question.question) < self.min_question_length:
                return False
            if len(question.question) > self.max_question_length:
                return False
        
        return True
    
    def _enrich_with_context(
        self,
        result: ParsedResponse,
        interview_type: Optional[InterviewType],
        experience_level: Optional[ExperienceLevel]
    ) -> ParsedResponse:
        """Enrich parsed result with contextual information."""
        # Add context to metadata
        if interview_type:
            result.metadata["interview_type"] = interview_type.value
        if experience_level:
            result.metadata["experience_level"] = experience_level.value
        
        # Try to infer difficulty if not set
        for question in result.questions:
            if not question.difficulty and experience_level:
                if experience_level == ExperienceLevel.JUNIOR:
                    question.difficulty = DifficultyLevel.EASY
                elif experience_level == ExperienceLevel.MID:
                    question.difficulty = DifficultyLevel.MEDIUM
                elif experience_level in [ExperienceLevel.SENIOR, ExperienceLevel.LEAD]:
                    question.difficulty = DifficultyLevel.HARD
        
        # Try to infer category if not set
        for question in result.questions:
            if not question.category and interview_type:
                if interview_type == InterviewType.TECHNICAL:
                    # Try to categorize based on keywords
                    q_lower = question.question.lower()
                    if any(kw in q_lower for kw in ['algorithm', 'complexity', 'sort', 'search']):
                        question.category = QuestionCategory.ALGORITHMS
                    elif any(kw in q_lower for kw in ['design', 'architecture', 'scale', 'system']):
                        question.category = QuestionCategory.SYSTEM_DESIGN
                    elif any(kw in q_lower for kw in ['code', 'implement', 'write', 'function']):
                        question.category = QuestionCategory.CODING
                    else:
                        question.category = QuestionCategory.CONCEPTUAL
                elif interview_type == InterviewType.BEHAVIORAL:
                    question.category = QuestionCategory.BEHAVIORAL
                elif interview_type == InterviewType.CASE_STUDY:
                    question.category = QuestionCategory.CASE_STUDY
        
        return result
    
    def _generate_default_response(
        self,
        interview_type: Optional[InterviewType] = None,
        experience_level: Optional[ExperienceLevel] = None,
        error: Optional[str] = None
    ) -> ParsedResponse:
        """Generate default response when parsing fails."""
        # Default questions based on interview type
        default_questions = {
            InterviewType.TECHNICAL: [
                "Can you describe your experience with the technologies mentioned in the job description?",
                "How do you approach debugging complex issues in production?",
                "What's your experience with system design and architecture?",
                "Can you walk me through a challenging technical problem you solved?",
                "How do you stay updated with new technologies and best practices?"
            ],
            InterviewType.BEHAVIORAL: [
                "Tell me about yourself and your background",
                "Why are you interested in this position?",
                "Describe a time when you had to work with a difficult team member",
                "How do you handle tight deadlines and pressure?",
                "What are your greatest strengths and areas for improvement?"
            ],
            InterviewType.CASE_STUDY: [
                "How would you approach analyzing this business problem?",
                "What key metrics would you use to measure success?",
                "What are the main risks and how would you mitigate them?",
                "How would you prioritize different solutions?",
                "What would be your implementation timeline?"
            ],
            InterviewType.REVERSE: [
                "What are the biggest challenges facing the team right now?",
                "How would you describe the team culture?",
                "What are the opportunities for growth and learning?",
                "What does success look like in this role?",
                "What's the typical career progression for this position?"
            ]
        }
        
        # Default recommendations
        default_recommendations = [
            "Review the job description and align your responses with key requirements",
            "Prepare specific examples from your past experience",
            "Research the company's recent news and initiatives",
            "Practice your responses out loud to improve delivery",
            "Prepare thoughtful questions to ask the interviewer"
        ]
        
        # Select questions based on interview type
        if interview_type and interview_type in default_questions:
            questions_text = default_questions[interview_type]
        else:
            # Mix of technical and behavioral
            questions_text = default_questions[InterviewType.TECHNICAL][:3] + \
                           default_questions[InterviewType.BEHAVIORAL][:2]
        
        # Create ParsedQuestion objects
        questions = []
        for q_text in questions_text:
            difficulty = DifficultyLevel.MEDIUM
            if experience_level == ExperienceLevel.JUNIOR:
                difficulty = DifficultyLevel.EASY
            elif experience_level in [ExperienceLevel.SENIOR, ExperienceLevel.LEAD]:
                difficulty = DifficultyLevel.HARD
            
            questions.append(ParsedQuestion(
                question=q_text,
                difficulty=difficulty,
                time_estimate=self.default_time_estimate
            ))
        
        return ParsedResponse(
            questions=questions,
            recommendations=default_recommendations,
            raw_questions=questions_text,
            strategy_used=ParseStrategy.DEFAULT,
            success=False,
            error_message=error or "Unable to parse AI response, using defaults",
            metadata={
                "is_default": True,
                "reason": "parsing_failed"
            }
        )
    
    def parse_simple(self, response: str) -> Dict[str, List[str]]:
        """
        Simple parsing interface for backward compatibility.
        
        Args:
            response: Raw AI response
            
        Returns:
            Dictionary with 'questions' and 'recommendations' lists
        """
        parsed = self.parse(response)
        return {
            "questions": parsed.raw_questions,
            "recommendations": parsed.recommendations
        }

    def _parse_markdown_questions(self, response: str) -> ParsedResponse:
        """
        Parse markdown-formatted questions with **Question X:** or **Question:** patterns.
        This handles the specific format returned by OpenAI API.
        """
        questions = []
        raw_questions = []
        recommendations = []

        # Split by lines and process
        lines = response.strip().split('\n')
        current_question = []
        in_question = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for question headers with various patterns
            question_header_patterns = [
                r'^\d+\.\s*\*\*Question\s*\d*:?\s*([^*]+)\*\*',  # 1. **Question 1: Title**
                r'^\*\*Question\s*\d*:?\s*([^*]+)\*\*',         # **Question 1: Title**
                r'^\*\*Question:\*\*\s*"([^"]+)"',               # **Question:** "Text"
                r'^\d+\.\s*\*\*([^*]+)\*\*',                     # 1. **Title**
            ]

            matched = False
            for pattern in question_header_patterns:
                match = re.search(pattern, line)
                if match:
                    # If we were building a previous question, save it
                    if current_question:
                        question_text = ' '.join(current_question).strip()
                        if question_text and len(question_text) >= self.min_question_length:
                            questions.append(ParsedQuestion(question=question_text))
                            raw_questions.append(question_text)

                    # Start new question
                    current_question = [match.group(1).strip()]
                    in_question = True
                    matched = True
                    break

            if not matched and in_question:
                # Continue building current question
                # Skip lines that look like metadata
                if not (line.startswith('- **') or line.startswith('*Tests:') or
                       line.startswith('*Focus:') or line.startswith('- *')):
                    # Clean up the line
                    clean_line = re.sub(r'^\s*-\s*', '', line)  # Remove leading dashes
                    clean_line = re.sub(r'^\s*\*\*[^*]*\*\*:?\s*', '', clean_line)  # Remove bold headers
                    if clean_line and not clean_line.startswith('*'):
                        current_question.append(clean_line)

        # Don't forget the last question
        if current_question:
            question_text = ' '.join(current_question).strip()
            if question_text and len(question_text) >= self.min_question_length:
                questions.append(ParsedQuestion(question=question_text))
                raw_questions.append(question_text)

        # If we didn't get enough questions, fall back to numbered parsing
        if len(questions) < 2:
            # Try simple numbered pattern as fallback
            numbered_questions = re.findall(r'^\d+\.\s*(.+)$', response, re.MULTILINE)
            for q in numbered_questions:
                if len(q) >= self.min_question_length:
                    questions.append(ParsedQuestion(question=q))
                    raw_questions.append(q)

        return ParsedResponse(
            questions=questions,
            recommendations=recommendations,
            raw_questions=raw_questions,
            strategy_used=ParseStrategy.TEXT_NUMBERED,
            success=len(questions) > 0,
            metadata={'parser': 'markdown_questions'}
        )


# Global parser instance
response_parser = ResponseParser()