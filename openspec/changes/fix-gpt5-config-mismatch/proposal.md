# Proposal: Fix GPT-5 Config Mismatch
# Auto-generated from: src/config.py:18, app.py:201 — review and refine as needed.

## Why
The system has a configuration mismatch where `src/config.py` defaults to GPT_5 but `app.py` hardcodes GPT_4O, causing confusion and potential runtime errors if GPT-5 is ever re-enabled.

Discovered in:
- `src/config.py:18` — `model: str = AIModel.GPT_5.value`
- `app.py:201` — GPT-5 removed from UI (commit a5330c3: "remove gpt-5 from the UI. Buggy, need to investigate.")
- `app.py:202` — `model: str = AIModel.GPT_4O.value` (hardcoded override)

Original context:
- Commit a5330c3: "remove gpt-5 from the UI. Buggy, need to investigate."
- GPT-5 uses new Response API (`client.responses.create()`) instead of ChatCompletion API
- Generator has `_call_gpt_5()` method (lines 120-148) but it's untested and potentially broken

## What Changes
- Update `src/config.py` to default to GPT_4O instead of GPT_5
- Document GPT-5 status as experimental/disabled
- Add comments explaining why GPT-5 is disabled
- Optionally: Remove or deprecate GPT-5 code paths if not planning to fix

**Files affected:**
- `src/config.py` — Change default model
- `src/ai/generator.py` — Add deprecation warnings or remove GPT-5 code
- `src/models/enums.py` — Optionally mark GPT_5 as deprecated

## Impact
**If NOT fixed:**
- Developers may be confused by config defaulting to a disabled model
- If someone removes the app.py override, GPT-5 will be used and likely fail
- Tests reference GPT-5 but it's not functional in production

**If fixed:**
- Config will match actual production behavior
- Clear documentation of GPT-5 status
- Reduced confusion for future developers
- Option to cleanly remove GPT-5 code or mark it as experimental

## Rollback
If this change causes issues:
1. Revert `src/config.py` to default to GPT_5
2. Restore any removed GPT-5 code
3. Re-add GPT-5 to UI model selector if needed

Simple rollback via git revert.

## Alternatives Considered

### Option: Keep GPT_5 default and fix the bugs
- Pros: GPT-5 may have better performance, future-proofing
- Cons: Requires investigating and fixing unknown bugs, new API is untested, may delay other work
- Why rejected: GPT-5 was explicitly removed due to bugs, fixing it is not a priority right now

### Option: Remove GPT-5 entirely from codebase
- Pros: Eliminates dead code, reduces maintenance burden, clearer codebase
- Cons: If GPT-5 is fixed in the future, code will need to be rewritten
- Why rejected: May want to re-enable GPT-5 later once bugs are resolved, keeping the code path is reasonable

### Option: Make GPT-5 opt-in via environment variable
- Pros: Allows testing GPT-5 without affecting production, clear experimental status
- Cons: Adds complexity, requires documentation
- Why rejected: Simpler to just change the default and document the status
