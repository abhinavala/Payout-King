# Payout King NinjaTrader Add-On

## Overview

This NinjaTrader 8 Add-On captures real-time account data and sends it to the Payout King backend for rule compliance tracking.

## Architecture

```
NinjaTrader Desktop
    ↓
PayoutKingAddOn (C#)
    ↓ (HTTP POST every 300ms)
Backend API (/api/v1/ninjatrader/account-update)
    ↓
Rules Engine
    ↓
Dashboard
```

## What It Does

✅ **Listens** to NinjaTrader account events:
- Account updates (equity, balance, PnL)
- Position updates (open positions, unrealized PnL)
- Order updates (order status changes)
- Execution updates (fills for daily PnL tracking)

✅ **Captures** account state:
- Current equity and balance
- Realized and unrealized PnL
- Open positions with peak unrealized loss (MAE)
- Daily PnL from fills
- Daily PnL history

✅ **Transmits** to backend:
- Sends AccountUpdate message every 300ms
- Matches AccountSnapshot interface exactly
- Handles errors gracefully

## What It Does NOT Do

❌ **Does NOT** decide rules (backend does this)
❌ **Does NOT** store rule logic (backend does this)
❌ **Does NOT** enforce constraints (backend does this)
❌ **Does NOT** place trades (read-only)

## Message Schema

The add-on sends `AccountUpdateMessage` which matches the `AccountSnapshot` interface in the rules engine:

```csharp
public class AccountUpdateMessage
{
    public string AccountId { get; set; }
    public long Timestamp { get; set; } // Unix milliseconds
    public decimal Equity { get; set; }
    public decimal Balance { get; set; }
    public decimal RealizedPnl { get; set; }
    public decimal UnrealizedPnl { get; set; }
    public decimal HighWaterMark { get; set; }
    public decimal DailyPnl { get; set; }
    public decimal StartingBalance { get; set; }
    public List<PositionMessage> OpenPositions { get; set; }
    public Dictionary<string, decimal> DailyPnlHistory { get; set; }
}
```

**This schema is SACRED** - changes require backend updates.

## Configuration

Create a config file at:
```
%USERDATA%\NinjaTrader 8\PayoutKing\config.json
```

Format:
```json
{
  "backendUrl": "http://localhost:8000",
  "apiKey": "your-api-key-here"
}
```

## Update Frequency

- **300ms** - Per Master Plan requirement (100-500ms for tick-level monitoring)
- Sends on every account/position/order/execution update
- Also sends periodically via timer

## Data Tracking

### Real-time Data
- ✅ Equity, balance, PnL (from NinjaTrader account)
- ✅ Open positions with unrealized PnL
- ✅ Peak unrealized loss per position (for MAE)

### Daily PnL Tracking
- ✅ Tracks fills via `ExecutionUpdate` event
- ✅ Accumulates daily PnL by date
- ✅ Provides daily PnL history dictionary

### State Tracking (Backend Responsibility)
- ⚠️ High-water mark (add-on provides current equity, backend tracks)
- ⚠️ Starting balance (add-on provides current balance, backend tracks)
- ⚠️ Daily PnL history (add-on provides tracked data, backend is source of truth)

## Building

1. Open `PayoutKingAddOn.csproj` in Visual Studio
2. Restore NuGet packages
3. Build solution
4. Copy DLL to `%USERDATA%\NinjaTrader 8\bin\Custom\AddOns\`

## Installation

1. Build the add-on
2. Copy DLL to NinjaTrader AddOns folder
3. Restart NinjaTrader
4. Add-on will appear in Tools → Add-Ons
5. Configure backend URL and API key

## Testing

### Manual Testing
1. Start NinjaTrader
2. Enable add-on
3. Check NinjaTrader output window for connection status
4. Verify data is being sent to backend

### Validation
- Verify equity matches NinjaTrader display exactly
- Verify unrealized PnL matches position PnL
- Verify daily PnL accumulates from fills
- Verify positions include all required fields

## Error Handling

- Logs errors to NinjaTrader output window
- Continues running on errors (doesn't crash)
- Retries on network failures (via HTTP client)
- Backend unavailable: logs warning, continues trying

## Performance

- Minimal CPU usage (300ms timer)
- Minimal memory footprint
- No impact on NinjaTrader performance
- Efficient JSON serialization

## Master Plan Compliance

✅ **PHASE 3.1**: Add-on only listens, captures, transmits
✅ **PHASE 3.2**: Message schema matches backend interface exactly
✅ **PHASE 3.3**: Built incrementally (connection → heartbeat → data)
✅ **PHASE 3.4**: Validates data matches NinjaTrader display

## Next Steps

1. Backend integration (PHASE 4)
2. WebSocket support (optional enhancement)
3. Configuration UI in NinjaTrader
4. Enhanced error handling and reconnection
