# Rule Specification: Topstep Daily Loss Limit (Evaluation)

## Rule Identity

- **Rule Name**: Daily Loss Limit
- **Firm**: Topstep
- **Account Type**: Evaluation
- **Applies To**: Evaluation accounts only

## Inputs Required

- [x] Current balance (realized PnL + starting balance)
- [ ] Unrealized PnL (NOT used - balance only)
- [x] Realized PnL (cumulative closed position PnL for today)
- [x] Starting account balance
- [x] Daily starting balance (balance at start of trading day)
- [x] Time of day (to determine if it's a new trading day)
- [ ] Position size (not used for this rule)
- [ ] Trading days count (not used for this rule)

## State Variables

- **daily_starting_balance**: Balance at start of current trading day
  - Initial value: Starting account balance (on first day)
  - Update condition: At start of each trading day (4:00 PM CT reset)
  - Reset condition: Daily at 4:00 PM CT

- **daily_loss_limit**: Maximum allowed loss for the day
  - Initial value: `starting_balance * 0.02` (approximately 2% of account size)
  - For $50,000 account: $1,000
  - Update condition: Never (fixed based on account size)
  - Reset condition: Never (constant value)

- **daily_realized_pnl**: Cumulative realized PnL for current trading day
  - Initial value: 0 (at start of each day)
  - Update condition: Increments/decrements with each closed trade
  - Reset condition: Daily at 4:00 PM CT

## Threshold Definition

- **Threshold Type**: Fixed dollar amount (approximately 2% of account size)
- **Threshold Value**: 
  - $50,000 account: $1,000
  - $100,000 account: $2,000
  - Formula: `account_size * 0.02` (approximately)
- **Calculation Method**: 
  1. Calculate daily loss: `daily_loss = daily_starting_balance - current_balance`
  2. Or equivalently: `daily_loss = -daily_realized_pnl`
  3. Violation occurs when: `daily_loss >= daily_loss_limit`

## Reset Behavior

- **Resets Daily**: Yes
- **Resets Weekly**: No
- **Resets Monthly**: No
- **Resets Never**: No
- **Reset Time**: 4:00 PM CT (Central Time)
- **Reset Condition**: At 4:00 PM CT, daily counters reset:
  - `daily_starting_balance` = current balance
  - `daily_realized_pnl` = 0

## Violation Condition

Exact mathematical condition that triggers violation:

```
daily_loss >= daily_loss_limit
```

Where:
- `daily_loss = daily_starting_balance - current_balance`
- `current_balance = daily_starting_balance + daily_realized_pnl`
- Therefore: `daily_loss = -daily_realized_pnl`

Or equivalently:
```
-daily_realized_pnl >= daily_loss_limit
```

Which means:
```
daily_realized_pnl <= -daily_loss_limit
```

**Important**: 
- Only realized PnL counts (unrealized PnL excluded)
- Evaluated continuously during trading day
- Resets daily at 4:00 PM CT

## Recoverability

- **Can violation be fixed?**: No
- **Recovery method**: N/A
- **Permanent consequence**: Account is failed. Cannot continue trading on this account.

## Edge Cases

1. **Edge Case**: Loss exactly equals limit
   - **Handling**: `daily_loss >= limit` means violation. Exact equality is a violation.

2. **Edge Case**: Open position with unrealized loss
   - **Handling**: Unrealized losses do not count. Only realized PnL matters. However, if you close the position at a loss, it will count toward daily loss.

3. **Edge Case**: Reset at 4:00 PM CT
   - **Handling**: At 4:00 PM CT, daily starting balance updates to current balance, and daily realized PnL resets to 0. Any trades after 4:00 PM CT count toward next day.

4. **Edge Case**: Multiple trades on same day
   - **Handling**: All closed trades on the same day accumulate toward daily loss limit.

5. **Edge Case**: Profitable trade then losing trade
   - **Handling**: Daily realized PnL is cumulative. If you make $500 then lose $1,200, daily realized PnL is -$700. If limit is $1,000, you're still safe.

## Status Levels

- **SAFE**: `daily_loss < (daily_loss_limit * 0.80)`
  - Less than 80% of limit used
  - Example: If limit is $1,000, safe if loss < $800

- **CAUTION**: `(daily_loss_limit * 0.80) <= daily_loss < (daily_loss_limit * 0.95)`
  - Between 80% and 95% of limit used
  - Example: If limit is $1,000, caution if loss is between $800 and $950

- **CRITICAL**: `(daily_loss_limit * 0.95) <= daily_loss < daily_loss_limit`
  - Between 95% and 100% of limit
  - Example: If limit is $1,000, critical if loss is between $950 and $1,000

- **VIOLATED**: `daily_loss >= daily_loss_limit`
  - At or above limit

## Distance-to-Violation Calculation

How to compute remaining buffer:

```
distance_to_violation = daily_loss_limit - daily_loss
```

Or equivalently:
```
distance_to_violation = daily_loss_limit - (-daily_realized_pnl)
distance_to_violation = daily_loss_limit + daily_realized_pnl
```

Units: Dollars

If `distance_to_violation <= 0`, violation has occurred.

## Validation Scenarios

### Scenario 1: Safe Case
- **Setup**: 
  - Account size: $50,000
  - Daily loss limit: $1,000
  - Daily starting balance: $50,000
  - Daily realized PnL: -$300
  - Current balance: $49,700
  - Daily loss: $300
- **Action**: Daily loss is $300, limit is $1,000
- **Expected Result**: 
  - Status: SAFE
  - Distance to violation: $700
  - Buffer: 70% of limit remaining

### Scenario 2: Boundary Case
- **Setup**:
  - Account size: $50,000
  - Daily loss limit: $1,000
  - Daily starting balance: $51,000 (had profit from previous day)
  - Daily realized PnL: -$950
  - Current balance: $50,050
  - Daily loss: $950
- **Action**: Daily loss is $950, which is 95% of limit
- **Expected Result**:
  - Status: CRITICAL
  - Distance to violation: $50
  - Buffer: 5% of limit remaining

### Scenario 3: Violation Case
- **Setup**:
  - Account size: $50,000
  - Daily loss limit: $1,000
  - Daily starting balance: $50,000
  - Daily realized PnL: -$1,200
  - Current balance: $48,800
  - Daily loss: $1,200
- **Action**: Daily loss is $1,200, which exceeds limit of $1,000
- **Expected Result**:
  - Status: VIOLATED
  - Distance to violation: -$200 (negative = violation)
  - Account failed

### Scenario 4: Daily Reset
- **Setup**:
  - Previous day ending balance: $49,500
  - Time: 4:00 PM CT (reset time)
- **Action**: New trading day begins
- **Expected Result**:
  - New daily starting balance: $49,500
  - Daily realized PnL: 0
  - Daily loss: 0
  - Status: SAFE

### Scenario 5: Profitable Then Losing
- **Setup**:
  - Account size: $50,000
  - Daily loss limit: $1,000
  - Daily starting balance: $50,000
  - Trade 1: +$500 (daily realized PnL: +$500)
  - Trade 2: -$1,200 (daily realized PnL: -$700)
  - Current balance: $49,300
  - Daily loss: $700
- **Action**: Net daily loss is $700
- **Expected Result**:
  - Status: SAFE (loss $700 < limit $1,000)
  - Distance to violation: $300
  - Buffer: 30% of limit remaining

## Implementation Notes

1. **Daily Reset**: At 4:00 PM CT, reset daily counters
2. **Balance Only**: Unrealized PnL does not count
3. **Continuous Evaluation**: Check on every closed trade
4. **Time Zone**: 4:00 PM CT (Central Time) is the reset time
5. **Account Size**: Daily loss limit is based on original account size, not current balance

## References

- Topstep official rules: Daily loss limit is approximately 2% of account size
- For $50,000 account: $1,000 daily loss limit
- Resets daily at 4:00 PM CT
- Only realized PnL counts
