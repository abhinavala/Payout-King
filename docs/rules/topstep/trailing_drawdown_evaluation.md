# Rule Specification: Topstep Trailing Max Drawdown (Evaluation)

## Rule Identity

- **Rule Name**: Trailing Max Drawdown (End-of-Day)
- **Firm**: Topstep
- **Account Type**: Evaluation
- **Applies To**: Evaluation accounts only

## Inputs Required

- [x] Current balance (realized PnL + starting balance, NO unrealized PnL)
- [ ] Unrealized PnL (NOT used for this rule - balance only)
- [x] Realized PnL (cumulative closed position PnL)
- [x] Starting account balance
- [x] High-water mark (highest balance reached, end-of-day)
- [ ] Position size (not used for this rule)
- [x] Time of day (to determine if it's end-of-day)
- [ ] Trading days count (not used for this rule)

## State Variables

- **high_water_mark**: Highest balance value reached at end of trading day
  - Initial value: Starting account balance
  - Update condition: At end of trading day (4:00 PM CT), if `end_of_day_balance > high_water_mark`
  - Reset condition: Never (except account reset/restart)

- **max_drawdown_threshold**: Current maximum allowed drawdown
  - Initial value: `starting_balance * 0.04` (4% of starting balance)
  - Update condition: Recalculated at end of day whenever `high_water_mark` changes
  - Calculation: `high_water_mark * 0.04`
  - Reset condition: Never (except account reset/restart)

- **end_of_day_balance**: Balance at end of trading day (4:00 PM CT)
  - Calculated as: `starting_balance + realized_pnl` (unrealized PnL excluded)
  - Used only for end-of-day evaluation

## Threshold Definition

- **Threshold Type**: Percentage-based, end-of-day (not trailing during day)
- **Threshold Value**: 4% of high-water mark
- **Calculation Method**: 
  1. At end of trading day (4:00 PM CT), calculate balance: `balance = starting_balance + realized_pnl`
  2. If balance exceeds current high-water mark, update HWM
  3. Calculate threshold: `threshold = high_water_mark * 0.04`
  4. Calculate minimum allowed balance: `min_balance = high_water_mark - threshold`
  5. Violation occurs when: `end_of_day_balance <= min_balance`

**Critical Difference from Apex**: 
- Topstep uses **balance only** (excludes unrealized PnL)
- Topstep evaluates **end-of-day only** (not intraday)
- Topstep uses **4%** (not 5%)

## Reset Behavior

- **Resets Daily**: No (HWM persists)
- **Resets Weekly**: No
- **Resets Monthly**: No
- **Resets Never**: Yes (only resets on account restart/reset)
- **Reset Time**: N/A
- **Reset Condition**: Account reset only

## Violation Condition

Exact mathematical condition that triggers violation:

**At end of trading day (4:00 PM CT)**:
```
end_of_day_balance <= (high_water_mark * 0.96)
```

Where:
- `end_of_day_balance = starting_balance + realized_pnl` (unrealized PnL excluded)
- `high_water_mark = max(all_end_of_day_balances_since_start)`

**Important**: This is evaluated ONLY at end of day. Intraday drawdown does not cause violation.

## Recoverability

- **Can violation be fixed?**: No
- **Recovery method**: N/A
- **Permanent consequence**: Account is failed. Cannot continue trading on this account.

## Edge Cases

1. **Edge Case**: Open position at end of day
   - **Handling**: Unrealized PnL is ignored. Only realized PnL counts. If you have open positions, they don't affect the drawdown calculation until closed.

2. **Edge Case**: Balance exactly equals threshold
   - **Handling**: `end_of_day_balance <= threshold` means violation. Exact equality is a violation.

3. **Edge Case**: Large unrealized loss during day
   - **Handling**: Unrealized losses do not cause violation. Only end-of-day balance matters. However, if you close the position at a loss, it will affect end-of-day balance.

4. **Edge Case**: HWM update at end of day
   - **Handling**: If end-of-day balance exceeds previous HWM, HWM updates immediately. New threshold applies to next day.

5. **Edge Case**: Trading after 4:00 PM CT
   - **Handling**: End-of-day is 4:00 PM CT. Any trades after this time count toward next day's balance.

## Status Levels

**During Trading Day** (before 4:00 PM CT):
- **SAFE**: Cannot determine (evaluation is end-of-day only)
- **CAUTION**: Cannot determine (evaluation is end-of-day only)
- **CRITICAL**: Cannot determine (evaluation is end-of-day only)
- **VIOLATED**: Cannot occur during day

**At End of Trading Day** (4:00 PM CT):
- **SAFE**: `end_of_day_balance > (high_water_mark * 0.96) + (threshold * 0.20)`
  - More than 20% buffer above threshold

- **CAUTION**: `(high_water_mark * 0.96) < end_of_day_balance <= (high_water_mark * 0.96) + (threshold * 0.20)`
  - Within 20% of threshold

- **CRITICAL**: `(high_water_mark * 0.96) < end_of_day_balance <= (high_water_mark * 0.96) + (threshold * 0.05)`
  - Within 5% of threshold

- **VIOLATED**: `end_of_day_balance <= (high_water_mark * 0.96)`
  - At or below threshold

## Distance-to-Violation Calculation

How to compute remaining buffer:

**At end of trading day**:
```
distance_to_violation = end_of_day_balance - (high_water_mark * 0.96)
```

**During trading day** (advisory only, not enforced):
```
projected_distance = (current_balance + unrealized_pnl) - (high_water_mark * 0.96)
```

Units: Dollars

If `distance_to_violation <= 0`, violation has occurred.

## Validation Scenarios

### Scenario 1: Safe Case
- **Setup**: 
  - Starting balance: $50,000
  - High-water mark: $50,000 (no profit yet)
  - Realized PnL: -$500
  - End-of-day balance: $49,500
  - Threshold: $2,000 (4% of $50,000)
  - Min allowed balance: $48,000
- **Action**: End-of-day balance is $1,500 above threshold
- **Expected Result**: 
  - Status: SAFE
  - Distance to violation: $1,500
  - Buffer: 75% of threshold remaining

### Scenario 2: Boundary Case
- **Setup**:
  - Starting balance: $50,000
  - High-water mark: $52,000 (reached after $2,000 profit on previous day)
  - Realized PnL: -$1,000
  - End-of-day balance: $49,000
  - Threshold: $2,080 (4% of $52,000)
  - Min allowed balance: $49,920
- **Action**: End-of-day balance is $920 below threshold
- **Expected Result**:
  - Status: VIOLATED
  - Distance to violation: -$920
  - Account failed

### Scenario 3: Violation Case
- **Setup**:
  - Starting balance: $50,000
  - High-water mark: $51,000
  - Realized PnL: -$2,100
  - End-of-day balance: $47,900
  - Threshold: $2,040 (4% of $51,000)
  - Min allowed balance: $48,960
- **Action**: End-of-day balance drops to $47,900, which is $1,060 below threshold
- **Expected Result**:
  - Status: VIOLATED
  - Distance to violation: -$1,060
  - Account failed

### Scenario 4: HWM Update at End of Day
- **Setup**:
  - Starting balance: $50,000
  - Previous high-water mark: $50,000
  - Realized PnL: +$3,000
  - End-of-day balance: $53,000
- **Action**: End-of-day balance exceeds previous HWM
- **Expected Result**:
  - New high-water mark: $53,000
  - New threshold: $2,120 (4% of $53,000)
  - New min allowed balance: $50,880
  - Status: SAFE (balance $53,000 > $50,880)

### Scenario 5: Open Position During Day (Advisory)
- **Setup**:
  - Starting balance: $50,000
  - High-water mark: $50,000
  - Realized PnL: $0
  - Current balance: $50,000
  - Unrealized PnL: -$1,500 (open losing position)
  - Current equity: $48,500
- **Action**: During trading day, equity shows $48,500
- **Expected Result**:
  - Status: Cannot determine (evaluation is end-of-day only)
  - Advisory: If position closes at -$1,500, end-of-day balance will be $48,500
  - Advisory threshold: $48,000 (4% of $50,000)
  - Advisory: Would be $500 above threshold if closed now
  - **Important**: Unrealized loss does not cause violation until position is closed

## Implementation Notes

1. **End-of-Day Evaluation**: Rule is ONLY evaluated at 4:00 PM CT
2. **Balance Only**: Unrealized PnL is excluded from calculation
3. **Intraday Advisory**: Can show projected violation, but not enforced
4. **HWM Updates**: Only at end of day when balance exceeds previous HWM
5. **Time Zone**: 4:00 PM CT (Central Time) is the cutoff
6. **Precision**: Use exact decimal math, not floating-point approximations

## References

- Topstep official rules: 4% end-of-day drawdown
- Balance only (excludes unrealized PnL)
- Evaluated at end of trading day (4:00 PM CT)
