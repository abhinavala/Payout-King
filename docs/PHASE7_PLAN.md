# PHASE 7 - Safety, Trust & UX

## Current Phase: PHASE 7 - Safety, Trust & UX

## Master Plan Requirements

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

## Implementation Strategy

### 1. Disclaimers
- Add disclaimer component to frontend
- Show on dashboard, account views, and rule breakdowns
- Clear, visible, not hidden

### 2. Logging System
- Create audit log model
- Log all warnings
- Log all state changes
- Log all violations
- Queryable audit trail

### 3. Audit Log API
- `GET /api/v1/audit-logs` - Query audit logs
- Filter by account, date range, event type
- Export functionality

## Implementation Steps

1. Create audit log database model
2. Add logging to rule evaluation
3. Add logging to state changes
4. Create audit log API endpoints
5. Add disclaimer component to frontend
6. Add disclaimers to all relevant views

## Key Principles

1. **Transparency**
   - All warnings logged
   - All state changes logged
   - All violations logged

2. **Trust**
   - Clear disclaimers
   - Objective rules only
   - Subjective rules flagged

3. **Auditability**
   - Complete audit trail
   - Queryable logs
   - Export capability

## Next Steps

1. Create audit log model
2. Implement logging in rule engine
3. Implement logging in account tracker
4. Create audit log API
5. Add disclaimer component
6. Add disclaimers to frontend
