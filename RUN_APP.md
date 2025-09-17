# 🚀 Quick Start Guide - AI Interview Prep

## Prerequisites

1. **Python 3.11+** installed
2. **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

## Installation

1. **Install dependencies** using the modern pyproject.toml:
```bash
# Install the package in editable mode with dependencies
pip install -e src/

# Or if you want development dependencies too:
pip install -e "src/[dev]"
```

2. **Set up your API key** (choose one):

   **Option A - Environment File (Recommended)**:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your API key:
   # OPENAI_API_KEY=sk-your-actual-key-here
   ```

   **Option B - Environment Variable**:
   ```bash
   # Windows
   set OPENAI_API_KEY=sk-your-actual-key-here
   
   # Mac/Linux
   export OPENAI_API_KEY=sk-your-actual-key-here
   ```

   **Option C - Enter in App**:
   - Just run the app and enter your key in the UI

## Running the Application

```bash
# Standard mode
streamlit run app.py

# Debug mode (shows more details)
streamlit run app.py -- --debug
```

The app will open in your browser at `http://localhost:8501`

## First Time Use

1. **Enter API Key** (if not set via environment)
2. **Enter Job Description** - Paste or type the job posting
3. **Select Interview Type** - Technical, Behavioral, Case Study, or Reverse
4. **Choose Experience Level** - Junior to Lead/Principal
5. **Click "Generate Interview Questions"**
6. **View Results** - Questions, recommendations, and export options

## Features

- **5 AI Techniques**: Structured Output, Few-Shot, Chain-of-Thought, Zero-Shot, Role-Based
- **4 Interview Types**: Technical, Behavioral, Case Study, Questions for Employer
- **Cost Tracking**: See exactly how much each generation costs
- **Session History**: Track your previous generations
- **Export Options**: Download as Text, Markdown, or JSON
- **Smart Recommendations**: Get preparation tips based on the role

## Troubleshooting

If you see import errors:
```bash
# Make sure you're in the project root directory
cd InterviewPreparationWithAI_Kiro

# Check Python version (should be 3.11+)
python --version

# Reinstall dependencies using pyproject.toml
pip install -e src/
```

If the app doesn't start:
- Check that port 8501 is not in use
- Try: `streamlit run main.py --server.port 8502`

## Cost Estimates

- Each generation typically costs $0.01-0.05 with GPT-4o
- Generating 5 questions uses ~500-1000 tokens
- You can see exact costs in the Results tab

## Support

- Check `HANDOFF_SUMMARY.md` for technical details
- Review `.kiro/specs/` for complete documentation
- Enable debug mode for detailed error information