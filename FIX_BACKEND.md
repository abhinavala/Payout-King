# Fix Backend Connection Issue

## Problem
- ✅ Frontend is running on http://localhost:5173
- ❌ Backend can't start: "Address already in use" on port 8000
- ❌ Frontend can't connect to backend (ECONNREFUSED errors)

## Solution

I've killed the process on port 8000. Now you need to restart the backend:

### In Terminal 1 (Backend):

```bash
cd /Users/abhinavala/payout-king/apps/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**You should now see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

### Verify It's Working:

**Test Backend:**
```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy","service":"payout-king-api","version":"0.1.0"}`

**Test Frontend Connection:**
Once backend is running, try logging in again at http://localhost:5173

The frontend proxy errors should stop once the backend is running!

## What Happened

Port 8000 was already in use (probably from my earlier attempt to start it). I've cleared it, so now you can start the backend properly.
