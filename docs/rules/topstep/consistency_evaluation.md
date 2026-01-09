# Rule Specification: Topstep Consistency Rule (Evaluation)

## Rule Identity

- **Rule Name**: Consistency Rule (Profit Concentration)
- **Firm**: Topstep
- **Account Type**: Evaluation
- **Applies To**: Evaluation accounts only

## Inputs Required

- [x] Total realized PnL (cumulative since account start)
- [x] Daily realized PnL (per trading day)
- [x] Trading days with closed trades
- [ ] Current equity (not used for this rule)
- [ ] Unrealized PnL (not used for this rule)
- [ ] Position size (not used for this rule)
- [ ] Time of day (not used for this rule)

## State Variables

- **total_realized_pnl**: Cumulative realized PnL since account start
  - Initial value: 0
  - Update condition: Increments/decrements with each closed trade
  - Reset condition: Never (except account reset/restart)

- **daily_realized_pnl_history**: Dictionary of daily realized PnL by date
  - Key: Trading date (YYYY-MM-DD)
  - Value: Realized PnL for that day
  - Update condition: Updated when trades close on a given day
  - Reset condition: Never (except account reset/restart)

- **max_single_day_profit**: Highest single-day profit achieved
  - Initial value: 0 (or negative if first day is a loss)
  - Update condition: Updated whenever a day's profit exceeds current max
  - Calculation: `max(all_daily_profits)`
  - Reset condition: Never (except account reset/restart)

## Threshold Definition

- **Threshold Type**: Percentage-based
- **Threshold Value**: 50% of total profit
- **Calculation Method**: 
  1. Calculate total realized PnL: `total_pnl = sum(all_daily_pnl)`
  2. Find maximum single-day profit: `max_day = max(daily_pnl_history.values())`
  3. Calculate percentage: `percentage = (max_day / total_pnl) * 100` (if total_pnl > 0)
  4. Violation occurs when: `max_day > (total_pnl * 0.50)` AND `total_pnl > 0`

**Important**: 
- Only applies when total PnL is positive
- If total PnL is negative or zero, rule does not apply
- Single day cannot account for more than 50% of total profit

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
max_single_day_profit > (total_realized_pnl * 0.50) AND total_realized_pnl > 0
```

Where:
- `max_single_day_profit = max(all_daily_profits)`
- `total_realized_pnl = sum(all_daily_profits)`

**Note**: If `total_realized_pnl <= 0`, rule does not apply (no violation possible).

## Recoverability

- **Can violation be fixed?**: Yes (by making profit on other days)
- **Recovery method**: Continue trading and make profits on additional days to reduce the percentage
- **Permanent consequence**: None. This is a pass requirement, not an immediate failure. Account cannot pass evaluation until requirement is met.

## Edge Cases

1. **Edge Case**: Total PnL is negative
   - **Handling**: Rule does not apply. No violation possible when total PnL is negative or zero.

2. **Edge Case**: Total PnL is exactly zero
   - **Handling**: Rule does not apply. No violation possible.

3. **Edge Case**: Single day equals exactly 50% of total
   - **Handling**: `max_day > (total * 0.50)` means violation. Exact 50% is allowed (not a violation).

4. **Edge Case**: Multiple days with same profit
   - **Handling**: Only the maximum single day matters. If multiple days have the same profit, it's still just one day's contribution.

5. **Edge Case**: First profitable day
   - **Handling**: If first day has $1,000 profit and total is $1,000, that's 100% (violation). Need additional profitable days.

6. **Edge Case**: Loss day then profit day
   - **Handling**: Only profitable days count toward the percentage. If you lose $500 on day 1 and make $1,000 on day 2, total is $500, max day is $1,000. But wait - if day 2 profit is $1,000 and total is $500, that means day 1 was -$500. So max day is $1,000 and total is $500, which means max day > total, which is impossible. Let me reconsider...
   
   Actually: If day 1: -$500, day 2: +$1,000, then total = $500, max day = $1,000. But max day cannot exceed total. The max day should be the maximum single-day profit, which is $1,000, but total is $500. This seems wrong.
   
   Correction: The consistency rule compares the largest single-day profit to the total profit. If day 1: -$500 and day 2: +$1,000, then:
   - Total PnL = $500
   - Max single-day profit = $1,000
   - But this doesn't make sense because max day profit cannot exceed total profit if we're summing all days.
   
   Actually, I think the rule means: "No single day can account for more than 50% of your total profit." So if total profit is $500, no single day should be more than $250. But if day 2 made $1,000, that's the issue.
   
   Let me reconsider: If you have losses and profits, the "total profit" might mean "net profit" (sum of all days). So if day 1: -$500, day 2: +$1,000, net = $500. The max single-day profit is $1,000. But $1,000 > 50% of $500? That's 200%, which violates the rule.
   
   I think the rule is: The largest profitable day cannot be more than 50% of your net profit. So if net is $500 and your best day was $1,000, that violates (because $1,000 > $500 * 0.50 = $250, wait that's not right either).
   
   Let me check the standard interpretation: "No single day can account for more than 50% of total profit" typically means: if your total profit across all days is $1,000, no single day should be more than $500. So if you made $600 on one day and $400 on another, the $600 day is 60% of total, which violates.
   
   So in the loss then profit case: day 1: -$500, day 2: +$1,000. Net profit = $500. Max single-day profit = $1,000. Is $1,000 > 50% of $500? $1,000 > $250? Yes, violation. But this seems odd because the $1,000 day includes recovering from the loss.
   
   I think the standard interpretation is that we look at profitable days only, or we look at net. Let me assume it's net profit for now, and note this as an edge case to clarify.

## Status Levels

- **SAFE**: `max_single_day_profit <= (total_realized_pnl * 0.40)` AND `total_realized_pnl > 0`
  - Max day is less than 40% of total
  - Example: Total $1,000, max day $350 (35%)

- **CAUTION**: `(total_realized_pnl * 0.40) < max_single_day_profit <= (total_realized_pnl * 0.45)` AND `total_realized_pnl > 0`
  - Max day is between 40% and 45% of total
  - Example: Total $1,000, max day $430 (43%)

- **CRITICAL**: `(total_realized_pnl * 0.45) < max_single_day_profit <= (total_realized_pnl * 0.50)` AND `total_realized_pnl > 0`
  - Max day is between 45% and 50% of total
  - Example: Total $1,000, max day $480 (48%)

- **VIOLATED**: `max_single_day_profit > (total_realized_pnl * 0.50)` AND `total_realized_pnl > 0`
  - Max day exceeds 50% of total
  - Example: Total $1,000, max day $600 (60%)

**Note**: If `total_realized_pnl <= 0`, status is N/A (rule does not apply).

## Distance-to-Violation Calculation

How to compute remaining buffer:

```
if total_realized_pnl > 0:
    max_allowed_single_day = total_realized_pnl * 0.50
    distance_to_violation = max_allowed_single_day - max_single_day_profit
else:
    distance_to_violation = N/A (rule does not apply)
```

Units: Dollars

If `distance_to_violation <= 0`, violation has occurred.

## Validation Scenarios

### Scenario 1: Safe Case
- **Setup**: 
  - Day 1: +$300
  - Day 2: +$400
  - Day 3: +$300
  - Total realized PnL: $1,000
  - Max single-day profit: $400
  - Percentage: 40%
- **Action**: Max day is 40% of total
- **Expected Result**: 
  - Status: SAFE
  - Distance to violation: $100 (can make up to $500 on a single day)
  - Requirement met: Yes

### Scenario 2: Boundary Case
- **Setup**:
  - Day 1: +$500
  - Day 2: +$300
  - Day 3: +$200
  - Total realized PnL: $1,000
  - Max single-day profit: $500
  - Percentage: 50%
- **Action**: Max day is exactly 50% of total
- **Expected Result**:
  - Status: SAFE (50% is allowed, violation is > 50%)
  - Distance to violation: $0 (at the limit)
  - Requirement met: Yes (barely)

### Scenario 3: Violation Case
- **Setup**:
  - Day 1: +$600
  - Day 2: +$200
  - Day 3: +$200
  - Total realized PnL: $1,000
  - Max single-day profit: $600
  - Percentage: 60%
- **Action**: Max day is 60% of total, exceeds 50% limit
- **Expected Result**:
  - Status: VIOLATED
  - Distance to violation: -$100 (exceeds limit by $100)
  - Requirement not met: Cannot pass evaluation

### Scenario 4: Recovery Case
- **Setup**:
  - Day 1: +$600 (60% of $1,000 total) - VIOLATED
  - Day 2: +$200
  - Day 3: +$200
  - Total: $1,000, Max day: $600
- **Action**: Continue trading, make $300 on Day 4
- **Expected Result**:
  - New total: $1,300
  - Max day: $600
  - New percentage: 46.2%
  - Status: CRITICAL → CAUTION (improving)
  - Distance to violation: $50 (can make up to $650 on a single day now)

### Scenario 5: Negative Total (Rule Does Not Apply)
- **Setup**:
  - Day 1: -$500
  - Day 2: -$300
  - Total realized PnL: -$800
  - Max single-day profit: N/A (all days are losses)
- **Action**: Total PnL is negative
- **Expected Result**:
  - Status: N/A (rule does not apply when total is negative)
  - No violation possible
  - Focus on getting to positive first

## Implementation Notes

1. **Only Profitable Totals**: Rule only applies when total realized PnL is positive
2. **Daily Tracking**: Must track realized PnL per trading day
3. **Date-Based**: Use trading dates, not calendar dates (account for weekends/holidays)
4. **Recovery Possible**: Violation can be fixed by making profits on additional days
5. **Pass Requirement**: This prevents passing evaluation, but doesn't cause immediate failure

## References

- Topstep official rules: 50% consistency rule for evaluation accounts
- No single day can account for more than 50% of total profit
- Only applies when total profit is positive
