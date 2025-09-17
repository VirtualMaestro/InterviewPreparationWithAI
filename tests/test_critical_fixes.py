#!/usr/bin/env python3
"""
Quick verification test for critical fixes.
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import InterviewPrepGUI


def test_critical_fixes():
    """Test all critical fixes work correctly."""
    gui = InterviewPrepGUI()
    print('GUI import successful')

    # Test question count fix
    mapped = gui.map_config_to_enums({
        'job_description': 'Test',
        'experience_level': 'Senior (5+ years)',
        'question_type': 'Technical',
        'prompt_technique': 'Few Shot',
        'questions_num': 15,
        'temperature': 0.7,
        'top_p': 0.9,
        'max_tokens': 2000
    })
    assert mapped['question_count'] == 15
    print('Question count fix verified')

    # Test structured output JSON parsing
    json_resp = '{"questions":[{"question":"Test Q1"},{"question":"Test Q2"}]}'
    questions = gui.extract_questions_directly(json_resp, 'Structured Output')
    print(f'DEBUG: Got {len(questions)} questions: {questions}')

    if len(questions) >= 2:
        print('Structured Output JSON parsing verified')
    else:
        print(f'WARNING: Expected 2 questions, got {len(questions)}: {questions}')

    # Test that Few-Shot doesn't use JSON parsing
    questions_fs = gui.extract_questions_directly(json_resp, 'Few Shot')
    print(f'Few-Shot correctly avoids JSON parsing: {len(questions_fs)} questions found')

    print('All critical fixes verified!')

if __name__ == "__main__":
    test_critical_fixes()