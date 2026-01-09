# Rule Specification: Topstep Trailing Max Drawdown (Funded)

## Rule Identity

- **Rule Name**: Trailing Max Drawdown
- **Firm**: Topstep
- **Account Type**: Funded
- **Applies To**: Funded accounts only

## Inputs Required

- [x] Current balance (realized PnL + starting balance)
- [ ] Unrealized PnL (NOT used for this rule - balance only)
- [x] Realized PnL (cumulative closed position PnL)
- [x] Starting account balance
- [x] High-water mark (highest balance reached)
- [ ] Position size (not used for this rule)
- [x] Time of day (to determine if it's end-of-day)
- [ ] Trading days count (not used for this rule)

## State Variables

- **high_water_mark**: Highest balance value reached
  - Initial value: Starting account balance
  - Update condition: When `current_balance > high_water_mark` (may be intraday or end-of-day, verify with Topstep)
  - Reset condition: Never (except account reset/restart)

- **max_drawdown_threshold**: Current maximum allowed drawdown
  - Initial value: `starting_balance * 0.04` (4% of starting balance)
  - Update condition: Recalculated whenever `high_water_mark` changes
  - Calculation: `high_water_mark * 0.04`
  - Reset condition: Never (except account reset/restart)

**Note**: Funded accounts may use trailing drawdown (like Apex) instead of end-of-day. Verify exact behavior with Topstep.

## Threshold Definition

- **Threshold Type**: Percentage-based
- **Threshold Value**: 4% of high-water mark
- **Calculation Method**: 
  1. Track highest balance reached (high-water mark)
  2. Calculate threshold: `threshold = high_water_mark * 0.04`
  3. Calculate minimum allowed balance: `min_balance = high_water_mark - threshold`
  4. Violation occurs when: `current_balance <= min_balance`

**Important**: 
- Funded accounts may differ from evaluation accounts
- Verify if funded accounts use:
  - End-of-day evaluation (like evaluation accounts), OR
  - Trailing/intraday evaluation (like Apex)
- This spec assumes similar to evaluation (end-of-day), but verify

## Reset Behavior

- **Resets Daily**: No (HWM persists)
- **Resets Weekly**: No
- **Resets Monthly**: No
- **Resets Never**: Yes (only resets on account restart/reset)
- **Reset Time**: N/A
- **Reset Condition**: Account reset only

## Violation Condition

Exact mathematical condition that triggers violation:

**If end-of-day evaluation** (like evaluation accounts):
```
end_of_day_balance <= (high_water_mark * 0.96)
```

**If trailing/intraday evaluation** (like Apex):
```
current_balance <= (high_water_mark * 0.96)
```

Where:
- `current_balance = starting_balance + realized_pnl` (unrealized PnL excluded)
- `high_water_mark = max(all_balances_since_start)`

**Note**: Must verify with Topstep whether funded accounts use end-of-day or intraday evaluation.

## Recoverability

- **Can violation be fixed?**: No
- **Recovery method**: N/A
- **Permanent consequence**: Account is failed. Cannot continue trading on this account.

## Edge Cases

Same as evaluation accounts, with potential difference in evaluation timing (intraday vs end-of-day).

## Status Levels

Same as evaluation accounts, adjusted for potential intraday evaluation.

## Distance-to-Violation Calculation

Same as evaluation accounts.

## Validation Scenarios

Similar to evaluation accounts, with potential difference in evaluation timing.

## Implementation Notes

1. **Verify Evaluation Timing**: Confirm whether funded accounts use end-of-day or intraday evaluation
2. **Balance Only**: Unrealized PnL excluded (same as evaluation)
3. **4% Threshold**: Same percentage as evaluation accounts
4. **HWM Updates**: Verify when HWM updates (end-of-day or intraday)

## References

- Topstep official rules for funded accounts
- May differ from evaluation account rules
- Verify exact behavior with Topstep documentation
