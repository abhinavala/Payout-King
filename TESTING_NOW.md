# 🚀 Ready to Test - Services Running!

## ✅ Setup Complete

**Backend:** Running on http://localhost:8000
**Frontend:** Running on http://localhost:5173

Both services are now running in the background. You can start testing immediately!

## 🧪 Quick Test Steps

### Step 1: Open Frontend
Open your browser and go to:
```
http://localhost:5173
```

### Step 2: Register a User
1. Click "Register" (or navigate to register page)
2. Enter:
   - **Email:** `test@example.com`
   - **Password:** `testpassword123`
3. Click "Register"
4. You should be redirected to the dashboard

### Step 3: Connect a Test Account
1. On the dashboard, click **"+ Connect Account"**
2. Fill in the form:
   - **Platform:** `ninjatrader`
   - **Account ID:** `TEST-001`
   - **Account Name:** `Test Account`
   - **Firm:** `apex` (or `topstep`)
   - **Account Type:** `eval` (or `pa`, `funded`)
   - **Account Size:** `50000` (for $50k account)
   - **Rule Set Version:** `v1`
   - **Username:** (leave empty for NinjaTrader)
   - **Password:** (leave empty for NinjaTrader)
3. Click "Connect"
4. Account should appear in the dashboard

### Step 4: Send Test Data

You have two options:

#### Option A: Use Test API Endpoint (Easiest)

First, get your auth token. Open browser console (F12) and run:
```javascript
localStorage.getItem('token')
```

Or login via API:
```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Send test account data
curl -X POST http://localhost:8000/api/v1/test/account-data \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "TEST-001",
    "timestamp": "2024-01-15T10:00:00Z",
    "equity": 51000,
    "balance": 50000,
    "realizedPnL": 0,
    "unrealizedPnL": 1000,
    "highWaterMark": 51000,
    "dailyPnL": 0,
    "startingBalance": 50000,
    "openPositions": [
      {
        "symbol": "ES",
        "quantity": 1,
        "avgPrice": 4500,
        "currentPrice": 4510,
        "unrealizedPnL": 50,
        "openedAt": "2024-01-15T09:00:00Z",
        "peakUnrealizedLoss": 0
      }
    ],
    "dailyPnLHistory": {},
    "orders": []
  }'
```

#### Option B: Use NinjaTrader Add-On

1. Build the add-on:
   ```bash
   cd /Users/abhinavala/payout-king/apps/ninjatrader-addon/PayoutKingAddOn
   dotnet build
   ```
2. Install in NinjaTrader
3. Configure backend URL: `http://localhost:8000`
4. Start NinjaTrader and enable add-on

### Step 5: Verify Everything Works

**Check Dashboard:**
- ✅ Account appears in table/cards
- ✅ Equity shows correctly ($51,000)
- ✅ Rule states are displayed
- ✅ Status badges show correct colors (likely SAFE)
- ✅ WebSocket connection (check browser console for messages)

**Check API:**
```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

**Check Audit Logs:**
```bash
# Get token first (from Step 4A)
curl -X GET "http://localhost:8000/api/v1/audit-logs?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

## 🎯 Expected Results

After sending test data, you should see:
1. ✅ Account in dashboard with equity $51,000
2. ✅ Rule states calculated (trailing drawdown, etc.)
3. ✅ Status badges (likely SAFE if equity > starting balance)
4. ✅ Audit logs created
5. ✅ WebSocket updates in browser console

## 🐛 Troubleshooting

### Backend not responding
- Check if it's running: `lsof -i :8000`
- Check logs in terminal where you started it
- Try restarting: Stop (Ctrl+C) and run `uvicorn main:app --reload --port 8000` again

### Frontend not loading
- Check if it's running: `lsof -i :5173`
- Check browser console for errors
- Try restarting: Stop (Ctrl+C) and run `npm run dev` again

### No data showing
- Check account is connected
- Check test data was sent successfully
- Check backend logs for errors
- Verify account ID matches

### WebSocket not connecting
- Check browser console for WebSocket errors
- Verify backend is running
- Check CORS settings in backend `.env`

## 📊 Test Different Scenarios

### Test 1: Safe Status
- Send data with equity > HWM
- Should show SAFE status (green)

### Test 2: Warning Status
- Send data approaching drawdown limit
- Should show CAUTION (yellow) or CRITICAL (red)
- Check audit logs for warnings

### Test 3: Violation
- Send data that violates a rule (e.g., equity < HWM - max drawdown)
- Should show VIOLATED status (red)
- Check audit logs for violation

### Test 4: Group Risk
1. Create a group:
   ```bash
   curl -X POST http://localhost:8000/api/v1/groups \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Group", "account_ids": ["TEST-001"]}'
   ```
2. Check group risk:
   ```bash
   # Get group ID from response, then:
   curl -X GET "http://localhost:8000/api/v1/groups/{group_id}/risk" \
     -H "Authorization: Bearer $TOKEN"
   ```

## 🎉 You're Ready!

Everything is set up and running. Start with Step 1 above and test the system!

**Quick Links:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

**Note:** Both services are running in the background. To stop them, you'll need to find and kill the processes, or restart your terminal.
