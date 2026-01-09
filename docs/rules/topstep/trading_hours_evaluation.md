# Rule Specification: Topstep Trading Hours (Evaluation)

## Rule Identity

- **Rule Name**: Trading Hours / Position Close Requirement
- **Firm**: Topstep
- **Account Type**: Evaluation
- **Applies To**: Evaluation accounts only

## Inputs Required

- [ ] Current equity (not used for this rule)
- [ ] Unrealized PnL (not used for this rule)
- [ ] Realized PnL (not used for this rule)
- [ ] High-water mark (not used for this rule)
- [x] Current time (to determine if within trading hours)
- [x] Open positions (to check if positions must be closed)
- [ ] Position size (not used for this rule)
- [ ] Trading days count (not used for this rule)

## State Variables

- **current_time**: Current timestamp
  - Update condition: Continuously
  - Reset condition: N/A

- **trading_day_end**: End of trading day time
  - Value: 3:10 PM CT (Central Time) or market close, whichever is earlier
  - Update condition: Never (fixed)
  - Reset condition: N/A

- **market_close_time**: Official market close time
  - Varies by instrument
  - Update condition: Varies by instrument
  - Reset condition: N/A

## Threshold Definition

- **Threshold Type**: Time-based
- **Threshold Value**: 3:10 PM CT (Central Time)
- **Calculation Method**: 
  1. Check current time
  2. If time >= 3:10 PM CT, positions must be closed
  3. If time >= market close (for instruments that close earlier), positions must be closed
  4. Violation occurs when: `current_time >= trading_day_end` AND `open_positions_count > 0`

**Important**: 
- Positions must be closed by 3:10 PM CT OR market close, whichever is earlier
- This applies to evaluation accounts
- Funded accounts may have different rules

## Reset Behavior

- **Resets Daily**: Yes
- **Resets Weekly**: No
- **Resets Monthly**: No
- **Resets Never**: No
- **Reset Time**: 3:10 PM CT (end of requirement period)
- **Reset Condition**: Daily - requirement applies each trading day

## Violation Condition

Exact mathematical condition that triggers violation:

```
current_time >= trading_day_end AND open_positions_count > 0
```

Where:
- `trading_day_end = min(3:10 PM CT, market_close_time)`
- `open_positions_count = count(all_open_positions)`

**Important**: 
- Violation occurs if positions are still open at or after 3:10 PM CT
- Must close positions before this time
- Time zone is Central Time (CT)

## Recoverability

- **Can violation be fixed?**: No (time-based, cannot go back)
- **Recovery method**: N/A
- **Permanent consequence**: Account is failed. Cannot continue trading on this account.

## Edge Cases

1. **Edge Case**: Position closed at exactly 3:10 PM CT
   - **Handling**: `current_time >= 3:10 PM CT` means violation. Must close before 3:10 PM CT. Closing exactly at 3:10 PM CT may be considered a violation (verify with Topstep).

2. **Edge Case**: Market closes before 3:10 PM CT
   - **Handling**: Use market close time as the deadline. If market closes at 3:00 PM CT, that's the deadline (not 3:10 PM CT).

3. **Edge Case**: Multiple positions
   - **Handling**: All positions must be closed. If any position remains open, violation occurs.

4. **Edge Case**: Partial close
   - **Handling**: All positions must be fully closed. Partial closes do not satisfy the requirement.

5. **Edge Case**: Time zone confusion
   - **Handling**: 3:10 PM CT (Central Time). Must account for daylight saving time changes.

6. **Edge Case**: Weekend/holiday
   - **Handling**: Rule applies only on trading days. No requirement on non-trading days.

## Status Levels

**Before 3:10 PM CT**:
- **SAFE**: `current_time < (trading_day_end - 30 minutes)` AND `open_positions_count == 0`
  - More than 30 minutes before deadline, positions closed

- **CAUTION**: `(trading_day_end - 30 minutes) <= current_time < (trading_day_end - 10 minutes)` AND `open_positions_count > 0`
  - Between 30 and 10 minutes before deadline, positions still open

- **CRITICAL**: `(trading_day_end - 10 minutes) <= current_time < trading_day_end` AND `open_positions_count > 0`
  - Less than 10 minutes before deadline, positions still open

- **VIOLATED**: `current_time >= trading_day_end` AND `open_positions_count > 0`
  - At or after deadline, positions still open

**After 3:10 PM CT**:
- If positions are closed: Status is N/A (requirement satisfied)
- If positions are open: Status is VIOLATED

## Distance-to-Violation Calculation

How to compute remaining buffer:

```
if open_positions_count > 0:
    time_until_deadline = trading_day_end - current_time
    distance_to_violation = time_until_deadline
else:
    distance_to_violation = N/A (requirement satisfied)
```

Units: Time (minutes/seconds)

If `distance_to_violation <= 0`, violation has occurred.

## Validation Scenarios

### Scenario 1: Safe Case
- **Setup**: 
  - Current time: 2:30 PM CT
  - Trading day end: 3:10 PM CT
  - Open positions: 0 (all closed)
- **Action**: Positions closed, 40 minutes before deadline
- **Expected Result**: 
  - Status: SAFE
  - Distance to violation: N/A (requirement satisfied)
  - No action needed

### Scenario 2: Caution Case
- **Setup**:
  - Current time: 2:50 PM CT
  - Trading day end: 3:10 PM CT
  - Open positions: 2 (still open)
- **Action**: 20 minutes before deadline, positions still open
- **Expected Result**:
  - Status: CAUTION
  - Distance to violation: 20 minutes
  - Must close positions soon

### Scenario 3: Critical Case
- **Setup**:
  - Current time: 3:05 PM CT
  - Trading day end: 3:10 PM CT
  - Open positions: 1 (still open)
- **Action**: 5 minutes before deadline, position still open
- **Expected Result**:
  - Status: CRITICAL
  - Distance to violation: 5 minutes
  - Must close immediately

### Scenario 4: Violation Case
- **Setup**:
  - Current time: 3:10 PM CT
  - Trading day end: 3:10 PM CT
  - Open positions: 1 (still open)
- **Action**: At deadline, position still open
- **Expected Result**:
  - Status: VIOLATED
  - Distance to violation: 0 minutes (violation occurred)
  - Account failed

### Scenario 5: Market Close Before 3:10 PM
- **Setup**:
  - Current time: 2:55 PM CT
  - Market close: 3:00 PM CT (for specific instrument)
  - Trading day end: 3:00 PM CT (market close, not 3:10 PM)
  - Open positions: 1 (still open)
- **Action**: 5 minutes before market close, position still open
- **Expected Result**:
  - Status: CRITICAL
  - Distance to violation: 5 minutes (to market close, not 3:10 PM)
  - Must close before market close

## Implementation Notes

1. **Time Zone**: Use Central Time (CT) consistently
2. **Daylight Saving**: Account for DST changes
3. **Market Close**: Check instrument-specific market close times
4. **Real-time**: Monitor continuously during trading day
5. **Position Count**: Check all open positions, not just net position
6. **Evaluation Only**: This rule applies to evaluation accounts. Funded accounts may have different rules.

## References

- Topstep official rules: Positions must be closed by 3:10 PM CT or market close
- Applies to evaluation accounts
- Time zone: Central Time (CT)
