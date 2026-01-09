# Setup Complete - Testing Instructions

## ✅ Setup Status

The following has been completed:
- ✅ Backend virtual environment created
- ✅ Backend dependencies installed
- ✅ Rules engine installed
- ✅ Frontend dependencies installed (or ready)
- ✅ `.env` file created with default values
- ⚠️ Database migrations need to be run (see below)

## 🚀 Next Steps to Test

### Step 1: Initialize Database

The database will be created automatically on first run, but you need to run migrations for the new tables:

```bash
cd /Users/abhinavala/payout-king/apps/backend

# Activate virtual environment
source venv/bin/activate

# Initialize database tables (if not exists)
python3 -c "
from app.core.database import Base, engine
from app.models import User, ConnectedAccount, AccountStateSnapshot, RuleSet, AccountGroup, AuditLog
Base.metadata.create_all(bind=engine)
print('Database tables created!')
"

# Run migrations for new tables
sqlite3 payout_king.db < migrations/001_create_account_groups.sql
sqlite3 payout_king.db < migrations/002_create_audit_logs.sql
```

**Note:** If `sqlite3` is not available, the tables will be created automatically when you first start the backend (SQLAlchemy will create them).

### Step 2: Start Backend Server

```bash
cd /Users/abhinavala/payout-king/apps/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify it's working:**
- Open browser: http://localhost:8000/health
- Should see: `{"status":"healthy","service":"payout-king-api","version":"0.1.0"}`
- API docs: http://localhost:8000/docs

### Step 3: Start Frontend (in a new terminal)

```bash
cd /Users/abhinavala/payout-king/apps/frontend
npm run dev
```

**Expected output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Verify it's working:**
- Open browser: http://localhost:5173
- Should see the Payout King login/register page

### Step 4: Test the System

#### 4.1 Register a User

1. Open http://localhost:5173 in your browser
2. Click "Register" (or navigate to register page)
3. Enter:
   - Email: `test@example.com`
   - Password: `testpassword123`
4. Click "Register"
5. You should be redirected to the dashboard

#### 4.2 Connect a Test Account

1. On the dashboard, click "+ Connect Account"
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

#### 4.3 Send Test Data

You have two options:

**Option A: Use Test API Endpoint**

```bash
# First, get your auth token from the frontend (check browser localStorage or network tab)
# Or login via API:
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}' \
  | jq -r '.access_token')

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

**Option B: Use NinjaTrader Add-On**

1. Build the add-on:
   ```bash
   cd /Users/abhinavala/payout-king/apps/ninjatrader-addon/PayoutKingAddOn
   dotnet build
   ```
2. Install in NinjaTrader
3. Configure backend URL: `http://localhost:8000`
4. Configure API key (if required)
5. Start NinjaTrader and enable add-on
6. Data will flow automatically

#### 4.4 Verify Everything Works

**Check Dashboard:**
- ✅ Account appears in table/cards
- ✅ Equity shows correctly
- ✅ Rule states are displayed
- ✅ Status badges show correct colors
- ✅ WebSocket connection (check browser console)

**Check Rules:**
- ✅ Trailing drawdown calculated
- ✅ Status levels (SAFE/CAUTION/CRITICAL/VIOLATED)
- ✅ Buffer percentages shown
- ✅ Distance-to-violation metrics

**Check Audit Logs:**
```bash
# Query audit logs
curl -X GET "http://localhost:8000/api/v1/audit-logs?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Check WebSocket:**
- Open browser console
- Should see WebSocket connection messages
- Account state updates should appear in real-time

### Step 5: Test Different Scenarios

#### Test 1: Safe Status
- Send data with equity > HWM
- Should show SAFE status

#### Test 2: Warning Status
- Send data approaching drawdown limit
- Should show CAUTION or CRITICAL
- Should see warnings in audit logs

#### Test 3: Violation
- Send data that violates a rule
- Should show VIOLATED status
- Should see violation in audit logs

#### Test 4: Group Risk
- Create a group with multiple accounts
- Add accounts to group
- Check group risk evaluation:
  ```bash
  curl -X GET "http://localhost:8000/api/v1/groups/{group_id}/risk" \
    -H "Authorization: Bearer $TOKEN"
  ```

## 🐛 Troubleshooting

### Backend won't start
- Check virtual environment is activated: `which python` should show venv path
- Check port 8000 is not in use: `lsof -i :8000`
- Check database file exists: `ls -la payout_king.db`

### Frontend won't start
- Check Node version: `node --version` (need 16+)
- Try: `rm -rf node_modules && npm install`
- Check port 5173 is not in use

### Database errors
- Make sure migrations are run
- Check `.env` DATABASE_URL is correct
- Try deleting `payout_king.db` and restarting (will recreate)

### WebSocket not connecting
- Check backend is running
- Check CORS settings in backend `.env`
- Check browser console for errors
- Verify WebSocket URL: `ws://localhost:8000/api/v1/ws/{account_id}`

### No data showing
- Check account is connected
- Check test data was sent
- Check backend logs for errors
- Verify account ID matches

## 📊 Expected Results

After sending test data, you should see:
1. ✅ Account in dashboard with equity $51,000
2. ✅ Rule states calculated (trailing drawdown, etc.)
3. ✅ Status badges (likely SAFE if equity > starting balance)
4. ✅ Audit logs created (check `/api/v1/audit-logs`)
5. ✅ WebSocket updates in browser console

## 🎯 Next Steps After Testing

Once basic testing works:
1. Test with real NinjaTrader account
2. Test different rule scenarios
3. Test group functionality
4. Review audit logs
5. Test edge cases
6. Performance testing

---

**You're ready to test!** Follow the steps above starting with Step 1.
