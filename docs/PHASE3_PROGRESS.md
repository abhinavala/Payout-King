# PHASE 3 Progress - Desktop Add-On

## Status: 🚧 IN PROGRESS

**Current Phase**: PHASE 3 - Desktop Add-On (Data Acquisition)

## Master Plan Compliance

### ✅ 3.1 Scope (Minimal First)
The add-on:
- ✅ Listens to NinjaTrader account events
- ✅ Captures account state (equity, PnL, positions)
- ✅ Transmits to backend

The add-on does NOT:
- ✅ Decide rules (backend does this)
- ✅ Store logic (backend does this)
- ✅ Enforce constraints (backend does this)

### ✅ 3.2 Data Contract
- ✅ Created `AccountUpdateMessage.cs` matching exact schema
- ✅ Matches `AccountSnapshot` interface from rules engine
- ✅ Schema is sacred - changes require backend updates

### ✅ 3.3 Incremental Build
1. ✅ Connect to backend - HTTP client implemented
2. ✅ Send heartbeat - Timer-based updates (300ms)
3. ✅ Send unrealized PnL - Included in AccountUpdate
4. ✅ Send order events - Subscribed to OrderUpdate
5. ✅ Send position changes - Subscribed to PositionUpdate

## Implementation Details

### Message Schema
- **AccountUpdateMessage** - Matches AccountSnapshot exactly
- **PositionMessage** - Matches PositionSnapshot exactly
- Uses Unix timestamps (milliseconds)
- Uses decimal precision for financial data

### Update Frequency
- **300ms** - Per Master Plan requirement (100-500ms for tick-level monitoring)
- Sends on every account/position/order update
- Also sends periodically via timer

### Data Captured
- ✅ Account equity
- ✅ Account balance
- ✅ Realized PnL
- ✅ Unrealized PnL
- ✅ High-water mark (placeholder - backend should track)
- ✅ Daily PnL (placeholder - needs fill tracking)
- ✅ Open positions (with peak unrealized loss for MAE)
- ✅ Starting balance (placeholder - backend should track)
- ⚠️ Daily PnL history (empty - needs fill tracking)

## Files Created/Updated

### New Files
- `AccountUpdateMessage.cs` - Message schema matching backend interface

### Updated Files
- `PayoutKingAddOn.cs` - Updated to use new schema and 300ms updates

## Remaining Tasks

### High Priority
1. **High-Water Mark Tracking**
   - Currently placeholder
   - Should be tracked by backend, but add-on can provide initial value
   - Backend is source of truth

2. **Daily PnL Calculation**
   - Currently uses realized PnL as placeholder
   - Need to track fills per day
   - Required for daily loss limit and consistency rules

3. **Daily PnL History**
   - Currently empty dictionary
   - Need to track daily PnL by date
   - Required for consistency rule and minimum trading days

4. **Starting Balance**
   - Currently uses current balance as placeholder
   - Should be provided by backend or stored locally

### Medium Priority
1. **WebSocket Support**
   - Currently using HTTP POST
   - WebSocket would be more efficient for real-time updates
   - Can add as enhancement

2. **Error Handling & Reconnection**
   - Basic error handling exists
   - Need automatic reconnection logic
   - Need message queuing if backend unavailable

3. **Configuration UI**
   - Currently uses config file
   - Could add NinjaTrader properties panel
   - Better UX for users

### Low Priority
1. **Logging**
   - Currently uses Print() statements
   - Could add structured logging
   - File-based logging for debugging

2. **Performance Optimization**
   - Currently sends full update every 300ms
   - Could optimize to send only changes
   - Reduces bandwidth

## Validation

### ✅ Master Plan Requirements Met
- ✅ Add-on only listens, captures, transmits
- ✅ No rule logic in add-on
- ✅ Message schema matches backend interface
- ✅ Updates sent every 300ms (within 100-500ms requirement)
- ✅ Subscribes to all necessary events

### ⚠️ Needs Backend Integration
- Backend must implement `/api/v1/ninjatrader/account-update` endpoint
- Backend must handle AccountUpdateMessage format
- Backend must track high-water mark, daily PnL history, starting balance

## Next Steps

1. **Test with Mock Backend**
   - Create simple HTTP server to receive messages
   - Verify message format matches schema
   - Test update frequency

2. **Implement Fill Tracking**
   - Track fills per day for daily PnL calculation
   - Build daily PnL history dictionary
   - Store in memory (backend is source of truth)

3. **Add Error Handling**
   - Automatic reconnection on failure
   - Message queuing
   - Exponential backoff

4. **Backend Integration**
   - Coordinate with PHASE 4 (Backend)
   - Ensure endpoint matches message format
   - Test end-to-end

## Notes

- **Backend is Source of Truth**: Add-on provides data, backend tracks state
- **High-Water Mark**: Should be tracked by backend, not add-on
- **Daily PnL History**: Backend should track this, but add-on can provide initial data
- **Real-time Updates**: 300ms is sufficient for tick-level monitoring
- **No Rule Logic**: Add-on is pure data acquisition

---

**PHASE 3: ~70% Complete** - Core functionality implemented, needs fill tracking and backend integration
