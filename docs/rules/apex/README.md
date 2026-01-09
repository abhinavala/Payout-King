# Apex Trading Rule Specifications

This directory contains detailed rule specifications for Apex Trader Funding prop firm accounts.

## Account Types

- **Evaluation**: Challenge accounts (must pass before PA)
- **PA (Paid Account)**: Funded accounts with profit targets
- **Funded**: Fully funded accounts

## Rules Documented

### Trailing Max Drawdown
- [x] [Evaluation](./trailing_drawdown_evaluation.md) - 5% trailing, includes unrealized PnL
- [x] [PA](./trailing_drawdown_pa.md) - 5% trailing, includes unrealized PnL
- [x] [Funded](./trailing_drawdown_funded.md) - 5% trailing, includes unrealized PnL

### Minimum Trading Days
- [x] [Evaluation](./minimum_trading_days_evaluation.md) - 1 trading day required

### Daily Loss Limit
- [ ] Not applicable - Apex has no daily loss limit

### Consistency Rule
- [ ] Not applicable - Apex has no consistency requirements

### Maximum Position Size
- [ ] To be specified (varies by account size)

### Trading Hours
- [ ] To be specified (typically standard futures hours)

### Profit Target
- [ ] To be specified (varies by account type and size)

## Key Characteristics

1. **Trailing Drawdown**: All account types use identical 5% trailing drawdown
   - Includes unrealized PnL in real-time
   - Updates as high-water mark changes
   - Never resets (except account restart)

2. **No Daily Loss Limit**: Apex does not enforce daily loss limits

3. **No Consistency Rule**: Apex does not require profit consistency

4. **News Trading**: Allowed

5. **Minimum Trading Days**: 1 day for evaluation accounts

## Status

🚧 **IN PROGRESS** - Following PHASE 1 of the master plan.

Each rule follows the [RULE_SPEC_TEMPLATE.md](../RULE_SPEC_TEMPLATE.md) format with:
- Exact mathematical formulas
- State variables
- Reset behavior
- Violation conditions
- Three validation scenarios (safe/boundary/violation)

## Next Steps

1. Complete remaining Apex rules (position size, trading hours, profit targets)
2. Validate all scenarios by hand
3. Move to Topstep specifications
