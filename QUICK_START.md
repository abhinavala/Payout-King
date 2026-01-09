# Quick Start Guide - Payout King

## 🚀 Ready to Test!

The system is **functionally complete** and ready for testing. Follow these steps to get started.

## Prerequisites

- Python 3.8+ (for backend)
- Node.js 16+ (for frontend)
- SQLite (default) or PostgreSQL (for production)
- NinjaTrader (for desktop add-on testing)

## Step 1: Backend Setup

```bash
# Navigate to backend
cd apps/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install rules-engine package
cd ../../packages/rules-engine
pip install -e .
cd ../../apps/backend

# Create .env file
cat > .env << EOF
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///./payout_king.db
ENCRYPTION_KEY=your-32-character-key-here!!
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
EOF

# Initialize database (if needed)
# SQLite will be created automatically on first run
# For PostgreSQL, create database first

# Start backend
uvicorn main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`

## Step 2: Frontend Setup

```bash
# Navigate to frontend
cd apps/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend will be available at: `http://localhost:5173` (or port shown in terminal)

## Step 3: Database Migrations

**Important:** Run these migrations before first use:

```bash
# For SQLite
cd apps/backend
sqlite3 payout_king.db < migrations/001_create_account_groups.sql
sqlite3 payout_king.db < migrations/002_create_audit_logs.sql

# For PostgreSQL
psql -d payout_king -f migrations/001_create_account_groups.sql
psql -d payout_king -f migrations/002_create_audit_logs.sql
```

**Note:** Base tables (users, connected_accounts, etc.) should be created automatically by SQLAlchemy on first run. If not, you may need to run:

```python
from app.core.database import Base, engine
Base.metadata.create_all(bind=engine)
```

## Step 4: Test the System

### 4.1 Register a User

1. Open frontend: `http://localhost:5173`
2. Click "Register"
3. Create an account

### 4.2 Connect a Test Account

1. Login to frontend
2. Click "Connect Account"
3. Fill in account details:
   - Platform: `ninjatrader`
   - Account ID: `TEST-001`
   - Account Name: `Test Account`
   - Firm: `apex` or `topstep`
   - Account Type: `eval`, `pa`, or `funded`
   - Account Size: `50000` (for $50k account)
   - Rule Set Version: `v1`

### 4.3 Test with NinjaTrader Add-On

1. Build the add-on:
   ```bash
   cd apps/ninjatrader-addon/PayoutKingAddOn
   dotnet build
   ```

2. Install in NinjaTrader
3. Configure backend URL in add-on config
4. Start NinjaTrader and enable add-on
5. Data should flow to backend automatically

### 4.4 Test with API (Alternative)

If you don't have NinjaTrader, you can test using the test endpoint:

```bash
# Get auth token first (from login)
TOKEN="your-jwt-token"

# Send test account data
curl -X POST http://localhost:8000/api/v1/test/account-data \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "TEST-001",
    "equity": 50000,
    "balance": 50000,
    "realizedPnL": 0,
    "unrealizedPnL": 0,
    "highWaterMark": 50000,
    "dailyPnL": 0,
    "openPositions": [],
    "dailyPnLHistory": {}
  }'
```

## Step 5: Verify Everything Works

### Check Backend Health
```bash
curl http://localhost:8000/health
```

### Check API Docs
Open: `http://localhost:8000/docs`

### Check Frontend
- Dashboard loads
- Accounts appear
- WebSocket connects (check browser console)
- Rules are evaluated
- Audit logs are created

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.8+)
- Check dependencies: `pip list`
- Check database connection in `.env`

### Frontend won't start
- Check Node version: `node --version` (need 16+)
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

### Database errors
- Make sure migrations are run
- Check database file exists (SQLite) or connection (PostgreSQL)
- Check `.env` DATABASE_URL

### WebSocket not connecting
- Check backend is running
- Check CORS settings in backend
- Check browser console for errors

## Next Steps

1. ✅ System is ready for testing
2. Test with real NinjaTrader account
3. Verify rule calculations
4. Check audit logs
5. Test group functionality
6. Review disclaimers

## Production Deployment

Before production:
- [ ] Change all default secrets in `.env`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up HTTPS
- [ ] Configure proper CORS origins
- [ ] Set up monitoring
- [ ] Set up backups
- [ ] Run security audit

---

**Status: ✅ READY FOR TESTING**

All 7 phases complete. Follow steps above to start testing!
