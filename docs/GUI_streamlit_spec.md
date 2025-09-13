# TECHNICAL SPECIFICATION: Interview Preparation Web Application in Python Streamlit

## PROJECT OVERVIEW

Create an exact replica of the provided HTML interface using Python Streamlit. This is a single-page web application for AI-powered interview preparation with two main modes: question generation and mock interviews.

## LAYOUT ARCHITECTURE

### Main Structure

```
- Use st.sidebar for left panel (30% width)
- Main content area (70% width) with three sections:
  1. Header section
  2. Chat area (scrollable container)
  3. Control panel (buttons + statistics)
```

## SIDEBAR COMPONENTS (Top to Bottom)

### 1. Header Section

```python
st.title("Interview Prep")
st.caption("Подготовка к собеседованию с ИИ")
```

### 2. Form Components

```python
# Job Description
job_desc = st.text_area(
    "Описание вакансии",
    placeholder="Вставьте описание вакансии или укажите позицию...",
    height=100
)

# Experience Level
seniority = st.selectbox(
    "Уровень опыта",
    options=["Junior (1-2 years)", "Mid-level (3-5 years)", "Senior (5+ years)", "Lead/Principal"],
    index=1
)

# Question Type
question_type = st.radio(
    "Тип вопросов",
    options=["Technical", "Behavioural"],
    index=0
)

# Session Mode
session_mode = st.radio(
    "Режим сессии",
    options=["Generate questions", "Mock Interview"],
    index=0
)

# Questions Number (conditional display)
if session_mode == "Generate questions":
    questions_num = st.selectbox(
        "Количество вопросов",
        options=[5, 10, 15, 20],
        index=0
    )
```

### 3. Advanced Settings (Expandable)

```python
with st.expander("Продвинутые настройки"):
    prompt_tech = st.selectbox(
        "Техника промптинга",
        options=["Zero Shot", "Few Shot", "Chain of Thought", "Role Based", "Structured Output"],
        index=1
    )
    
    temperature = st.slider(
        "Temperature",
        min_value=0.1,
        max_value=0.9,
        value=0.7,
        step=0.1
    )
    
    top_p = st.slider(
        "Top-P",
        min_value=0.1,
        max_value=0.9,
        value=0.9,
        step=0.1
    )
    
    max_tokens = st.number_input(
        "Max Tokens",
        min_value=100,
        max_value=4000,
        value=2000,
        step=100
    )
```

## MAIN CONTENT AREA

### 1. Header Section

```python
st.header("Диалог с Ассистентом")
st.caption("Область для генерации вопросов и проведения mock интервью")
```

### 2. Chat Area

```python
# Create chat container with fixed height
chat_container = st.container(height=400)
with chat_container:
    # Initialize with welcome message
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = [
            "Добро пожаловать! Настройте параметры слева и нажмите кнопку для начала."
        ]
    
    # Display messages
    for message in st.session_state.chat_messages:
        st.markdown(f"📝 {message}")
```

### 3. Control Panel

```python
# Create columns for buttons and stats
col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    # Dynamic button text based on mode
    button_text = "Generate Questions" if session_mode == "Generate questions" else "Start Mock Interview"
    main_button = st.button(button_text, type="primary")

with col2:
    # Next question button (only in mock mode)
    if session_mode == "Mock Interview":
        next_button = st.button("Next Question")

with col3:
    # Statistics (only in mock mode)
    if session_mode == "Mock Interview":
        col3_1, col3_2 = st.columns(2)
        with col3_1:
            st.metric("Правильных", st.session_state.get('correct', 0))
        with col3_2:
            st.metric("Неправильных", st.session_state.get('incorrect', 0))
```

### 4. User Input Area (Mock Mode Only)

```python
if session_mode == "Mock Interview" and st.session_state.get('mock_started', False):
    user_answer = st.text_area(
        "Введите ваш ответ...",
        placeholder="Введите ваш ответ...",
        height=80,
        key="user_input"
    )
    
    if st.button("Submit Answer"):
        # Process answer logic here
        pass
```

## STATE MANAGEMENT

### Required Session State Variables

```python
# Initialize all session states
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
```

## STYLING AND APPEARANCE

### Custom CSS

```python
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
```

## FUNCTIONAL BEHAVIOR

### 1. Mode Switching Logic

- When "Generate questions" is selected: Show questions number selector
- When "Mock Interview" is selected: Hide questions number selector, prepare for interactive mode

### 2. Generate Questions Mode

```python
if main_button and session_mode == "Generate questions":
    # Generate sample questions
    sample_questions = [
        "1. Объясните разницу между синхронным и асинхронным программированием в Python.",
        "2. Как бы вы оптимизировали медленный SQL запрос?",
        "3. Расскажите о принципах SOLID и приведите примеры.",
        "4. Как работает сборщик мусора в Python?",
        "5. Опишите архитектуру микросервисов и её преимущества."
    ]
    
    st.session_state.chat_messages = [
        "**Сгенерированные вопросы:**\n\n" + "\n\n".join(sample_questions[:questions_num])
    ]
    st.rerun()
```

### 3. Mock Interview Mode

```python
if main_button and session_mode == "Mock Interview":
    st.session_state.mock_started = True
    st.session_state.chat_messages = [
        "**Вопрос 1:**\nОбъясните разницу между синхронным и асинхронным программированием в Python. Приведите примеры использования."
    ]
    st.rerun()
```

## TECHNICAL REQUIREMENTS

### Dependencies

```python
import streamlit as st
import openai  # for API integration
import json
import time
```

### Streamlit Configuration

```python
st.set_page_config(
    page_title="Interview Prep",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

### Error Handling

- Implement try-catch blocks for API calls
- Show loading spinners during processing
- Display error messages in user-friendly format

### Responsive Design

- Ensure proper display on different screen sizes
- Use Streamlit's column system for responsive layout
- Test on mobile devices

## INTEGRATION POINTS

### OpenAI API Integration

```python
# Placeholder for API integration
def generate_questions(job_desc, seniority, question_type, num_questions, advanced_settings):
    # API call logic here
    pass

def evaluate_answer(question, answer, correct_count, incorrect_count):
    # Answer evaluation logic here
    pass
```

## CRITICAL IMPLEMENTATION NOTES

### 1. Dynamic UI Behavior
- **Button Text Changes**: Main button must dynamically change text based on selected mode
- **Conditional Elements**: Questions number selector appears only in "Generate questions" mode
- **Statistics Display**: Metrics for correct/incorrect answers show only in mock interview mode

### 2. Chat Area Implementation
- Use `st.container(height=400)` for fixed-height scrollable area
- Implement message history using `st.session_state.chat_messages` list
- Each message should be displayed with consistent formatting

### 3. State Persistence
- All form inputs must persist across interactions using session state
- Chat history must be maintained throughout the session
- Mock interview progress (question number, scores) must be tracked

### 4. User Experience Flow
1. **Initial State**: Welcome message displayed, all controls available
2. **Generate Mode**: Click button → Questions appear in chat area
3. **Mock Mode**: Click button → First question appears → User input area becomes active
4. **Mock Progression**: Submit answer → Evaluation appears → Next Question button becomes available

### 5. Visual Consistency
- Match the gradient backgrounds from original HTML design
- Ensure proper spacing and alignment of all elements
- Implement hover effects for interactive elements
- Use consistent color scheme (purple gradients, proper contrast)

This specification provides a complete blueprint for recreating the HTML interface in Streamlit while maintaining all functionality and visual appeal.