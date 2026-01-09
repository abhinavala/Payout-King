# Rule Specification: Apex Trailing Max Drawdown (Evaluation)

## Rule Identity

- **Rule Name**: Trailing Max Drawdown
- **Firm**: Apex Trader Funding
- **Account Type**: Evaluation
- **Applies To**: Evaluation accounts only

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
current_equity <= (high_water_mark - (high_water_mark * 0.05))
```

Or equivalently:

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

4. **Edge Case**: Starting balance edge case
   - **Handling**: If starting balance is $50,000, initial threshold is $2,500. If equity never exceeds $50,000, threshold remains $2,500. If equity reaches $52,500, new threshold becomes $2,625.

## Status Levels

- **SAFE**: `current_equity > (high_water_mark * 0.95) + (threshold * 0.20)`
  - More than 20% buffer above threshold
  - Example: If threshold is $2,500, safe if equity > threshold + $500

- **CAUTION**: `(high_water_mark * 0.95) < current_equity <= (high_water_mark * 0.95) + (threshold * 0.20)`
  - Within 20% of threshold
  - Example: If threshold is $2,500, caution if equity is between threshold and threshold + $500

- **CRITICAL**: `(high_water_mark * 0.95) < current_equity <= (high_water_mark * 0.95) + (threshold * 0.05)`
  - Within 5% of threshold
  - Example: If threshold is $2,500, critical if equity is between threshold and threshold + $125

- **VIOLATED**: `current_equity <= (high_water_mark * 0.95)`
  - At or below threshold

## Distance-to-Violation Calculation

How to compute remaining buffer:

```
distance_to_violation = current_equity - (high_water_mark * 0.95)
```

Units: Dollars

If `distance_to_violation <= 0`, violation has occurred.

## Validation Scenarios

### Scenario 1: Safe Case
- **Setup**: 
  - Starting balance: $50,000
  - High-water mark: $50,000 (no profit yet)
  - Current equity: $49,000
  - Threshold: $2,500 (5% of $50,000)
  - Min allowed equity: $47,500
- **Action**: Equity is $1,500 above threshold
- **Expected Result**: 
  - Status: SAFE
  - Distance to violation: $1,500
  - Buffer: 60% of threshold remaining

### Scenario 2: Boundary Case
- **Setup**:
  - Starting balance: $50,000
  - High-water mark: $52,500 (reached after $2,500 profit)
  - Current equity: $50,000
  - Threshold: $2,625 (5% of $52,500)
  - Min allowed equity: $49,875
- **Action**: Equity is exactly $125 above threshold (5% buffer)
- **Expected Result**:
  - Status: CRITICAL
  - Distance to violation: $125
  - Buffer: 5% of threshold remaining

### Scenario 3: Violation Case
- **Setup**:
  - Starting balance: $50,000
  - High-water mark: $52,500
  - Current equity: $49,800
  - Threshold: $2,625
  - Min allowed equity: $49,875
- **Action**: Equity drops to $49,800, which is $75 below threshold
- **Expected Result**:
  - Status: VIOLATED
  - Distance to violation: -$75 (negative = violation)
  - Account failed

### Scenario 4: HWM Update During Trade
- **Setup**:
  - Starting balance: $50,000
  - High-water mark: $50,000
  - Current equity: $51,000 (open position with +$1,000 unrealized)
  - Threshold: $2,500
- **Action**: Equity reaches $51,000, HWM updates to $51,000
- **Expected Result**:
  - New threshold: $2,550 (5% of $51,000)
  - New min allowed equity: $48,450
  - Status: SAFE (equity $51,000 > $48,450)
  - If position closes at $51,000, HWM remains $51,000

## Implementation Notes

1. **Real-time Updates**: HWM must update on every tick when equity exceeds previous HWM
2. **Unrealized PnL**: Must be included in equity calculation at all times
3. **Precision**: Use exact decimal math, not floating-point approximations
4. **State Persistence**: HWM must persist across sessions
5. **Initial State**: On account creation, HWM = starting balance

## References

- Apex Trader Funding official rules
- Community verification: Trailing drawdown is 5% of high-water mark
- Includes unrealized PnL in real-time calculation
