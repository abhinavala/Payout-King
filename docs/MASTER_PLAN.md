# Payout King — Master Execution Plan

## PHASE 0 — FOUNDATION & DISCIPLINE ✅

### 0.1 Lock the Ground Truth
- ✅ Canvas project context is authoritative
- ✅ Desktop-first architecture is final
- ✅ Rule engine is core IP

**Action**: Treat the canvas doc as immutable truth. Every Cursor prompt references it.

### 0.2 No-Rewrite Rule

> **If something is wrong, we fix it at the spec level, not by patching code.**

This mindset alone will save months.

---

## PHASE 1 — RULE SPECIFICATION (MOST IMPORTANT PHASE) 🚧

⚠️ **Nothing else matters if this is wrong.**
**Do not code during this phase.**

### 1.1 Create Rule Spec Templates
For each rule, define:
- Rule name
- Firm
- Account type
- Applies to (Eval / PA / Funded)
- Inputs required
- State variables
- Threshold definition
- Reset behavior
- Violation condition
- Recoverability (can it be fixed?)
- Edge cases

### 1.2 Write Full Rule Specs (Human-Written)
Start with:
- Apex
- Topstep

For each firm, list every rule:
- Trailing DD
- MAE (if applicable)
- Daily loss
- Consistency
- Max contracts
- Trading hours
- Minimum days
- Inactivity

⚠️ If you don't understand a rule perfectly, do not ask Cursor to guess.

### 1.3 Validate Rule Specs with Scenarios
For every rule:
- Write 3 numerical examples
- Include: Safe case, Boundary case, Violation case
- If you can't simulate it by hand → you don't understand it yet.

---

## PHASE 2 — RULE ENGINE IMPLEMENTATION (CORE IP)

### 2.1 Lock Rule Engine Constraints
- No network calls
- No platform-specific logic
- Deterministic math only
- Explicit state transitions
- Unit tests required

### 2.2 Implement One Rule at a Time
Order:
1. Trailing drawdown
2. Daily loss
3. Max position
4. MAE
5. Consistency

Never batch rules together.

### 2.3 Cursor Workflow per Rule (STRICT)
For each rule:
1. Ask Cursor to restate the rule spec
2. Correct it
3. Ask for implementation
4. Ask for tests
5. Ask for edge-case tests
6. Manually review math

❌ Never accept:
- "This should work"
- "Approximately"
- "Based on typical prop firm behavior"

### 2.4 Rule Engine Validation Checklist
A rule is "done" only if:
- Tests cover unrealized PnL
- Tests fail on incorrect math
- State persists across updates
- No time-based assumptions exist

---

## PHASE 3 — DESKTOP ADD-ON (DATA ACQUISITION)

### 3.1 NinjaTrader Add-On Scope (Minimal First)
The add-on must only:
- Listen
- Capture
- Transmit

It must not:
- Decide rules
- Store logic
- Enforce constraints

### 3.2 Data Contract Definition (Critical)
Before coding, define a message schema. This schema is sacred.

### 3.3 Build Add-On Incrementally
Order:
1. Connect to backend
2. Send heartbeat
3. Send unrealized PnL
4. Send order events
5. Send position changes

Verify each step in isolation.

### 3.4 Validation Rule
If NinjaTrader shows a drawdown but backend doesn't → stop and fix immediately.

---

## PHASE 4 — BACKEND STATE & RULE APPLICATION

### 4.1 Backend Is the Source of Truth
Backend responsibilities:
- Persist state
- Track high-water marks
- Apply daily resets
- Version rule sets

### 4.2 Implement Account Tracker Service
Explicitly track:
- Equity history
- HWM
- Rule state
- Last update time

No derived shortcuts.

### 4.3 WebSocket Pipeline
Order:
1. Add-on → backend
2. Backend → rule engine
3. Rule engine → alerts
4. Alerts → frontend

Test latency end-to-end.

---

## PHASE 5 — FRONTEND (VISUALIZATION, NOT LOGIC)

### 5.1 UI Principles
- Frontend never computes rules
- Frontend never infers state
- Frontend reflects backend truth

### 5.2 Build Views in This Order
1. Multi-account table
2. Risk status indicators
3. Rule breakdown per account
4. Distance-to-violation metrics
5. Alert feed

### 5.3 Color Logic (Strict)
- Green: safe
- Yellow: approaching
- Red: imminent
- Gray: disconnected

No creativity here.

---

## PHASE 6 — MULTI-ACCOUNT & COPY-TRADE LOGIC

### 6.1 Account Grouping
Define:
- Group ID
- Member accounts
- Weakest account logic

### 6.2 Group Risk Evaluation
Rules:
- Lowest buffer dominates
- One account can invalidate group safety
- Surface this clearly

---

## PHASE 7 — SAFETY, TRUST & UX

### 7.1 Explicit Disclaimers
Always show:
- "Advisory, not guaranteed"
- "Objective rules only"
- "Subjective rules flagged only"

### 7.2 Logging & Auditability
Log:
- Every warning
- Every state change
- Every violation

This protects you and builds trust.

---

## PHASE 8 — OPTIONAL / ADVANCED

Only after everything above is rock solid:
- Trade blocking (opt-in)
- OAuth analytics
- Mobile notifications
- Additional platforms

---

## FINAL MENTAL MODEL

You are building:

> A **real-time constraint engine** that continuously computes safe operating boundaries for a trading account and exposes those boundaries to the trader *before* violations occur.

**Speed is irrelevant. Correctness is everything.**
