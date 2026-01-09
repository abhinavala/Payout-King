# Rule Specification: Apex Trailing Max Drawdown (PA - Paid Account)

## Rule Identity

- **Rule Name**: Trailing Max Drawdown
- **Firm**: Apex Trader Funding
- **Account Type**: PA (Paid Account)
- **Applies To**: PA accounts only

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

**Note**: PA accounts use the same trailing drawdown calculation as Evaluation accounts.

## Reset Behavior

- **Resets Daily**: No
- **Resets Weekly**: No
- **Resets Monthly**: No
- **Resets Never**: Yes (only resets on account restart/reset)
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

1. **Edge Case**: Equity exactly equals threshold
   - **Handling**: `current_equity <= threshold` means violation. Exact equality is a violation.

2. **Edge Case**: Gap moves causing instant violation
   - **Handling**: If equity drops below threshold due to gap (overnight or during trading halt), violation is immediate. System must detect this on next update.

3. **Edge Case**: High-water mark reached with open position
   - **Handling**: HWM updates immediately when equity exceeds previous HWM, even with open positions. Threshold recalculates immediately.

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

### Scenario 1: Safe Case
- **Setup**: 
  - Starting balance: $50,000
  - High-water mark: $55,000
  - Current equity: $53,000
  - Threshold: $2,750 (5% of $55,000)
  - Min allowed equity: $52,250
- **Action**: Equity is $750 above threshold
- **Expected Result**: 
  - Status: SAFE
  - Distance to violation: $750

### Scenario 2: Boundary Case
- **Setup**:
  - Starting balance: $50,000
  - High-water mark: $60,000
  - Current equity: $57,000
  - Threshold: $3,000 (5% of $60,000)
  - Min allowed equity: $57,000
- **Action**: Equity exactly at threshold
- **Expected Result**:
  - Status: VIOLATED (equity <= min allowed)
  - Distance to violation: $0

### Scenario 3: Violation Case
- **Setup**:
  - Starting balance: $50,000
  - High-water mark: $55,000
  - Current equity: $52,000
  - Threshold: $2,750
  - Min allowed equity: $52,250
- **Action**: Equity drops to $52,000, which is $250 below threshold
- **Expected Result**:
  - Status: VIOLATED
  - Distance to violation: -$250

## Implementation Notes

Same as Evaluation accounts. PA accounts follow identical trailing drawdown rules.

## References

- Apex Trader Funding official rules
- PA accounts use same 5% trailing drawdown as Evaluation
