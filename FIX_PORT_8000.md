# Fix Port 8000 Issue

## Problem
Port 8000 is still in use, preventing backend from starting.

## Solution - Run This Command

**In your Terminal 1, run this to kill the process:**

```bash
kill -9 $(lsof -ti :8000)
```

Or if that doesn't work, try:

```bash
# Find the process
lsof -i :8000

# Kill it manually (replace PID with the number you see)
kill -9 <PID>
```

## Alternative: Use Different Port

If you can't free port 8000, start backend on a different port:

```bash
cd /Users/abhinavala/payout-king/apps/backend
source venv/bin/activate
uvicorn main:app --reload --port 8001
```

Then update frontend proxy in `apps/frontend/vite.config.ts`:
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8001',  // Change 8000 to 8001
    changeOrigin: true,
  },
},
```

And restart frontend.

## After Killing Process

Once port 8000 is free, start backend:

```bash
cd /Users/abhinavala/payout-king/apps/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```
