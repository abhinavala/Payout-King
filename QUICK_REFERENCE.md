# 🚀 Quick Reference - VM Setup

## Current Task: Build & Install NinjaTrader Add-On

### Quick Commands

```bash
# Verify project structure
cd Payout-King
ls apps/ninjatrader-addon/PayoutKingAddOn/

# Build location (after building in Visual Studio)
apps/ninjatrader-addon/PayoutKingAddOn/bin/Debug/PayoutKingAddOn.dll

# Install location
C:\Users\<YourUser>\Documents\NinjaTrader 8\bin\Custom\AddOns\PayoutKingAddOn.dll

# Config location
C:\Users\<YourUser>\Documents\NinjaTrader 8\PayoutKing\config.json
```

### Config File Template

```json
{
  "backendUrl": "http://<your-mac-ip>:8000",
  "apiKey": ""
}
```

### Key Paths

- **Add-On Project:** `apps/ninjatrader-addon/PayoutKingAddOn/`
- **Built DLL:** `apps/ninjatrader-addon/PayoutKingAddOn/bin/Debug/PayoutKingAddOn.dll`
- **Install To:** `...\NinjaTrader 8\bin\Custom\AddOns\`
- **Config:** `...\NinjaTrader 8\PayoutKing\config.json`

### Account ID

- Must match NinjaTrader account name **exactly**
- Usually: `Sim101` for demo accounts
- Case-sensitive!

### Mac IP Address

**On Mac, run:**
```bash
ipconfig getifaddr en0
```

### Verification Steps

1. ✅ Add-on appears in NinjaTrader → Tools → Add-Ons
2. ✅ Output window shows "initialized"
3. ✅ Backend logs show POST requests
4. ✅ Frontend shows account connected
5. ✅ Real-time updates when trading

---

**See `VM_CURSOR_INSTRUCTIONS.md` for detailed step-by-step guide!**
