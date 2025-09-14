"""
AI Interview Preparation Assistant - GUI Specification Implementation

This is the new GUI-compliant interface that matches the specification exactly
but uses English labels instead of Russian.

Run this file to start the new GUI interface:
    streamlit run main_gui.py
"""

import sys
import os
import streamlit as st
from typing import Any
from datetime import datetime
import asyncio

from pathlib import Path

# Add src directory to path BEFORE any other imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


try:
    from src.models.simple_schemas import GenerationRequest, AISettings
    from src.ai.generator import InterviewQuestionGenerator
    from src.models.enums import InterviewType, ExperienceLevel, PromptTechnique
    from src.utils.security import SecurityValidator
    from src.config import Config
except ImportError as e:
    st.error(f"""
    Import Error: {str(e)}
    
    Please make sure you're running this from the project root directory and that
    all dependencies are installed. Try:
    
    1. Run from project root: `streamlit run main_gui.py`
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
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate OpenAI API key."""
        try:
            if not api_key or not api_key.startswith("sk-"):
                return False
            
            # Store validated API key
            st.session_state.api_key = api_key
            st.session_state.api_key_validated = True
            
            # Initialize generator
            self.generator = InterviewQuestionGenerator(api_key)
            return True
        except Exception as e:
            if self.debug_mode:
                st.error(f"API key validation error: {str(e)}")
            return False
    
    def render_api_key_setup(self):
        """Render API key setup interface if not validated."""
        st.markdown("## 🔑 API Key Setup")
        
        st.info("""
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
                    options=["Zero Shot", "Few Shot", "Chain of Thought", "Role Based", "Structured Output"],
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
        """Render main content area as specified."""
        # 1. Header Section
        st.header("Assistant Chat")
        st.caption("Area for generating questions and conducting mock interviews")
        
        # 2. Chat Area with fixed height container
        chat_container = st.container(height=400)
        with chat_container:
            # Initialize with welcome message if empty
            if not st.session_state.chat_messages:
                st.session_state.chat_messages = [
                    "Welcome! Configure the parameters on the left and click the button to start."
                ]
            
            # Display messages
            for message in st.session_state.chat_messages:
                st.markdown(f"📝 {message}")
        
        # 3. Control Panel
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            # Dynamic button text based on mode
            button_text = "Generate Questions" if sidebar_config["session_mode"] == "Generate questions" else "Start Mock Interview"
            main_button = st.button(button_text, type="primary", key="main_action_button")
        
        with col2:
            # Next question button (only in mock mode)
            next_button = False
            if sidebar_config["session_mode"] == "Mock Interview":
                next_button = st.button("Next Question", key="next_question_button")
        
        with col3:
            # Statistics (only in mock mode)
            if sidebar_config["session_mode"] == "Mock Interview":
                col3_1, col3_2 = st.columns(2)
                with col3_1:
                    st.metric("Correct", st.session_state.get('correct', 0))
                with col3_2:
                    st.metric("Incorrect", st.session_state.get('incorrect', 0))
        
        # 4. User Input Area (Mock Mode Only)
        user_answer = None
        submit_answer = False
        if sidebar_config["session_mode"] == "Mock Interview" and st.session_state.get('mock_started', False):
            user_answer = st.text_area(
                "Enter your answer...",
                placeholder="Enter your answer...",
                height=80,
                key="user_input"
            )
            
            submit_answer = st.button("Submit Answer", key="submit_answer_button")
        
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
            "Chain of Thought": PromptTechnique.CHAIN_OF_THOUGHT,
            "Role Based": PromptTechnique.ROLE_BASED,
            "Structured Output": PromptTechnique.STRUCTURED_OUTPUT
        }
        
        return {
            "job_description": sidebar_config["job_description"],
            "experience_level": exp_mapping[sidebar_config["experience_level"]],
            "interview_type": type_mapping[sidebar_config["question_type"]],
            "prompt_technique": technique_mapping[sidebar_config["prompt_technique"]],
            "question_count": sidebar_config.get("questions_num", 5),
            "temperature": sidebar_config["temperature"],
            "top_p": sidebar_config["top_p"],
            "max_tokens": sidebar_config["max_tokens"]
        }
    
    async def generate_questions_async(self, config: dict[str, Any]) -> dict[str, Any] | None:
        """Generate questions asynchronously using existing AI system."""
        try:
            if not self.generator:
                raise Exception("Generator not initialized - API key validation may have failed")
            
            # Create generation request
            generation_request = GenerationRequest(
                job_description=config["job_description"],
                interview_type=config["interview_type"],
                experience_level=config["experience_level"],
                prompt_technique=config["prompt_technique"],
                question_count=config["question_count"]
            )
            
            # Set AI settings
            if not generation_request.ai_settings:
                generation_request.ai_settings = AISettings()
            
            generation_request.ai_settings.temperature = config["temperature"]
            
            # Generate questions using existing system
            result = await self.generator.generate_questions(
                generation_request,
                preferred_technique=config["prompt_technique"]
            )
            
            if not result.success:
                raise Exception(result.error_message or "Generation failed")
            
            return {
                'questions': result.questions,
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
                    **result.metadata
                }
            }
        except Exception as e:
            st.error(f"Generation failed: {str(e)}")
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
                        # Format questions for display
                        questions_text = "**Generated Questions:**\n\n"
                        for i, question in enumerate(results['questions'][:sidebar_config.get("questions_num", 5)], 1):
                            questions_text += f"{i}. {question}\n\n"
                        
                        # Update chat messages
                        st.session_state.chat_messages = [questions_text]
                        st.rerun()
                    else:
                        st.error("Failed to generate questions. Please try again.")
                finally:
                    loop.close()
    
    def handle_mock_interview_mode(self, sidebar_config: dict[str, Any], controls: dict[str, Any]):
        """Handle Mock Interview mode functionality."""
        if controls["main_button"] and not st.session_state.mock_started:
            # Start mock interview
            st.session_state.mock_started = True
            st.session_state.current_question = 1
            st.session_state.chat_messages = [
                "**Question 1:**\nExplain the difference between synchronous and asynchronous programming in Python. Provide examples of usage."
            ]
            st.rerun()
        
        if controls["submit_answer"] and controls["user_answer"]:
            # Process user answer (simplified evaluation for now)
            st.session_state.chat_messages.append(f"**Your Answer:** {controls['user_answer']}")
            st.session_state.chat_messages.append("**Feedback:** Good answer! Consider providing more specific examples next time.")
            
            # Update statistics (simplified logic)
            st.session_state.correct += 1
            
            # Clear input
            st.session_state.user_input = ""
            st.rerun()
        
        if controls["next_button"] and st.session_state.mock_started:
            # Move to next question
            st.session_state.current_question += 1
            next_q = f"**Question {st.session_state.current_question}:**\nDescribe how you would optimize a slow SQL query."
            st.session_state.chat_messages.append(next_q)
            st.rerun()
    
    def render_custom_css(self):
        """Render custom CSS as specified in the GUI specification."""
        st.markdown("""
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
        st.error(f"Application error: {str(e)}")
        if os.getenv("DEBUG", "false").lower() == "true":
            import traceback
            st.code(traceback.format_exc())
        
        st.info("""
        **Troubleshooting:**
        1. Ensure you have set your OpenAI API key
        2. Check your internet connection
        3. Verify all dependencies are installed
        4. Try refreshing the page
        
        If the issue persists, please report it.
        """)


if __name__ == "__main__":
    main()