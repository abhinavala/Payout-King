# Rule Specifications

This directory contains the authoritative rule specifications for each prop firm.

## Structure

```
/rules
  /apex
    - evaluation.md
    - pa.md
    - funded.md
  /topstep
    - evaluation.md
    - pa.md
    - funded.md
  /mff
    - [future]
  /bulenox
    - [future]
  /takeprofit
    - [future]
```

## Rule Categories

### Objective (Enforced)
- Trailing max drawdown (including unrealized PnL)
- Maximum adverse excursion (MAE)
- Daily loss limit
- Overall max loss
- Max position size
- Trading hours
- Minimum trading days
- Consistency / profit concentration

### Subjective (Adjective only)
- "Gaming" behavior
- Excessive scalping
- Latency abuse

Subjective rules never hard-block actions.

## Status Levels

Every rule must define these status levels:

- **SAFE**: Well within limits
- **CAUTION**: Approaching threshold (e.g., within 20%)
- **CRITICAL**: Imminent violation (e.g., within 5%)
- **VIOLATED**: Threshold breached

## Validation Requirements

Each rule specification must include:
1. Exact mathematical formulas
2. Three validation scenarios (safe, boundary, violation)
3. Edge case handling
4. Reset behavior
5. Recoverability status

## Template

Use [RULE_SPEC_TEMPLATE.md](./RULE_SPEC_TEMPLATE.md) as the starting point for all new rule specifications.
