# NinjaTrader Integration Guide

## Overview

NinjaTrader is our **primary free integration** for prop firm traders. It requires no paid API subscription and provides full account access.

## Why NinjaTrader?

✅ **FREE** - No paid API subscription required  
✅ Full account access (balance, PnL, positions, orders)  
✅ Real-time unrealized PnL tracking  
✅ Used by Apex, Topstep, MFF, etc.  
✅ Extremely popular with prop traders  

## Architecture

```
┌─────────────────────┐
│ NinjaTrader Desktop │
│   (User's Machine)  │
└──────────┬──────────┘
           │
           │ Add-On (C#)
           │ Reads account data
           │
           ▼
┌─────────────────────┐
│   Backend API       │
│  (Your Server)      │
│  POST /api/v1/      │
│  ninjatrader/       │
│  account-data       │
└──────────┬──────────┘
           │
           │ Processes & evaluates
           │
           ▼
┌─────────────────────┐
│   Rules Engine      │
│  (Trailing DD, etc) │
└──────────┬──────────┘
           │
           │ Results
           │
           ▼
┌─────────────────────┐
│   Dashboard         │
│  (WebSocket)        │
└─────────────────────┘
```

## Setup Steps

### 1. Build the Add-On

**Requirements**:
- Visual Studio 2019+
- .NET Framework 4.8+
- NinjaTrader 8 installed

**Steps**:
1. Open `apps/ninjatrader-addon/PayoutKingAddOn.sln` in Visual Studio
2. Restore NuGet packages
3. Build solution (Release mode)
4. Copy `PayoutKingAddOn.dll` to:
   ```
   C:\Users\<YourUser>\Documents\NinjaTrader 8\bin\Custom\AddOns\
   ```

### 2. Configure the Add-On

Create config file:
```
C:\Users\<YourUser>\Documents\NinjaTrader 8\PayoutKing\config.json
```

Content:
```json
{
  "backendUrl": "http://localhost:8000",
  "apiKey": "your-api-key-here"
}
```

### 3. Enable in NinjaTrader

1. Open NinjaTrader
2. Go to Tools → Add-Ons
3. Find "Payout King Add-On"
4. Enable it
5. Restart NinjaTrader

### 4. Connect Account in Backend

The account must be registered in the backend first:

```bash
POST /api/v1/accounts/
{
  "platform": "ninjatrader",
  "accountId": "NT-12345",  # Your NinjaTrader account name
  "accountName": "My Account",
  "firm": "apex",
  "accountType": "pa",
  "accountSize": 50000,
  "ruleSetVersion": "1.0",
  "username": "",  # Not needed for NinjaTrader
  "password": ""   # Not needed for NinjaTrader
}
```

## What Data Is Sent

The add-on sends account snapshots every 2 seconds:

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
  "openPositions": [
    {
      "symbol": "ES 03-26",
      "quantity": 2,
      "avgPrice": 4000.25,
      "currentPrice": 4001.50,
      "unrealizedPnL": 62.50,
      "openedAt": "2026-01-05T10:30:00Z"
    }
  ],
  "orders": [...]
}
```

## What Rules Can Be Tracked

✅ **ALL objective rules**:
- Trailing drawdown (real-time with unrealized PnL)
- Daily loss limits
- Contract limits
- Trading hours
- Consistency rules
- Minimum trading days
- Inactivity rules

## Advantages

1. **Free** - No API subscription cost
2. **Real-time** - Data updates every 2 seconds
3. **Complete** - All account data available
4. **Reliable** - Direct access to NinjaTrader account

## Disadvantages

1. **Desktop-only** - Requires NinjaTrader Desktop installed
2. **User setup** - Users must install the add-on
3. **C# maintenance** - You maintain a C# component

## Testing

### Test the Add-On Locally

1. Start backend:
   ```bash
   cd apps/backend
   uvicorn main:app --reload
   ```

2. Enable add-on in NinjaTrader

3. Check backend logs for incoming data

4. Check dashboard for updates

### Test End-to-End

1. Connect account in backend
2. Enable add-on in NinjaTrader
3. Open a position
4. Watch dashboard update in real-time
5. Verify rule calculations

## Troubleshooting

### Add-On Not Sending Data

- Check NinjaTrader logs: `Tools → Log`
- Verify backend URL in config.json
- Check backend is running and accessible
- Verify account ID matches

### Data Not Appearing in Dashboard

- Check backend logs for errors
- Verify account is connected in backend
- Check WebSocket connection
- Verify rule set is configured

## Next Steps

1. **Build and test** the add-on locally
2. **Connect a test account**
3. **Verify data flow** end-to-end
4. **Test rule calculations** with real positions
5. **Deploy** to users

## Files

- `apps/ninjatrader-addon/PayoutKingAddOn/` - C# Add-On source
- `apps/backend/app/api/v1/endpoints/ninjatrader.py` - Backend endpoint
- `docs/NINJATRADER_INTEGRATION.md` - This guide

