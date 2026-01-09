# Rule Specification Template

## Rule Identity

- **Rule Name**: [e.g., "Trailing Max Drawdown"]
- **Firm**: [Apex / Topstep / MFF / etc.]
- **Account Type**: [Evaluation / PA / Funded]
- **Applies To**: [Eval / PA / Funded / All]

## Inputs Required

List all data points needed to evaluate this rule:

- [ ] Current equity
- [ ] Unrealized PnL
- [ ] Realized PnL
- [ ] High-water mark
- [ ] Position size
- [ ] Time of day
- [ ] Trading days count
- [ ] Other: [specify]

## State Variables

What persistent state must be tracked:

- **Variable Name**: [Description]
  - Initial value: [value]
  - Update condition: [when it changes]
  - Reset condition: [when it resets]

## Threshold Definition

- **Threshold Type**: [Fixed / Percentage / Calculated]
- **Threshold Value**: [exact formula or value]
- **Calculation Method**: [step-by-step math]

## Reset Behavior

- **Resets Daily**: [Yes / No]
- **Resets Weekly**: [Yes / No]
- **Resets Monthly**: [Yes / No]
- **Resets Never**: [Yes / No]
- **Reset Time**: [if applicable, e.g., "5:00 PM ET"]
- **Reset Condition**: [specific trigger]

## Violation Condition

Exact mathematical condition that triggers violation:

```
[Formula or condition]
```

Example: `equity <= (high_water_mark - max_drawdown_threshold)`

## Recoverability

- **Can violation be fixed?**: [Yes / No]
- **Recovery method**: [if yes, how?]
- **Permanent consequence**: [if no, what happens?]

## Edge Cases

List all known edge cases and how they're handled:

1. **Edge Case**: [Description]
   - **Handling**: [How it's resolved]

2. **Edge Case**: [Description]
   - **Handling**: [How it's resolved]

## Status Levels

Define the status levels for this rule:

- **SAFE**: [Condition]
- **CAUTION**: [Condition - e.g., "Within 20% of threshold"]
- **CRITICAL**: [Condition - e.g., "Within 5% of threshold"]
- **VIOLATED**: [Condition]

## Distance-to-Violation Calculation

How to compute remaining buffer:

```
[Formula]
```

Units: [Dollars / Ticks / Contracts / Time / Percentage]

## Validation Scenarios

### Scenario 1: Safe Case
- **Setup**: [Initial state]
- **Action**: [What happens]
- **Expected Result**: [Status and values]

### Scenario 2: Boundary Case
- **Setup**: [Initial state]
- **Action**: [What happens]
- **Expected Result**: [Status and values]

### Scenario 3: Violation Case
- **Setup**: [Initial state]
- **Action**: [What happens]
- **Expected Result**: [Status and values]

## Implementation Notes

Any special considerations for implementation:

- [Note 1]
- [Note 2]

## References

- Firm documentation: [URL or citation]
- Community discussions: [if applicable]
- Historical examples: [if applicable]
