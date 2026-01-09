# PHASE 4 - Backend Implementation Plan

## Current Phase: PHASE 4 - Backend State & Rule Application

## Master Plan Requirements

### 4.1 Backend Is the Source of Truth
Backend responsibilities:
- ✅ Persist state
- ✅ Track high-water marks
- ✅ Apply daily resets
- ✅ Version rule sets

### 4.2 Implement Account Tracker Service
Explicitly track:
- ✅ Equity history
- ✅ HWM (high-water mark)
- ✅ Rule state
- ✅ Last update time

No derived shortcuts.

### 4.3 WebSocket Pipeline
Order:
1. ✅ Add-on → backend (HTTP POST endpoint exists)
2. ✅ Backend → rule engine (evaluation happens)
3. 🚧 Rule engine → alerts (needs implementation)
4. 🚧 Alerts → frontend (needs WebSocket)

Test latency end-to-end.

## Current State Analysis

### ✅ Already Implemented
1. **NinjaTrader Endpoint** (`/api/v1/ninjatrader/account-data`)
   - Receives AccountUpdate messages
   - Converts to AccountSnapshot
   - Evaluates rules
   - Stores snapshots

2. **Account Tracker Service** (`account_tracker.py`)
   - Exists and tracks state
   - Needs verification against PHASE 4 requirements

3. **Database Models**
   - `AccountStateSnapshot` - Stores snapshots
   - `ConnectedAccount` - Account metadata

### 🚧 Needs Implementation/Verification

1. **High-Water Mark Tracking**
   - Backend must track HWM (not add-on)
   - Update HWM when equity exceeds current HWM
   - Persist HWM across sessions

2. **Daily Reset Logic**
   - Reset daily PnL at 4:00 PM CT (Topstep)
   - Reset daily loss counters
   - Track trading days

3. **Daily PnL History**
   - Track daily PnL by date
   - Required for consistency rule
   - Required for minimum trading days

4. **WebSocket Broadcasting**
   - Broadcast rule evaluation results
   - Real-time updates to frontend
   - Handle multiple clients

5. **Account State Persistence**
   - Ensure state persists correctly
   - Handle HWM updates
   - Track equity history

## Implementation Tasks

### Task 1: Verify/Update Account Tracker Service
- Ensure HWM is tracked correctly
- Verify equity history is stored
- Check daily reset logic

### Task 2: Implement Daily Reset Logic
- Scheduled task for daily resets
- Timezone-aware (4:00 PM CT for Topstep)
- Reset daily PnL, daily loss counters

### Task 3: Implement Daily PnL History Tracking
- Track daily PnL by date
- Store in database or in-memory cache
- Provide to rule engine for consistency rule

### Task 4: Implement WebSocket Broadcasting
- WebSocket endpoint for frontend
- Broadcast rule evaluation results
- Handle connection management

### Task 5: Update NinjaTrader Endpoint
- Update to use new `/account-update` endpoint name
- Ensure message format matches AccountUpdateMessage
- Handle daily_pnl_history from add-on

## Key Principles

1. **Backend is Source of Truth**
   - HWM tracked by backend, not add-on
   - Daily PnL history tracked by backend
   - Starting balance tracked by backend

2. **State Persistence**
   - All state changes persisted
   - No derived shortcuts
   - Explicit tracking

3. **Real-time Updates**
   - WebSocket for low-latency updates
   - Broadcast to all connected clients
   - Handle disconnections gracefully

## Files to Create/Update

1. `app/services/account_tracker.py` - Verify/update HWM tracking
2. `app/services/daily_reset.py` - Daily reset logic
3. `app/services/websocket_manager.py` - WebSocket broadcasting
4. `app/api/v1/endpoints/ninjatrader.py` - Update endpoint
5. `app/models/account_state.py` - Add daily PnL history field

## Next Steps

1. Review account_tracker.py implementation
2. Verify HWM tracking logic
3. Implement daily reset scheduler
4. Implement WebSocket manager
5. Update endpoint to match new message format
