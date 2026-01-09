# Rule Specification: Apex Maximum Position Size

## Rule Identity

- **Rule Name**: Maximum Position Size
- **Firm**: Apex Trader Funding
- **Account Type**: All (Evaluation, PA, Funded)
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
  - **$25,000 account**: 3 contracts (standard) or equivalent
  - **$50,000 account**: 6 contracts (standard) or equivalent
  - **$75,000 account**: 9 contracts (standard) or equivalent
  - **$100,000 account**: 12 contracts (standard) or equivalent
  - **$150,000 account**: 18 contracts (standard) or equivalent
  - **$250,000 account**: 30 contracts (standard) or equivalent
  - **$300,000 account**: 36 contracts (standard) or equivalent

**General Formula**: Approximately 12 contracts per $100,000 account size

**Micro Contracts**: 
- 1 standard contract = 10 micro contracts
- Example: $50,000 account = 6 standard OR 60 micro contracts

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
- Position size is the total of all open positions (can be net or gross, verify with Apex)
- Typically calculated as gross position (sum of absolute values of all positions)
- Applies to all instruments combined (not per-instrument)

## Recoverability

- **Can violation be fixed?**: Yes (by reducing position size)
- **Recovery method**: Close positions to bring total below limit
- **Permanent consequence**: None if corrected before account review. May cause account closure if persistent.

## Edge Cases

1. **Edge Case**: Position size exactly equals limit
   - **Handling**: `current_position_size > max_position_size` means violation. Exact equality is allowed (not a violation).

2. **Edge Case**: Multiple instruments
   - **Handling**: Position size is typically calculated as total across all instruments. Verify if Apex uses gross or net position.

3. **Edge Case**: Micro vs Standard contracts
   - **Handling**: Must convert to equivalent. 1 standard = 10 micro. Calculate total in standard contract equivalents.

4. **Edge Case**: Partial fills
   - **Handling**: Position size is based on filled quantity, not order quantity.

5. **Edge Case**: Account size between tiers
   - **Handling**: Use the lower tier's limit. Example: $60,000 account uses $50,000 tier limit (6 contracts).

## Status Levels

- **SAFE**: `current_position_size <= (max_position_size * 0.80)`
  - Less than 80% of limit
  - Example: If limit is 6 contracts, safe if position <= 4 contracts

- **CAUTION**: `(max_position_size * 0.80) < current_position_size <= (max_position_size * 0.95)`
  - Between 80% and 95% of limit
  - Example: If limit is 6 contracts, caution if position is 5 contracts

- **CRITICAL**: `(max_position_size * 0.95) < current_position_size < max_position_size`
  - Between 95% and 100% of limit
  - Example: If limit is 6 contracts, critical if position is 5-6 contracts

- **VIOLATED**: `current_position_size > max_position_size`
  - Exceeds limit

## Distance-to-Violation Calculation

How to compute remaining buffer:

```
distance_to_violation = max_position_size - current_position_size
```

Units: Contracts

If `distance_to_violation < 0`, violation has occurred.

## Validation Scenarios

### Scenario 1: Safe Case
- **Setup**: 
  - Account size: $50,000
  - Max position size: 6 contracts
  - Current position: 3 contracts (long ES)
- **Action**: Position is 50% of limit
- **Expected Result**: 
  - Status: SAFE
  - Distance to violation: 3 contracts
  - Buffer: 50% of limit remaining

### Scenario 2: Boundary Case
- **Setup**:
  - Account size: $50,000
  - Max position size: 6 contracts
  - Current position: 6 contracts (long ES)
- **Action**: Position exactly at limit
- **Expected Result**:
  - Status: SAFE (at limit, not exceeding)
  - Distance to violation: 0 contracts
  - Buffer: 0% remaining

### Scenario 3: Violation Case
- **Setup**:
  - Account size: $50,000
  - Max position size: 6 contracts
  - Current position: 8 contracts (long ES)
- **Action**: Position exceeds limit by 2 contracts
- **Expected Result**:
  - Status: VIOLATED
  - Distance to violation: -2 contracts (negative = violation)
  - Must reduce position immediately

### Scenario 4: Multiple Instruments
- **Setup**:
  - Account size: $50,000
  - Max position size: 6 contracts (standard equivalent)
  - Current positions: 3 contracts ES (standard) + 30 contracts MES (micro = 3 standard equivalent)
  - Total: 6 standard contract equivalents
- **Action**: Total position equals limit
- **Expected Result**:
  - Status: SAFE (at limit)
  - Distance to violation: 0 contracts
  - Cannot add more positions

### Scenario 5: Mixed Long/Short
- **Setup**:
  - Account size: $50,000
  - Max position size: 6 contracts
  - Current positions: 5 contracts long ES + 2 contracts short ES
  - Net position: 3 contracts
  - Gross position: 7 contracts
- **Action**: Gross position exceeds limit
- **Expected Result**:
  - Status: VIOLATED (if Apex uses gross position)
  - OR Status: SAFE (if Apex uses net position)
  - **Note**: Must verify with Apex whether they use gross or net position calculation

## Implementation Notes

1. **Account Size Tiers**: Position limits are based on account size tiers, not continuous calculation
2. **Contract Equivalents**: Must convert micro to standard (1:10 ratio)
3. **Gross vs Net**: Verify whether Apex uses gross (sum of absolute values) or net (algebraic sum) position
4. **All Instruments**: Typically applies to total across all instruments, not per-instrument
5. **Real-time**: Check on every order fill and position change

## References

- Apex Trader Funding official rules
- Position limits vary by account size
- Approximately 12 contracts per $100,000 account size
- Verify gross vs net position calculation method
