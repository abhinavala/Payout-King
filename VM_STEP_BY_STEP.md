# Step-by-Step: VM Setup for NinjaTrader Testing

## Pre-Flight Checklist

Before starting, make sure you have on your VM:

- [ ] Windows installed
- [ ] NinjaTrader 8 Desktop installed
- [ ] Visual Studio 2022 (Community is fine)
- [ ] .NET Framework 4.8 (usually comes with Windows)
- [ ] Cursor installed and logged in
- [ ] Project files accessible on VM

## Step 1: Get Project on VM

### Method A: Git Clone (If you have a repo)

```bash
# In Cursor terminal on VM
git clone <your-repo-url>
cd payout-king
```

### Method B: Copy Files

1. **On Mac:** Zip the project (excluding node_modules, venv, etc.)
2. **Transfer to VM:** Via shared folder, USB, or network
3. **On VM:** Extract and open in Cursor

### Method C: Network Share

1. **Share folder from Mac**
2. **Map drive on VM**
3. **Open in Cursor**

## Step 2: Open Project in Cursor (VM)

1. **Open Cursor on VM**
2. **File → Open Folder**
3. **Navigate to:** `payout-king` directory
4. **Click "Open"**

**You should see:**
- `apps/` folder
- `packages/` folder
- `docs/` folder
- Project structure

## Step 3: Verify Backend Connection

**Important:** Your backend is running on your Mac, not the VM.

**You have two options:**

### Option A: Use Mac's IP Address

1. **Find your Mac's IP:**
   ```bash
   # On Mac terminal
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```
   Example: `192.168.1.100`

2. **Update config on VM:**
   ```json
   {
     "backendUrl": "http://192.168.1.100:8000",
     "apiKey": ""
   }
   ```

### Option B: Run Backend on VM (Optional)

If you want backend on VM too:
```bash
# Install Python on VM
# Install dependencies
# Run backend
```

**Recommendation:** Use Option A (Mac's IP) - simpler!

## Step 4: Build Add-On (I'll Help With This)

Once project is open in Cursor on VM, I'll guide you through:

1. Opening in Visual Studio
2. Restoring NuGet packages
3. Building the DLL
4. Installing to NinjaTrader

## Step 5: Create Config File

**Location on VM:**
```
C:\Users\<YourWindowsUser>\Documents\NinjaTrader 8\PayoutKing\config.json
```

**Content:**
```json
{
  "backendUrl": "http://<your-mac-ip>:8000",
  "apiKey": ""
}
```

## Step 6: Install Add-On

**Copy DLL to:**
```
C:\Users\<YourWindowsUser>\Documents\NinjaTrader 8\bin\Custom\AddOns\PayoutKingAddOn.dll
```

## Step 7: Connect Account

**In frontend (on Mac):**
- Account ID must match NinjaTrader account name exactly
- Usually: `Sim101` for demo accounts

## Step 8: Enable Add-On

**In NinjaTrader:**
- Tools → Add-Ons
- Enable "Payout King Add-On"
- Check Output window

## Step 9: Verify

**Check backend logs (on Mac):**
- Should see: `POST /api/v1/ninjatrader/account-update HTTP/1.1" 200 OK`

**Check frontend (on Mac):**
- Account should appear with live data

## Current Status

**Ready for you to:**
1. Open project in Cursor on VM
2. Tell me when it's open
3. I'll guide you through each step!

---

**Once you have the project open in Cursor on the VM, let me know and I'll help you with the build and setup!**
