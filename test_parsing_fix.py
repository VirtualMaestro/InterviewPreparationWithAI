#!/usr/bin/env python3
"""
Test script to verify the parsing fix for structured AI responses.
"""

from src.ai.parser import ResponseParser
from src.models.enums import InterviewType, ExperienceLevel

# Test the exact format provided by the user
test_response = """1. **Question 1: Python Performance Optimization**
   - *Scenario:* You are working on a data processing application that reads large datasets from a file, processes them, and writes the results to a database. The application is currently facing performance bottlenecks, especially during file I/O operations.
   - *Question:* Describe the steps you would take to identify and resolve these performance bottlenecks. Specifically, how would you optimize the file reading and writing operations in Python? What tools or libraries would you use to profile and enhance the application's performance?

2. **Question 2: System Design and Scalability**
   - *Scenario:* Your team is tasked with designing a new feature for an existing web application that allows users to upload and process images. The feature must handle high traffic and ensure quick processing times.
   - *Question:* How would you approach designing this system to ensure scalability and reliability? Discuss the architecture you would propose, considering both the front-end and back-end components. What Python frameworks or libraries might be useful in implementing this feature, and why?"""

def main():
    print("Testing parsing fix for structured AI responses...")
    
    parser = ResponseParser()
    result = parser.parse(
        test_response, 
        InterviewType.TECHNICAL, 
        ExperienceLevel.SENIOR
    )
    
    print(f"\n[SUCCESS] Success: {result.success}")
    print(f"[STRATEGY] Strategy used: {result.strategy_used.value}")
    print(f"[COUNT] Number of questions found: {len(result.questions)}")
    
    print("\n[QUESTIONS] Parsed Questions:")
    for i, question in enumerate(result.questions, 1):
        print(f"\n{i}. Question (length: {len(question.question)} chars):")
        print(f"   {question.question[:200]}{'...' if len(question.question) > 200 else ''}")
    
    print(f"\n[RAW] Raw questions count: {len(result.raw_questions)}")
    
    # Check if we're getting the full content now instead of just titles
    if result.questions:
        first_question = result.questions[0].question
        has_scenario = "Scenario:" in first_question
        has_question_section = "Question:" in first_question
        
        print(f"\n[ANALYSIS] Content Analysis:")
        print(f"   - Contains 'Scenario:': {has_scenario}")
        print(f"   - Contains 'Question:': {has_question_section}")
        print(f"   - Full structured content: {has_scenario and has_question_section}")
        
        if has_scenario and has_question_section:
            print("\n🎉 SUCCESS: Parser now extracts complete structured content!")
        else:
            print("\n❌ ISSUE: Parser still only extracting partial content")

if __name__ == "__main__":
    main()