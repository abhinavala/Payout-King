# 🚀 Run Payout King RIGHT NOW

## Fastest Way to See Everything

### Step 1: Start Backend (Terminal 1)

```bash
cd apps/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ../../packages/rules-engine && pip install -e . && cd ../../apps/backend
uvicorn main:app --reload --port 8000
```

**✅ Backend running at:** http://localhost:8000
**✅ API Docs:** http://localhost:8000/docs

### Step 2: Start Frontend (Terminal 2)

```bash
cd apps/frontend
npm install
npm run dev
```

**✅ Frontend running at:** http://localhost:5173

### Step 3: Open in Browser

1. Go to: **http://localhost:5173**
2. Register a new account
3. Click "Connect Account"
4. Select a prop firm (Apex, Topstep, etc.)
5. Select account type (eval, PA, funded)
6. See the rules preview!

## What You Can Test

### API Endpoints (in browser or curl)

- **Health Check:** http://localhost:8000/health
- **List Firms:** http://localhost:8000/api/v1/firms/
- **Apex Rules:** http://localhost:8000/api/v1/firms/apex/rules?account_type=eval
- **Topstep Rules:** http://localhost:8000/api/v1/firms/topstep/rules?account_type=eval

### Frontend Features

- ✅ Login/Register
- ✅ Dashboard
- ✅ Connect Account modal
- ✅ Firm selection dropdown
- ✅ Rules preview
- ✅ Account cards

## Troubleshooting

**Backend won't start?**
- Make sure Python 3.11+ is installed
- Activate venv: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

**Frontend won't start?**
- Make sure Node.js 18+ is installed
- Install dependencies: `npm install`
- Check if port 5173 is available

**Database errors?**
- SQLite is used by default (no setup needed)
- Database file created automatically at `apps/backend/payout_king.db`

## Quick Test Commands

```bash
# Test backend health
curl http://localhost:8000/health

# List all firms
curl http://localhost:8000/api/v1/firms/

# Get Apex rules
curl http://localhost:8000/api/v1/firms/apex/rules?account_type=eval
```

---

**That's it!** You should now see the full Payout King platform running! 🎉
