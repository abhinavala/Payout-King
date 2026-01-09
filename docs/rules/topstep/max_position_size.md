# Rule Specification: Topstep Maximum Position Size

## Rule Identity

- **Rule Name**: Maximum Position Size
- **Firm**: Topstep
- **Account Type**: All (Evaluation, Funded)
- **Applies To**: All account types

## Inputs Required

- [ ] Current equity (not used for this rule)
- [ ] Unrealized PnL (not used for this rule)
- [ ] Realized PnL (not used for this rule)
- [x] Account size (starting balance)
- [x] Current position size (total contracts/lots in open positions)
- [x] Instrument type (micro vs standard contracts)
- [ ] Time of day (not used for this rule)
- [ ] Trading days count (not used for this rule)

## State Variables

- **account_size**: Starting account balance
  - Initial value: Account creation balance
  - Update condition: Never (fixed at account creation)
  - Reset condition: Account reset only

- **max_position_size**: Maximum allowed position size
  - Initial value: Calculated based on account size
  - Update condition: Never (fixed based on account size)
  - Calculation: See threshold definition below
  - Reset condition: Account reset only

## Threshold Definition

- **Threshold Type**: Fixed based on account size
- **Threshold Value**: Varies by account size
  - **$50,000 account**: 5 contracts (standard) or equivalent
  - **$100,000 account**: 10 contracts (standard) or equivalent
  - **$150,000 account**: 15 contracts (standard) or equivalent

**General Formula**: Approximately 10 contracts per $100,000 account size

**Micro Contracts**: 
- 1 standard contract = 10 micro contracts
- Example: $50,000 account = 5 standard OR 50 micro contracts

- **Calculation Method**: 
  1. Determine account size tier
  2. Look up maximum position size for that tier
  3. Violation occurs when: `current_position_size > max_position_size`

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
current_position_size > max_position_size
```

Where:
- `current_position_size = sum(all_open_position_quantities)` (absolute value)
- `max_position_size = lookup_by_account_size(account_size)`

**Important**: 
- Position size is typically calculated as gross position (sum of absolute values)
- Applies to all instruments combined
- Verify exact calculation method with Topstep

## Recoverability

- **Can violation be fixed?**: Yes (by reducing position size)
- **Recovery method**: Close positions to bring total below limit
- **Permanent consequence**: None if corrected before account review. May cause account closure if persistent.

## Edge Cases

1. **Edge Case**: Position size exactly equals limit
   - **Handling**: `current_position_size > max_position_size` means violation. Exact equality is allowed (not a violation).

2. **Edge Case**: Multiple instruments
   - **Handling**: Position size is typically calculated as total across all instruments.

3. **Edge Case**: Micro vs Standard contracts
   - **Handling**: Must convert to equivalent. 1 standard = 10 micro.

4. **Edge Case**: Account size between tiers
   - **Handling**: Use the lower tier's limit.

## Status Levels

- **SAFE**: `current_position_size <= (max_position_size * 0.80)`
- **CAUTION**: `(max_position_size * 0.80) < current_position_size <= (max_position_size * 0.95)`
- **CRITICAL**: `(max_position_size * 0.95) < current_position_size < max_position_size`
- **VIOLATED**: `current_position_size > max_position_size`

## Distance-to-Violation Calculation

```
distance_to_violation = max_position_size - current_position_size
```

Units: Contracts

## Validation Scenarios

### Scenario 1: Safe Case
- **Setup**: 
  - Account size: $50,000
  - Max position size: 5 contracts
  - Current position: 2 contracts (long ES)
- **Action**: Position is 40% of limit
- **Expected Result**: 
  - Status: SAFE
  - Distance to violation: 3 contracts

### Scenario 2: Boundary Case
- **Setup**:
  - Account size: $50,000
  - Max position size: 5 contracts
  - Current position: 5 contracts
- **Action**: Position exactly at limit
- **Expected Result**:
  - Status: SAFE (at limit, not exceeding)
  - Distance to violation: 0 contracts

### Scenario 3: Violation Case
- **Setup**:
  - Account size: $50,000
  - Max position size: 5 contracts
  - Current position: 6 contracts
- **Action**: Position exceeds limit
- **Expected Result**:
  - Status: VIOLATED
  - Distance to violation: -1 contract

## Implementation Notes

1. **Account Size Tiers**: Position limits are based on account size tiers
2. **Contract Equivalents**: Must convert micro to standard (1:10 ratio)
3. **Verify Calculation**: Confirm gross vs net position with Topstep
4. **Real-time**: Check on every order fill

## References

- Topstep official rules
- Position limits vary by account size
- Approximately 10 contracts per $100,000 account size
