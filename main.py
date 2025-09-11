"""
AI Interview Preparation Assistant - Main Entry Point

Run this file to start the Streamlit application:
    streamlit run main.py

Or with debug mode:
    streamlit run main.py -- --debug
"""

import sys
import os
from pathlib import Path

# Add src directory to path BEFORE any other imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import streamlit as st
from app import app


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="AI Interview Prep",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/yourusername/interview-prep',
            'Report a bug': 'https://github.com/yourusername/interview-prep/issues',
            'About': """
            # AI Interview Prep Assistant
            
            Generate personalized interview questions using AI.
            
            Built with Streamlit and OpenAI GPT-4.
            """
        }
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    /* Main content area */
    .main {
        padding-top: 1rem;
    }
    
    /* Improve button styling */
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
        height: 3rem;
        font-weight: 500;
    }
    
    /* Primary button enhancement */
    .stButton > button[kind="primary"] {
        background-color: #FF4B4B;
        color: white;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background-color: rgba(28, 131, 225, 0.1);
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid rgba(28, 131, 225, 0.2);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: rgba(28, 131, 225, 0.05);
        border-radius: 0.5rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Success/Error message styling */
    .stAlert {
        border-radius: 0.5rem;
    }
    
    /* Code block styling */
    .stCodeBlock {
        border-radius: 0.5rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Progress bar enhancement */
    .stProgress > div > div > div > div {
        background-color: #FF4B4B;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check for debug mode
    if "--debug" in sys.argv:
        os.environ["DEBUG"] = "true"
    
    # Run the application
    try:
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
        
        If the issue persists, please report it on GitHub.
        """)


if __name__ == "__main__":
    main()