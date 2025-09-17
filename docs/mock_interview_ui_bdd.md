# Mock Interview UI Behaviour - BDD Acceptance Criteria

Feature: Mock Interview UI Flow As a user preparing for an interview I
want the UI to behave consistently during a mock interview session So
that I can focus on answering questions and receiving feedback.

Scenario: Interview just started Given the interview has not started
Then the user sees labels and titles And the user sees the "Questions
Area" And the user sees the "Start Mock Interview" button And the user
does not see the "Next Question" button And the user does not see the
"Answer Field" And the user does not see the "Submit Answer" button

Scenario: User clicks "Start Mock Interview" Given the user sees the
"Start Mock Interview" button When the user clicks "Start Mock
Interview" Then the "Start Mock Interview" button is hidden And the
"Next Question" button is visible but disabled And the "Answer Field" is
hidden And the "Submit Answer" button is hidden And the Assistant
generates a question

Scenario: Assistant generates a question Given the Assistant is
generating a question When the question is ready Then the "Next
Question" button is visible but disabled And the "Answer Field" is
visible and cleared And the "Submit Answer" button is visible only if
the user has typed something

Scenario: User submits an answer Given the user has typed an answer in
the "Answer Field" When the user clicks "Submit Answer" Then the "Submit
Answer" button is hidden And the "Answer Field" is hidden And the answer
is sent to the Assistant And the user waits for the Assistant evaluation

Scenario: Assistant evaluates answer Given the user has submitted an
answer When the Assistant provides evaluation Then the user sees their
answer and the evaluation in the "Questions Area" And the "Next
Question" button is visible

Scenario: User clicks "Next Question" Given the user sees the "Next
Question" button When the user clicks "Next Question" Then the "Next
Question" button is visible but disabled And the "Questions Area" is
cleared
