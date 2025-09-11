"""
Session Management System for Interview Prep Application.

Handles Streamlit session state, history tracking, and data persistence.
"""

import streamlit as st
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
import os
from pathlib import Path

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


@dataclass
class SessionData:
    """Complete session data structure."""
    session_id: str
    timestamp: datetime
    input_config: Dict[str, Any]
    generation_request: Optional[GenerationRequest] = None
    results: Optional[InterviewResults] = None
    questions: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    cost_breakdown: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    success: bool = False


class SessionManager:
    """
    Manages Streamlit session state and history.
    
    Features:
    - Session state initialization
    - History tracking (last 10 sessions)
    - Data persistence
    - Session clearing and reset
    """
    
    def __init__(self, max_history: int = 10):
        """
        Initialize session manager.
        
        Args:
            max_history: Maximum number of sessions to keep in history
        """
        self.max_history = max_history
        self.history_file = Path("exports") / "session_history.json"
        
        # Ensure exports directory exists
        self.history_file.parent.mkdir(exist_ok=True)
        
        # Initialize session state
        self._initialize_state()
    
    def _initialize_state(self) -> None:
        """Initialize Streamlit session state variables."""
        # Core session variables
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.session_count = 0
            st.session_state.current_session = None
            st.session_state.session_history = []
            st.session_state.api_key = None
            st.session_state.api_key_validated = False
            
            # Load history from file if exists
            self._load_history()
        
        # UI state variables
        if 'generation_in_progress' not in st.session_state:
            st.session_state.generation_in_progress = False
            st.session_state.show_results = False
            st.session_state.show_debug = False
            st.session_state.last_error = None
        
        # Cost tracking
        if 'total_cost' not in st.session_state:
            st.session_state.total_cost = 0.0
            st.session_state.total_tokens = 0
    
    def get_api_key(self) -> Optional[str]:
        """
        Get API key from session state or environment.
        
        Returns:
            API key string or None
        """
        # Check session state first
        if st.session_state.api_key:
            return st.session_state.api_key
        
        # Check environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            st.session_state.api_key = api_key
            return api_key
        
        return None
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set API key in session state.
        
        Args:
            api_key: OpenAI API key
        """
        st.session_state.api_key = api_key
        st.session_state.api_key_validated = False
    
    def mark_api_key_validated(self, valid: bool = True) -> None:
        """
        Mark API key as validated.
        
        Args:
            valid: Whether the API key is valid
        """
        st.session_state.api_key_validated = valid
    
    def create_session(
        self,
        input_config: Dict[str, Any],
        generation_request: GenerationRequest
    ) -> SessionData:
        """
        Create a new session.
        
        Args:
            input_config: Input configuration from UI
            generation_request: Generation request object
            
        Returns:
            New SessionData object
        """
        import uuid
        
        session_id = str(uuid.uuid4())[:8]
        session = SessionData(
            session_id=session_id,
            timestamp=datetime.now(),
            input_config=input_config,
            generation_request=generation_request,
            metadata={
                "session_number": st.session_state.session_count + 1,
                "api_key_used": bool(st.session_state.api_key)
            }
        )
        
        st.session_state.current_session = session
        st.session_state.session_count += 1
        
        return session
    
    def update_session_results(
        self,
        questions: List[str],
        recommendations: List[str],
        cost_breakdown: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update current session with results.
        
        Args:
            questions: Generated questions
            recommendations: Generated recommendations
            cost_breakdown: Cost information
            metadata: Additional metadata
        """
        if not st.session_state.current_session:
            return
        
        session = st.session_state.current_session
        session.questions = questions
        session.recommendations = recommendations
        session.cost_breakdown = cost_breakdown
        session.success = True
        
        if metadata:
            session.metadata.update(metadata)
        
        # Update totals
        if cost_breakdown:
            st.session_state.total_cost += cost_breakdown.get('total_cost', 0)
            if 'total_tokens' in metadata:
                st.session_state.total_tokens += metadata['total_tokens']
        
        # Add to history
        self._add_to_history(session)
    
    def update_session_error(self, error: str) -> None:
        """
        Update current session with error.
        
        Args:
            error: Error message
        """
        if st.session_state.current_session:
            st.session_state.current_session.error = error
            st.session_state.current_session.success = False
            self._add_to_history(st.session_state.current_session)
        
        st.session_state.last_error = error
    
    def _add_to_history(self, session: SessionData) -> None:
        """
        Add session to history.
        
        Args:
            session: Session to add
        """
        # Convert to dict for storage
        session_dict = self._session_to_dict(session)
        
        # Add to history
        st.session_state.session_history.insert(0, session_dict)
        
        # Limit history size
        if len(st.session_state.session_history) > self.max_history:
            st.session_state.session_history = st.session_state.session_history[:self.max_history]
        
        # Save to file
        self._save_history()
    
    def get_session_history(self) -> List[Dict[str, Any]]:
        """
        Get session history.
        
        Returns:
            List of session dictionaries
        """
        return st.session_state.session_history
    
    def get_session_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session by ID.
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            Session dictionary or None
        """
        for session in st.session_state.session_history:
            if session.get('session_id') == session_id:
                return session
        return None
    
    def clear_current_session(self) -> None:
        """Clear current session data."""
        st.session_state.current_session = None
        st.session_state.generation_in_progress = False
        st.session_state.show_results = False
        st.session_state.last_error = None
    
    def clear_history(self) -> None:
        """Clear all session history."""
        st.session_state.session_history = []
        st.session_state.session_count = 0
        st.session_state.total_cost = 0.0
        st.session_state.total_tokens = 0
        self._save_history()
    
    def reset_all(self) -> None:
        """Reset all session state."""
        # Clear specific keys
        keys_to_clear = [
            'initialized', 'session_count', 'current_session',
            'session_history', 'api_key', 'api_key_validated',
            'generation_in_progress', 'show_results', 'show_debug',
            'last_error', 'total_cost', 'total_tokens'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Re-initialize
        self._initialize_state()
    
    def _session_to_dict(self, session: SessionData) -> Dict[str, Any]:
        """
        Convert SessionData to dictionary.
        
        Args:
            session: SessionData object
            
        Returns:
            Dictionary representation
        """
        return {
            'session_id': session.session_id,
            'timestamp': session.timestamp.isoformat(),
            'input_config': session.input_config,
            'questions': session.questions,
            'recommendations': session.recommendations,
            'cost_breakdown': session.cost_breakdown,
            'metadata': session.metadata,
            'error': session.error,
            'success': session.success
        }
    
    def _save_history(self) -> None:
        """Save session history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump({
                    'history': st.session_state.session_history,
                    'total_cost': st.session_state.total_cost,
                    'total_tokens': st.session_state.total_tokens,
                    'session_count': st.session_state.session_count
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def _load_history(self) -> None:
        """Load session history from file."""
        if not self.history_file.exists():
            return
        
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
                st.session_state.session_history = data.get('history', [])
                st.session_state.total_cost = data.get('total_cost', 0.0)
                st.session_state.total_tokens = data.get('total_tokens', 0)
                st.session_state.session_count = data.get('session_count', 0)
        except Exception as e:
            print(f"Error loading history: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get session statistics.
        
        Returns:
            Statistics dictionary
        """
        successful_sessions = sum(
            1 for s in st.session_state.session_history 
            if s.get('success', False)
        )
        
        failed_sessions = len(st.session_state.session_history) - successful_sessions
        
        avg_questions = 0
        if successful_sessions > 0:
            total_questions = sum(
                len(s.get('questions', [])) 
                for s in st.session_state.session_history 
                if s.get('success', False)
            )
            avg_questions = total_questions / successful_sessions
        
        return {
            'total_sessions': st.session_state.session_count,
            'successful_sessions': successful_sessions,
            'failed_sessions': failed_sessions,
            'total_cost': st.session_state.total_cost,
            'total_tokens': st.session_state.total_tokens,
            'average_questions': avg_questions,
            'history_count': len(st.session_state.session_history)
        }


# Create global instance
session_manager = SessionManager()