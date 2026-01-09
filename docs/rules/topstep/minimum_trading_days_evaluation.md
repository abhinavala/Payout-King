# Rule Specification: Topstep Minimum Trading Days (Evaluation)

## Rule Identity

- **Rule Name**: Minimum Trading Days
- **Firm**: Topstep
- **Account Type**: Evaluation
- **Applies To**: Evaluation accounts only

## Inputs Required

- [ ] Current equity (not used for this rule)
- [ ] Unrealized PnL (not used for this rule)
- [ ] Realized PnL (not used for this rule)
- [x] Trading days count (days with at least one closed trade)
- [x] Account start date
- [x] Current date
- [ ] Position size (not used for this rule)
- [ ] Time of day (not used for this rule)

## State Variables

- **trading_days_count**: Number of days with at least one closed trade
  - Initial value: 0
  - Update condition: Increments when a day has at least one closed trade
  - Reset condition: Never (except account reset/restart)

- **account_start_date**: Date when account was created/started
  - Initial value: Account creation timestamp
  - Update condition: Never
  - Reset condition: Account reset only

## Threshold Definition

- **Threshold Type**: Fixed count
- **Threshold Value**: 2 trading days
- **Calculation Method**: 
  - Count days where at least one trade was closed
  - Requirement: `trading_days_count >= 2`

## Reset Behavior

- **Resets Daily**: No
- **Resets Weekly**: No
- **Resets Monthly**: No
- **Resets Never**: Yes (only resets on account restart/reset)
- **Reset Time**: N/A
- **Reset Condition**: Account reset only

## Violation Condition

This rule does not cause account failure. It is a requirement to pass evaluation.

**Requirement Condition**:
```
trading_days_count < 2
```

If requirement is not met, account cannot pass evaluation (but is not failed).

## Recoverability

- **Can violation be fixed?**: Yes
- **Recovery method**: Trade on at least two days and close at least one position on each day
- **Permanent consequence**: None. This is a pass requirement, not a failure condition.

## Edge Cases

1. **Edge Case**: Multiple trades on same day
   - **Handling**: Only counts as one trading day, regardless of number of trades

2. **Edge Case**: Trade opened but not closed
   - **Handling**: Only closed trades count. Open positions do not count toward trading days.

3. **Edge Case**: Trade closed at 11:59 PM
   - **Handling**: Trading day is determined by date of trade close, not time. Any trade closed on a given calendar day counts.

4. **Edge Case**: Weekend/holiday trading
   - **Handling**: If markets are open and trade is closed, it counts as a trading day.

## Status Levels

- **SAFE**: `trading_days_count >= 2`
  - Requirement met

- **CAUTION**: `trading_days_count == 1` AND account has been active for a few days
  - Requirement partially met (1 of 2 days)

- **CRITICAL**: `trading_days_count == 0` OR (`trading_days_count == 1` AND account has been active for extended period)
  - Requirement not met or barely met

- **VIOLATED**: N/A (this rule does not cause violation, only prevents passing)

## Distance-to-Violation Calculation

This rule doesn't have a "violation" in the traditional sense. Instead, calculate:

```
days_remaining_to_requirement = max(0, 2 - trading_days_count)
```

Units: Days

## Validation Scenarios

### Scenario 1: Requirement Met
- **Setup**: 
  - Account start date: 2024-01-01
  - Current date: 2024-01-05
  - Trading days count: 3 (traded on Jan 2, Jan 3, and Jan 4)
- **Action**: Requirement is 2 days, have 3 days
- **Expected Result**: 
  - Status: SAFE
  - Requirement met: Yes
  - Days remaining: 0

### Scenario 2: Partially Met
- **Setup**:
  - Account start date: 2024-01-01
  - Current date: 2024-01-03
  - Trading days count: 1 (traded on Jan 2 only)
- **Action**: Have 1 of 2 required days
- **Expected Result**:
  - Status: CAUTION
  - Requirement met: No
  - Days remaining: 1

### Scenario 3: Not Met (New Account)
- **Setup**:
  - Account start date: 2024-01-01
  - Current date: 2024-01-01 (same day)
  - Trading days count: 0
- **Action**: Account just started, no trades yet
- **Expected Result**:
  - Status: CRITICAL (new account, expected)
  - Requirement met: No
  - Days remaining: 2

### Scenario 4: Not Met (Extended Period)
- **Setup**:
  - Account start date: 2024-01-01
  - Current date: 2024-01-10
  - Trading days count: 0
- **Action**: Account has been active for 10 days with no closed trades
- **Expected Result**:
  - Status: CRITICAL
  - Requirement met: No
  - Days remaining: 2

## Implementation Notes

1. **Day Counting**: A trading day is a calendar day (00:00:00 to 23:59:59) where at least one trade was closed
2. **Open Positions**: Do not count toward trading days
3. **Multiple Trades**: Multiple closed trades on same day = 1 trading day
4. **Time Zone**: Use account timezone or UTC consistently
5. **Requirement**: Topstep requires 2 trading days (vs Apex's 1 day)

## References

- Topstep official rules: Minimum 2 trading days for evaluation accounts
- This is a pass requirement, not a failure condition
