# Quick Fix for Registration Issue

## Most Common Issues & Fixes

### Issue 1: Backend Not Actually Running

**Check:** In Terminal 1, do you see `INFO:     Uvicorn running on http://127.0.0.1:8000`?

**If not, restart backend:**
```bash
cd /Users/abhinavala/payout-king/apps/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Issue 2: Database Error

**If you see "database is locked" or SQL errors:**

The database might be locked. Try:
```bash
# Stop backend (Ctrl+C in Terminal 1)
# Then restart it
cd /Users/abhinavala/payout-king/apps/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Issue 3: Email Already Exists

**If email is already registered:**
- Try a different email address
- Or check existing users:
```bash
cd /Users/abhinavala/payout-king/apps/backend
sqlite3 payout_king.db "SELECT email FROM users;"
```

### Issue 4: Check Browser Console

**Open browser console (F12) and look for:**
- The exact error message
- Network tab → Click the failed `/api/v1/auth/register` request
- Check the "Response" tab for the error message

### Issue 5: Test Directly

**Run this test script:**
```bash
cd /Users/abhinavala/payout-king
./TEST_REGISTRATION.sh
```

This will test the registration endpoint directly and show you the exact error.

## What to Share

Please share:
1. **The exact error message** from browser console (F12)
2. **Any error messages** from Terminal 1 (backend terminal)
3. **The output** of `./TEST_REGISTRATION.sh`

This will help me fix it quickly!

## Quick Test

**Test if backend is responding:**
```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy","service":"payout-king-api","version":"0.1.0"}`

**If this fails, backend isn't running properly!**
