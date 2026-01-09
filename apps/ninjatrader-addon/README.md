# NinjaTrader Add-On for Payout King

This is a NinjaTrader Add-On that reads account data and sends it to the Payout King backend.

## Why NinjaTrader?

- ✅ **FREE** - No paid API subscription required
- ✅ Full account access (balance, PnL, positions, orders)
- ✅ Real-time unrealized PnL tracking
- ✅ Used by Apex, Topstep, MFF, etc.
- ✅ Extremely popular with prop traders

## Architecture

```
NinjaTrader Desktop
    ↓
Add-On (C#)
    ↓ (WebSocket/HTTPS)
Backend API
    ↓
Rules Engine
    ↓
Dashboard
```

## What It Tracks

✅ **ALL objective rules**:
- Trailing drawdown (real-time)
- Daily loss limits
- Contract limits
- Trading hours
- Consistency
- Minimum days
- Inactivity

## Setup

### Prerequisites

- NinjaTrader 8 installed
- Visual Studio 2019+ (for building)
- .NET Framework 4.8+

### Building

1. Open `PayoutKingAddOn.sln` in Visual Studio
2. Restore NuGet packages
3. Build solution
4. Copy DLL to NinjaTrader AddOns folder

### Configuration

The add-on needs:
- Backend API URL (e.g., `http://localhost:8000`)
- API key/token (for authentication)
- Account ID (to identify which account)

## How It Works

1. Add-on subscribes to NinjaTrader account events
2. Reads account balance, equity, positions, orders
3. Calculates unrealized PnL
4. Sends data to backend every 1-2 seconds
5. Backend processes and evaluates rules

## Data Sent

```json
{
  "accountId": "NT-12345",
  "timestamp": "2026-01-05T19:00:00Z",
  "equity": 10200.50,
  "balance": 10000.00,
  "realizedPnL": 100.00,
  "unrealizedPnL": 100.50,
  "highWaterMark": 10500.00,
  "dailyPnL": -50.00,
  "openPositions": [...],
  "orders": [...]
}
```

