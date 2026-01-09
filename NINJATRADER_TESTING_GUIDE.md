# Testing Payout King with NinjaTrader Demo Account

## Overview

This guide will help you test the Payout King add-on with a real NinjaTrader demo account, simulating actual production usage.

## Prerequisites

1. ✅ **NinjaTrader 8** installed
2. ✅ **Backend running** on http://localhost:8000
3. ✅ **Frontend running** on http://localhost:5173
4. ✅ **Demo account** connected in NinjaTrader

## Step 1: Build the Add-On

### Option A: Using Visual Studio (Recommended)

1. **Open the project:**
   ```bash
   cd /Users/abhinavala/payout-king/apps/ninjatrader-addon/PayoutKingAddOn
   # Open PayoutKingAddOn.csproj in Visual Studio or Visual Studio Code
   ```

2. **Restore NuGet packages:**
   - Right-click project → "Restore NuGet Packages"
   - Or run: `dotnet restore`

3. **Build the project:**
   - Build → Build Solution (or Ctrl+Shift+B)
   - Or run: `dotnet build`

4. **Find the DLL:**
   - Output will be in: `bin/Debug/net8.0/PayoutKingAddOn.dll` (or `bin/Release/net8.0/`)

### Option B: Using Command Line

```bash
cd /Users/abhinavala/payout-king/apps/ninjatrader-addon/PayoutKingAddOn
dotnet restore
dotnet build
```

The DLL will be in: `bin/Debug/net8.0/PayoutKingAddOn.dll`

## Step 2: Install the Add-On

1. **Find NinjaTrader User Data Directory:**
   - Windows: `C:\Users\<YourUsername>\Documents\NinjaTrader 8\`
   - Or check: NinjaTrader → Tools → Options → Data → User data folder path

2. **Create AddOns folder (if it doesn't exist):**
   ```
   %USERDATA%\NinjaTrader 8\bin\Custom\AddOns\
   ```

3. **Copy the DLL:**
   - Copy `PayoutKingAddOn.dll` to the AddOns folder
   - Also copy any dependencies (Newtonsoft.Json.dll, etc.) if needed

4. **Restart NinjaTrader**

## Step 3: Configure the Add-On

1. **Create config directory:**
   ```
   %USERDATA%\NinjaTrader 8\PayoutKing\
   ```

2. **Create config.json:**
   ```json
   {
     "backendUrl": "http://localhost:8000",
     "apiKey": ""
   }
   ```

   **Note:** The API key is optional for now. The backend endpoint should accept requests without authentication for testing, or you can generate a token.

3. **Get API Key (Optional):**
   - Login to frontend: http://localhost:5173
   - Open browser console (F12)
   - Run: `localStorage.getItem('token')`
   - Copy the token to `apiKey` in config.json

## Step 4: Connect Your Demo Account in Backend

**Before starting NinjaTrader, connect the account in the frontend:**

1. **Open frontend:** http://localhost:5173
2. **Login** to your account
3. **Click "+ Connect Account"**
4. **Fill in the form:**
   - **Platform:** `ninjatrader`
   - **Account ID:** `YourNinjaTraderAccountName` (e.g., "Sim101" or "Demo123")
   - **Account Name:** `Demo Account` (or any name)
   - **Firm:** `apex` (or `topstep` - choose based on your demo account rules)
   - **Account Type:** `eval` (or `pa`, `funded` - choose based on your demo account)
   - **Account Size:** `50000` (or your demo account size)
   - **Rule Set Version:** `v1`
   - **Username:** (leave empty)
   - **Password:** (leave empty)
5. **Click "Connect"**

**Important:** The Account ID must match the account name in NinjaTrader exactly!

## Step 5: Enable the Add-On in NinjaTrader

1. **Start NinjaTrader 8**
2. **Connect to your demo account** (Sim101, etc.)
3. **Go to:** Tools → Add-Ons
4. **Find:** "Payout King Add-On"
5. **Enable it** (check the box)
6. **Check the Output window** (Tools → Output) for messages:
   - Should see: `✅ Connected to account: YourAccountName`
   - Should see: `✅ Loaded config from: ...`
   - Should see: `✅ Payout King Add-On started`

## Step 6: Verify Data Flow

### Check Backend Logs

**In Terminal 1 (backend), you should see:**
```
INFO:     127.0.0.1:xxxxx - "POST /api/v1/ninjatrader/account-update HTTP/1.1" 200 OK
```

This means data is being received!

### Check Frontend

1. **Open dashboard:** http://localhost:5173
2. **Your account should appear**
3. **Data should update in real-time:**
   - Equity updates
   - Balance updates
   - Rule states calculated
   - Status badges change

### Check NinjaTrader Output

**In NinjaTrader Output window, you should see:**
- `✅ Payout King Add-On started`
- Periodic updates (every 300ms)
- Any error messages if backend is unreachable

## Step 7: Test with Real Trading

### Test 1: Monitor Account State

1. **Open a chart** in NinjaTrader
2. **Watch the dashboard** in your browser
3. **Equity should update** as positions change
4. **Rule states should calculate** in real-time

### Test 2: Place a Trade

1. **Place a trade** in NinjaTrader (buy/sell)
2. **Watch dashboard:**
   - Position should appear
   - Unrealized PnL should update
   - Rule states should recalculate
   - Status may change if approaching limits

### Test 3: Test Drawdown

1. **Let a position go negative** (unrealized loss)
2. **Watch dashboard:**
   - Trailing drawdown should calculate
   - Status may change to CAUTION or CRITICAL
   - Warnings should appear
   - Alerts should show in alert feed

### Test 4: Test Daily PnL

1. **Close a position** (realize PnL)
2. **Watch dashboard:**
   - Daily PnL should update
   - Daily loss limit rule should evaluate
   - Consistency rule should evaluate (if applicable)

## Step 8: Verify Rule Calculations

### Check Rule States

1. **Expand account row** in dashboard (table view)
2. **Verify rule breakdown:**
   - Trailing drawdown calculated correctly
   - Buffer percentages shown
   - Distance-to-violation metrics
   - Status colors (green/yellow/red)

### Check Audit Logs

```bash
# Get your token first
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your-email@example.com","password":"your-password"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Query audit logs
curl -X GET "http://localhost:8000/api/v1/audit-logs?accountId=YourAccountId&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

Should see:
- Rule evaluations
- Warnings
- State changes
- Violations (if any)

## Troubleshooting

### Add-On Not Appearing

**Check:**
- DLL is in correct folder: `%USERDATA%\NinjaTrader 8\bin\Custom\AddOns\`
- NinjaTrader was restarted after copying DLL
- Check Tools → Add-Ons list

### "No account found" Error

**Fix:**
- Make sure you're logged into a demo account in NinjaTrader
- Account must be connected before enabling add-on

### "Backend error" Messages

**Check:**
- Backend is running: `curl http://localhost:8000/health`
- Config file has correct URL: `http://localhost:8000`
- Backend endpoint is correct: `/api/v1/ninjatrader/account-update`

### Data Not Updating in Frontend

**Check:**
- Account ID in frontend matches NinjaTrader account name exactly
- WebSocket connection (check browser console)
- Backend is receiving data (check backend logs)

### Rule States Not Calculating

**Check:**
- Firm and account type match your demo account
- Rule set version is correct
- Backend logs for rule engine errors

## Expected Behavior

### Real-Time Updates

- **Every 300ms:** Account data sent to backend
- **Immediately:** On account/position/order updates
- **Real-time:** Frontend updates via WebSocket

### Rule Evaluation

- **Trailing Drawdown:** Calculated from HWM
- **Daily Loss Limit:** Based on daily PnL
- **Position Size:** Based on open positions
- **Consistency:** Based on daily PnL history

### Status Changes

- **SAFE (green):** All rules within safe limits
- **CAUTION (yellow):** Approaching limits
- **CRITICAL (red):** Close to violation
- **VIOLATED (red):** Rule exceeded

## Testing Checklist

- [ ] Add-on builds successfully
- [ ] Add-on installed in NinjaTrader
- [ ] Config file created
- [ ] Account connected in frontend
- [ ] Add-on enabled in NinjaTrader
- [ ] Data flowing to backend (check logs)
- [ ] Frontend showing account data
- [ ] Real-time updates working
- [ ] Rule states calculating
- [ ] Status badges updating
- [ ] Alerts appearing
- [ ] Audit logs being created

## Next Steps

Once basic testing works:

1. **Test with multiple accounts**
2. **Test group functionality**
3. **Test different rule scenarios**
4. **Test edge cases** (boundary conditions)
5. **Performance testing** (multiple accounts, high frequency)

---

**You're ready to test with a real NinjaTrader demo account!**

Follow the steps above to set up end-to-end testing.
