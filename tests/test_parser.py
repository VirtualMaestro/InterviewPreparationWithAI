"""
Comprehensive tests for Response Parser with all parsing scenarios.

Tests cover:
- JSON structured and simple parsing
- Text parsing (numbered, bulleted, paragraph)
- Fallback mechanisms
- Default response generation
- Edge cases and error handling
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
import json
import sys
from pathlib import Path

# Add parent directory to path

from src.ai.parser import (
    ResponseParser,
    ParsedResponse,
    ParsedQuestion,
    ParseStrategy
)
from src.models.enums import (
    InterviewType,
    ExperienceLevel,
    DifficultyLevel,
    QuestionCategory
)


class TestResponseParser(unittest.TestCase):
    """Tests for ResponseParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = ResponseParser()
    
    def test_parse_json_structured_complete(self):
        """Test parsing fully structured JSON response."""
        response = json.dumps({
            "questions": [
                {
                    "question": "How do you handle state management in React?",
                    "difficulty": "medium",
                    "category": "conceptual",
                    "time_estimate": 15,
                    "hints": ["Consider Redux", "Think about Context API"],
                    "follow_ups": ["What about performance?"]
                },
                {
                    "question": "Implement a binary search algorithm",
                    "difficulty": "easy",
                    "category": "algorithms",
                    "time_estimate": 20
                }
            ],
            "recommendations": [
                "Review React documentation",
                "Practice algorithm problems"
            ],
            "metadata": {
                "total_questions": 2,
                "difficulty_distribution": {"easy": 1, "medium": 1}
            }
        })
        
        result = self.parser.parse(response, InterviewType.CASE_STUDY, ExperienceLevel.JUNIOR)
        
        self.assertTrue(result.success)
        self.assertEqual(result.strategy_used, ParseStrategy.JSON_STRUCTURED)
        self.assertEqual(len(result.questions), 2)
        self.assertEqual(len(result.recommendations), 2)
        
        # Check first question details
        q1 = result.questions[0]
        self.assertIn("state management", q1.question)
        self.assertEqual(q1.difficulty, DifficultyLevel.MEDIUM)
        self.assertEqual(q1.category, QuestionCategory.CONCEPTUAL)
        self.assertEqual(q1.time_estimate, 15)
        self.assertEqual(len(q1.hints), 2)
        self.assertEqual(len(q1.follow_ups), 1)
    
    def test_parse_json_structured_in_markdown(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        response = """Here are the questions:
        
```json
{
    "questions": [
        {"question": "What is Python GIL?", "difficulty": "hard"},
        {"question": "Explain decorators", "difficulty": "medium"}
    ],
    "recommendations": ["Study Python internals"]
}
```
        
Hope this helps!"""
        
        result = self.parser.parse(response)
        
        self.assertTrue(result.success)
        self.assertEqual(result.strategy_used, ParseStrategy.JSON_STRUCTURED)
        self.assertEqual(len(result.questions), 2)
        self.assertEqual(result.questions[0].difficulty, DifficultyLevel.HARD)
    
    def test_parse_json_simple(self):
        """Test parsing simple JSON with string arrays."""
        response = json.dumps({
            "questions": [
                "What is your experience with microservices?",
                "How do you ensure code quality?",
                "Describe your CI/CD process"
            ],
            "recommendations": [
                "Prepare specific examples",
                "Review best practices"
            ]
        })
        
        result = self.parser.parse(response)
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.questions), 3)
        self.assertEqual(len(result.raw_questions), 3)
        self.assertIn("microservices", result.raw_questions[0])
    
    def test_parse_text_numbered(self):
        """Test parsing numbered list format."""
        response = """Interview Questions:
        
1. How do you handle database migrations in production?
2. What's your approach to API versioning?
3. Describe your experience with containerization

Recommendations:
1. Review database best practices
2. Prepare examples from past projects"""
        
        result = self.parser.parse(response)
        
        self.assertTrue(result.success)
        self.assertEqual(result.strategy_used, ParseStrategy.TEXT_NUMBERED)
        self.assertEqual(len(result.questions), 3)
        self.assertEqual(len(result.recommendations), 2)
        self.assertIn("database migrations", result.raw_questions[0])
    
    def test_parse_text_numbered_mixed_formats(self):
        """Test parsing with mixed numbering styles."""
        response = """Questions:
1) First question about testing strategies
2. Second question about code review process
3) Third question about documentation

Tips:
• Review testing frameworks
• Practice explaining your process"""
        
        result = self.parser.parse(response)
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.questions), 3)
        self.assertEqual(len(result.recommendations), 2)
    
    def test_parse_text_bulleted(self):
        """Test parsing bullet point format."""
        response = """Technical Interview Questions:
        
• How do you optimize database queries?
• What's your experience with caching strategies?
• Describe a challenging bug you solved
- How do you approach system design?

Preparation Tips:
- Review your past projects
- Practice explaining technical concepts
• Prepare questions for the interviewer"""
        
        result = self.parser.parse(response)
        
        self.assertTrue(result.success)
        self.assertEqual(result.strategy_used, ParseStrategy.TEXT_BULLETED)
        self.assertEqual(len(result.questions), 4)
        self.assertEqual(len(result.recommendations), 3)
    
    def test_parse_text_paragraph(self):
        """Test parsing paragraph format."""
        response = """Let me provide some interview questions for you.
        
What is your experience with distributed systems? How do you handle 
scalability challenges? Can you describe a time when you had to 
optimize performance?

For preparation, I recommend reviewing system design principles. You should 
also practice explaining your technical decisions."""
        
        result = self.parser.parse(response)
        
        self.assertTrue(result.success)
        self.assertEqual(result.strategy_used, ParseStrategy.TEXT_PARAGRAPH)
        self.assertTrue(len(result.questions) >= 2)
        self.assertTrue(all('?' in q.question for q in result.questions))
    
    def test_parse_fallback_basic(self):
        """Test fallback parsing for poorly formatted response."""
        response = """Some interview content here
Experience with Python
Knowledge of databases
Understanding of REST APIs
Leadership skills
Team collaboration"""
        
        result = self.parser.parse(response)
        
        self.assertTrue(result.success)
        self.assertTrue(len(result.questions) > 0)
    
    def test_parse_empty_response(self):
        """Test parsing empty or null responses."""
        # Empty string
        result = self.parser.parse("")
        self.assertFalse(result.success)
        self.assertEqual(result.strategy_used, ParseStrategy.DEFAULT)
        self.assertTrue(len(result.questions) > 0)  # Should have defaults
        
        # Whitespace only
        result = self.parser.parse("   \n\n  ")
        self.assertFalse(result.success)
        self.assertEqual(result.strategy_used, ParseStrategy.DEFAULT)
    
    def test_parse_invalid_json(self):
        """Test parsing malformed JSON."""
        response = '{"questions": ["Q1", "Q2"'  # Missing closing brackets
        
        result = self.parser.parse(response)
        
        # Should fall back to text parsing or default
        self.assertNotEqual(result.strategy_used, ParseStrategy.JSON_STRUCTURED)
        self.assertTrue(len(result.questions) > 0)
    
    def test_parse_with_context_enrichment(self):
        """Test context enrichment with interview type and experience level."""
        response = json.dumps({
            "questions": [
                {"question": "How do you implement a sorting algorithm?"},
                {"question": "Explain database normalization"}
            ],
            "recommendations": ["Practice coding"]
        })
        
        result = self.parser.parse(
            response,
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.SENIOR
        )
        
        self.assertTrue(result.success)
        # Check that difficulty was inferred
        self.assertEqual(result.questions[0].difficulty, DifficultyLevel.HARD)
        # Check that category was inferred
        self.assertEqual(result.questions[0].category, QuestionCategory.ALGORITHMS)
        # Check metadata
        self.assertEqual(result.metadata["interview_type"], "Technical Questions")
        self.assertEqual(result.metadata["experience_level"], "Senior (5+ years)")
    
    def test_generate_default_response_technical(self):
        """Test default response generation for technical interviews."""
        result = self.parser._generate_default_response(
            interview_type=InterviewType.TECHNICAL,
            experience_level=ExperienceLevel.MID
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.strategy_used, ParseStrategy.DEFAULT)
        self.assertEqual(len(result.questions), 5)
        self.assertEqual(len(result.recommendations), 5)
        self.assertTrue(result.metadata["is_default"])
        
        # Check questions are technical
        self.assertTrue(any("technical" in q.question.lower() or 
                          "technology" in q.question.lower() 
                          for q in result.questions))
    
    def test_generate_default_response_behavioral(self):
        """Test default response generation for behavioral interviews."""
        result = self.parser._generate_default_response(
            interview_type=InterviewType.BEHAVIORAL,
            experience_level=ExperienceLevel.JUNIOR
        )
        
        self.assertEqual(len(result.questions), 5)
        # Check difficulty matches junior level
        self.assertTrue(all(q.difficulty == DifficultyLevel.EASY 
                          for q in result.questions))
    
    def test_question_validation(self):
        """Test question length validation."""
        # Too short questions should be filtered
        response = json.dumps({
            "questions": [
                "OK?",  # Too short
                "What is your experience with cloud computing?",  # Good
                "x" * 501  # Too long
            ],
            "recommendations": []
        })
        
        result = self.parser.parse(response)
        
        # Should fail validation and fall back
        self.assertNotEqual(result.strategy_used, ParseStrategy.JSON_STRUCTURED)
    
    # def test_parse_simple_interface(self):
    #     """Test backward-compatible simple interface."""
    #     response = json.dumps({
    #         "questions": ["Q1", "Q2", "Q3"],
    #         "recommendations": ["R1", "R2"]
    #     })
        
    #     result = self.parser.parse_simple(response)
        
    #     self.assertIsInstance(result, dict)
    #     self.assertIn("questions", result)
    #     self.assertIn("recommendations", result)
    #     self.assertEqual(len(result["questions"]), 3)
    #     self.assertEqual(len(result["recommendations"]), 2)
    
    def test_extract_json_from_mixed_content(self):
        """Test JSON extraction from mixed content."""
        response = """The AI responded with:
        Some text here
        {"questions": ["Q1"], "recommendations": ["R1"]}
        More text after"""
        
        json_str = self.parser._extract_json(response)
        data = json.loads(json_str)
        
        self.assertEqual(len(data["questions"]), 1)
        self.assertEqual(data["questions"][0], "Q1")
    
    def test_section_header_detection(self):
        """Test section header detection."""
        self.assertTrue(self.parser._is_section_header("Questions:"))
        self.assertTrue(self.parser._is_section_header("Interview Questions"))
        self.assertTrue(self.parser._is_section_header("# Questions"))
        self.assertFalse(self.parser._is_section_header("This is a regular sentence"))
    
    def test_recommendation_detection(self):
        """Test recommendation text detection."""
        self.assertTrue(self.parser._is_recommendation("I recommend studying algorithms"))
        self.assertTrue(self.parser._is_recommendation("Practice coding daily"))
        self.assertTrue(self.parser._is_recommendation("Review the documentation"))
        self.assertFalse(self.parser._is_recommendation("What is your experience?"))
    
    def test_question_detection(self):
        """Test question text detection."""
        self.assertTrue(self.parser._looks_like_question("What is your experience?"))
        self.assertTrue(self.parser._looks_like_question("How do you handle errors?"))
        self.assertTrue(self.parser._looks_like_question("Can you explain this?"))
        self.assertFalse(self.parser._looks_like_question("This is a statement"))
    
    def test_complex_nested_json(self):
        """Test parsing complex nested JSON structures."""
        response = json.dumps({
            "questions": [
                {
                    "question": "Design a URL shortener",
                    "difficulty": "hard",
                    "category": "system_design",
                    "hints": ["Think about scalability", "Consider caching"],
                    "follow_ups": [
                        "How would you handle custom URLs?",
                        "What about analytics?"
                    ],
                    "metadata": {
                        "estimated_time": 30,
                        "topics": ["distributed systems", "databases"]
                    }
                }
            ],
            "recommendations": ["Study system design patterns"],
            "metadata": {
                "generated_by": "gpt-4",
                "timestamp": "2024-01-01"
            }
        })
        
        result = self.parser.parse(response)
        
        self.assertTrue(result.success)
        self.assertEqual(result.strategy_used, ParseStrategy.JSON_STRUCTURED)
        q = result.questions[0]
        self.assertEqual(q.category, QuestionCategory.SYSTEM_DESIGN)
        self.assertEqual(len(q.hints), 2)
        self.assertEqual(len(q.follow_ups), 2)
        self.assertIn("estimated_time", q.metadata)
    
    def test_parse_with_all_strategies_failing(self):
        """Test that default response is generated when all strategies fail."""
        # Create a response that will fail all parsers
        response = "\x00\x01\x02\x03"  # Binary data
        
        result = self.parser.parse(response)
        
        self.assertFalse(result.success)
        self.assertEqual(result.strategy_used, ParseStrategy.DEFAULT)
        self.assertTrue(len(result.questions) > 0)
        self.assertIsNotNone(result.error_message)


class TestParserIntegration(unittest.TestCase):
    """Integration tests for parser with real-world examples."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = ResponseParser()
    
    def test_gpt_style_response(self):
        """Test parsing GPT-style response."""
        response = """Based on the job description for a Senior Python Developer, here are 
some interview questions:

**Technical Questions:**
1. Explain the Global Interpreter Lock (GIL) in Python and its implications for multi-threading.
2. How would you implement a decorator that caches function results?
3. What's the difference between `asyncio` and threading in Python?

**Behavioral Questions:**
- Describe a time when you had to refactor legacy code
- How do you approach code reviews?

**Recommendations:**
• Review Python's advanced features like metaclasses and descriptors
• Practice system design questions
• Prepare examples of performance optimization"""
        
        result = self.parser.parse(
            response,
            InterviewType.TECHNICAL,
            ExperienceLevel.SENIOR
        )
        
        self.assertTrue(result.success)
        self.assertTrue(len(result.questions) >= 5)
        self.assertTrue(len(result.recommendations) >= 3)
    
    def test_claude_style_response(self):
        """Test parsing Claude-style response."""
        response = """I'll help you prepare for your interview. Here are relevant questions:

## Technical Assessment
• Can you walk through your experience with microservices architecture?
• How do you ensure data consistency in distributed systems?
• What strategies do you use for API versioning?

## Problem-Solving
• Describe a challenging technical problem you solved recently
• How do you approach debugging production issues?

To prepare effectively:
- Review your recent projects and quantify your impact
- Practice explaining technical concepts to non-technical stakeholders
- Prepare questions about the team's technical challenges"""
        
        result = self.parser.parse(response)
        
        self.assertTrue(result.success)
        self.assertTrue(len(result.questions) >= 5)
        self.assertTrue(len(result.recommendations) >= 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)