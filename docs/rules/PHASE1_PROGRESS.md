# PHASE 1 Progress Report

## Status: IN PROGRESS

Following the Master Execution Plan, we are in **PHASE 1: RULE SPECIFICATION**.

## Completed Specifications

### Apex Trader Funding

#### ✅ Trailing Max Drawdown
- [x] Evaluation accounts - 5% trailing, includes unrealized PnL
- [x] PA accounts - 5% trailing, includes unrealized PnL  
- [x] Funded accounts - 5% trailing, includes unrealized PnL

**Key Details:**
- Real-time evaluation (not end-of-day)
- Includes unrealized PnL
- HWM updates immediately when equity exceeds previous HWM
- Never resets (except account restart)

#### ✅ Minimum Trading Days
- [x] Evaluation accounts - 1 trading day required

### Topstep

#### ✅ Trailing Max Drawdown (End-of-Day)
- [x] Evaluation accounts - 4% end-of-day, balance only

**Key Details:**
- End-of-day evaluation only (4:00 PM CT)
- Balance only (excludes unrealized PnL)
- HWM updates only at end of day
- Never resets (except account restart)

#### ✅ Daily Loss Limit
- [x] Evaluation accounts - ~2% of account size ($1,000 for $50k account)

**Key Details:**
- Resets daily at 4:00 PM CT
- Balance only (excludes unrealized PnL)
- Continuous evaluation during trading day

#### ✅ Consistency Rule
- [x] Evaluation accounts - 50% maximum single-day profit concentration

**Key Details:**
- Only applies when total profit is positive
- Prevents passing evaluation if violated
- Can be recovered by making profits on additional days

#### ✅ Minimum Trading Days
- [x] Evaluation accounts - 2 trading days required

## Remaining Specifications

### Apex
- [ ] Maximum Position Size (all account types)
- [ ] Trading Hours (all account types)
- [ ] Profit Targets (all account types)

### Topstep
- [ ] Trailing Drawdown - Funded accounts
- [ ] Daily Loss Limit - Funded accounts (if different)
- [ ] Consistency Rule - Funded accounts (if applicable)
- [ ] Maximum Position Size (all account types)
- [ ] Trading Hours (all account types)
- [ ] Profit Targets (all account types)

## Specification Quality Checklist

Each completed specification includes:
- [x] Exact mathematical formulas
- [x] State variables with update/reset conditions
- [x] Threshold definitions
- [x] Reset behavior
- [x] Violation conditions
- [x] Recoverability status
- [x] Edge cases
- [x] Status levels (SAFE/CAUTION/CRITICAL/VIOLATED)
- [x] Distance-to-violation calculations
- [x] Three validation scenarios (safe/boundary/violation)

## Next Steps

1. **Complete remaining rule specifications** for Apex and Topstep
2. **PHASE 1.3: Validate all scenarios** by hand calculation
3. **Review all specifications** for mathematical correctness
4. **Move to PHASE 2** only after all specs are complete and validated

## Important Notes

⚠️ **Do not code during PHASE 1** - All rule specifications must be complete and validated before implementation.

✅ **Follow the No-Rewrite Rule** - If something is wrong, fix it at the spec level, not by patching code.

## Files Created

### Apex
- `docs/rules/apex/trailing_drawdown_evaluation.md`
- `docs/rules/apex/trailing_drawdown_pa.md`
- `docs/rules/apex/trailing_drawdown_funded.md`
- `docs/rules/apex/minimum_trading_days_evaluation.md`
- `docs/rules/apex/README.md`

### Topstep
- `docs/rules/topstep/trailing_drawdown_evaluation.md`
- `docs/rules/topstep/daily_loss_limit_evaluation.md`
- `docs/rules/topstep/consistency_evaluation.md`
- `docs/rules/topstep/minimum_trading_days_evaluation.md`
- `docs/rules/topstep/README.md`
