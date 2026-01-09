# NinjaTrader Testing - Complete Summary

## 🎯 What You Want to Do

Test Payout King with a **real NinjaTrader demo account** to simulate actual production usage.

## ✅ What I've Created

1. **Fixed configuration bug** in add-on
2. **Created comprehensive testing guide** (`NINJATRADER_TESTING_GUIDE.md`)
3. **Created quick start guide** (`NINJATRADER_QUICK_START.md`)
4. **Created build instructions** (`BUILD_AND_INSTALL.md`)

## 🚀 Quick Steps to Test

### Step 1: Build Add-On

**Using Visual Studio:**
1. Open `apps/ninjatrader-addon/PayoutKingAddOn/PayoutKingAddOn.csproj`
2. Restore NuGet packages
3. Build solution
4. Find DLL in `bin/Debug/PayoutKingAddOn.dll`

### Step 2: Install Add-On

1. **Copy DLL to:**
   ```
   %USERDATA%\NinjaTrader 8\bin\Custom\AddOns\PayoutKingAddOn.dll
   ```

2. **Create config:**
   ```
   %USERDATA%\NinjaTrader 8\PayoutKing\config.json
   ```
   ```json
   {
     "backendUrl": "http://localhost:8000",
     "apiKey": ""
   }
   ```

### Step 3: Connect Account in Frontend

1. Open http://localhost:5173
2. Connect account with:
   - Platform: `ninjatrader`
   - Account ID: `YourNinjaTraderAccountName` (e.g., "Sim101")
   - **Must match exactly!**

### Step 4: Enable Add-On

1. Start NinjaTrader
2. Connect to demo account
3. Tools → Add-Ons → Enable "Payout King Add-On"
4. Check Output window for status

### Step 5: Verify

**Backend logs should show:**
```
INFO: Received data from NinjaTrader account: Sim101
INFO: POST /api/v1/ninjatrader/account-update HTTP/1.1" 200 OK
```

**Frontend should show:**
- Account with live data
- Real-time updates
- Rule states calculated

## 📚 Documentation

- **`NINJATRADER_TESTING_GUIDE.md`** - Complete step-by-step guide
- **`NINJATRADER_QUICK_START.md`** - Quick 5-step setup
- **`BUILD_AND_INSTALL.md`** - Build and installation details

## 🎯 Testing Scenarios

1. **Monitor account** - Watch real-time updates
2. **Place trades** - See positions and PnL
3. **Test drawdown** - Watch rule states change
4. **Close positions** - See daily PnL tracking

## ⚠️ Important Notes

1. **Account ID must match exactly** - Case-sensitive
2. **Backend must be running** - Check with `curl http://localhost:8000/health`
3. **Config file required** - Add-on won't work without it
4. **Restart NinjaTrader** - After installing DLL

## 🐛 Common Issues

### "Account not found"
- Check Account ID matches exactly
- Check account is connected in frontend
- Check backend logs for available accounts

### "Backend error"
- Verify backend is running
- Check config.json URL
- Check firewall settings

### No data in frontend
- Verify account connected
- Check Account ID matches
- Check WebSocket connection

---

**You're all set!** Follow the guides above to test with a real NinjaTrader demo account.
