# NinjaTrader Testing - Quick Start

## 🎯 Goal

Test Payout King with a real NinjaTrader demo account to simulate actual production usage.

## ⚡ Quick Setup (5 Steps)

### 1. Build Add-On

```bash
cd /Users/abhinavala/payout-king/apps/ninjatrader-addon/PayoutKingAddOn
dotnet build
```

**Output:** `bin/Debug/net8.0/PayoutKingAddOn.dll`

### 2. Install Add-On

**Copy DLL to:**
```
%USERDATA%\NinjaTrader 8\bin\Custom\AddOns\PayoutKingAddOn.dll
```

**Find UserData folder:**
- Windows: `C:\Users\<YourUsername>\Documents\NinjaTrader 8\`
- Or: NinjaTrader → Tools → Options → Data → User data folder

### 3. Create Config File

**Create directory:**
```
%USERDATA%\NinjaTrader 8\PayoutKing\
```

**Create `config.json`:**
```json
{
  "backendUrl": "http://localhost:8000",
  "apiKey": ""
}
```

### 4. Connect Account in Frontend

1. **Open:** http://localhost:5173
2. **Login**
3. **Click "+ Connect Account"**
4. **Fill in:**
   - Platform: `ninjatrader`
   - Account ID: `YourNinjaTraderAccountName` (e.g., "Sim101")
   - Account Name: `Demo Account`
   - Firm: `apex` (or `topstep`)
   - Account Type: `eval`
   - Account Size: `50000` (or your demo size)
   - Rule Set Version: `v1`
5. **Click "Connect"**

**⚠️ IMPORTANT:** Account ID must match NinjaTrader account name exactly!

### 5. Enable Add-On in NinjaTrader

1. **Start NinjaTrader**
2. **Connect to demo account**
3. **Tools → Add-Ons**
4. **Enable "Payout King Add-On"**
5. **Check Output window** (Tools → Output)

## ✅ Verify It's Working

### Check Backend Logs

**In Terminal 1 (backend), you should see:**
```
INFO: Received data from NinjaTrader account: Sim101
INFO: Found connected account: ...
INFO:     127.0.0.1:xxxxx - "POST /api/v1/ninjatrader/account-update HTTP/1.1" 200 OK
```

### Check Frontend

- Account appears in dashboard
- Equity updates in real-time
- Rule states calculated
- Status badges show correct colors

### Check NinjaTrader Output

- `✅ Connected to account: Sim101`
- `✅ Payout King Add-On started`
- No error messages

## 🧪 Test Scenarios

### Scenario 1: Monitor Account
- Open chart in NinjaTrader
- Watch dashboard update in real-time
- Equity should match NinjaTrader exactly

### Scenario 2: Place Trade
- Place a buy/sell order
- Watch position appear in dashboard
- Unrealized PnL updates
- Rule states recalculate

### Scenario 3: Test Drawdown
- Let position go negative
- Watch trailing drawdown calculate
- Status may change to CAUTION/CRITICAL
- Warnings appear

### Scenario 4: Close Position
- Close a position
- Daily PnL updates
- Consistency rule evaluates
- Audit logs created

## 🐛 Troubleshooting

### "Account not found" Error

**Problem:** Account ID mismatch

**Fix:**
1. Check NinjaTrader account name (exact spelling)
2. Update Account ID in frontend to match exactly
3. Check backend logs for available accounts

### "Backend error" in NinjaTrader

**Problem:** Backend not reachable

**Fix:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check config.json URL is correct
3. Check firewall/network settings

### No Data in Frontend

**Problem:** Account not connected or ID mismatch

**Fix:**
1. Verify account is connected in frontend
2. Check Account ID matches exactly
3. Check backend logs for incoming data
4. Check WebSocket connection (browser console)

## 📋 Testing Checklist

- [ ] Add-on built successfully
- [ ] DLL copied to AddOns folder
- [ ] Config file created
- [ ] Account connected in frontend
- [ ] Add-on enabled in NinjaTrader
- [ ] Backend receiving data (check logs)
- [ ] Frontend showing account
- [ ] Real-time updates working
- [ ] Rule states calculating
- [ ] Status badges updating

## 🎉 Success Indicators

✅ **Backend logs show:** `POST /api/v1/ninjatrader/account-update HTTP/1.1" 200 OK`  
✅ **Frontend shows:** Account with live data  
✅ **NinjaTrader shows:** `✅ Payout King Add-On started`  
✅ **Dashboard updates:** In real-time as you trade  

---

**You're ready to test with a real NinjaTrader demo account!**

See `NINJATRADER_TESTING_GUIDE.md` for detailed instructions.
