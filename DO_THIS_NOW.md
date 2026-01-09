# 🚀 DO THIS NOW - Connect Your NinjaTrader Account

## Step-by-Step Checklist

Follow these steps **in order** to connect and test your account.

---

## ✅ STEP 1: Make Sure Backend & Frontend Are Running

### Check Backend:
```bash
curl http://localhost:8000/health
```

**If not running:**
```bash
cd apps/backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
echo $! > ../backend.pid
```

### Check Frontend:
Open browser: http://localhost:5173

**If not running:**
```bash
cd apps/frontend
npm run dev
```

---

## ✅ STEP 2: Build the NinjaTrader Add-On

### Option A: If you have Visual Studio (Windows)

1. **Open Visual Studio**
2. **Open:** `apps/ninjatrader-addon/PayoutKingAddOn/PayoutKingAddOn.csproj`
3. **Restore NuGet packages** (right-click solution → Restore)
4. **Build → Build Solution** (Release mode)
5. **Copy the DLL:**
   - Find: `apps/ninjatrader-addon/PayoutKingAddOn/bin/Release/PayoutKingAddOn.dll`
   - Copy to: `C:\Users\<YourUser>\Documents\NinjaTrader 8\bin\Custom\AddOns\`

### Option B: If you DON'T have Visual Studio

**You need to:**
- Install Visual Studio Community (free) OR
- Use a Windows machine with Visual Studio OR
- Ask someone to build it for you

**The Add-On MUST be built on Windows with Visual Studio.**

---

## ✅ STEP 3: Create Config File

**On Windows, create this file:**

```
C:\Users\<YourUser>\Documents\NinjaTrader 8\PayoutKing\config.json
```

**Content:**
```json
{
  "backendUrl": "http://localhost:8000",
  "apiKey": ""
}
```

**Note:** If your backend is on a different machine, use that IP instead of `localhost`.

---

## ✅ STEP 4: Enable Add-On in NinjaTrader

1. **Open NinjaTrader 8**
2. **Go to:** Tools → Add-Ons
3. **Find:** "Payout King Add-On"
4. **Check the box** to enable it
5. **Restart NinjaTrader** (required!)

**After restart, check the log:**
- Tools → Log
- Look for: `✅ Connected to account: [YourAccount]`
- Look for: `✅ Payout King Add-On started`

---

## ✅ STEP 5: Get Your NinjaTrader Account Name

**In NinjaTrader:**
1. Go to: **Tools → Options → General**
2. Look for your account name (e.g., "Sim101", "Demo123", etc.)

**OR**

1. Open **Control Center**
2. Click **Accounts** tab
3. See your account name there

**Write it down!** You'll need it in the next step.

---

## ✅ STEP 6: Connect Account in Dashboard

1. **Open browser:** http://localhost:5173
2. **Login** (or register if needed)
3. **Click "Connect Account"** button
4. **Fill in the form:**
   - **Platform:** NinjaTrader ✅
   - **Prop Firm:** Select one (e.g., Apex)
   - **Account Type:** Select (e.g., eval)
   - **Account ID:** ⚠️ **Enter your NinjaTrader account name** (from Step 5)
   - **Account Name:** Give it a friendly name (e.g., "My Demo Account")
   - **Account Size:** Enter your demo account size (e.g., 50000)
5. **Click "Connect Account"**

**You should see:** Account appears in your dashboard!

---

## ✅ STEP 7: Verify Connection

### Check NinjaTrader Log:
1. **In NinjaTrader:** Tools → Log
2. **Look for:**
   ```
   ✅ Connected to account: [YourAccount]
   ✅ Payout King Add-On started
   ✅ Data sent successfully
   ```

### Check Backend Logs:
```bash
tail -f apps/backend.log
```

**You should see:**
```
INFO: POST /api/v1/ninjatrader/account-data HTTP/1.1 200 OK
```

### Check Dashboard:
1. **Refresh:** http://localhost:5173
2. **You should see:**
   - Your account card
   - Equity, balance showing
   - Rule states (trailing drawdown, daily loss, etc.)
   - Updates every 2 seconds

---

## ✅ STEP 8: Test Real-Time Updates

1. **In NinjaTrader:** Open a position (buy or sell a contract)
2. **Watch the dashboard** - it should update within 2 seconds
3. **You should see:**
   - Unrealized PnL showing up
   - Equity changing
   - Rule states updating

---

## ✅ STEP 9: Test Alerts

1. **Open a losing position** in NinjaTrader (or use test scenarios)
2. **Watch the dashboard** as unrealized loss increases
3. **You should see:**
   - Status changing: SAFE → CAUTION → CRITICAL
   - Warnings appearing
   - Buffer decreasing
   - Recovery paths (if recoverable)

**OR use the test button:**
1. **Click "🧪 Test Account"** on the account card
2. **Select:** "Near Drawdown Violation"
3. **Click:** "Run Test Scenario"
4. **See:** Detailed results with warnings

---

## 🔧 Troubleshooting

### Add-On Not Loading?
- ✅ DLL in correct location: `NinjaTrader 8\bin\Custom\AddOns\`
- ✅ Restart NinjaTrader completely
- ✅ Check NinjaTrader log for errors

### No Data Sending?
- ✅ Backend running? `curl http://localhost:8000/health`
- ✅ Config file path correct?
- ✅ Account logged in to NinjaTrader?
- ✅ Add-on enabled and restarted?

### Account Not Found?
- ✅ Account ID matches NinjaTrader account name **exactly**
- ✅ Account connected in dashboard?
- ✅ Check: `curl http://localhost:8000/api/v1/ninjatrader/debug/accounts`

### No Data in Dashboard?
- ✅ WebSocket connected? (check browser console)
- ✅ Backend receiving data? (check logs)
- ✅ Refresh dashboard

---

## 📋 Quick Checklist

- [ ] Backend running (http://localhost:8000/health)
- [ ] Frontend running (http://localhost:5173)
- [ ] Add-On built and installed
- [ ] Config file created
- [ ] Add-On enabled in NinjaTrader
- [ ] NinjaTrader restarted
- [ ] Account connected in dashboard
- [ ] Data appearing in dashboard
- [ ] Real-time updates working
- [ ] Alerts showing when close to violation

---

## 🎯 What Success Looks Like

✅ **NinjaTrader Log:**
```
✅ Connected to account: Sim101
✅ Payout King Add-On started
✅ Data sent successfully (every 2 seconds)
```

✅ **Dashboard:**
- Account card visible
- Equity, balance updating
- Rule states showing
- Status badges (SAFE/CAUTION/CRITICAL)
- Real-time updates every 2 seconds

✅ **When you trade:**
- Dashboard updates within 2 seconds
- Unrealized PnL shows
- Rule states recalculate
- Warnings appear when close to limits

---

**Start with Step 1 and work through each step!** 🚀

