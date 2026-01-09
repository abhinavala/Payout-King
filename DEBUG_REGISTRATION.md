# Debug Registration Issue

## Check These Things

### 1. Is Backend Actually Running?

**In Terminal 1 (where backend should be running), check:**
- Do you see: `INFO:     Uvicorn running on http://127.0.0.1:8000`?
- Are there any error messages?

**Test backend:**
```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy","service":"payout-king-api","version":"0.1.0"}`

### 2. Check Browser Console

**Open browser console (F12) and look for:**
- Network errors
- CORS errors
- The actual error message from the registration request

### 3. Check Backend Logs

**In Terminal 1, look for error messages when you try to register:**
- Database errors
- Validation errors
- Any traceback/stack trace

### 4. Common Issues

**Issue 1: Database Lock**
If you see "database is locked" error:
```bash
# Check if database file is locked
lsof /Users/abhinavala/payout-king/apps/backend/payout_king.db
```

**Issue 2: CORS Error**
If browser shows CORS error, check `.env` file:
```bash
cat /Users/abhinavala/payout-king/apps/backend/.env
```

CORS_ORIGINS should be: `["http://localhost:5173","http://localhost:3000"]`

**Issue 3: Email Already Exists**
If email is already registered, try a different email.

**Issue 4: Password Too Short**
Password must be at least 6 characters (frontend validates this).

### 5. Test Registration Directly

**Try registering via curl:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com","password":"test123456"}'
```

**Expected response:**
```json
{"id":"...","email":"newuser@example.com","created_at":"..."}
```

**If you get an error, share the error message!**

### 6. Check Database

**Verify users table exists:**
```bash
cd /Users/abhinavala/payout-king/apps/backend
sqlite3 payout_king.db "SELECT * FROM users LIMIT 5;"
```

## What Error Message Do You See?

Please share:
1. **Browser console error** (F12 → Console tab)
2. **Network tab error** (F12 → Network tab → Click failed request → Response)
3. **Backend terminal error** (any red error messages in Terminal 1)

This will help me diagnose the exact issue!
