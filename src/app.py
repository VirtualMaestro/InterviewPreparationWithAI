"""
Main Application Orchestrator for Interview Prep Application.

Coordinates all components and manages the application workflow.
"""

import streamlit as st
import asyncio
from typing import Optional, Dict, Any
import os
from datetime import datetime

from models.simple_schemas import GenerationRequest
from ai.generator import InterviewQuestionGenerator
from ui.components import input_components, results_display, progress_indicators
from ui.session import session_manager
from utils.security import SecurityValidator
from utils.error_handler import (
    global_error_handler, 
    handle_errors, 
    handle_async_errors,
    ErrorContext,
    ConfigurationError,
    ErrorCategory
)
from config import Config


class InterviewPrepApp:
    """
    Main application orchestrator.
    
    Manages initialization, API key validation, question generation workflow,
    and error handling.
    """
    
    def __init__(self):
        """Initialize the application."""
        self.config = Config()
        self.security = SecurityValidator()
        self.generator = None
        self.debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    
    @handle_errors(
        error_handler=global_error_handler,
        attempt_recovery=True,
        reraise=False
    )
    def initialize(self) -> bool:
        """
        Initialize application and validate setup.
        
        Returns:
            True if initialization successful
        """
        error_context = ErrorContext(
            operation="app_initialization",
            additional_info={"debug_mode": self.debug_mode}
        )
        
        try:
            # Initialize session
            session_manager._initialize_state()
            
            # Check for API key
            api_key = session_manager.get_api_key()
            
            if not api_key:
                global_error_handler.handle_error(
                    ConfigurationError("No API key provided"),
                    error_context
                )
                return False
            
            # Initialize generator if not already done
            if not self.generator:
                try:
                    self.generator = InterviewQuestionGenerator(api_key)
                    return True
                except Exception as e:
                    global_error_handler.handle_error(e, error_context)
                    st.error(f"Failed to initialize AI generator: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            global_error_handler.handle_error(e, error_context)
            st.error(f"Application initialization failed: {str(e)}")
            return False
    
    async def validate_api_key(self, api_key: str) -> bool:
        """
        Validate OpenAI API key.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid
        """
        try:
            # Create temporary generator
            temp_generator = InterviewQuestionGenerator(api_key)
            
            # Validate key
            is_valid = await temp_generator.validate_api_key()
            
            if is_valid:
                session_manager.set_api_key(api_key)
                session_manager.mark_api_key_validated(True)
                self.generator = temp_generator
                return True
            
            return False
            
        except Exception as e:
            if self.debug_mode:
                st.error(f"API key validation error: {str(e)}")
            return False
    
    def render_api_key_setup(self) -> None:
        """Render API key setup interface."""
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
            elif not api_key.startswith("sk-"):
                st.error("Invalid API key format. Should start with 'sk-'")
            else:
                with st.spinner("Validating API key..."):
                    # Run async validation
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        is_valid = loop.run_until_complete(
                            self.validate_api_key(api_key)
                        )
                        
                        if is_valid:
                            st.success("✅ API key validated successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid API key. Please check and try again.")
                    finally:
                        loop.close()
    
    @handle_async_errors(
        error_handler=global_error_handler,
        attempt_recovery=True,
        reraise=False
    )
    async def generate_questions_async(
        self,
        config: Any,
        progress_callback: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Generate questions asynchronously.
        
        Args:
            config: Input configuration
            progress_callback: Optional progress callback
            
        Returns:
            Results dictionary
        """
        error_context = ErrorContext(
            operation="generate_questions_async",
            additional_info={
                "interview_type": config.interview_type.value if hasattr(config, 'interview_type') else None,
                "experience_level": config.experience_level.value if hasattr(config, 'experience_level') else None,
                "prompt_technique": config.prompt_technique.value if hasattr(config, 'prompt_technique') else None,
                "question_count": getattr(config, 'question_count', None)
            }
        )
        
        try:
            # Update progress
            if progress_callback:
                progress_callback("validating", 0.1, "Validating input...")
            
            # Create generation request
            generation_request = GenerationRequest(
                job_description=config.job_description,
                interview_type=config.interview_type,
                experience_level=config.experience_level,
                prompt_technique=config.prompt_technique,
                question_count=config.question_count
            )
            
            # Add optional attributes
            if config.company_type or config.focus_areas or config.persona:
                generation_request.additional_context = {}
                if config.company_type:
                    generation_request.additional_context['company_type'] = config.company_type
                if config.focus_areas:
                    generation_request.additional_context['focus_areas'] = config.focus_areas
                if config.persona:
                    generation_request.additional_context['persona'] = config.persona
            
            generation_request.temperature = config.temperature
            
            # Create session
            session = session_manager.create_session(
                input_config={
                    'job_description': config.job_description[:100] + '...',
                    'interview_type': config.interview_type.value,
                    'experience_level': config.experience_level.value,
                    'prompt_technique': config.prompt_technique.value,
                    'question_count': config.question_count,
                    'temperature': config.temperature,
                    'company_type': config.company_type,
                    'ai_model': config.ai_model.value
                },
                generation_request=generation_request
            )
            
            # Update progress
            if progress_callback:
                progress_callback("generating", 0.3, "Generating questions with AI...")
            
            # Generate questions
            result = await self.generator.generate_questions(
                generation_request,
                preferred_technique=config.prompt_technique
            )
            
            # Update progress
            if progress_callback:
                progress_callback("parsing", 0.7, "Processing response...")
            
            # Check success
            if not result.success:
                raise Exception(result.error_message or "Generation failed")
            
            # Update progress
            if progress_callback:
                progress_callback("formatting", 0.9, "Formatting results...")
            
            # Prepare results
            results = {
                'questions': result.questions,
                'recommendations': result.recommendations,
                'cost_breakdown': {
                    'input_cost': result.cost_breakdown.input_cost,
                    'output_cost': result.cost_breakdown.output_cost,
                    'total_cost': result.cost_breakdown.total_cost
                },
                'token_counts': {
                    'input_tokens': result.cost_breakdown.input_tokens,
                    'output_tokens': result.cost_breakdown.output_tokens,
                    'total_tokens': result.cost_breakdown.input_tokens + result.cost_breakdown.output_tokens
                },
                'metadata': {
                    'technique_used': result.technique_used.value,
                    'model_used': result.model_used.value,
                    'timestamp': datetime.now().isoformat(),
                    **result.metadata
                }
            }
            
            # Update session
            session_manager.update_session_results(
                questions=results['questions'],
                recommendations=results['recommendations'],
                cost_breakdown=results['cost_breakdown'],
                metadata=results['metadata']
            )
            
            # Update progress
            if progress_callback:
                progress_callback("complete", 1.0, "Generation complete!")
            
            return results
            
        except Exception as e:
            error_msg = str(e)
            global_error_handler.handle_error(e, error_context)
            session_manager.update_session_error(error_msg)
            raise Exception(f"Generation failed: {error_msg}")
    
    def generate_questions(self, config: Any) -> Optional[Dict[str, Any]]:
        """
        Generate questions synchronously with progress display.
        
        Args:
            config: Input configuration
            
        Returns:
            Results dictionary or None on error
        """
        # Create status container
        status_container = progress_indicators.create_status_container()
        
        def update_progress(status: str, progress: float, details: str):
            progress_indicators.update_status_container(
                status_container,
                progress_indicators.status_messages.get(status, status),
                progress,
                details
            )
        
        try:
            # Mark generation in progress
            st.session_state.generation_in_progress = True
            
            # Run async generation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                results = loop.run_until_complete(
                    self.generate_questions_async(config, update_progress)
                )
                
                st.session_state.show_results = True
                return results
                
            finally:
                loop.close()
                
        except Exception as e:
            progress_indicators.show_error_details(e, show_traceback=self.debug_mode)
            return None
            
        finally:
            st.session_state.generation_in_progress = False
    
    def render_sidebar(self) -> None:
        """Render application sidebar."""
        with st.sidebar:
            st.markdown("# 🎯 Interview Prep AI")
            
            # Session statistics
            stats = session_manager.get_statistics()
            
            st.markdown("### 📊 Statistics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Sessions", stats['total_sessions'])
                st.metric("Success Rate", 
                         f"{(stats['successful_sessions'] / max(stats['total_sessions'], 1) * 100):.0f}%")
            
            with col2:
                st.metric("Total Cost", f"${stats['total_cost']:.4f}")
                st.metric("Avg Questions", f"{stats['average_questions']:.1f}")
            
            st.divider()
            
            # Session history
            st.markdown("### 📜 Recent Sessions")
            
            history = session_manager.get_session_history()[:5]
            
            if history:
                for session in history:
                    timestamp = session.get('timestamp', '')
                    if timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp)
                            time_str = dt.strftime("%H:%M")
                        except:
                            time_str = "N/A"
                    else:
                        time_str = "N/A"
                    
                    status_icon = "✅" if session.get('success') else "❌"
                    interview_type = session.get('input_config', {}).get('interview_type', 'N/A')
                    
                    if st.button(f"{status_icon} {time_str} - {interview_type}", 
                               key=f"session_{session.get('session_id')}"):
                        # Load session (implement if needed)
                        st.info("Session viewing not yet implemented")
            else:
                st.caption("No sessions yet")
            
            st.divider()
            
            # Actions
            st.markdown("### ⚙️ Actions")
            
            if st.button("🔄 New Session", use_container_width=True):
                session_manager.clear_current_session()
                st.rerun()
            
            if st.button("🗑️ Clear History", use_container_width=True):
                session_manager.clear_history()
                st.success("History cleared")
                st.rerun()
            
            if self.debug_mode:
                if st.button("🐛 Show Debug Info", use_container_width=True):
                    st.session_state.show_debug = not st.session_state.get('show_debug', False)
            
            st.divider()
            
            # Error monitoring
            from ui.error_display import ErrorDisplayManager
            ErrorDisplayManager.show_error_summary_widget()
            
            st.divider()
            
            # About
            with st.expander("ℹ️ About"):
                st.markdown("""
                **AI Interview Prep v1.0**
                
                Generate personalized interview questions using advanced AI.
                
                Features:
                - 5 prompt techniques
                - 4 interview types
                - Cost tracking
                - Session history
                - Error monitoring
                
                Built with OpenAI GPT-4
                """)
    
    def run(self) -> None:
        """Run the main application."""
        # Page config is set in main.py
        
        # Render sidebar
        self.render_sidebar()
        
        # Main content
        st.title("🎯 AI Interview Preparation Assistant")
        st.markdown("Generate personalized interview questions based on job descriptions")
        
        # Check initialization
        if not self.initialize():
            self.render_api_key_setup()
            return
        
        # Debug info
        if st.session_state.get('show_debug', False):
            progress_indicators.show_debug_info({
                'session_state': {
                    k: str(v)[:100] if not k.startswith('api_key') else '***'
                    for k, v in st.session_state.items()
                },
                'generator_ready': self.generator is not None,
                'debug_mode': self.debug_mode
            })
        
        # Main interface tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Generate", "📊 Results", "📈 Analytics", "🚨 Errors"])
        
        with tab1:
            # Get input configuration
            config = input_components.get_input_config()
            
            if config:
                # Show summary
                input_components.render_input_summary(config)
                
                # Generate button
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button(
                        "🚀 Generate Interview Questions",
                        type="primary",
                        use_container_width=True,
                        disabled=st.session_state.generation_in_progress
                    ):
                        results = self.generate_questions(config)
                        
                        if results:
                            st.success("✅ Questions generated successfully!")
                            st.session_state.current_results = results
                            st.rerun()
        
        with tab2:
            if st.session_state.get('show_results') and st.session_state.get('current_results'):
                results = st.session_state.current_results
                
                # Display questions
                results_display.render_questions(
                    results['questions'],
                    results.get('metadata', {}).get('questions_metadata')
                )
                
                # Display cost metrics
                results_display.render_cost_metrics(
                    results['cost_breakdown'],
                    results.get('token_counts')
                )
                
                # Display recommendations
                results_display.render_recommendations(
                    results['recommendations']
                )
                
                # Session metadata
                results_display.render_session_metadata(
                    results['metadata']
                )
                
                # Export options
                results_display.render_export_options(
                    results['questions'],
                    results['recommendations'],
                    results['metadata']
                )
            else:
                st.info("No results to display. Generate questions in the Generate tab.")
        
        with tab3:
            st.markdown("### 📈 Usage Analytics")
            
            stats = session_manager.get_statistics()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Sessions", stats['total_sessions'])
            with col2:
                st.metric("Successful", stats['successful_sessions'])
            with col3:
                st.metric("Failed", stats['failed_sessions'])
            with col4:
                st.metric("Success Rate", 
                         f"{(stats['successful_sessions'] / max(stats['total_sessions'], 1) * 100):.0f}%")
            
            st.divider()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Cost", f"${stats['total_cost']:.4f}")
            with col2:
                st.metric("Total Tokens", f"{stats['total_tokens']:,}")
            with col3:
                st.metric("Avg Questions/Session", f"{stats['average_questions']:.1f}")
            
            # Rate limit status
            if self.generator:
                gen_stats = self.generator.get_generation_stats()
                if 'rate_limit_status' in gen_stats:
                    st.divider()
                    st.markdown("### 🚦 API Status")
                    st.json(gen_stats['rate_limit_status'])
        
        with tab4:
            # Error monitoring and debugging
            from ui.error_display import ErrorDisplayManager
            ErrorDisplayManager.show_error_dashboard()


# Create global instance
app = InterviewPrepApp()