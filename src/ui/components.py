"""
Streamlit UI Components for Interview Prep Application.

This module provides reusable UI components for the interview preparation
application, including input forms, display components, and status indicators.
"""

from typing import List, Any, Callable
from dataclasses import dataclass
from datetime import datetime

import streamlit as st
from ..utils.cost import cost_calculator
from ..utils.error_handler import global_error_handler, ErrorContext
from ..ui.error_display import ErrorDisplayManager

from ..models.enums import (
    InterviewType,
    ExperienceLevel,
    PromptTechnique,
    AIModel
)

from ..utils.security import SecurityValidator

@dataclass
class InputConfig:
    """Configuration from input interface."""
    job_description: str
    interview_type: InterviewType
    experience_level: ExperienceLevel
    prompt_technique: PromptTechnique
    ai_model: AIModel
    question_count: int
    temperature: float
    company_type: str | None = None
    focus_areas: str | None = None
    persona: str | None = None


class InputComponents:
    """
    Input configuration interface components.
    
    Provides job description input, interview type selection,
    experience level selection, and advanced settings.
    """
    
    def __init__(self):
        """Initialize input components."""
        self.security = SecurityValidator()
        self.min_description_length = 20
        self.max_description_length = 5000
    
    def render_job_description(self, key: str = "job_description") -> tuple[str, bool, str | None]:
        """
        Render job description text area with validation.
        
        Args:
            key: Unique key for the component
            
        Returns:
            Tuple of (job_description, is_valid, error_message)
        """
        st.markdown("### 📝 Job Description")
        
        # Help text
        help_text = """
        Paste the job description or provide details about:
        - Role title and responsibilities
        - Required skills and technologies
        - Company type and culture
        - Experience requirements
        """
        
        # Text area input
        job_description = st.text_area(
            "Enter job description",
            height=200,
            max_chars=self.max_description_length,
            help=help_text,
            placeholder="e.g., Senior Python Developer at a fintech startup...",
            key=key
        )
        
        # Validation
        is_valid = True
        error_message = None
        
        if job_description:
            # Length validation
            if len(job_description) < self.min_description_length:
                is_valid = False
                error_message = f"Job description must be at least {self.min_description_length} characters"
                _ = st.error(f"❌ {error_message}")
            
            # Security validation
            validation_result = self.security.validate_input(
                job_description,
                field_name="job_description"
            )
            
            if not validation_result.is_valid:
                is_valid = False
                error_message = validation_result.warnings[0] if validation_result.warnings else "Security validation failed"
                _ = st.error(f"🔒 Security: {error_message}")
            
            # Character count
            char_count = len(job_description)
            if is_valid:
                st.success(f"✅ Valid input ({char_count}/{self.max_description_length} characters)")
            else:
                st.info(f"📊 {char_count}/{self.max_description_length} characters")
        
        return job_description, is_valid, error_message
    
    def render_interview_type_selector(self, key: str = "interview_type") -> InterviewType:
        """
        Render interview type selection.
        
        Args:
            key: Unique key for the component
            
        Returns:
            Selected InterviewType
        """
        st.markdown("### 🎯 Interview Type")
        
        # Create columns for better layout
        col1, col2 = st.columns(2)
        
        with col1:
            # Radio button selection
            type_options = {
                "Technical Questions": InterviewType.TECHNICAL,
                "Behavioral Questions": InterviewType.BEHAVIORAL,
                "Case Studies": InterviewType.CASE_STUDY,
                "Questions for Employer": InterviewType.REVERSE
            }
            
            selected_label = st.radio(
                "Select interview type",
                options=list(type_options.keys()),
                key=key,
                help="Choose the type of interview questions you want to prepare for"
            )
            
            selected_type = type_options[selected_label]
        
        with col2:
            # Display description for selected type
            descriptions = {
                InterviewType.TECHNICAL: "🔧 Technical skills, coding, system design, algorithms",
                InterviewType.BEHAVIORAL: "💭 Soft skills, teamwork, leadership, problem-solving",
                InterviewType.CASE_STUDY: "📊 Business problems, analytical thinking, strategy",
                InterviewType.REVERSE: "🤔 Questions to ask the interviewer about the role/company"
            }
            
            st.info(descriptions[selected_type])
        
        return selected_type
    
    def render_experience_level_selector(self, key: str = "experience_level") -> ExperienceLevel:
        """
        Render experience level selection.
        
        Args:
            key: Unique key for the component
            
        Returns:
            Selected ExperienceLevel
        """
        st.markdown("### 📈 Experience Level")
        
        # Slider for visual selection
        level_mapping = {
            0: ExperienceLevel.JUNIOR,
            1: ExperienceLevel.MID,
            2: ExperienceLevel.SENIOR,
            3: ExperienceLevel.LEAD
        }
        
        level_labels = {
            0: "Junior (1-2 years)",
            1: "Mid-level (3-5 years)",
            2: "Senior (5+ years)",
            3: "Lead/Principal"
        }
        
        selected_index = st.select_slider(
            "Select your experience level",
            options=list(level_labels.keys()),
            format_func=lambda x: level_labels[x],
            value=1,  # Default to Mid-level
            key=key,
            help="This helps tailor question difficulty and complexity"
        )
        
        selected_level = level_mapping[selected_index]
        
        # Display level-specific tips
        tips = {
            ExperienceLevel.JUNIOR: "💡 Focus on fundamentals, learning ability, and enthusiasm",
            ExperienceLevel.MID: "💡 Demonstrate solid technical skills and project experience",
            ExperienceLevel.SENIOR: "💡 Showcase architecture decisions and mentoring experience",
            ExperienceLevel.LEAD: "💡 Emphasize leadership, strategy, and cross-functional collaboration"
        }
        
        st.info(tips[selected_level])
        
        return selected_level
    
    def render_advanced_settings(
        self,
        key_prefix: str = "advanced"
    ) -> dict[str, Any]:
        """
        Render advanced settings expander.
        
        Args:
            key_prefix: Prefix for component keys
            
        Returns:
            Dictionary of advanced settings
        """
        with st.expander("⚙️ Advanced Settings", expanded=False):
            st.markdown("### 🤖 AI Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Model selection
                model_options = {
                    "GPT-5 (Recommended)": AIModel.GPT_5,
                    "GPT-4o": AIModel.GPT_4O,
                    "GPT-4o Mini (Faster/Cheaper)": AIModel.GPT_4O_MINI
                }
                
                selected_model_label = st.selectbox(
                    "AI Model",
                    options=list(model_options.keys()),
                    index=0,
                    key=f"{key_prefix}_model",
                    help="Choose the AI model for generation"
                )
                
                ai_model = model_options[selected_model_label]
                
                # Display model info
                model_info = {
                    AIModel.GPT_5: "Latest model with superior performance",
                    AIModel.GPT_4O: "Balanced performance and cost",
                    AIModel.GPT_4O_MINI: "Faster and more cost-effective"
                }
                st.caption(f"ℹ️ {model_info[ai_model]}")
                
                # Prompt technique selection
                technique_options = {
                    "Structured Output": PromptTechnique.STRUCTURED_OUTPUT,
                    "Few-Shot Learning": PromptTechnique.FEW_SHOT,
                    "Chain-of-Thought": PromptTechnique.CHAIN_OF_THOUGHT,
                    "Zero-Shot": PromptTechnique.ZERO_SHOT,
                    "Role-Based": PromptTechnique.ROLE_BASED
                }
                
                selected_technique_label = st.selectbox(
                    "Prompt Technique",
                    options=list(technique_options.keys()),
                    index=0,
                    key=f"{key_prefix}_technique",
                    help="Choose the prompt engineering technique"
                )
                
                prompt_technique = technique_options[selected_technique_label]
            
            with col2:
                # Number of questions
                question_count = st.number_input(
                    "Number of Questions",
                    min_value=1,
                    max_value=20,
                    value=5,
                    step=1,
                    key=f"{key_prefix}_count",
                    help="How many questions to generate"
                )
                
                # Temperature (creativity)
                temperature = st.slider(
                    "Temperature (Creativity)",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.7,
                    step=0.1,
                    key=f"{key_prefix}_temperature",
                    help="Higher values = more creative, lower = more focused"
                )
                
                # Display temperature guidance
                if temperature < 0.3:
                    st.caption("🎯 Very focused and deterministic")
                elif temperature < 0.7:
                    st.caption("⚖️ Balanced creativity")
                else:
                    st.caption("🎨 High creativity and variation")
            
            st.markdown("### 🏢 Additional Context")
            
            col3, col4 = st.columns(2)
            
            with col3:
                # Company type
                company_types = [
                    "Startup",
                    "Scale-up",
                    "Enterprise",
                    "FAANG",
                    "Consulting",
                    "Agency",
                    "Non-profit",
                    "Government"
                ]
                
                company_type = st.selectbox(
                    "Company Type (Optional)",
                    options=["Not specified"] + company_types,
                    index=0,
                    key=f"{key_prefix}_company",
                    help="Helps tailor questions to company culture"
                )
                
                if company_type == "Not specified":
                    company_type = None
            
            with col4:
                # Focus areas
                focus_areas = st.text_input(
                    "Focus Areas (Optional)",
                    placeholder="e.g., microservices, machine learning, frontend",
                    key=f"{key_prefix}_focus",
                    help="Specific topics or skills to emphasize"
                )
                
                if not focus_areas:
                    focus_areas = None
            
            # Role-based specific settings
            if prompt_technique == PromptTechnique.ROLE_BASED:
                st.markdown("### 🎭 Interviewer Persona")
                
                persona_options = {
                    "Neutral": "neutral",
                    "Friendly": "friendly",
                    "Strict": "strict"
                }
                
                selected_persona_label = st.selectbox(
                    "Select Interviewer Persona",
                    options=list(persona_options.keys()),
                    index=0,
                    key=f"{key_prefix}_persona",
                    help="Choose the interviewer's personality style"
                )
                
                persona = persona_options[selected_persona_label]
                
                persona_descriptions = {
                    "neutral": "📊 Professional and balanced approach",
                    "friendly": "😊 Warm and encouraging style",
                    "strict": "🎯 Direct and challenging questions"
                }
                
                st.info(persona_descriptions[persona])
            else:
                persona = None
            
            # Cost estimation
            st.markdown("### 💰 Cost Estimation")
            
            # Get pricing info
            pricing = cost_calculator.get_model_pricing_info(ai_model.value)
            
            if pricing:
                # Estimate tokens (rough approximation)
                estimated_input_tokens = len(focus_areas or "") * 2 if focus_areas else 500
                estimated_output_tokens = question_count * 100  # ~100 tokens per question
                
                estimated_cost = cost_calculator.calculate_cost(
                    ai_model.value,
                    estimated_input_tokens,
                    estimated_output_tokens
                )
                
                st.info(f"""
                **Estimated Cost**: ${estimated_cost['total_cost']:.4f}
                - Input: ~{estimated_input_tokens} tokens (${estimated_cost['input_cost']:.4f})
                - Output: ~{estimated_output_tokens} tokens (${estimated_cost['output_cost']:.4f})
                """)
            
            return {
                "ai_model": ai_model,
                "prompt_technique": prompt_technique,
                "question_count": question_count,
                "temperature": temperature,
                "company_type": company_type,
                "focus_areas": focus_areas,
                "persona": persona
            }
    
    def get_input_config(self) -> InputConfig | None:
        """
        Get complete input configuration from all components.
        
        Returns:
            InputConfig object or None if validation fails
        """
        # Get job description
        job_desc, is_valid, _ = self.render_job_description()
        
        if not job_desc:
            st.warning("⚠️ Please enter a job description to continue")
            return None
        
        if not is_valid:
            return None
        
        # Get interview type and experience level
        interview_type = self.render_interview_type_selector()
        experience_level = self.render_experience_level_selector()
        
        # Get advanced settings
        advanced = self.render_advanced_settings()
        
        return InputConfig(
            job_description=job_desc,
            interview_type=interview_type,
            experience_level=experience_level,
            prompt_technique=advanced["prompt_technique"],
            ai_model=advanced["ai_model"],
            question_count=advanced["question_count"],
            temperature=advanced["temperature"],
            company_type=advanced["company_type"],
            focus_areas=advanced["focus_areas"],
            persona=advanced["persona"]
        )
    
    def render_input_summary(self, config: InputConfig) -> None:
        """
        Render a summary of the input configuration.
        
        Args:
            config: InputConfig object to summarize
        """
        st.markdown("### 📋 Configuration Summary")
        
        summary = f"""
        - **Interview Type**: {config.interview_type.value}
        - **Experience Level**: {config.experience_level.value}
        - **Questions**: {config.question_count}
        - **AI Model**: {config.ai_model.value}
        - **Technique**: {config.prompt_technique.value}
        """
        
        if config.company_type:
            summary += f"\n- **Company**: {config.company_type}"
        if config.focus_areas:
            summary += f"\n- **Focus**: {config.focus_areas}"
        
        st.info(summary)


class ResultsDisplay:
    """
    Results display interface components.
    
    Provides question display, cost metrics, recommendations,
    and session metadata display.
    """
    
    def __init__(self):
        """Initialize results display components."""
        pass
    
    def render_questions(
        self,
        questions: List[str],
        metadata: List[dict[str, Any]] | None = None
    ) -> None:
        """
        Render interview questions with formatting.
        
        Args:
            questions: List of question strings
            metadata: Optional metadata for each question
        """
        st.markdown("### 📝 Interview Questions")
        
        if not questions:
            st.warning("No questions generated")
            return
        
        # Display questions in an organized format
        for i, question in enumerate(questions, 1):
            # Create expandable section for each question
            with st.expander(f"Question {i}", expanded=True):
                # Display the question
                st.markdown(f"**{question}**")
                
                # Add metadata if available
                if metadata and isinstance(metadata, list) and i <= len(metadata):
                    q_meta = metadata[i-1]
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if "difficulty" in q_meta:
                            difficulty_emoji = {
                                "easy": "🟢",
                                "medium": "🟡",
                                "hard": "🔴"
                            }
                            emoji = difficulty_emoji.get(q_meta["difficulty"], "⚪")
                            st.caption(f"{emoji} {q_meta['difficulty'].title()}")
                    
                    with col2:
                        if "category" in q_meta:
                            st.caption(f"📁 {q_meta['category'].replace('_', ' ').title()}")
                    
                    with col3:
                        if "time_estimate" in q_meta:
                            st.caption(f"⏱️ {q_meta['time_estimate']} min")
                    
                    # Display hints if available
                    if "hints" in q_meta and q_meta["hints"]:
                        st.markdown("**💡 Hints:**")
                        for hint in q_meta["hints"]:
                            st.caption(f"• {hint}")
                    
                    # Display follow-ups if available
                    if "follow_ups" in q_meta and q_meta["follow_ups"]:
                        st.markdown("**🔄 Potential Follow-ups:**")
                        for follow_up in q_meta["follow_ups"]:
                            st.caption(f"• {follow_up}")
        
        # Add copy all button
        all_questions = "\n\n".join([f"{i}. {q}" for i, q in enumerate(questions, 1)])
        st.markdown("### 📋 Copy All Questions")
        st.code(all_questions, language=None)
    
    def render_cost_metrics(
        self,
        cost_breakdown: dict[str, float],
        token_counts: dict[str, int] | None = None
    ) -> None:
        """
        Render cost metrics display.
        
        Args:
            cost_breakdown: Cost breakdown dictionary
            token_counts: Optional token count information
        """
        st.markdown("### 💰 Cost Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Input Cost",
                value=f"${cost_breakdown.get('input_cost', 0):.4f}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Output Cost",
                value=f"${cost_breakdown.get('output_cost', 0):.4f}",
                delta=None
            )
        
        with col3:
            st.metric(
                label="Total Cost",
                value=f"${cost_breakdown.get('total_cost', 0):.4f}",
                delta=None
            )
        
        with col4:
            if token_counts:
                total_tokens = token_counts.get('total_tokens', 0)
                st.metric(
                    label="Total Tokens",
                    value=f"{total_tokens:,}",
                    delta=None
                )
        
        # Show cumulative stats if available
        cumulative_stats = cost_calculator.get_cumulative_stats()
        if cumulative_stats and cumulative_stats.get("session_count", 0) > 0:
            with st.expander("📊 Session Statistics", expanded=False):
                st.markdown(f"""
                - **Total Sessions**: {cumulative_stats['session_count']}
                - **Total Cost**: ${cumulative_stats['total_cost']:.4f}
                - **Average Cost**: ${cumulative_stats['average_cost_per_session']:.4f}
                - **Total Tokens**: {(cumulative_stats['total_input_tokens'] + cumulative_stats['total_output_tokens']):,}
                """)
    
    def render_recommendations(
        self,
        recommendations: List[str]
    ) -> None:
        """
        Render preparation recommendations.
        
        Args:
            recommendations: List of recommendation strings
        """
        if not recommendations:
            return
        
        st.markdown("### 💡 Preparation Recommendations")
        
        # Display recommendations in a nice format
        for i, rec in enumerate(recommendations, 1):
            st.info(f"**{i}.** {rec}")
        
        # Add actionable tips
        st.markdown("### 🎯 Quick Action Items")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Before the Interview:**
            - ✅ Review all questions and prepare answers
            - ✅ Practice speaking your answers out loud
            - ✅ Prepare specific examples from experience
            - ✅ Research the company and role
            """)
        
        with col2:
            st.markdown("""
            **During the Interview:**
            - 🎯 Use the STAR method for behavioral questions
            - 🎯 Think out loud for technical problems
            - 🎯 Ask clarifying questions when needed
            - 🎯 Have your own questions ready
            """)
    
    def render_session_metadata(
        self,
        session_data: dict[str, Any]
    ) -> None:
        """
        Render session metadata and information.
        
        Args:
            session_data: Session metadata dictionary
        """
        with st.expander("📊 Generation Details", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Configuration:**")
                st.caption(f"• Model: {session_data.get('model', 'N/A')}")
                st.caption(f"• Technique: {session_data.get('technique', 'N/A')}")
                st.caption(f"• Temperature: {session_data.get('temperature', 'N/A')}")
                st.caption(f"• Questions: {session_data.get('question_count', 'N/A')}")
            
            with col2:
                st.markdown("**Context:**")
                st.caption(f"• Interview Type: {session_data.get('interview_type', 'N/A')}")
                st.caption(f"• Experience: {session_data.get('experience_level', 'N/A')}")
                st.caption(f"• Company: {session_data.get('company_type', 'N/A') or 'Not specified'}")
                st.caption(f"• Timestamp: {session_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))}")
            
            # Show parsing strategy if available
            if "parsing_strategy" in session_data:
                st.markdown("**Technical Details:**")
                st.caption(f"• Parsing Strategy: {session_data['parsing_strategy']}")
                st.caption(f"• Success: {'✅' if session_data.get('success', False) else '⚠️'}")
    
    def render_export_options(
        self,
        questions: List[str],
        recommendations: List[str],
        session_data: dict[str, Any]
    ) -> None:
        """
        Render export options for results.
        
        Args:
            questions: List of questions
            recommendations: List of recommendations
            session_data: Session metadata
        """
        st.markdown("### 💾 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Export as text
            export_text = self._format_as_text(questions, recommendations, session_data)
            st.download_button(
                label="📄 Download as Text",
                data=export_text,
                file_name=f"interview_prep_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )
        
        with col2:
            # Export as markdown
            export_md = self._format_as_markdown(questions, recommendations, session_data)
            st.download_button(
                label="📝 Download as Markdown",
                data=export_md,
                file_name=f"interview_prep_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown"
            )
        
        with col3:
            # Export as JSON
            import json
            export_json = json.dumps({
                "questions": questions,
                "recommendations": recommendations,
                "metadata": session_data
            }, indent=2)
            st.download_button(
                label="🔧 Download as JSON",
                data=export_json,
                file_name=f"interview_prep_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )
    
    def _format_as_text(
        self,
        questions: List[str],
        recommendations: List[str],
        session_data: dict[str, Any]
    ) -> str:
        """Format results as plain text."""
        text = f"""INTERVIEW PREPARATION QUESTIONS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Type: {session_data.get('interview_type', 'N/A')}
Level: {session_data.get('experience_level', 'N/A')}

QUESTIONS:
{chr(10).join([f'{i}. {q}' for i, q in enumerate(questions, 1)])}

RECOMMENDATIONS:
{chr(10).join([f'• {r}' for r in recommendations])}

---
Generated with AI Interview Prep
Model: {session_data.get('model', 'N/A')}
Technique: {session_data.get('technique', 'N/A')}
"""
        return text
    
    def _format_as_markdown(
        self,
        questions: List[str],
        recommendations: List[str],
        session_data: dict[str, Any]
    ) -> str:
        """Format results as markdown."""
        md = f"""# Interview Preparation Questions

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Type:** {session_data.get('interview_type', 'N/A')}  
**Level:** {session_data.get('experience_level', 'N/A')}

## Questions

{chr(10).join([f'{i}. {q}' for i, q in enumerate(questions, 1)])}

## Preparation Recommendations

{chr(10).join([f'- {r}' for r in recommendations])}

---

*Generated with AI Interview Prep*  
*Model: {session_data.get('model', 'N/A')}*  
*Technique: {session_data.get('technique', 'N/A')}*
"""
        return md


class ProgressIndicators:
    """
    Progress and status indicator components.
    
    Provides progress bars, loading spinners, notifications,
    and debug information display.
    """
    
    def __init__(self):
        """Initialize progress indicator components."""
        self.status_messages = {
            "initializing": "🚀 Initializing AI generator...",
            "validating": "🔍 Validating input...",
            "generating": "🤖 Generating interview questions...",
            "parsing": "📝 Processing response...",
            "formatting": "✨ Formatting results...",
            "complete": "✅ Generation complete!",
            "error": "❌ An error occurred",
            "rate_limited": "⏱️ Rate limit reached, please wait...",
            "retrying": "🔄 Retrying request..."
        }
    
    def show_progress_bar(
        self,
        progress: float,
        status: str,
        details: str | None = None
    ) -> None:
        """
        Display progress bar with status message.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            status: Status key from status_messages
            details: Optional additional details
        """
        # Get status message
        message = self.status_messages.get(status, status)
        
        # Display progress bar
        progress_bar = st.progress(progress)
        
        # Display status message
        col1, col2 = st.columns([3, 1])
        with col1:
            _ = st.markdown(f"**{message}**")
            if details:
                _ = st.caption(details)
        
        with col2:
            _ = st.markdown(f"**{int(progress * 100)}%**")
        
    
    def show_spinner(
        self,
        message: str = "Processing...",
        key: str | None = None
    ) -> Any:
        """
        Display loading spinner.
        
        Args:
            message: Loading message
            key: Optional unique key
            
        Returns:
            Spinner context manager
        """
        return st.spinner(message)
    
    def show_generation_steps(self) -> dict[str, Any]:
        """
        Display step-by-step generation progress.
        
        Returns:
            Dictionary of step placeholders
        """
        st.markdown("### 🔄 Generation Progress")
        
        # Create placeholders for each step
        steps = {
            "validation": st.empty(),
            "prompt": st.empty(),
            "api_call": st.empty(),
            "parsing": st.empty(),
            "formatting": st.empty()
        }
        
        # Initialize steps
        steps["validation"].info("⏳ Input validation pending...")
        steps["prompt"].info("⏳ Prompt preparation pending...")
        steps["api_call"].info("⏳ AI generation pending...")
        steps["parsing"].info("⏳ Response parsing pending...")
        steps["formatting"].info("⏳ Result formatting pending...")
        
        return steps
    
    def update_step(
        self,
        steps: dict[str, Any],
        step_name: str,
        status: str,
        message: str,
        details: str | None = None
    ) -> None:
        """
        Update a specific generation step.
        
        Args:
            steps: Dictionary of step placeholders
            step_name: Name of the step to update
            status: Status ('pending', 'running', 'success', 'error')
            message: Status message
            details: Optional additional details
        """
        if step_name not in steps:
            return
        
        # Determine display based on status
        if status == "pending":
            steps[step_name].info(f"⏳ {message}")
        elif status == "running":
            steps[step_name].warning(f"🔄 {message}")
        elif status == "success":
            content = f"✅ {message}"
            if details:
                content += f"\n\n*{details}*"
            steps[step_name].success(content)
        elif status == "error":
            content = f"❌ {message}"
            if details:
                content += f"\n\n*{details}*"
            steps[step_name].error(content)
    
    def show_notification(
        self,
        message: str,
        type: str = "info",
        icon: str | None = None
    ) -> None:
        """
        Display notification message.
        
        Args:
            message: Notification message
            type: Type ('success', 'info', 'warning', 'error')
            icon: Optional emoji icon
        """
        if icon:
            message = f"{icon} {message}"
        
        if type == "success":
            st.success(message)
        elif type == "warning":
            st.warning(message)
        elif type == "error":
            st.error(message)
        else:
            st.info(message)
    
    def show_debug_info(
        self,
        data: dict[str, Any],
        title: str = "Debug Information"
    ) -> None:
        """
        Display debug information in expandable section.
        
        Args:
            data: Debug data dictionary
            title: Section title
        """
        with st.expander(f"🐛 {title}", expanded=False):
            import json
            
            # Format data nicely
            formatted = json.dumps(data, indent=2, default=str)
            st.code(formatted, language="json")
            
            # Add copy button and error statistics
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📋 Copy Debug Info",
                    data=formatted,
                    file_name="debug_info.json",
                    mime="application/json"
                )
            with col2:
                if st.button("📊 Show Error Statistics"):
                    from ..ui.error_display import ErrorDisplayManager
                    ErrorDisplayManager.show_error_dashboard()
    
    def show_rate_limit_status(
        self,
        remaining_calls: int,
        reset_time: float,
        max_calls: int = 100
    ) -> None:
        """
        Display rate limit status.
        
        Args:
            remaining_calls: Number of remaining API calls
            reset_time: Time until reset in seconds
            max_calls: Maximum calls allowed
        """
        st.markdown("### 🚦 Rate Limit Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Progress bar for remaining calls
            progress = remaining_calls / max_calls
            st.metric(
                label="Remaining Calls",
                value=f"{remaining_calls}/{max_calls}",
                delta=None
            )
            st.progress(progress)
        
        with col2:
            # Time until reset
            if reset_time > 0:
                minutes = int(reset_time // 60)
                seconds = int(reset_time % 60)
                st.metric(
                    label="Reset In",
                    value=f"{minutes}m {seconds}s",
                    delta=None
                )
            else:
                st.metric(
                    label="Reset In",
                    value="Ready",
                    delta=None
                )
        
        with col3:
            # Status indicator
            if remaining_calls > max_calls * 0.5:
                st.success("✅ Healthy")
            elif remaining_calls > max_calls * 0.2:
                st.warning("⚠️ Limited")
            else:
                st.error("❌ Critical")
    
    def show_retry_status(
        self,
        attempt: int,
        max_attempts: int = 3,
        error: str | None = None
    ) -> None:
        """
        Display retry attempt status.
        
        Args:
            attempt: Current attempt number
            max_attempts: Maximum attempts allowed
            error: Optional error message from last attempt
        """
        st.markdown(f"### 🔄 Retry Attempt {attempt}/{max_attempts}")
        
        # Progress bar
        progress = attempt / max_attempts
        st.progress(progress)
        
        # Error from last attempt
        if error:
            st.warning(f"Previous attempt failed: {error}")
        
        # Remaining attempts
        remaining = max_attempts - attempt
        if remaining > 0:
            st.info(f"📊 {remaining} attempts remaining")
        else:
            st.error("❌ No attempts remaining")
    
    def _get_error_suggestions(self, error: Exception) -> List[str]:
        """
        Get suggestions based on error type.
        
        Args:
            error: Exception object
            
        Returns:
            List of suggestion strings
        """
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        suggestions = []
        
        # API key errors
        if "api" in error_msg and "key" in error_msg:
            suggestions.append("Check that your OpenAI API key is correctly set")
            suggestions.append("Verify the API key has sufficient credits")
            suggestions.append("Ensure the API key has the necessary permissions")
        
        # Rate limit errors
        elif "rate" in error_msg and "limit" in error_msg:
            suggestions.append("Wait a few minutes before trying again")
            suggestions.append("Consider using a lower number of questions")
            suggestions.append("Upgrade your API plan for higher limits")
        
        # Network errors
        elif "connection" in error_msg or "network" in error_msg:
            suggestions.append("Check your internet connection")
            suggestions.append("Try again in a few moments")
            suggestions.append("Verify firewall settings aren't blocking the API")
        
        # Input validation errors
        elif "validation" in error_msg or "invalid" in error_msg:
            suggestions.append("Review your input for any special characters")
            suggestions.append("Ensure the job description is detailed enough")
            suggestions.append("Try simplifying your input")
        
        # Generic suggestions
        else:
            suggestions.append("Try refreshing the page")
            suggestions.append("Simplify your input and try again")
            suggestions.append("Contact support if the issue persists")
        
        return suggestions
    
    def create_status_container(self) -> Any:
        """
        Create a container for dynamic status updates.
        
        Returns:
            Streamlit container object
        """
        container = st.container()
        with container:
            st.markdown("### 📊 Status")
            status_placeholder = st.empty()
            progress_placeholder = st.empty()
            details_placeholder = st.empty()
        
        return {
            "container": container,
            "status": status_placeholder,
            "progress": progress_placeholder,
            "details": details_placeholder
        }
    
    def update_status_container(
        self,
        container: dict[str, Any],
        status: str,
        progress: float = 0.0,
        details: str | None = None
    ) -> None:
        """
        Update status container with new information.
        
        Args:
            container: Container dictionary from create_status_container
            status: Status message
            progress: Progress value (0.0 to 1.0)
            details: Optional details message
        """
        container["status"].markdown(f"**{status}**")
        container["progress"].progress(progress)
        if details:
            container["details"].caption(details)
        else:
            container["details"].empty()
    
    def show_error_details(
        self,
        error: Exception,
        show_traceback: bool = False,
        context: str | None = None
    ) -> None:
        """
        Display error details with optional troubleshooting information.
        
        Args:
            error: The exception that occurred
            show_traceback: Whether to show the full traceback
            context: Optional context description
        """
        # Handle the error through the error handler
        error_context = ErrorContext(
            operation=context or "ui_operation",
            additional_info={"ui_component": "progress_indicators"}
        )
        
        recovery_successful, user_message, recovery_result = global_error_handler.handle_error(
            error, error_context, attempt_recovery=False
        )
        
        # Get the error record for display
        if global_error_handler.error_history:
            error_record = global_error_handler.error_history[-1]
            ErrorDisplayManager.show_error_message(
                error_record,
                show_details=show_traceback,
                show_recovery_options=True
            )
        else:
            # Fallback display
            st.error(f"An error occurred: {str(error)}")
            
        # Show debug information if requested
        if show_traceback:
            self.show_debug_info({
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "timestamp": datetime.now().isoformat()
            })
    
    
    def show_error_recovery_options(
        self,
        error_type: str,
        recovery_action: Callable[[], None] | None = None
    ) -> None:
        """
        Show error recovery options with action buttons.
        
        Args:
            error_type: Type of error that occurred
            recovery_action: Optional function to call for recovery
        """
        st.markdown("### 🛠️ Recovery Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Retry Operation"):
                if recovery_action:
                    try:
                        recovery_action()
                        st.success("✅ Recovery attempt initiated")
                    except Exception as e:
                        st.error(f"❌ Recovery failed: {str(e)}")
                else:
                    st.info("Please try the operation again manually")
        
        with col2:
            if st.button("🔧 Reset Session"):
                # Clear any cached data
                for key in list(st.session_state.keys()):
                    if isinstance(key, str) and key.startswith(('generation_', 'current_', 'error_')):
                        del st.session_state[key]
                st.success("✅ Session reset")
                st.rerun()
        
        with col3:
            if st.button("📞 Get Help"):
                self._show_help_information(error_type)
    
    def _show_help_information(self, error_type: str) -> None:
        """Show contextual help information based on error type."""
        help_messages = {
            "api_error": """
            **API Error Help:**
            - Check your internet connection
            - Verify your OpenAI API key is valid
            - Ensure you have sufficient API credits
            - Try again in a moment
            """,
            "rate_limit": """
            **Rate Limit Help:**
            - Wait for the rate limit to reset
            - Consider upgrading your API plan
            - Reduce the number of requests
            """,
            "validation_error": """
            **Validation Error Help:**
            - Check your input meets requirements
            - Ensure text is within length limits
            - Remove any special characters
            - Try rephrasing your input
            """,
            "network_error": """
            **Network Error Help:**
            - Check your internet connection
            - Try refreshing the page
            - Disable VPN if using one
            - Check firewall settings
            """
        }
        
        help_text = help_messages.get(
            error_type, 
            "Contact support if the issue persists."
        )
        
        st.info(help_text)
    
    def show_operation_status(
        self,
        operation: str,
        status: str,
        progress: float = 0.0,
        details: str | None = None,
        error: Exception | None = None
    ) -> None:
        """
        Show comprehensive operation status with error handling.
        
        Args:
            operation: Name of the operation
            status: Current status
            progress: Progress value (0.0 to 1.0)
            details: Additional details
            error: Optional error that occurred
        """
        st.markdown(f"### {operation}")
        
        if error:
            # Show error state
            st.error(f"❌ {status}")
            self.show_error_details(error, context=operation)
        else:
            # Show normal progress
            if progress > 0:
                st.progress(progress)
            
            if status in self.status_messages:
                st.info(self.status_messages[status])
            else:
                st.info(status)
            
            if details:
                st.caption(details)


# Create global instances
input_components = InputComponents()
results_display = ResultsDisplay()
progress_indicators = ProgressIndicators()