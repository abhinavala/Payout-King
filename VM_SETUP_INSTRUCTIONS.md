# VM Setup Instructions - NinjaTrader Testing

## Option 1: Clone Project on VM (Recommended)

### On Your VM (Windows):

1. **Open Cursor on VM**
2. **Clone or access the project:**
   ```bash
   # If using git:
   git clone <your-repo-url>
   cd payout-king
   
   # Or if you have the project on a network share:
   # Access it via shared folder
   ```

3. **Open the project in Cursor:**
   - File → Open Folder
   - Navigate to the `payout-king` directory

## Option 2: Copy Project Files

### On Your Mac:

1. **Create a zip of the project:**
   ```bash
   cd /Users/abhinavala
   zip -r payout-king.zip payout-king -x "*/node_modules/*" "*/venv/*" "*/__pycache__/*" "*/bin/*" "*/obj/*"
   ```

2. **Transfer to VM:**
   - Use shared folder, USB, or network transfer
   - Extract on VM

### On Your VM:

1. **Extract the zip**
2. **Open in Cursor:**
   - File → Open Folder
   - Navigate to extracted `payout-king` folder

## Option 3: Use Network Share

### On Your Mac:

1. **Share the folder:**
   - System Preferences → Sharing
   - Enable File Sharing
   - Share the `payout-king` folder

### On Your VM:

1. **Map network drive:**
   - Connect to `\\<your-mac-ip>\payout-king`
   - Or use shared folder feature

2. **Open in Cursor:**
   - File → Open Folder
   - Navigate to network share

## Once Project is Open in Cursor on VM

I can help you with the setup steps. Here's what we'll do:

1. ✅ Build the add-on
2. ✅ Install to NinjaTrader
3. ✅ Create config file
4. ✅ Connect account
5. ✅ Test end-to-end

## Quick Start Commands for VM

Once you have the project open in Cursor on the VM, I can guide you through:

```bash
# Navigate to add-on
cd apps/ninjatrader-addon/PayoutKingAddOn

# Open in Visual Studio (if installed)
# Or I can help you build it
```

## What I Can Help With

Once you have the project open in Cursor on the VM, I can:

1. ✅ Help build the add-on
2. ✅ Create config files
3. ✅ Verify installation paths
4. ✅ Troubleshoot any issues
5. ✅ Test the integration

## Next Step

**Tell me when you have the project open in Cursor on the VM**, and I'll guide you through each step!

---

**Current Status:**
- ✅ Project structure ready
- ✅ Add-on code ready
- ✅ Backend ready (on Mac)
- ⏳ Waiting for you to open project on VM
