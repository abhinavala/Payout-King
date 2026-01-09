# 🚀 Connect Your NinjaTrader Demo Account - Step-by-Step Guide

## Overview

This guide will help you connect your NinjaTrader demo account to Payout King and verify that:
- ✅ Account data is being read correctly
- ✅ Rules are being evaluated in real-time
- ✅ Alerts and warnings are showing up
- ✅ Dashboard updates live

## Prerequisites

1. ✅ NinjaTrader 8 installed and running
2. ✅ Demo account logged in
3. ✅ Backend running on `http://localhost:8000`
4. ✅ Frontend running on `http://localhost:5173`
5. ✅ You're logged into Payout King dashboard

## Step 1: Build the NinjaTrader Add-On

### Option A: Using Visual Studio (Recommended)

1. **Open Visual Studio**
2. **Open the solution:**
   ```
   apps/ninjatrader-addon/PayoutKingAddOn/PayoutKingAddOn.csproj
   ```
3. **Restore NuGet packages** (right-click solution → Restore NuGet Packages)
4. **Build in Release mode:**
   - Select "Release" from dropdown
   - Build → Build Solution (or Ctrl+Shift+B)
5. **Copy the DLL:**
   - Find: `apps/ninjatrader-addon/PayoutKingAddOn/bin/Release/PayoutKingAddOn.dll`
   - Copy to: `C:\Users\<YourUser>\Documents\NinjaTrader 8\bin\Custom\AddOns\`

### Option B: Using Command Line (if you have .NET SDK)

```bash
cd apps/ninjatrader-addon/PayoutKingAddOn
dotnet build -c Release
# Then copy the DLL as above
```

## Step 2: Configure the Add-On

1. **Create config directory:**
   ```
   C:\Users\<YourUser>\Documents\NinjaTrader 8\PayoutKing\
   ```

2. **Create `config.json` file:**
   ```json
   {
     "backendUrl": "http://localhost:8000",
     "apiKey": ""
   }
   ```

   **Note:** Leave `apiKey` empty for now (we'll add authentication later if needed).

## Step 3: Enable Add-On in NinjaTrader

1. **Open NinjaTrader**
2. **Go to:** Tools → Add-Ons
3. **Find:** "Payout King Add-On"
4. **Enable it** (check the box)
5. **Restart NinjaTrader** (required for add-ons to load)

## Step 4: Get Your NinjaTrader Account Name

1. **In NinjaTrader**, go to: Tools → Options → General
2. **Look for your account name** (e.g., "Sim101", "Demo123", etc.)
3. **Write it down** - you'll need it in the next step

**OR** check the NinjaTrader Control Center → Accounts tab to see your account name.

## Step 5: Connect Account in Payout King Dashboard

1. **Open browser:** http://localhost:5173
2. **Make sure you're logged in**
3. **Click "Connect Account" button**
4. **Fill in the form:**
   - **Platform:** NinjaTrader ✅
   - **Prop Firm:** Select one (e.g., Apex)
   - **Account Type:** Select (e.g., eval)
   - **Account ID:** Enter your NinjaTrader account name (from Step 4)
   - **Account Name:** Give it a friendly name (e.g., "My Demo Account")
   - **Account Size:** Enter your demo account size (e.g., 50000)
5. **Click "Connect Account"**

✅ Account should now appear in your dashboard!

## Step 6: Verify Connection

### Check NinjaTrader Logs

1. **In NinjaTrader**, go to: Tools → Log
2. **Look for messages like:**
   ```
   ✅ Connected to account: Sim101
   ✅ Payout King Add-On started
   ✅ Data sent successfully
   ```

### Check Backend Logs

```bash
tail -f apps/backend.log
```

You should see:
```
INFO: POST /api/v1/ninjatrader/account-data HTTP/1.1 200 OK
```

### Check Dashboard

1. **Refresh your dashboard** (http://localhost:5173)
2. **You should see:**
   - Your account card
   - Account state (equity, balance, etc.)
   - Rule states (trailing drawdown, daily loss, etc.)
   - Real-time updates every 2 seconds

## Step 7: Test Real-Time Updates

### Test 1: Open a Position

1. **In NinjaTrader**, open a position (buy/sell a contract)
2. **Watch the dashboard** - it should update within 2 seconds
3. **Check for:**
   - Unrealized PnL showing up
   - Equity changing
   - Rule states updating

### Test 2: Watch Trailing Drawdown

1. **If you have a losing position**, watch the trailing drawdown rule
2. **As unrealized loss increases**, you should see:
   - Buffer decreasing
   - Status changing (safe → caution → critical)
   - Warnings appearing

### Test 3: Test Alerts

1. **Use the test scenarios** (click "🧪 Test Account" button)
2. **Select "Near Drawdown Violation"**
3. **Run the test**
4. **Verify:**
   - Warnings appear
   - Status shows "CAUTION" or "CRITICAL"
   - Recovery paths shown (if recoverable)

## Troubleshooting

### Add-On Not Loading

**Problem:** Add-on doesn't appear in Tools → Add-Ons

**Solutions:**
- ✅ Make sure DLL is in correct location: `NinjaTrader 8\bin\Custom\AddOns\`
- ✅ Restart NinjaTrader completely
- ✅ Check NinjaTrader log for errors
- ✅ Verify DLL was built in Release mode

### Add-On Not Sending Data

**Problem:** No "Data sent successfully" messages in NinjaTrader log

**Solutions:**
- ✅ Check backend is running: `curl http://localhost:8000/health`
- ✅ Verify config.json path is correct
- ✅ Check backend URL in config.json matches your backend
- ✅ Check firewall isn't blocking connection
- ✅ Verify account is logged in to NinjaTrader

### Account Not Found Error

**Problem:** Backend returns "Account not found"

**Solutions:**
- ✅ Verify account ID in dashboard matches NinjaTrader account name exactly
- ✅ Check account is connected in dashboard
- ✅ Verify account is active (not deleted)
- ✅ Check backend logs for exact account ID being sent

### No Data in Dashboard

**Problem:** Account connected but no data showing

**Solutions:**
- ✅ Check WebSocket connection (browser console)
- ✅ Verify account is sending data (check backend logs)
- ✅ Refresh dashboard
- ✅ Check browser console for errors
- ✅ Verify rules are loaded for your firm/account type

### Data Not Updating

**Problem:** Initial data shows but doesn't update

**Solutions:**
- ✅ Check NinjaTrader is still running
- ✅ Verify add-on is still enabled
- ✅ Check backend is still running
- ✅ Verify WebSocket connection is active
- ✅ Check browser console for WebSocket errors

## What to Look For

### ✅ Success Indicators

1. **NinjaTrader Log:**
   - ✅ "Connected to account: [YourAccount]"
   - ✅ "Payout King Add-On started"
   - ✅ "Data sent successfully" (every 2 seconds)

2. **Backend Log:**
   - ✅ `POST /api/v1/ninjatrader/account-data 200 OK`
   - ✅ No errors

3. **Dashboard:**
   - ✅ Account card shows equity, balance
   - ✅ Rule states showing (trailing drawdown, daily loss, etc.)
   - ✅ Status badges (SAFE, CAUTION, CRITICAL)
   - ✅ Real-time updates when you trade

4. **Alerts:**
   - ✅ Warnings appear when close to violation
   - ✅ Status changes as you approach limits
   - ✅ Recovery paths shown for recoverable rules

## Next Steps

Once connected:

1. **Test different scenarios:**
   - Open winning positions
   - Open losing positions
   - Approach drawdown limits
   - Test daily loss limits

2. **Verify rule calculations:**
   - Check trailing drawdown math
   - Verify daily loss tracking
   - Test consistency rules

3. **Test alerts:**
   - Get close to violations
   - Verify warnings appear
   - Check recovery paths

## Quick Test Checklist

- [ ] Add-on built and installed
- [ ] Config.json created
- [ ] Add-on enabled in NinjaTrader
- [ ] Account connected in dashboard
- [ ] Data appearing in dashboard
- [ ] Real-time updates working
- [ ] Rule states showing
- [ ] Alerts appearing when close to violation

---

**Ready to connect!** Follow these steps and you'll have your NinjaTrader account connected and tracking rules in real-time! 🚀

