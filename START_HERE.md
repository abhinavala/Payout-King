# 🚀 START HERE - Run Payout King

## ✅ Everything is Ready!

All dependencies are installed and configured. Just start the servers!

## Quick Start (2 Terminals)

### Terminal 1 - Backend
```bash
cd /Users/abhinavala/payout-king
./start_backend.sh
```

**OR manually:**
```bash
cd apps/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Terminal 2 - Frontend
```bash
cd /Users/abhinavala/payout-king
./start_frontend.sh
```

**OR manually:**
```bash
cd apps/frontend
npm run dev
```

**You should see:**
```
  VITE v5.x.x  ready in XXX ms
  ➜  Local:   http://localhost:5173/
```

## Open in Browser

1. Go to: **http://localhost:5173**
2. You should see the **Login page**
3. Click **"Register"** to create an account
4. After registering, you'll be logged in
5. Click **"Connect Account"** to add a prop firm account

## Verify Everything Works

### Test Backend API
```bash
# Health check
curl http://localhost:8000/health

# List firms
curl http://localhost:8000/api/v1/firms/

# Get Apex rules
curl http://localhost:8000/api/v1/firms/apex/rules?account_type=eval
```

### Test Frontend
- Open http://localhost:5173
- Should see login page (not blank)
- Try registering/logging in
- Dashboard should load after login

## Troubleshooting

### Backend won't start?
- Make sure port 8000 is free: `lsof -ti:8000`
- Check Python version: `python3 --version` (need 3.11+)
- Activate venv: `source venv/bin/activate`

### Frontend won't start?
- Make sure port 5173 is free: `lsof -ti:5173`
- Check Node version: `node --version` (need 18+)
- Reinstall: `npm install`

### Blank page?
- Check browser console (F12)
- Make sure backend is running
- Try http://localhost:5173/login directly

## What You Can Do

✅ **Register/Login** - Create account
✅ **Connect Account** - Add prop firm account
✅ **View Rules** - See firm-specific rules
✅ **Dashboard** - See account cards
✅ **API Docs** - http://localhost:8000/docs

---

**Ready to go!** Start both servers and open http://localhost:5173 🎉
