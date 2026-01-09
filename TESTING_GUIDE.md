# Complete Testing Guide - Payout King

## ✅ What We've Built

1. **User Authentication** - Register/Login
2. **Account Management** - Connect trading accounts
3. **Rule Engine** - Real-time rule evaluation
4. **Risk Monitoring** - Status indicators, buffers, warnings
5. **Multi-Account Groups** - Group risk evaluation
6. **Audit Logging** - Complete audit trail
7. **Real-time Updates** - WebSocket notifications

## 🧪 Testing Steps

### Phase 1: Basic Setup ✅ (You've Done This!)

- [x] Register user
- [x] Login
- [x] Backend running
- [x] Frontend running

### Phase 2: Connect Test Account

1. **On Dashboard, click "+ Connect Account"**

2. **Fill in the form:**
   - **Platform:** `ninjatrader`
   - **Account ID:** `TEST-001`
   - **Account Name:** `Test Account 1`
   - **Firm:** `apex` (or `topstep`)
   - **Account Type:** `eval` (or `pa`, `funded`)
   - **Account Size:** `50000` (for $50k account)
   - **Rule Set Version:** `v1`
   - **Username:** (leave empty)
   - **Password:** (leave empty)

3. **Click "Connect"**

4. **Verify:**
   - ✅ Account appears in dashboard
   - ✅ Shows "No data yet" or "DISCONNECTED" status

### Phase 3: Send Test Data

You have two options:

#### Option A: Use Test API Endpoint (Easiest)

**Step 1: Get your auth token**

Open browser console (F12) and run:
```javascript
localStorage.getItem('token')
```

Or login via API:
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your-email@example.com","password":"your-password"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

**Step 2: Send test account data**

```bash
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

1. Build add-on:
   ```bash
   cd /Users/abhinavala/payout-king/apps/ninjatrader-addon/PayoutKingAddOn
   dotnet build
   ```
2. Install in NinjaTrader
3. Configure backend URL: `http://localhost:8000`
4. Start NinjaTrader and enable add-on

### Phase 4: Verify Rule Evaluation

**After sending test data, check:**

1. **Dashboard:**
   - ✅ Account shows equity: $51,000
   - ✅ Status badge appears (likely SAFE - green)
   - ✅ Rule states are displayed

2. **Expand Account Row (if using table view):**
   - ✅ Rule breakdown panel shows
   - ✅ Trailing drawdown rule
   - ✅ Status, buffer, distance-to-violation

3. **Check Browser Console (F12):**
   - ✅ WebSocket connection messages
   - ✅ Account state update messages

### Phase 5: Test Different Scenarios

#### Test 1: Safe Status ✅

**Send data with equity > starting balance:**
```bash
curl -X POST http://localhost:8000/api/v1/test/account-data \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "TEST-001",
    "equity": 55000,
    "balance": 50000,
    "highWaterMark": 55000,
    "startingBalance": 50000,
    "openPositions": [],
    "dailyPnLHistory": {}
  }'
```

**Expected:**
- ✅ Status: SAFE (green)
- ✅ All rules show SAFE status
- ✅ Positive buffer remaining

#### Test 2: Warning Status (CAUTION) ⚠️

**Send data approaching drawdown limit:**

For Apex $50k account, max drawdown is typically $2,500 (5%).

```bash
curl -X POST http://localhost:8000/api/v1/test/account-data \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "TEST-001",
    "equity": 52500,
    "balance": 50000,
    "highWaterMark": 55000,
    "startingBalance": 50000,
    "openPositions": [],
    "dailyPnLHistory": {}
  }'
```

**Expected:**
- ✅ Status: CAUTION (yellow) or CRITICAL (red)
- ✅ Warnings appear
- ✅ Buffer percentage shown
- ✅ Alert in alert feed

#### Test 3: Violation Status ❌

**Send data that violates a rule:**

```bash
curl -X POST http://localhost:8000/api/v1/test/account-data \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "TEST-001",
    "equity": 52000,
    "balance": 50000,
    "highWaterMark": 55000,
    "startingBalance": 50000,
    "openPositions": [],
    "dailyPnLHistory": {}
  }'
```

**Expected:**
- ✅ Status: VIOLATED (red)
- ✅ Violation warnings
- ✅ Alert feed shows violation
- ✅ Audit log entry created

### Phase 6: Test Multi-Account Groups

#### Create a Group

```bash
# Create group
curl -X POST http://localhost:8000/api/v1/groups \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Group",
    "description": "Testing group functionality",
    "account_ids": ["TEST-001"]
  }'
```

**Save the group ID from response!**

#### Get Group Risk Evaluation

```bash
# Replace {group_id} with actual group ID
curl -X GET "http://localhost:8000/api/v1/groups/{group_id}/risk" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:**
- ✅ Group overall status
- ✅ Weakest account identified
- ✅ Per-rule summaries

### Phase 7: Test Audit Logging

#### Query Audit Logs

```bash
# Get all audit logs
curl -X GET "http://localhost:8000/api/v1/audit-logs?limit=20" \
  -H "Authorization: Bearer $TOKEN"

# Filter by account
curl -X GET "http://localhost:8000/api/v1/audit-logs?accountId=TEST-001&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Filter by event type
curl -X GET "http://localhost:8000/api/v1/audit-logs?eventType=violation&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:**
- ✅ Logs for warnings
- ✅ Logs for state changes
- ✅ Logs for violations
- ✅ Timestamps and details

### Phase 8: Test Real-time Updates

1. **Open browser console (F12)**
2. **Send test data multiple times with different values**
3. **Watch console for WebSocket messages:**
   - ✅ `account_state_update` messages
   - ✅ Real-time status changes
   - ✅ Alert feed updates

### Phase 9: Test Frontend Features

#### Dashboard Views

1. **Toggle between Table and Card views**
   - ✅ Table view shows all accounts
   - ✅ Card view shows account cards
   - ✅ Both update in real-time

2. **Expand Account Details**
   - ✅ Click account row to expand
   - ✅ Rule breakdown panel shows
   - ✅ Distance-to-violation metrics
   - ✅ Warnings displayed

3. **Alert Feed**
   - ✅ Alerts appear when status changes
   - ✅ Timestamps shown
   - ✅ Severity colors (info/warning/critical/violated)

4. **Disclaimers**
   - ✅ Disclaimer visible on dashboard
   - ✅ Disclaimer in rule breakdown panel

## 📊 Expected Results Summary

### After Sending Test Data:

1. ✅ **Account appears** in dashboard
2. ✅ **Equity displayed** correctly
3. ✅ **Rule states calculated** (trailing drawdown, etc.)
4. ✅ **Status badges** show correct colors
5. ✅ **WebSocket updates** in browser console
6. ✅ **Audit logs created** for all events
7. ✅ **Alerts generated** for status changes

### Rule Evaluation:

- ✅ **Trailing Drawdown** - Calculated from HWM
- ✅ **Daily Loss Limit** - For Topstep accounts
- ✅ **Consistency Rule** - Based on daily PnL history
- ✅ **Max Position Size** - Based on open positions
- ✅ **Trading Hours** - Time-based rule
- ✅ **Minimum Trading Days** - Based on trading history

## 🐛 Troubleshooting

### No data showing
- Check account ID matches
- Check backend logs for errors
- Verify test data was sent successfully

### Rules not calculating
- Check rule set version matches
- Verify firm and account type are correct
- Check backend logs for rule engine errors

### WebSocket not updating
- Check browser console for connection errors
- Verify backend is running
- Check CORS settings

### Audit logs empty
- Check database connection
- Verify audit logging is enabled
- Check backend logs for errors

## 🎯 Next Steps

1. ✅ Test with real NinjaTrader account
2. ✅ Test with multiple accounts
3. ✅ Test group functionality
4. ✅ Review audit logs
5. ✅ Test edge cases (boundary conditions)

---

**You're ready to test!** Start with Phase 2 and work through each phase.
