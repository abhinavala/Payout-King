# 🚀 VM Setup Instructions - Complete Guide

## ✅ Current Status

- ✅ Project is open in Cursor on VM
- ✅ Code cloned from GitHub
- ✅ Ready to build NinjaTrader add-on

## 📋 Step-by-Step Instructions

### STEP 1: Verify Project Structure

**In Cursor terminal on VM, run:**

```bash
# Check you're in the right place
pwd
# Should show: C:\Users\<YourUser>\...\Payout-King

# Verify files are there
ls
# Should show: apps/, packages/, docs/, etc.

# Check add-on exists
ls apps/ninjatrader-addon/PayoutKingAddOn/
# Should show: PayoutKingAddOn.cs, PayoutKingAddOn.csproj, etc.
```

### STEP 2: Open Add-On in Visual Studio

**Option A: From Cursor (Easiest)**

1. **In Cursor file explorer:**
   - Navigate to: `apps/ninjatrader-addon/PayoutKingAddOn/`
   - Right-click: `PayoutKingAddOn.csproj`
   - Select: "Open with" → "Visual Studio 2022"

**Option B: From Visual Studio**

1. **Open Visual Studio 2022**
2. **File → Open → Project/Solution**
3. **Navigate to:** `apps/ninjatrader-addon/PayoutKingAddOn/PayoutKingAddOn.csproj`
4. **Click "Open"**

**You should see in Visual Studio:**
- Solution Explorer on the right
- `PayoutKingAddOn.csproj` in the solution
- C# files: `PayoutKingAddOn.cs`, `AccountUpdateMessage.cs`

### STEP 3: Restore NuGet Packages

**In Visual Studio:**

1. **Right-click the solution** (or project) in Solution Explorer
2. **Click:** "Restore NuGet Packages"
3. **Wait** for restore to complete
4. **Check Output window** (View → Output) for any errors

**Expected packages:**
- `Newtonsoft.Json` (for JSON serialization)
- NinjaTrader SDK references (should be automatic)

**If restore fails:**
- Check internet connection
- Try: Tools → NuGet Package Manager → Package Manager Console
- Run: `Update-Package -reinstall`

### STEP 4: Build the Add-On

**In Visual Studio:**

1. **Set Configuration:**
   - Top toolbar: Select **"Debug"** from dropdown
   - Platform: **"Any CPU"** (default)

2. **Build:**
   - Click: **Build → Build Solution**
   - Or press: `Ctrl+Shift+B`
   - Or right-click solution → "Build"

**Expected result:**
- ✅ **Build succeeded** (in Output window)
- ✅ **0 errors** (warnings are OK)
- ✅ DLL created at: `bin/Debug/PayoutKingAddOn.dll`

**If build fails:**
- Check Output window for specific errors
- Verify .NET Framework 4.8 is installed
- Verify NinjaTrader SDK is referenced correctly

### STEP 5: Find Your Mac's IP Address

**On your Mac, run:**

```bash
# Find IP address
ipconfig getifaddr en0
# Or try en1 if en0 doesn't work
# Or check: System Preferences → Network → Wi-Fi → IP address
```

**Example output:** `192.168.1.100`

**Write this down** - you'll need it for the config file!

### STEP 6: Create Config File

**On VM, create folder:**

```bash
# In Cursor terminal or File Explorer
mkdir "C:\Users\<YourWindowsUser>\Documents\NinjaTrader 8\PayoutKing"
```

**Create file:** `config.json` in that folder

**Content (replace `<your-mac-ip>` with actual IP):**

```json
{
  "backendUrl": "http://192.168.1.100:8000",
  "apiKey": ""
}
```

**Example if your Mac IP is 192.168.1.100:**
```json
{
  "backendUrl": "http://192.168.1.100:8000",
  "apiKey": ""
}
```

**Save the file!**

### STEP 7: Install Add-On to NinjaTrader

**⚠️ IMPORTANT: Close NinjaTrader if it's running!**

**In Cursor terminal or File Explorer:**

1. **Find the DLL:**
   - Location: `apps/ninjatrader-addon/PayoutKingAddOn/bin/Debug/PayoutKingAddOn.dll`

2. **Copy DLL:**
   - Copy: `PayoutKingAddOn.dll`
   - Paste to: `C:\Users\<YourWindowsUser>\Documents\NinjaTrader 8\bin\Custom\AddOns\PayoutKingAddOn.dll`

3. **Create folder if needed:**
   - If `AddOns` folder doesn't exist, create it first

**Verify:**
- DLL exists at: `...\NinjaTrader 8\bin\Custom\AddOns\PayoutKingAddOn.dll`

### STEP 8: Enable Add-On in NinjaTrader

1. **Open NinjaTrader 8 Desktop**

2. **Go to:** Tools → Add-Ons

3. **Find:** "Payout King Add-On" in the list

4. **Enable it:**
   - Check the box next to it
   - Click "OK"

5. **Restart NinjaTrader** if prompted

### STEP 9: Verify Add-On is Running

**In NinjaTrader:**

1. **Open Output window:**
   - New → Output
   - Or: Tools → Output

2. **Look for logs:**
   - ✅ "PayoutKing initialized"
   - ✅ "Account Sim101 detected" (or your account name)
   - ✅ "Data sent successfully"
   - ✅ "Connected to backend"

**If you see errors:**
- Check config file path and content
- Verify backend is running on Mac
- Check Mac's IP address is correct
- Verify firewall isn't blocking connection

### STEP 10: Connect Account in Frontend

**On your Mac (frontend running at localhost:5173):**

1. **Go to dashboard**
2. **Click:** "Connect Account" button
3. **Enter:**
   - **Platform:** NinjaTrader
   - **Account ID:** Sim101 (must match NinjaTrader account name exactly!)
   - **Firm:** Select appropriate firm (Apex or Topstep)
4. **Click:** "Save" or "Connect"

**⚠️ Critical:** Account ID must match NinjaTrader account name exactly!

### STEP 11: Verify Backend Receives Data

**On your Mac (backend terminal):**

You should see logs like:
```
INFO: POST /api/v1/ninjatrader/account-update HTTP/1.1" 200 OK
INFO: Account Sim101 updated
INFO: Rule evaluation completed
```

**This means:**
- ✅ Add-on → backend connection works
- ✅ Data format is valid
- ✅ Rule engine is executing

### STEP 12: Verify Frontend Updates Live

**Place a trade in NinjaTrader (Sim101 account):**

1. **Open a chart** in NinjaTrader
2. **Place a trade** (buy or sell)
3. **Watch the frontend** (on Mac)

**You should see:**
- ✅ PnL updating in real time
- ✅ Risk state changing (green/yellow/red)
- ✅ Distance-to-violation numbers moving
- ✅ Rule breakdown updating

## 🎯 Success Checklist

- [ ] Add-on built successfully
- [ ] Config file created with correct Mac IP
- [ ] DLL installed to NinjaTrader AddOns folder
- [ ] Add-on enabled in NinjaTrader
- [ ] Output window shows "initialized" and "connected"
- [ ] Account connected in frontend
- [ ] Backend receiving data (check logs)
- [ ] Frontend updating in real time

## 🐛 Troubleshooting

### Add-On Not Appearing in NinjaTrader

- **Check DLL location:** Must be in `...\NinjaTrader 8\bin\Custom\AddOns\`
- **Check DLL name:** Must be `PayoutKingAddOn.dll`
- **Restart NinjaTrader** after copying DLL
- **Check Output window** for errors

### Add-On Not Connecting to Backend

- **Verify backend is running** on Mac (check terminal)
- **Check Mac IP address** is correct in config
- **Check firewall** isn't blocking port 8000
- **Verify config file** path and content
- **Check Output window** in NinjaTrader for specific errors

### Frontend Not Showing Account

- **Verify Account ID** matches NinjaTrader account name exactly
- **Check backend logs** to see if data is being received
- **Refresh frontend** page
- **Check WebSocket connection** (browser console)

### No Real-Time Updates

- **Check WebSocket connection** in browser console
- **Verify backend is sending updates** (check backend logs)
- **Check account is connected** in frontend
- **Verify add-on is sending data** (check NinjaTrader Output)

## 📝 Next Steps After Setup

Once everything is working:

1. **Test with real trades** in NinjaTrader
2. **Monitor rule violations** in frontend
3. **Check audit logs** in backend
4. **Test multiple accounts** if you have them
5. **Test account groups** for copy-trade logic

---

**Ready to start? Begin with STEP 1 and work through each step!**
