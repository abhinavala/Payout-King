# PHASE 3 - Desktop Add-On Implementation Plan

## Current Phase: PHASE 3 - Desktop Add-On (Data Acquisition)

## Master Plan Requirements

### 3.1 NinjaTrader Add-On Scope (Minimal First)
The add-on must only:
- ✅ Listen
- ✅ Capture
- ✅ Transmit

It must not:
- ❌ Decide rules
- ❌ Store logic
- ❌ Enforce constraints

### 3.2 Data Contract Definition (Critical)
**This schema is sacred.** Defined in `docs/ARCHITECTURE.md`:

```typescript
interface AccountUpdate {
  accountId: string;
  timestamp: number; // Unix timestamp in milliseconds
  realizedPnl: number;
  unrealizedPnl: number;
  equity: number;
  positions: Position[];
  openOrders: Order[];
}

interface Position {
  instrument: string;
  quantity: number;
  avgPrice: number;
  unrealizedPnl: number;
}
```

### 3.3 Build Add-On Incrementally
Order:
1. ✅ Connect to backend
2. ✅ Send heartbeat
3. ✅ Send unrealized PnL
4. ✅ Send order events
5. ✅ Send position changes

Verify each step in isolation.

### 3.4 Validation Rule
If NinjaTrader shows a drawdown but backend doesn't → stop and fix immediately.

## Implementation Strategy

### Step 1: Connection & Authentication
- Connect to backend WebSocket/HTTPS endpoint
- Authenticate with device token
- Handle reconnection logic

### Step 2: Data Capture
- Subscribe to NinjaTrader account events
- Capture:
  - Order submissions
  - Order fills
  - Position changes
  - Unrealized PnL
  - Realized PnL
  - Account equity
- Track per-tick state

### Step 3: Data Transmission
- Send state updates to backend every 100–500ms
- Use AccountUpdate message schema
- Handle network errors gracefully

### Step 4: Error Handling
- Log all errors
- Retry connection on failure
- Queue messages if backend unavailable

## Key Principles

1. **No Rule Logic**: Add-on only captures and transmits data
2. **Real-time Updates**: Send updates every 100–500ms
3. **Reliable Transmission**: Handle network failures gracefully
4. **Minimal Footprint**: Don't impact NinjaTrader performance

## Files to Create/Update

1. `PayoutKingAddOn.cs` - Main add-on class
2. `BackendClient.cs` - WebSocket/HTTP client for backend
3. `AccountDataCollector.cs` - Collects account state from NinjaTrader
4. `MessageSerializer.cs` - Serializes AccountUpdate messages
5. `PayoutKingAddOn.csproj` - Project file

## Testing Strategy

1. Unit tests for message serialization
2. Integration tests with mock backend
3. Manual testing in NinjaTrader
4. Verify data matches NinjaTrader display exactly

## Next Steps

1. Review existing add-on code
2. Define exact message schema (C# classes)
3. Implement backend connection
4. Implement data capture
5. Implement data transmission
6. Add error handling and logging
