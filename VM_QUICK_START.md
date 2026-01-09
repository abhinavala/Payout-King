# VM Quick Start - What to Do Now

## Current Situation

- ✅ **Backend:** Running on Mac at `localhost:8000`
- ✅ **Frontend:** Running on Mac at `localhost:5173`
- ✅ **Project:** Ready on Mac at `/Users/abhinavala/payout-king`
- ⏳ **VM:** Need to get project there and set up

## What You Need to Do

### Step 1: Get Project on VM

**Option A: Git (if you have a repo)**
```bash
# In Cursor terminal on VM
git clone <your-repo-url>
```

**Option B: Copy Files**
1. Zip the project on Mac (excluding node_modules, venv)
2. Transfer to VM
3. Extract and open in Cursor

**Option C: Network Share**
1. Share folder from Mac
2. Access from VM
3. Open in Cursor

### Step 2: Open in Cursor on VM

1. **Open Cursor on VM**
2. **File → Open Folder**
3. **Navigate to:** `payout-king` folder
4. **Click "Open"**

### Step 3: Tell Me When Ready

**Once project is open in Cursor on VM, say:**
- "Project is open on VM"
- "Ready to build add-on"
- Or just "ready"

**Then I'll guide you through:**
1. Building the add-on
2. Installing to NinjaTrader
3. Creating config
4. Testing

## Important: Backend URL

**Your backend is on Mac, not VM!**

**Find your Mac's IP:**
```bash
# On Mac terminal
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Use this IP in config on VM:**
```json
{
  "backendUrl": "http://<your-mac-ip>:8000",
  "apiKey": ""
}
```

**Example:**
```json
{
  "backendUrl": "http://192.168.1.100:8000",
  "apiKey": ""
}
```

## Quick Checklist

- [ ] Project files on VM
- [ ] Project open in Cursor on VM
- [ ] Mac's IP address noted
- [ ] Ready to build add-on

## Next Steps (After Project is Open)

1. **I'll help you build the add-on**
2. **I'll help you install it**
3. **I'll help you configure it**
4. **I'll help you test it**

---

**Tell me when you have the project open in Cursor on the VM, and I'll start guiding you through the setup!**
