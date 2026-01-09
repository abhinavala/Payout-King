# Project Status

## Current Phase: PHASE 1 — RULE SPECIFICATION

### ✅ Completed

#### PHASE 0 — FOUNDATION & DISCIPLINE
- [x] Project structure created (monorepo)
- [x] Foundational documentation
  - [x] README.md
  - [x] Master Execution Plan
  - [x] No-Rewrite Rule document
  - [x] Architecture documentation
- [x] Rule specification template created
- [x] Directory structure for firm-specific rules

### 🚧 In Progress

#### PHASE 1 — RULE SPECIFICATION
- [x] 1.1 Create Rule Spec Templates ✅
- [ ] 1.2 Write Full Rule Specs
  - [ ] Apex (Evaluation, PA, Funded)
  - [ ] Topstep (Evaluation, Funded)
- [ ] 1.3 Validate Rule Specs with Scenarios

### 📋 Next Steps

1. **Write Apex Rule Specs** (PHASE 1.2)
   - Start with Trailing Max Drawdown for Evaluation accounts
   - Document all rules for each account type
   - Include exact mathematical formulas

2. **Write Topstep Rule Specs** (PHASE 1.2)
   - Follow same structure as Apex
   - Document all rules for each account type

3. **Validate with Scenarios** (PHASE 1.3)
   - Create safe/boundary/violation cases for each rule
   - Verify math by hand

## Project Structure

```
payout-king/
├── apps/
│   ├── backend/          (FastAPI - not started)
│   ├── frontend/         (React - not started)
│   └── ninjatrader-addon/ (C# - not started)
├── packages/
│   └── rules-engine/     (Python - not started)
├── docs/
│   ├── MASTER_PLAN.md
│   ├── NO_REWRITE_RULE.md
│   ├── ARCHITECTURE.md
│   ├── PROJECT_STATUS.md
│   └── rules/
│       ├── RULE_SPEC_TEMPLATE.md
│       ├── README.md
│       ├── apex/
│       └── topstep/
├── README.md
└── package.json
```

## Important Reminders

⚠️ **Do not code during PHASE 1**
- Rule specifications must be complete and validated before implementation
- All rules must have exact mathematical formulas
- All rules must have three validation scenarios

✅ **Follow the No-Rewrite Rule**
- Fix specs, not code
- Every change must reference a spec

## Notes

- Desktop-first architecture is locked
- Rule engine is core IP
- Exact math > heuristics
- Real-time correctness > convenience
