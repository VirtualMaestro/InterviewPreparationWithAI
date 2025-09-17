"""
AI Interview Preparation Assistant - GUI Specification Implementation

This is the new GUI-compliant interface that matches the specification exactly
but uses English labels instead of Russian.

Run this file to start the new GUI interface:
    streamlit run app.py
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

# Add src directory to path BEFORE any other imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


try:
    from src.ai.generator import InterviewQuestionGenerator
    from src.config import Config
    from src.models.enums import (
        AIModel,
        ExperienceLevel,
        InterviewState,
        InterviewType,
        PromptTechnique,
    )
    from src.models.simple_schemas import SimpleAISettings, SimpleGenerationRequest
    from src.utils.security import SecurityValidator
except ImportError as e:
    _ = st.error(f"""
    Import Error: {str(e)}
    
    Please make sure you're running this from the project root directory and that
    all dependencies are installed. Try:
    
    1. Run from project root: `streamlit run app.py`
    2. Check that src/ directory contains all required modules
    3. Ensure virtual environment is activated
    """)
    st.stop()


class InterviewPrepGUI:
    """
    GUI specification compliant interface for Interview Preparation Application.
    
    Implements the exact layout and functionality specified in GUI_streamlit_spec.md
    but with English labels instead of Russian.
    """
    
    def __init__(self):
        """Initialize the GUI application."""
        self.config = Config()
        self.security = SecurityValidator()
        self.generator = None
        self.debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    
    def initialize_session_state(self):
        """Initialize all required session state variables as specified."""
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        if 'mock_started' not in st.session_state:
            st.session_state.mock_started = False
        if 'current_question' not in st.session_state:
            st.session_state.current_question = 0
        if 'correct' not in st.session_state:
            st.session_state.correct = 0
        if 'incorrect' not in st.session_state:
            st.session_state.incorrect = 0
        if 'api_key_validated' not in st.session_state:
            st.session_state.api_key_validated = False
        if 'generation_in_progress' not in st.session_state:
            st.session_state.generation_in_progress = False
        # BDD Mock Interview State Management
        if 'interview_state' not in st.session_state:
            st.session_state.interview_state = InterviewState.NOT_STARTED
        if 'user_input_cleared' not in st.session_state:
            st.session_state.user_input_cleared = False
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate OpenAI API key."""
        try:
            if not api_key or not api_key.startswith("sk-"):
                return False

            # Store validated API key
            st.session_state.api_key = api_key
            st.session_state.api_key_validated = True

            # Initialize generator with AIModel
            self.generator = InterviewQuestionGenerator(api_key, AIModel.GPT_4O)
            return True
        except Exception as e:
            if self.debug_mode:
                st.error(f"API key validation error: {str(e)}")
            return False
    
    def render_api_key_setup(self):
        """Render API key setup interface if not validated."""
        st.markdown("## 🔑 API Key Setup")
        
        _ = st.info("""
        To use this application, you need an OpenAI API key.
        
        **How to get an API key:**
        1. Go to [OpenAI Platform](https://platform.openai.com)
        2. Sign up or log in
        3. Navigate to API Keys section
        4. Create a new secret key
        5. Copy and paste it below
        """)
        
        # API key input
        api_key = st.text_input(
            "Enter your OpenAI API key",
            type="password",
            placeholder="sk-...",
            help="Your API key will be stored in the session and not saved permanently"
        )
        
        # Validate button
        if st.button("Validate API Key", type="primary"):
            if not api_key:
                st.error("Please enter an API key")
            elif self.validate_api_key(api_key):
                st.success("✅ API key validated successfully!")
                st.rerun()
            else:
                st.error("❌ Invalid API key. Please check and try again.")
    
    def render_sidebar(self):
        """Render sidebar components as specified in GUI specification."""
        with st.sidebar:
            # 1. Header Section
            st.title("Interview Prep")
            st.caption("AI-Powered Interview Preparation")
            
            # 2. Form Components
            
            # Job Description
            job_desc = st.text_area(
                "Job Description",
                placeholder="Paste job description or specify position...",
                height=100,
                key="job_description"
            )
            
            # Experience Level
            seniority = st.selectbox(
                "Experience Level",
                options=["Junior (1-2 years)", "Mid-level (3-5 years)", "Senior (5+ years)", "Lead/Principal"],
                index=1,
                key="experience_level"
            )
            
            # Question Type
            question_type = st.radio(
                "Question Type",
                options=["Technical", "Behavioural"],
                index=0,
                key="question_type"
            )
            
            # Session Mode
            session_mode = st.radio(
                "Session Mode",
                options=["Generate questions", "Mock Interview"],
                index=0,
                key="session_mode"
            )
            
            # Questions Number (conditional display)
            questions_num = None
            if session_mode == "Generate questions":
                questions_num = st.selectbox(
                    "Number of Questions",
                    options=[5, 10, 15, 20],
                    index=0,
                    key="questions_number"
                )
            
            # 3. Advanced Settings (Expandable)
            with st.expander("Advanced Settings"):
                prompt_tech = st.selectbox(
                    "Prompting Technique",
                    options=["Zero Shot", "Few Shot", "Role Based", "Chain of Thought", "Structured Output"],
                    index=1,
                    key="prompt_technique"
                )
                
                temperature = st.slider(
                    "Temperature",
                    min_value=0.1,
                    max_value=0.9,
                    value=0.7,
                    step=0.1,
                    key="temperature"
                )
                
                top_p = st.slider(
                    "Top-P",
                    min_value=0.1,
                    max_value=0.9,
                    value=0.9,
                    step=0.1,
                    key="top_p"
                )
                
                max_tokens = st.number_input(
                    "Max Tokens",
                    min_value=100,
                    max_value=4000,
                    value=2000,
                    step=100,
                    key="max_tokens"
                )
        
        return {
            "job_description": job_desc,
            "experience_level": seniority,
            "question_type": question_type,
            "session_mode": session_mode,
            "questions_num": questions_num,
            "prompt_technique": prompt_tech,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens
        }
    
    def render_main_content(self, sidebar_config: dict[str, Any]):
        """Render main content area as specified with BDD compliance."""
        # 1. Header Section
        st.header("Assistant Chat")
        st.caption("Area for generating questions and conducting mock interviews")
        
        # 2. Questions Area with fixed height container (BDD requirement)
        questions_container = st.container(height=400)
        with questions_container:
            # Initialize with welcome message if empty
            if not st.session_state.chat_messages:
                if sidebar_config["session_mode"] == "Mock Interview":
                    st.session_state.chat_messages = [
                        "Welcome! Configure the parameters on the left and click 'Start Mock Interview' to begin."
                    ]
                else:
                    st.session_state.chat_messages = [
                        "Welcome! Configure the parameters on the left and click the button to start."
                    ]
            
            # Display messages in Questions Area
            for message in st.session_state.chat_messages:
                st.markdown(f"📝 {message}")
        
        # 3. Control Panel - BDD Button Visibility Logic
        col1, col2, col3 = st.columns([2, 1, 2])
        
        # BDD State Management for Button Visibility
        interview_state = st.session_state.get('interview_state', InterviewState.NOT_STARTED)
        is_mock_mode = sidebar_config["session_mode"] == "Mock Interview"
        
        with col1:
            # Start Mock Interview Button - BDD Logic
            if is_mock_mode and interview_state == InterviewState.NOT_STARTED:
                main_button = st.button("Start Mock Interview", type="primary", key="main_action_button")
            elif not is_mock_mode:
                # Generate Questions mode
                main_button = st.button("Generate Questions", type="primary", key="main_action_button")
            else:
                # Hidden after clicked in mock mode
                main_button = False
        
        with col2:
            # Next Question Button - BDD Logic
            next_button = False
            if is_mock_mode:
                if interview_state == InterviewState.GENERATING_QUESTION:
                    # Visible but disabled during generation
                    next_button = st.button("Next Question", key="next_question_button", disabled=True)
                elif interview_state == InterviewState.SHOWING_EVALUATION:
                    # Visible and enabled after evaluation
                    next_button = st.button("Next Question", key="next_question_button", disabled=False)
                # Hidden in other states (NOT_STARTED, QUESTION_READY, EVALUATING_ANSWER)
        
        with col3:
            # Statistics (only in mock mode)
            if is_mock_mode:
                col3_1, col3_2 = st.columns(2)
                with col3_1:
                    st.metric("Correct", st.session_state.get('correct', 0))
                with col3_2:
                    st.metric("Incorrect", st.session_state.get('incorrect', 0))
        
        # 4. User Input Area - BDD Logic (Mock Mode Only)
        user_answer = None
        submit_answer = False
        
        if is_mock_mode:
            if interview_state == InterviewState.QUESTION_READY:
                # Answer Field visible after question ready
                user_input_key = f"user_input_{st.session_state.get('current_question', 0)}"
                user_answer = st.text_area(
                    "Enter your answer...",
                    placeholder="Enter your answer...",
                    height=80,
                    key=user_input_key,
                    value="" if st.session_state.get('user_input_cleared', False) else None
                )
                
                # Submit Answer button visible only if user has typed something
                if user_answer and user_answer.strip():
                    submit_answer = st.button("Submit Answer", key="submit_answer_button")
                
                # Reset the cleared flag
                if st.session_state.get('user_input_cleared', False):
                    st.session_state.user_input_cleared = False
                    
            # Hidden during evaluation and other states
        
        return {
            "main_button": main_button,
            "next_button": next_button,
            "user_answer": user_answer,
            "submit_answer": submit_answer
        }
    
    def map_config_to_enums(self, sidebar_config: dict[str, Any]) -> dict[str, Any]:
        """Map sidebar configuration to internal enums."""
        # Map experience level
        exp_mapping = {
            "Junior (1-2 years)": ExperienceLevel.JUNIOR,
            "Mid-level (3-5 years)": ExperienceLevel.MID,
            "Senior (5+ years)": ExperienceLevel.SENIOR,
            "Lead/Principal": ExperienceLevel.LEAD
        }
        
        # Map question type
        type_mapping = {
            "Technical": InterviewType.TECHNICAL,
            "Behavioural": InterviewType.BEHAVIORAL
        }
        
        # Map prompt technique
        technique_mapping = {
            "Zero Shot": PromptTechnique.ZERO_SHOT,
            "Few Shot": PromptTechnique.FEW_SHOT,
            "Role Based": PromptTechnique.ROLE_BASED,
            "Chain of Thought": PromptTechnique.CHAIN_OF_THOUGHT,
            "Structured Output": PromptTechnique.STRUCTURED_OUTPUT
        }
        
        return {
            "job_description": sidebar_config["job_description"],
            "experience_level": exp_mapping[sidebar_config["experience_level"]],
            "interview_type": type_mapping[sidebar_config["question_type"]],
            "prompt_technique": technique_mapping[sidebar_config["prompt_technique"]],
            "question_count": sidebar_config.get("questions_num") or 5,  # Fix: Handle None properly
            "temperature": sidebar_config["temperature"],
            "top_p": sidebar_config["top_p"],
            "max_tokens": sidebar_config["max_tokens"]
        }
    
    def ensure_generator_initialized(self):
        """Ensure generator is initialized with current session API key."""
        if not self.generator and st.session_state.get('api_key'):
            try:
                self.generator = InterviewQuestionGenerator(
                    st.session_state.api_key,
                    AIModel.GPT_4O
                )
            except Exception as e:
                if self.debug_mode:
                    st.error(f"Failed to reinitialize generator: {str(e)}")

    def _get_fallback_questions(self, question_type: str) -> list[str]:
        """Get fallback questions when API fails."""
        fallback_questions = {
            "Technical": [
                "Explain the difference between list and tuple in Python.",
                "How would you implement a simple caching mechanism?",
                "What is the difference between synchronous and asynchronous programming?",
                "How do you handle exceptions in your preferred programming language?",
                "Describe the concept of database indexing and its importance."
            ],
            "Behavioural": [
                "Tell me about a challenging project you worked on recently.",
                "How do you handle conflicts with team members?",
                "Describe a time when you had to learn a new technology quickly.",
                "How do you prioritize tasks when you have multiple deadlines?",
                "Give an example of when you went above and beyond in your role."
            ],
            "Case Studies": [
                "How would you design a system to handle 1 million concurrent users?",
                "Walk me through how you would approach debugging a production issue.",
                "How would you design a recommendation system for an e-commerce platform?",
                "Explain how you would migrate a monolith to microservices architecture.",
                "How would you handle data consistency in a distributed system?"
            ],
            "Questions for Employer": [
                "What does a typical day look like for this role?",
                "What are the biggest challenges facing the team right now?",
                "How do you measure success in this position?",
                "What opportunities are there for professional development?",
                "Can you tell me about the team culture and working environment?"
            ]
        }
        return fallback_questions.get(question_type, fallback_questions["Technical"])

    def extract_questions_directly(self, raw_response: str, technique: str) -> list[str]:
        """
        Emergency method to extract questions directly from raw response.
        This bypasses the complex parser to get actual content.
        """
        if not raw_response:
            return []

        questions = []

        # Method 0: Check if this is a JSON response (ONLY for Structured Output)
        import json
        import re

        # Only try JSON parsing for Structured Output technique
        if technique and "structured" in technique.lower():
            try:
                # Try to parse as JSON first
                json_data = json.loads(raw_response)
                if isinstance(json_data, dict) and "questions" in json_data:
                    print(f"DEBUG: Found JSON structured output with {len(json_data['questions'])} question objects")
                    # Handle structured output format
                    for item in json_data["questions"]:
                        if isinstance(item, dict) and "question" in item:
                            question_text = item["question"].strip()
                            if question_text and len(question_text) > 5:  # Reduced minimum length for better extraction
                                questions.append(question_text)
                                print(f"DEBUG: Extracted JSON question: {question_text[:100]}...")
                    if questions:
                        print(f"DEBUG: Successfully extracted {len(questions)} questions from JSON")
                        return questions
            except (json.JSONDecodeError, KeyError, TypeError):
                # Not JSON or doesn't have expected structure, continue with text parsing
                print(f"DEBUG: JSON parsing failed for structured output, falling back to text parsing")
                pass

        # Method 1: Look for numbered questions with various patterns

        # Pattern 1: Numbered with bold titles
        pattern1 = r'^\d+\.\s*\*\*([^*]+)\*\*(.*)$'
        matches1 = re.findall(pattern1, raw_response, re.MULTILINE | re.DOTALL)

        for title, content in matches1:
            # Combine title and content, clean up formatting
            full_question = f"{title.strip()}: {content.strip()}" if content.strip() else title.strip()
            full_question = re.sub(r'\s*-\s*\*\*[^*]*\*\*:.*$', '', full_question, flags=re.MULTILINE)
            full_question = re.sub(r'\s*-\s*\*Tests:.*$', '', full_question, flags=re.MULTILINE)
            full_question = re.sub(r'\s*-\s*\*Focus:.*$', '', full_question, flags=re.MULTILINE)
            full_question = full_question.strip()
            if len(full_question) > 10:
                questions.append(full_question)

        # Method 2: If method 1 didn't work, try simple numbered extraction
        if len(questions) < 3:
            questions = []
            pattern2 = r'^\d+\.\s*(.+)$'
            matches2 = re.findall(pattern2, raw_response, re.MULTILINE)

            for match in matches2:
                clean_question = match.strip()
                # Remove markdown formatting
                clean_question = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_question)
                # Remove metadata lines
                if not any(word in clean_question.lower() for word in ['tests:', 'focus:', 'scenario:']):
                    if len(clean_question) > 10:
                        questions.append(clean_question)

        # Method 3: Extract complete question blocks (enhanced)
        if len(questions) < 3:
            questions = []
            # Split into sections by ### or numbered questions
            sections = re.split(r'(?=###\s*Question\s*\d+|^\d+\.\s*\*\*)', raw_response, flags=re.MULTILINE)

            for section in sections:
                section = section.strip()
                if not section:
                    continue

                # Extract question from section
                lines = section.split('\n')
                question_lines = []
                collecting = False

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Start collecting when we see "Question:" pattern
                    if re.search(r'\*\*Question[:\]]*\*\*', line) or line.startswith('**Question'):
                        collecting = True
                        # Extract the actual question text
                        question_match = re.search(r'["\"]([^"\"]+)["\"]', line)
                        if question_match:
                            question_lines.append(question_match.group(1))
                        continue
                    elif collecting and ('**Assessment' in line or '**What it tests' in line or
                                       '*Rationale*' in line or 'Skills required' in line):
                        break
                    elif collecting and not line.startswith('*') and not line.startswith('-'):
                        question_lines.append(line)

                if question_lines:
                    full_question = ' '.join(question_lines).strip()
                    # Clean up any remaining markdown
                    full_question = re.sub(r'\*\*([^*]+)\*\*', r'\1', full_question)
                    if len(full_question) > 20:
                        questions.append(full_question)

        # Method 4: Fallback - just get sentences that end with question marks or look substantial
        if len(questions) < 2:
            sentences = re.split(r'[.!?]+', raw_response)
            for sentence in sentences:
                sentence = sentence.strip()
                if (len(sentence) > 50 and
                    ('would you' in sentence.lower() or 'how would' in sentence.lower() or
                     'what' in sentence.lower() or 'describe' in sentence.lower() or
                     'explain' in sentence.lower() or 'design' in sentence.lower())):
                    questions.append(sentence + '?')
                    if len(questions) >= 10:  # Don't go overboard
                        break

        return questions[:10]  # Allow up to 10 questions

    async def generate_questions_async(self, config: dict[str, Any]) -> dict[str, Any] | None:
        """Generate questions asynchronously using existing AI system."""
        try:
            print(f"DEBUG: Starting question generation with config: {config}")
            st.info(f"🔍 Debug: Starting generation with {config['question_count']} questions")

            # Ensure generator is initialized
            self.ensure_generator_initialized()

            if not self.generator:
                error_msg = "Generator not initialized - API key validation may have failed"
                print(f"DEBUG ERROR: {error_msg}")
                st.error(f"🔍 Debug Error: {error_msg}")
                raise Exception(error_msg)

            print(f"DEBUG: Generator initialized successfully")
            st.info("🔍 Debug: Generator initialized successfully")

            # Create generation request with enhanced job description
            enhanced_job_description = f"{config['job_description']}\n\nIMPORTANT: Generate exactly {config['question_count']} complete interview questions with detailed scenarios and context, not just titles or topic names."

            generation_request = SimpleGenerationRequest(
                job_description=enhanced_job_description,
                interview_type=config["interview_type"],
                experience_level=config["experience_level"],
                prompt_technique=config["prompt_technique"],
                question_count=config["question_count"]
            )
            
            # Set AI settings
            if not generation_request.ai_settings:
                generation_request.ai_settings = SimpleAISettings()
            
            generation_request.ai_settings.temperature = config["temperature"]
            
            print(f"DEBUG: Making API call with request: {generation_request}")
            st.info("🔍 Debug: Making API call to OpenAI...")

            # Generate questions using existing system
            result = await self.generator.generate_questions(
                generation_request,
                preferred_technique=config["prompt_technique"]
            )

            print(f"DEBUG: API call completed. Success: {result.success}")
            if result.success:
                print(f"DEBUG: Got {len(result.questions)} questions")
                print(f"DEBUG: Raw response: {result.raw_response}")
                print(f"DEBUG: Questions list: {result.questions}")
                print(f"DEBUG: Question types: {[type(q) for q in result.questions]}")

                st.success(f"🔍 Debug: API call successful! Got {len(result.questions)} questions")
                st.code(f"Raw API Response:\n{result.raw_response}")
                st.code(f"Parsed Questions:\n{result.questions}")

                # Check each question individually
                for i, q in enumerate(result.questions):
                    st.write(f"Question {i+1}: '{q}' (length: {len(str(q))}, type: {type(q)})")
                    if not str(q).strip():
                        st.error(f"🚨 Empty question detected at index {i+1}!")
            else:
                print(f"DEBUG: API call failed: {result.error_message}")
                st.error(f"🔍 Debug: API call failed: {result.error_message}")

            if not result.success:
                # Provide more helpful error messages and fallback questions
                error_msg = result.error_message or "Generation failed"
                if error_msg == "'content'":
                    error_msg = "API response format error. This usually indicates an API key issue or OpenAI service problem."
                elif "content" in error_msg.lower():
                    error_msg = f"API communication error: {error_msg}. Please check your API key and internet connection."

                print(f"DEBUG: Generation failed with error: {error_msg}")

                # Show error but provide fallback questions so users can still test the app
                st.warning(f"⚠️ API Error: {error_msg}")
                st.info("💡 Using fallback questions for demonstration. Please check your API key to generate personalized questions.")

                # Return fallback questions based on interview type
                fallback_questions = self._get_fallback_questions(st.session_state.get("question_type", "Technical"))
                return {
                    "questions": fallback_questions,
                    "recommendations": [
                        "Fix your API key to get personalized questions.",
                        "Check your OpenAI account balance.",
                        "Verify your internet connection."
                    ],
                    "cost_breakdown": {
                        "input_cost": 0.0,
                        "output_cost": 0.0,
                        "total_cost": 0.0,
                        "input_tokens": 0,
                        "output_tokens": 0
                    },
                    "metadata": {
                        "technique": "Fallback",
                        "model": "demo-mode",
                        "error": error_msg
                    }
                }

            # EMERGENCY FIX: Bypass parser and extract questions directly from raw response
            print(f"DEBUG: Applying emergency question extraction fix")
            technique_used = result.technique_used.value if result.technique_used else "Unknown technique"
            raw_questions = self.extract_questions_directly(result.raw_response, technique_used)
            print(f"DEBUG: Emergency extraction found {len(raw_questions)} questions: {raw_questions}")

            # Use direct extraction if it found more questions than the parser OR if parser questions look incomplete
            parser_questions_incomplete = any(len(q.strip()) < 50 or q.strip().endswith(':') for q in result.questions)

            if len(raw_questions) > len(result.questions) or parser_questions_incomplete:
                final_questions = raw_questions
                print(f"DEBUG: Using emergency extraction due to better count or quality")
            else:
                final_questions = result.questions
                print(f"DEBUG: Using parser results")

            # Post-process to ensure we have exactly the requested count
            if len(final_questions) < config["question_count"]:
                print(f"DEBUG: Warning - got {len(final_questions)} questions but requested {config['question_count']}")
                st.warning(f"⚠️ Generated {len(final_questions)} questions instead of {config['question_count']}. This may be due to API limitations.")
            else:
                # Trim to exact count if we have more
                final_questions = final_questions[:config["question_count"]]

            return {
                'questions': final_questions,
                'recommendations': result.recommendations,
                'cost_breakdown': {
                    'input_cost': result.cost_breakdown.input_cost,
                    'output_cost': result.cost_breakdown.output_cost,
                    'total_cost': result.cost_breakdown.total_cost
                },
                'metadata': {
                    'technique_used': result.technique_used.value,
                    'model_used': result.model_used.value,
                    'timestamp': datetime.now().isoformat(),
                    'emergency_extraction': len(raw_questions) > len(result.questions),
                    **result.metadata
                }
            }
        except Exception as e:
            error_msg = f"Generation failed: {str(e)}"
            print(f"DEBUG ERROR: {error_msg}")
            print(f"DEBUG ERROR TYPE: {type(e)}")
            import traceback
            print(f"DEBUG TRACEBACK: {traceback.format_exc()}")
            st.error(f"🔍 Debug Error: {error_msg}")
            st.code(f"Error type: {type(e)}\nTraceback: {traceback.format_exc()}")
            return None
    
    def handle_generate_questions_mode(self, sidebar_config: dict[str, Any], controls: dict[str, Any]):
        """Handle Generate Questions mode functionality."""
        if controls["main_button"]:
            if not sidebar_config["job_description"]:
                st.warning("Please enter a job description")
                return
            
            with st.spinner("Generating questions..."):
                # Map configuration to internal format
                mapped_config = self.map_config_to_enums(sidebar_config)
                
                # Run async generation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    results = loop.run_until_complete(
                        self.generate_questions_async(mapped_config)
                    )
                    
                    if results and results.get('questions'):
                        # Debug: Show what we got
                        if self.debug_mode:
                            st.write("Debug - Raw results:", results)
                            st.write("Debug - Questions list:", results['questions'])

                        # Format questions for display
                        questions_text = "**Generated Questions:**\n\n"
                        # Fix: Use the correct key and handle None values properly
                        requested_count = sidebar_config.get("questions_num") or 5

                        # Debug information
                        if self.debug_mode:
                            st.write(f"🐛 Debug - Requested count: {requested_count}")
                            st.write(f"🐛 Debug - Total questions generated: {len(results['questions'])}")
                            st.write(f"🐛 Debug - Sidebar config: {sidebar_config}")

                        questions_list = results['questions'][:requested_count]

                        # Check if questions are empty
                        if not any(q.strip() for q in questions_list):
                            st.error("Generated questions are empty. This might be an API response parsing issue.")
                            if self.debug_mode:
                                st.write("Empty questions detected:", questions_list)
                            return

                        for i, question in enumerate(questions_list, 1):
                            if question.strip():  # Only show non-empty questions
                                questions_text += f"{i}. {question.strip()}\n\n"

                        # Update chat messages
                        st.session_state.chat_messages = [questions_text]
                        st.rerun()
                    else:
                        st.error("Failed to generate questions. Please try again.")
                        if self.debug_mode and results:
                            st.write("Debug - Full results:", results)
                finally:
                    loop.close()
    
    async def generate_mock_questions_async(self, sidebar_config: dict[str, Any], count: int = 5) -> list[str]:
        """Generate questions for mock interview using AI system."""
        try:
            # Map configuration for AI generation
            mapped_config = self.map_config_to_enums(sidebar_config)
            mapped_config["question_count"] = count  # Generate a pool of questions

            # Ensure generator is initialized
            self.ensure_generator_initialized()

            if not self.generator:
                raise Exception("Generator not initialized - API key validation may have failed")

            # Create generation request for mock interview
            generation_request = SimpleGenerationRequest(
                job_description=f"{mapped_config['job_description']}\n\nFORMAT INSTRUCTIONS FOR MOCK INTERVIEW:\n- Generate ONLY complete, specific interview questions\n- Each question must be directly actionable and answerable\n- Use numbered list format: '1. [Complete question here]'\n- Do NOT use category headers or section titles\n- Do NOT include explanatory text after questions\n- Examples of GOOD questions: '1. How would you implement user authentication in a web application?' '2. Explain the differences between REST and GraphQL APIs'\n- Examples of BAD format: 'Advanced Concepts:', 'Technical Skills:', 'System Design Topics'",
                interview_type=mapped_config["interview_type"],
                experience_level=mapped_config["experience_level"],
                prompt_technique=mapped_config["prompt_technique"],
                question_count=count
            )

            if not generation_request.ai_settings:
                generation_request.ai_settings = SimpleAISettings()
            generation_request.ai_settings.temperature = mapped_config["temperature"]

            # Generate questions
            result = await self.generator.generate_questions(
                generation_request,
                preferred_technique=mapped_config["prompt_technique"]
            )

            if result.success and result.questions:
                # Extract questions using our improved parser
                technique_used = str(result.technique_used.value) if result.technique_used else "Unknown technique"
                questions = self.extract_questions_directly(result.raw_response, technique_used)
                return questions if questions else result.questions
            else:
                return []

        except Exception as e:
            print(f"DEBUG ERROR: Mock question generation failed: {str(e)}")
            return []

    async def evaluate_answer_async(self, question: str, answer: str, job_description: str, experience_level: str) -> dict[str, Any]:
        """Evaluate user's answer using AI and provide feedback."""
        try:
            # Ensure generator is available, create if needed
            if not self.generator and st.session_state.get('api_key'):
                try:
                    self.generator = InterviewQuestionGenerator(
                        st.session_state.api_key,
                        AIModel.GPT_4O
                    )
                except Exception as e:
                    return {"feedback": f"Unable to initialize evaluator: {str(e)}", "score": 0}

            if not self.generator:
                return {"feedback": "Unable to evaluate - no API key available", "score": 0}

            # Create evaluation prompt
            evaluation_prompt = f"""
            As an expert interviewer, evaluate this interview answer:

            **Job Context:** {job_description[:200]}...
            **Experience Level:** {experience_level}
            **Question:** {question}
            **Candidate's Answer:** {answer}

            Please provide:
            1. A score from 1-10
            2. Specific feedback on strengths and areas for improvement
            3. Suggestions for a better answer

            Format your response as:
            SCORE: [1-10]
            FEEDBACK: [Your detailed feedback]
            SUGGESTIONS: [Specific suggestions for improvement]
            """

            # Use the generator's OpenAI client for evaluation
            import openai
            client = openai.AsyncOpenAI(api_key=st.session_state.get('api_key'))

            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer providing constructive feedback."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )

            feedback_text = response.choices[0].message.content

            # Parse the response with better multi-line handling
            score = 7  # Default score
            feedback = "Good effort! Keep practicing."
            suggestions = "Continue developing your technical skills."

            if feedback_text:
                lines = feedback_text.split('\n')
                current_section = None
                current_content = []

                for line in lines:
                    line = line.strip()

                    if line.startswith('SCORE:'):
                        # Save previous section
                        if current_section == 'FEEDBACK' and current_content:
                            feedback = ' '.join(current_content).strip()
                        elif current_section == 'SUGGESTIONS' and current_content:
                            suggestions = ' '.join(current_content).strip()

                        # Parse score
                        try:
                            score = int(line.split(':')[1].strip())
                        except:
                            pass
                        current_section = None
                        current_content = []

                    elif line.startswith('FEEDBACK:'):
                        # Save previous section
                        if current_section == 'SUGGESTIONS' and current_content:
                            suggestions = ' '.join(current_content).strip()

                        # Start new section
                        current_section = 'FEEDBACK'
                        initial_content = line.split(':', 1)[1].strip()
                        current_content = [initial_content] if initial_content else []

                    elif line.startswith('SUGGESTIONS:'):
                        # Save previous section
                        if current_section == 'FEEDBACK' and current_content:
                            feedback = ' '.join(current_content).strip()

                        # Start new section
                        current_section = 'SUGGESTIONS'
                        initial_content = line.split(':', 1)[1].strip()
                        current_content = [initial_content] if initial_content else []

                    elif current_section and line:
                        # Continue building current section
                        current_content.append(line)

                # Don't forget the last section
                if current_section == 'FEEDBACK' and current_content:
                    feedback = ' '.join(current_content).strip()
                elif current_section == 'SUGGESTIONS' and current_content:
                    suggestions = ' '.join(current_content).strip()

            return {
                "score": score,
                "feedback": feedback,
                "suggestions": suggestions
            }

        except Exception as e:
            print(f"DEBUG ERROR: Answer evaluation failed: {str(e)}")
            return {
                "score": 7,
                "feedback": "Your answer shows good understanding. Keep practicing!",
                "suggestions": "Try to provide more specific examples and technical details."
            }

    def handle_mock_interview_mode(self, sidebar_config: dict[str, Any], controls: dict[str, Any]):
        """Handle Mock Interview mode functionality with BDD-compliant state transitions."""
        
        interview_state = st.session_state.get('interview_state', InterviewState.NOT_STARTED)
        
        # BDD Scenario: User clicks "Start Mock Interview"
        if controls["main_button"] and interview_state == InterviewState.NOT_STARTED:
            if not sidebar_config["job_description"]:
                st.warning("Please enter a job description to start the mock interview")
                return

            # Transition to generating_question state
            st.session_state.interview_state = InterviewState.GENERATING_QUESTION
            st.session_state.mock_started = True
            
            with st.spinner("Generating interview questions..."):
                # Generate questions using AI
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    questions = loop.run_until_complete(
                        self.generate_mock_questions_async(sidebar_config, count=10)
                    )

                    if questions:
                        # Initialize mock interview state
                        st.session_state.mock_questions = questions
                        st.session_state.current_question = 0
                        st.session_state.correct = 0
                        st.session_state.incorrect = 0
                        st.session_state.total_score = 0
                        st.session_state.answers_given = []

                        # Clean up first question formatting
                        first_question = questions[0] if questions else "Tell me about yourself."
                        clean_question = first_question
                        if clean_question.lower().startswith('question '):
                            parts = clean_question.split(':', 1)
                            if len(parts) > 1:
                                clean_question = parts[1].strip()

                        # Update Questions Area and transition to question_ready state
                        st.session_state.chat_messages = [
                            f"**🎯 Mock Interview Started!**\n\n**Question 1:**\n{clean_question}"
                        ]
                        st.session_state.interview_state = InterviewState.QUESTION_READY
                        st.rerun()
                    else:
                        st.error("Failed to generate questions. Please check your API key and try again.")
                        # Reset state on failure
                        st.session_state.interview_state = InterviewState.NOT_STARTED
                        st.session_state.mock_started = False
                finally:
                    loop.close()

        # BDD Scenario: User submits an answer
        elif controls["submit_answer"] and controls["user_answer"] and interview_state == InterviewState.QUESTION_READY:
            user_answer = controls["user_answer"].strip()
            if not user_answer:
                st.warning("Please enter an answer before submitting.")
                return

            # Transition to evaluating_answer state
            st.session_state.interview_state = InterviewState.EVALUATING_ANSWER
            
            with st.spinner("Evaluating your answer..."):
                # Get current question
                current_q_index = st.session_state.get('current_question', 0)
                questions = st.session_state.get('mock_questions', [])

                if current_q_index < len(questions):
                    current_question = questions[current_q_index]

                    # Evaluate answer using AI
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        evaluation = loop.run_until_complete(
                            self.evaluate_answer_async(
                                current_question,
                                user_answer,
                                sidebar_config["job_description"],
                                sidebar_config["experience_level"]
                            )
                        )

                        # Store the answer and evaluation
                        st.session_state.answers_given.append({
                            "question": current_question,
                            "answer": user_answer,
                            "evaluation": evaluation
                        })

                        # Update statistics
                        score = evaluation.get("score", 7)
                        st.session_state.total_score += score
                        if score >= 7:
                            st.session_state.correct += 1
                        else:
                            st.session_state.incorrect += 1

                        # Add answer and evaluation to Questions Area
                        st.session_state.chat_messages.append(f"**Your Answer:** {user_answer}")
                        st.session_state.chat_messages.append(
                            f"**AI Feedback (Score: {score}/10):**\n{evaluation.get('feedback', 'Good effort!')}\n\n"
                            f"**💡 Suggestions:** {evaluation.get('suggestions', 'Keep practicing!')}"
                        )

                        # Transition to showing_evaluation state
                        st.session_state.interview_state = InterviewState.SHOWING_EVALUATION
                        st.session_state.user_input_cleared = True  # Flag to clear input field
                        st.rerun()

                    finally:
                        loop.close()

        # BDD Scenario: User clicks "Next Question"
        elif controls["next_button"] and interview_state == InterviewState.SHOWING_EVALUATION:
            current_q_index = st.session_state.get('current_question', 0)
            questions = st.session_state.get('mock_questions', [])

            if current_q_index + 1 < len(questions):
                # Move to next question
                st.session_state.current_question = current_q_index + 1
                next_question = questions[current_q_index + 1]

                # Clean up question formatting
                clean_next_question = next_question
                if clean_next_question.lower().startswith('question '):
                    parts = clean_next_question.split(':', 1)
                    if len(parts) > 1:
                        clean_next_question = parts[1].strip()

                # Add next question to Questions Area
                st.session_state.chat_messages.append(
                    f"**Question {current_q_index + 2}:**\n{clean_next_question}"
                )
                
                # Transition back to question_ready state for the new question
                st.session_state.interview_state = InterviewState.QUESTION_READY
                st.session_state.user_input_cleared = True  # Clear input field for new question
                st.rerun()
            else:
                # End of interview
                total_questions = len(st.session_state.get('answers_given', []))
                avg_score = st.session_state.get('total_score', 0) / max(total_questions, 1)

                st.session_state.chat_messages.append(
                    f"**🎉 Mock Interview Complete!**\n\n"
                    f"**Final Results:**\n"
                    f"- Questions Answered: {total_questions}\n"
                    f"- Average Score: {avg_score:.1f}/10\n"
                    f"- Strong Answers: {st.session_state.get('correct', 0)}\n"
                    f"- Needs Improvement: {st.session_state.get('incorrect', 0)}\n\n"
                    f"Great job! Review the feedback above to improve your interview skills."
                )

                # Reset for next interview - transition back to not_started
                st.session_state.interview_state = InterviewState.NOT_STARTED
                st.session_state.mock_started = False
                st.rerun()
    
    def render_custom_css(self):
        """Render custom CSS as specified in the GUI specification."""
        _ = st.markdown("""
        <style>
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        /* Main content area */
        .main .block-container {
            background: rgba(255, 255, 255, 0.9);
            padding-top: 2rem;
        }
        
        /* Chat container styling */
        .element-container:has(> .stContainer) {
            background: #fafbfc;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 15px;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(139, 92, 246, 0.2);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(139, 92, 246, 0.3);
        }
        
        /* Message styling */
        .chat-message {
            margin-bottom: 12px;
            padding: 10px 12px;
            border-radius: 8px;
            background: #f7fafc;
            border-left: 3px solid #a78bfa;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Run the main GUI application."""
        # Initialize session state
        self.initialize_session_state()
        
        # Apply custom CSS
        self.render_custom_css()
        
        # Check API key validation
        if not st.session_state.get('api_key_validated', False):
            self.render_api_key_setup()
            return
        
        # Render sidebar and get configuration
        sidebar_config = self.render_sidebar()
        
        # Render main content and get controls
        controls = self.render_main_content(sidebar_config)
        
        # Handle mode-specific functionality
        if sidebar_config["session_mode"] == "Generate questions":
            self.handle_generate_questions_mode(sidebar_config, controls)
        elif sidebar_config["session_mode"] == "Mock Interview":
            self.handle_mock_interview_mode(sidebar_config, controls)


def main():
    """Main application entry point."""
    # Page configuration matching GUI specification
    st.set_page_config(
        page_title="Interview Prep",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Check for debug mode
    if "--debug" in sys.argv:
        os.environ["DEBUG"] = "true"
    
    # Initialize and run GUI application
    try:
        app = InterviewPrepGUI()
        app.run()
    except Exception as e:
        _ = st.error(f"Application error: {str(e)}")
        if os.getenv("DEBUG", "false").lower() == "true":
            import traceback
            _ = st.code(traceback.format_exc())
        
        _ = st.info("""
        **Troubleshooting:**
        1. Ensure you have set your OpenAI API key
        2. Check your internet connection
        3. Verify all dependencies are installed
        4. Try refreshing the page
        
        If the issue persists, please report it.
        """)


if __name__ == "__main__":
    main()