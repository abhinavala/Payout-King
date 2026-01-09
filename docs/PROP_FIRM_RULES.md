# Prop Firm Rules Reference

This document details the specific rules for each supported prop firm.

## Apex Trader Funding

**Account Types**: Eval, PA, Funded

### Rules

- **Trailing Drawdown**: 5% (intraday, includes unrealized PnL)
  - Updates in real-time as equity changes
  - Based on highest equity reached (high-water mark)
  
- **Daily Loss Limit**: None
  - No daily loss limit restriction
  
- **Consistency Rule**: None
  - No consistency requirements
  
- **News Trading**: Allowed
  - Can trade during news events
  
- **Minimum Trading Days**: 1 day (for evaluation)

### Example
- $50,000 account → $2,500 trailing drawdown
- If equity reaches $52,500, drawdown threshold becomes $49,875

---

## Topstep

**Account Types**: Eval, PA, Funded

### Rules

- **Trailing Drawdown**: 4% (end-of-day, balance only)
  - Calculated at end of trading day
  - Based on balance, not intraday equity
  
- **Daily Loss Limit**: $1,000 (for $50k account)
  - Approximately 2% of account size
  - Resets at 4:00 PM CT
  
- **Consistency Rule**: 50% during evaluation
  - No single day can account for more than 50% of total profit
  
- **News Trading**: Allowed
  - Can trade during news events
  
- **Minimum Trading Days**: 2 days (for evaluation)

### Example
- $50,000 account → $2,000 end-of-day drawdown
- Daily loss limit: $1,000
- Must close positions before 3:10 PM CT or market close

---

## My Funded Futures (MFF)

**Account Types**: Eval, PA, Funded

### Rules

- **Trailing Drawdown**: 5% (varies by account type)
  - Includes unrealized PnL
  - Updates in real-time
  
- **Daily Loss Limit**: ~5% of account balance
  - For $50k account: ~$2,500
  - Resets daily
  
- **Consistency Rule**: Varies by account type
  - Check specific account terms
  
- **News Trading**: Allowed
  - With restrictions during high-impact events

---

## Bulenox

**Account Types**: Eval, PA, Funded

### Rules

- **Trailing Drawdown**: 5% (intraday, includes unrealized PnL)
  - Updates in real-time
  - Based on high-water mark
  
- **Daily Loss Limit**: 4% of account balance
  - For $50k account: $2,000
  - Resets daily
  
- **Consistency Rule**: 40%
  - No single day can account for more than 40% of total profit
  
- **News Trading**: **NOT Allowed**
  - Cannot trade during news events
  
- **Position Holding**: Overnight allowed, not over weekends

### Example
- $50,000 account → $2,500 trailing drawdown
- Daily loss limit: $2,000

---

## TakeProfitTrader

**Account Types**: Eval, PA, Funded

### Rules

**During Evaluation**:
- **Trailing Drawdown**: 5% (end-of-day, balance only)
- **Daily Loss Limit**: Varies by account size
- **Consistency Rule**: 50%
  - No single day > 50% of total profit
- **News Trading**: **NOT Allowed**

**When Funded**:
- **Trailing Drawdown**: 5% (trailing, includes unrealized PnL)
- **Daily Loss Limit**: None
- **Consistency Rule**: None
- **News Trading**: **NOT Allowed**

- **Minimum Trading Days**: 5 days (for evaluation)

---

## Rule Comparison Table

| Firm | Drawdown Type | Drawdown % | Daily Loss Limit | Consistency | News Trading |
|------|--------------|------------|------------------|-------------|--------------|
| **Apex** | Trailing (intraday) | 5% | None | None | ✅ Allowed |
| **Topstep** | End-of-day | 4% | $1k ($50k acct) | 50% (eval) | ✅ Allowed |
| **MFF** | Trailing (intraday) | 5% | ~5% of balance | Varies | ✅ Allowed |
| **Bulenox** | Trailing (intraday) | 5% | 4% of balance | 40% | ❌ Not Allowed |
| **TakeProfit** | EOD (eval), Trailing (funded) | 5% | Varies | 50% (eval) | ❌ Not Allowed |

---

## Important Notes

1. **Trailing vs End-of-Day**: 
   - Trailing = updates in real-time as equity changes
   - End-of-day = calculated at end of trading day only

2. **Unrealized PnL**:
   - Some firms include unrealized PnL in drawdown calculations
   - Others use balance only

3. **Account Type Differences**:
   - Eval accounts often have stricter rules
   - Funded accounts may have different rules

4. **Rule Versions**:
   - Rules may change over time
   - Always verify current rules with firm

---

## Implementation

Rules are implemented in `apps/backend/app/services/rule_loader.py`

To add a new firm:
1. Add firm info to `_get_{firm}_rules()` method
2. Add firm to `get_supported_firms()` list
3. Update this documentation
4. Test with real account scenarios

