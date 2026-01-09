# Rule Specification: Apex Trailing Max Drawdown (Funded)

## Rule Identity

- **Rule Name**: Trailing Max Drawdown
- **Firm**: Apex Trader Funding
- **Account Type**: Funded
- **Applies To**: Funded accounts only

## Inputs Required

- [x] Current equity (realized PnL + unrealized PnL + starting balance)
- [x] Unrealized PnL (current open position PnL)
- [x] Realized PnL (cumulative closed position PnL)
- [x] Starting account balance
- [x] High-water mark (highest equity reached)
- [ ] Position size (not used for this rule)
- [ ] Time of day (not used for this rule)
- [ ] Trading days count (not used for this rule)

## State Variables

- **high_water_mark**: Highest equity value reached since account start
  - Initial value: Starting account balance
  - Update condition: Whenever `current_equity > high_water_mark`
  - Reset condition: Never (except account reset/restart)

- **max_drawdown_threshold**: Current maximum allowed drawdown
  - Initial value: `starting_balance * 0.05` (5% of starting balance)
  - Update condition: Recalculated whenever `high_water_mark` changes
  - Calculation: `high_water_mark * 0.05`
  - Reset condition: Never (except account reset/restart)

## Threshold Definition

- **Threshold Type**: Percentage-based, trailing
- **Threshold Value**: 5% of high-water mark
- **Calculation Method**: 
  1. Track highest equity reached (high-water mark)
  2. Calculate threshold: `threshold = high_water_mark * 0.05`
  3. Calculate minimum allowed equity: `min_equity = high_water_mark - threshold`
  4. Violation occurs when: `current_equity <= min_equity`

**Note**: Funded accounts use the same trailing drawdown calculation as Evaluation and PA accounts.

## Reset Behavior

- **Resets Daily**: No
- **Resets Weekly**: No
- **Resets Monthly**: No
- **Resets Never**: Yes (only resets on account reset/restart)
- **Reset Time**: N/A
- **Reset Condition**: Account reset only

## Violation Condition

Exact mathematical condition that triggers violation:

```
current_equity <= (high_water_mark * 0.95)
```

Where:
- `current_equity = starting_balance + realized_pnl + unrealized_pnl`
- `high_water_mark = max(all_equity_values_since_start)`

## Recoverability

- **Can violation be fixed?**: No
- **Recovery method**: N/A
- **Permanent consequence**: Account is failed. Cannot continue trading on this account.

## Edge Cases

Same as Evaluation and PA accounts.

## Status Levels

- **SAFE**: `current_equity > (high_water_mark * 0.95) + (threshold * 0.20)`
- **CAUTION**: `(high_water_mark * 0.95) < current_equity <= (high_water_mark * 0.95) + (threshold * 0.20)`
- **CRITICAL**: `(high_water_mark * 0.95) < current_equity <= (high_water_mark * 0.95) + (threshold * 0.05)`
- **VIOLATED**: `current_equity <= (high_water_mark * 0.95)`

## Distance-to-Violation Calculation

```
distance_to_violation = current_equity - (high_water_mark * 0.95)
```

Units: Dollars

## Validation Scenarios

Same structure as Evaluation accounts. Funded accounts follow identical trailing drawdown rules.

## Implementation Notes

All Apex account types (Evaluation, PA, Funded) use identical trailing drawdown rules:
- 5% of high-water mark
- Includes unrealized PnL
- Updates in real-time
- Never resets (except account restart)

## References

- Apex Trader Funding official rules
- All account types use same 5% trailing drawdown
