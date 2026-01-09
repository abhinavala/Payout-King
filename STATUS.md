# 🚀 Setup Status & Testing Instructions

## ✅ Completed Steps

1. ✅ **Database Initialized** - All tables created successfully
2. ✅ **Backend Dependencies** - Already installed in venv
3. ✅ **Environment Config** - `.env` file created and fixed
4. ⚠️ **Rules Engine** - Installation had SSL issues (may work anyway if already installed)
5. ⚠️ **Frontend Dependencies** - npm install had permission issues

## 🎯 Current Status

**Database:** ✅ Ready (tables created)
**Backend:** ⚠️ Needs to be started manually
**Frontend:** ⚠️ Needs dependencies installed and started manually

## 🚀 Quick Start Commands

### Option 1: Start Services Manually

**Terminal 1 - Backend:**
```bash
cd /Users/abhinavala/payout-king/apps/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
# First, fix npm permissions (if needed):
sudo chown -R $(whoami) ~/.npm

# Then install dependencies:
cd /Users/abhinavala/payout-king/apps/frontend
npm install

# Start frontend:
npm run dev
```

### Option 2: Use Start Script

```bash
chmod +x /Users/abhinavala/payout-king/START_SERVICES.sh
/Users/abhinavala/payout-king/START_SERVICES.sh
```

## 🧪 Testing Steps (Once Services Are Running)

### 1. Verify Services

**Backend Health Check:**
```bash
curl http://localhost:8000/health
```
Should return: `{"status":"healthy","service":"payout-king-api","version":"0.1.0"}`

**Frontend:**
Open browser: http://localhost:5173

### 2. Register User

1. Open http://localhost:5173
2. Click "Register"
3. Enter:
   - Email: `test@example.com`
   - Password: `testpassword123`
4. Click "Register"

### 3. Connect Test Account

1. Click "+ Connect Account"
2. Fill in:
   - Platform: `ninjatrader`
   - Account ID: `TEST-001`
   - Account Name: `Test Account`
   - Firm: `apex`
   - Account Type: `eval`
   - Account Size: `50000`
   - Rule Set Version: `v1`
3. Click "Connect"

### 4. Send Test Data

**Get Auth Token:**
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

**Send Test Data:**
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
    "openPositions": [],
    "dailyPnLHistory": {},
    "orders": []
  }'
```

### 5. Verify Results

- ✅ Account appears in dashboard
- ✅ Equity shows $51,000
- ✅ Rule states calculated
- ✅ Status badges displayed
- ✅ WebSocket updates (check browser console)

## 🐛 Troubleshooting

### Backend won't start
- Check virtual environment: `source venv/bin/activate`
- Check port 8000: `lsof -i :8000`
- Check `.env` file format (CORS_ORIGINS should be JSON array)

### Frontend won't start
- Fix npm permissions: `sudo chown -R $(whoami) ~/.npm`
- Install dependencies: `npm install`
- Check port 5173: `lsof -i :5173`

### Rules engine not found
- Try: `cd packages/rules-engine && source ../../apps/backend/venv/bin/activate && pip install -e .`
- Or add to Python path manually

## 📋 Files Created

- ✅ `apps/backend/.env` - Backend configuration
- ✅ `apps/backend/payout_king.db` - Database file
- ✅ `START_SERVICES.sh` - Service startup script
- ✅ `TESTING_NOW.md` - Detailed testing guide
- ✅ `STATUS.md` - This file

## 🎯 Next Steps

1. **Start Backend** (Terminal 1)
2. **Start Frontend** (Terminal 2) 
3. **Open Browser** to http://localhost:5173
4. **Follow Testing Steps** above

---

**You're almost ready!** Just start the services and begin testing.
