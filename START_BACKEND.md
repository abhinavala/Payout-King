# Backend Not Running - Start It Now!

## Problem
The backend server is NOT running. That's why registration fails.

## Solution

**In Terminal 1, run these commands:**

```bash
cd /Users/abhinavala/payout-king/apps/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

## What You Should See

When backend starts successfully, you'll see:

```
INFO:     Will watch for changes in these directories: ['/Users/abhinavala/payout-king/apps/backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Verify It's Running

**In a NEW terminal, test:**
```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy","service":"payout-king-api","version":"0.1.0"}`

## Once Backend is Running

1. ✅ Backend terminal shows "Uvicorn running"
2. ✅ `curl http://localhost:8000/health` works
3. ✅ Frontend can now connect (no more ECONNREFUSED errors)
4. ✅ Registration will work!

## Keep Both Terminals Running

- **Terminal 1:** Backend (uvicorn command)
- **Terminal 2:** Frontend (npm run dev)

Both need to stay running for the app to work!
