# Topstep Rule Specifications

This directory contains detailed rule specifications for Topstep prop firm accounts.

## Account Types

- **Evaluation**: Challenge accounts (must pass before Funded)
- **Funded**: Fully funded accounts

## Rules Documented

### Trailing Max Drawdown (End-of-Day)
- [x] [Evaluation](./trailing_drawdown_evaluation.md) - 4% end-of-day, balance only (no unrealized PnL)

### Daily Loss Limit
- [x] [Evaluation](./daily_loss_limit_evaluation.md) - ~2% of account size (e.g., $1,000 for $50k account)

### Consistency Rule
- [x] [Evaluation](./consistency_evaluation.md) - 50% maximum single-day profit concentration

### Minimum Trading Days
- [x] [Evaluation](./minimum_trading_days_evaluation.md) - 2 trading days required

### Maximum Position Size
- [ ] To be specified (varies by account size)

### Trading Hours
- [ ] To be specified (must close positions before 3:10 PM CT or market close)

### Profit Target
- [ ] To be specified (varies by account type and size)

## Key Characteristics

1. **End-of-Day Drawdown**: 4% of high-water mark, evaluated only at end of trading day (4:00 PM CT)
   - Uses balance only (excludes unrealized PnL)
   - Not trailing during the day (unlike Apex)
   - HWM updates only at end of day

2. **Daily Loss Limit**: Approximately 2% of account size
   - For $50,000 account: $1,000
   - Resets daily at 4:00 PM CT
   - Only realized PnL counts

3. **Consistency Rule**: No single day can account for more than 50% of total profit
   - Only applies when total profit is positive
   - Prevents passing evaluation if violated (not immediate failure)

4. **Minimum Trading Days**: 2 days for evaluation accounts

5. **News Trading**: Allowed

## Critical Differences from Apex

| Feature | Apex | Topstep |
|---------|------|---------|
| Drawdown Type | Trailing (intraday) | End-of-day only |
| Drawdown % | 5% | 4% |
| Includes Unrealized | Yes | No (balance only) |
| Daily Loss Limit | None | ~2% of account |
| Consistency Rule | None | 50% max |
| Min Trading Days | 1 | 2 |

## Status

🚧 **IN PROGRESS** - Following PHASE 1 of the master plan.

Each rule follows the [RULE_SPEC_TEMPLATE.md](../RULE_SPEC_TEMPLATE.md) format with:
- Exact mathematical formulas
- State variables
- Reset behavior
- Violation conditions
- Three validation scenarios (safe/boundary/violation)

## Next Steps

1. Complete remaining Topstep rules (position size, trading hours, profit targets)
2. Add Funded account specifications
3. Validate all scenarios by hand
4. Move to PHASE 1.3 (validation)
