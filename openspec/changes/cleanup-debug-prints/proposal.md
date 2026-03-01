# Proposal: Cleanup Debug Print Statements
# Auto-generated from: app.py (17 instances), src/ai/parser.py:154 — review and refine as needed.

## Why
The codebase contains 17+ debug print statements using `print(f"DEBUG: ...")` instead of the proper logging system, causing inconsistent logging and debug output going to stdout instead of log files.

Discovered in:
- `app.py:448, 475, 481-486, 523, 534, 568, 575, 600-603, 668, 788` — 17 debug print statements
- `src/ai/parser.py:154` — `print(f"DEBUG: Successfully parsed with strategy: {strategy.value}")`

Original pattern:
```python
print(f"DEBUG: {message}")
```

Should be:
```python
logger.debug(message)
```

## What Changes
Replace all `print(f"DEBUG: ...")` statements with proper `logger.debug(...)` calls.

**Files affected:**
- `app.py` — 17 debug print statements
- `src/ai/parser.py` — 1 debug print statement

## Impact
**If NOT fixed:**
- Debug output goes to stdout instead of log files
- Inconsistent with the rest of the codebase (which uses logger)
- Debug output not captured in logs for troubleshooting
- Harder to control debug verbosity (can't disable via log level)

**If fixed:**
- Consistent logging throughout codebase
- Debug output properly captured in log files
- Can control debug verbosity via logging configuration
- Better alignment with Python logging best practices

## Rollback
If this change causes issues:
1. Revert the changes via git revert
2. Debug output will go back to stdout

Simple rollback, no risk.

## Alternatives Considered

### Option: Keep print statements and add logger calls
- Pros: Maintains stdout output for immediate visibility
- Cons: Duplicate output, inconsistent, clutters stdout
- Why rejected: Proper logging is the standard approach, print statements are not appropriate for production code

### Option: Remove debug statements entirely
- Pros: Cleaner code, no debug noise
- Cons: Loses valuable debugging information
- Why rejected: Debug information is useful for troubleshooting, should be kept but logged properly

### Option: Use a debug flag to control print statements
- Pros: Can toggle debug output
- Cons: Reinventing logging system, adds complexity
- Why rejected: Python logging already provides this functionality via log levels
