# ⚡ Quick Connect - NinjaTrader Demo Account

## 5-Minute Setup

### 1. Build Add-On (One-Time)

```bash
# Open in Visual Studio
apps/ninjatrader-addon/PayoutKingAddOn/PayoutKingAddOn.csproj

# Build → Build Solution (Release mode)
# Copy DLL to: C:\Users\<YourUser>\Documents\NinjaTrader 8\bin\Custom\AddOns\
```

### 2. Create Config

Create: `C:\Users\<YourUser>\Documents\NinjaTrader 8\PayoutKing\config.json`

```json
{
  "backendUrl": "http://localhost:8000",
  "apiKey": ""
}
```

### 3. Enable in NinjaTrader

- Tools → Add-Ons → Enable "Payout King Add-On"
- Restart NinjaTrader

### 4. Connect in Dashboard

1. Go to: http://localhost:5173
2. Click "Connect Account"
3. Fill in:
   - Platform: **NinjaTrader**
   - Account ID: **Your NinjaTrader account name** (e.g., "Sim101")
   - Firm: Apex (or any)
   - Account Type: eval
   - Account Size: 50000
4. Click "Connect Account"

### 5. Verify

**Check NinjaTrader Log (Tools → Log):**
```
✅ Connected to account: Sim101
✅ Payout King Add-On started
✅ Data sent successfully
```

**Check Dashboard:**
- Account card appears
- Equity, balance showing
- Rule states updating every 2 seconds

## Troubleshooting

**No data?**
- Check backend: `curl http://localhost:8000/health`
- Check NinjaTrader log for errors
- Verify account ID matches exactly

**Add-on not loading?**
- Verify DLL is in: `NinjaTrader 8\bin\Custom\AddOns\`
- Restart NinjaTrader completely

**Account not found?**
- Verify account ID in dashboard matches NinjaTrader account name exactly
- Check account is connected and active

---

**That's it!** Your account should now be tracking rules in real-time! 🚀

