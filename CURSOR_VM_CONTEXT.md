# Context & Instructions for Cursor on VM

## Project Context

**Payout King** is a desktop-first risk monitoring platform for futures prop-firm traders. It prevents rule violations by monitoring live account states and issuing warnings.

**Current Status:**
- ✅ Rule engine implemented (all rules)
- ✅ Backend running on Mac (localhost:8000)
- ✅ Frontend running on Mac (localhost:5173)
- ✅ NinjaTrader add-on code ready
- ⏳ Need to build and test add-on on VM

**Architecture:**
- **Add-On (C#):** Captures live data from NinjaTrader → sends to backend
- **Backend (Python/FastAPI):** Receives data, runs rule engine, broadcasts via WebSocket
- **Frontend (React):** Displays real-time risk status

## Testing Goal

Test end-to-end flow with NinjaTrader demo account (Sim101):
1. Build and install add-on
2. Connect to backend on Mac
3. Send live account data
4. Verify frontend updates in real-time

## Instructions: Build & Test NinjaTrader Add-On

### Step 1: Build Add-On in Visual Studio

**Action:**
1. Open `apps/ninjatrader-addon/PayoutKingAddOn/PayoutKingAddOn.csproj` in Visual Studio 2022
2. Restore NuGet packages (right-click solution → Restore NuGet Packages)
3. Build Solution (Build → Build Solution or Ctrl+Shift+B)
4. Verify: DLL created at `bin/Debug/PayoutKingAddOn.dll`

**Expected:** Build succeeds with 0 errors

### Step 2: Get Mac IP Address

**Action:** Ask user for Mac's IP address, or provide command:
```bash
# On Mac terminal
ipconfig getifaddr en0
```

**Purpose:** Needed for config file to connect add-on to backend

### Step 3: Create Config File

**Action:** Create file at:
```
C:\Users\<WindowsUser>\Documents\NinjaTrader 8\PayoutKing\config.json
```

**Content:**
```json
{
  "backendUrl": "http://<mac-ip>:8000",
  "apiKey": ""
}
```

**Replace `<mac-ip>` with actual IP from Step 2**

### Step 4: Install DLL to NinjaTrader

**Action:**
1. Copy `apps/ninjatrader-addon/PayoutKingAddOn/bin/Debug/PayoutKingAddOn.dll`
2. Paste to: `C:\Users\<WindowsUser>\Documents\NinjaTrader 8\bin\Custom\AddOns\PayoutKingAddOn.dll`
3. Create `AddOns` folder if it doesn't exist

**Important:** NinjaTrader must be closed during this step

### Step 5: Enable Add-On in NinjaTrader

**Action:**
1. Open NinjaTrader 8 Desktop
2. Tools → Add-Ons
3. Find "Payout King Add-On"
4. Enable it (check box)
5. Restart NinjaTrader if prompted

### Step 6: Verify Add-On Running

**Action:**
1. In NinjaTrader: New → Output (or Tools → Output)
2. Look for logs:
   - ✅ "PayoutKing initialized"
   - ✅ "Account Sim101 detected" (or account name)
   - ✅ "Connected to backend"
   - ✅ "Data sent successfully"

**If errors:** Check config file path/content, verify backend running on Mac, check Mac IP

### Step 7: Connect Account in Frontend

**Action (on Mac):**
1. Open frontend: http://localhost:5173
2. Login/Register if needed
3. Click "Connect Account"
4. Enter:
   - Platform: **NinjaTrader**
   - Account ID: **Sim101** (must match NinjaTrader account name exactly)
   - Firm: Select appropriate (Apex or Topstep)
5. Save

**Critical:** Account ID must match NinjaTrader account name exactly (case-sensitive)

### Step 8: Verify Backend Receives Data

**Action (check Mac backend terminal):**
- Should see: `POST /api/v1/ninjatrader/account-update HTTP/1.1" 200 OK`
- Should see: `Account Sim101 updated`

**If not receiving:**
- Check add-on Output window for errors
- Verify config file backendUrl is correct
- Check firewall isn't blocking port 8000

### Step 9: Test Real-Time Updates

**Action:**
1. In NinjaTrader: Place a trade (buy/sell) on Sim101 account
2. Watch frontend dashboard (on Mac)
3. Should see:
   - ✅ PnL updating in real-time
   - ✅ Risk status changing (green/yellow/red)
   - ✅ Distance-to-violation numbers updating
   - ✅ Rule breakdown updating

**Success Criteria:**
- ✅ Add-on sends data every 300ms
- ✅ Backend receives and processes data
- ✅ Frontend updates in real-time
- ✅ Rule engine calculates correctly

## Key Files & Paths

- **Add-On Project:** `apps/ninjatrader-addon/PayoutKingAddOn/`
- **Built DLL:** `apps/ninjatrader-addon/PayoutKingAddOn/bin/Debug/PayoutKingAddOn.dll`
- **Install To:** `C:\Users\<User>\Documents\NinjaTrader 8\bin\Custom\AddOns\PayoutKingAddOn.dll`
- **Config:** `C:\Users\<User>\Documents\NinjaTrader 8\PayoutKing\config.json`

## Troubleshooting

**Add-on not appearing:**
- Verify DLL in correct location
- Restart NinjaTrader
- Check Output window for errors

**Not connecting to backend:**
- Verify Mac IP in config
- Check backend is running on Mac
- Check firewall settings

**Frontend not updating:**
- Verify Account ID matches exactly
- Check WebSocket connection (browser console)
- Verify backend is sending updates

## Success Indicators

✅ Add-on appears in NinjaTrader Add-Ons list
✅ Output window shows "initialized" and "connected"
✅ Backend logs show POST requests
✅ Frontend shows account connected
✅ Real-time updates when trading

---

**Execute these steps in order. Ask user for Mac IP if needed. Report any errors immediately.**
