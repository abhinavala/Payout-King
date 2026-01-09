# No-Rewrite Rule

## Core Principle

> **If something is wrong, we fix it at the spec level, not by patching code.**

## Why This Matters

- Prevents technical debt accumulation
- Ensures correctness from the start
- Saves months of refactoring
- Maintains architectural integrity

## When to Apply

1. **Rule specification is unclear** → Clarify the spec, don't code around it
2. **Edge case discovered** → Update the spec, then implement
3. **Architecture conflict** → Resolve at design level, not with workarounds
4. **Math doesn't match reality** → Fix the math model, not the display

## Enforcement

- Every code change must reference a spec
- Specs live in `/docs/rules/`
- No "quick fixes" that bypass spec updates
- Code reviews check spec compliance first

## Example

❌ **Wrong**: "The trailing drawdown calculation is off by $100, let me add a fudge factor."

✅ **Correct**: "The trailing drawdown calculation doesn't match the spec. Let me review the spec, identify the error, update it, then fix the implementation."
