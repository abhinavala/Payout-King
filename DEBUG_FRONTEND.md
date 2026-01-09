# 🐛 Debug Frontend - Step by Step

## The frontend IS running on port 5173 ✅

But you're seeing a blank page. Let's debug:

## Step 1: Check Browser Console

1. Open http://localhost:5173 in your browser
2. Press **F12** (or Cmd+Option+I on Mac)
3. Go to **Console** tab
4. Look for **red error messages**

**What to look for:**
- `Failed to fetch` → Backend not running
- `Cannot read property` → JavaScript error
- `404` errors → Missing files
- CORS errors → Backend CORS config

## Step 2: Check Network Tab

1. In DevTools, go to **Network** tab
2. Refresh the page (F5)
3. Check which files load/fail

**Should see:**
- `index.html` → 200 ✅
- `main.tsx` → 200 ✅
- `App.tsx` → 200 ✅
- API calls to `/api/v1/...` → Check status

## Step 3: Check Backend

The frontend needs the backend API:

```bash
# Test if backend is running
curl http://localhost:8000/health

# Should return: {"status":"healthy",...}
```

**If backend isn't running:**
```bash
cd apps/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

## Step 4: Try Direct Routes

Try these URLs directly:

1. **Login page:** http://localhost:5173/login
   - Should show login form
   - If blank, check console errors

2. **Root:** http://localhost:5173/
   - Might redirect to /login if not authenticated
   - Should show "Loading..." then redirect

## Step 5: Common Issues & Fixes

### Issue: Blank White Page

**Possible causes:**
- React app not mounting
- JavaScript error preventing render
- Backend API call failing

**Fix:**
1. Check browser console (F12)
2. Look for React errors
3. Check if backend is running

### Issue: "Loading..." Forever

**Cause:** Backend API call hanging

**Fix:**
```bash
# Make sure backend is running
curl http://localhost:8000/health

# If not running, start it:
cd apps/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Issue: CORS Errors

**Error:** `Access to fetch at 'http://localhost:8000/...' from origin 'http://localhost:5173' has been blocked by CORS policy`

**Fix:** Backend CORS is already configured, but verify:
- Backend is running
- CORS allows `http://localhost:5173`

### Issue: 404 Errors

**Error:** `Failed to load resource: the server responded with a status of 404`

**Fix:**
- Check if files exist in `apps/frontend/src/`
- Check Vite is serving files correctly
- Restart frontend: `npm run dev`

## Step 6: Quick Test

Run this to test everything:

```bash
# Terminal 1 - Backend
cd apps/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend  
cd apps/frontend
npm run dev

# Terminal 3 - Test
# Wait for both to start, then:
curl http://localhost:8000/health
curl http://localhost:5173
```

## Step 7: What Should You See?

### When Everything Works:

1. **Open http://localhost:5173**
   - Should redirect to `/login` (if not authenticated)
   - OR show dashboard (if authenticated)

2. **Login page should show:**
   - "Payout King" heading
   - Email input field
   - Password input field
   - "Login" button
   - "Register" link

3. **After login:**
   - Redirects to dashboard
   - Shows account cards (if accounts connected)
   - Shows "Connect Account" button

## Still Not Working?

**Share these details:**

1. **Browser console errors** (F12 → Console)
2. **Network tab** - which requests fail?
3. **Terminal output** from `npm run dev`
4. **What you see** - blank page? error message? something else?

**Quick diagnostic:**

```bash
# Check if frontend is actually running
curl http://localhost:5173

# Should return HTML (index.html)
# If empty or error, frontend isn't serving properly
```

---

**Most likely issue:** Backend not running, causing API calls to fail and blank page.

**Quick fix:** Start backend in separate terminal, then refresh browser.

