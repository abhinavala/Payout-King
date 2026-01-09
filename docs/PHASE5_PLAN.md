# PHASE 5 - Frontend Implementation Plan

## Current Phase: PHASE 5 - Frontend Dashboard (Visualization Only)

## Master Plan Requirements

### 5.1 UI Principles
- ✅ Frontend never computes rules
- ✅ Frontend never infers state
- ✅ Frontend reflects backend truth

### 5.2 Build Views in This Order
1. Multi-account table
2. Risk status indicators
3. Rule breakdown per account
4. Distance-to-violation metrics
5. Alert feed

### 5.3 Color Logic (Strict)
- Green: safe
- Yellow: approaching (caution)
- Red: imminent (critical/violated)
- Gray: disconnected

No creativity here.

## Implementation Strategy

### View 1: Multi-Account Table
- List all connected accounts
- Show overall risk level per account
- Show key metrics (equity, PnL, status)
- Click to view details

### View 2: Risk Status Indicators
- Color-coded status badges
- Overall risk level per account
- Quick visual reference

### View 3: Rule Breakdown Per Account
- Expandable panel per account
- Show all rule states
- Status, buffer, distance-to-violation
- Color-coded by status

### View 4: Distance-to-Violation Metrics
- Progress bars showing buffer
- Dollar amounts remaining
- Percentage of threshold used
- Visual warnings

### View 5: Alert Feed
- Real-time alerts from backend
- Rule violations
- Status changes
- Timestamped

## Data Flow

```
Backend WebSocket
    ↓ (Real-time updates)
Frontend WebSocket Hook
    ↓ (State management)
React Components
    ↓ (Display only)
UI (Visualization)
```

## Key Principles

1. **No Rule Logic in Frontend**
   - All rule states come from backend
   - Frontend only displays
   - No calculations

2. **Real-time Updates**
   - WebSocket for live data
   - Update UI on state changes
   - Show last update time

3. **Color Coding**
   - Strict color logic
   - Green/Yellow/Red/Gray only
   - Consistent across all views

## Components to Create

1. `MultiAccountTable.tsx` - Main dashboard table
2. `RiskStatusBadge.tsx` - Status indicator component
3. `RuleBreakdownPanel.tsx` - Detailed rule view
4. `DistanceToViolation.tsx` - Buffer visualization
5. `AlertFeed.tsx` - Alert display
6. `AccountDetailView.tsx` - Individual account view

## Next Steps

1. Review existing Dashboard component
2. Create Multi-Account Table
3. Add Risk Status Indicators
4. Create Rule Breakdown Panel
5. Add Distance-to-Violation Metrics
6. Create Alert Feed
