# InterviewPreparationWithAI
The AI Interview Prep App is an intelligent platform designed to help software engineers prepare for technical job interviews. Powered by advanced AI agents, it generates realistic, role-specific interview questions based on a provided job description (JD).

## Features

- **5 AI Techniques**: Structured Output, Few-Shot, Chain-of-Thought, Zero-Shot, Role-Based
- **4 Interview Types**: Technical, Behavioral, Case Study, Questions for Employer
- **Cost Tracking**: See exactly how much each generation costs
- **Session History**: Track your previous generations
- **Export Options**: Download as Text, Markdown, or JSON
- **Smart Recommendations**: Get preparation tips based on the role

## Prerequisites

1. **Python 3.11+** installed
2. **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

## Installation

1. **Install dependencies** using the modern pyproject.toml:
```bash
# Install the dependencies
Windows (recommended): py -m pip install 
Windows (alternative): python -m pip install 
```

## Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501` (port can change, usually it is 850X)  