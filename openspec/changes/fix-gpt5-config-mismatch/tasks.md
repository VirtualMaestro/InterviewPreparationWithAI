# Tasks

## 1. Update Config Default Model
- [ ] 1.1 Change default model in src/config.py from GPT_5 to GPT_4O
  - Files: `src/config.py`
  - Details: Line 18, change `model: str = AIModel.GPT_5.value` to `model: str = AIModel.GPT_4O.value`
  - Add comment explaining GPT-5 is disabled due to bugs

## 2. Document GPT-5 Status
- [ ] 2.1 Add deprecation comment to GPT_5 enum
  - Files: `src/models/enums.py`
  - Details: Add comment to GPT_5 enum value indicating experimental/disabled status

- [ ] 2.2 Add warning comment to _call_gpt_5() method
  - Files: `src/ai/generator.py`
  - Details: Lines 120-148, add docstring warning that GPT-5 is experimental and disabled

## 3. Update Tests
- [ ] 3.1 Review tests that reference GPT-5
  - Files: `tests/test_*.py`
  - Details: Ensure tests don't rely on GPT-5 being the default model
  - Update any tests that assume GPT_5 is default

## 4. Verify Configuration
- [ ] 4.1 Test that app.py no longer needs to override config default
  - Files: `app.py`
  - Details: Verify line 202 override is now redundant (config and app match)
  - Optionally remove the override if it's now unnecessary
