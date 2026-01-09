# 🔧 Troubleshooting Frontend Issues

## Problem: Frontend says it's running but nothing shows

### Quick Fixes

#### 1. Check Which Port It's Actually Running On

The frontend might be running on a different port than expected.

```bash
# Check what's running on common ports
lsof -ti:5173 && echo "Port 5173 is in use"
lsof -ti:3000 && echo "Port 3000 is in use"

# Or check all node processes
ps aux | grep node
```

**Try accessing:**
- http://localhost:5173
- http://localhost:3000
- http://127.0.0.1:5173

#### 2. Check Browser Console for Errors

1. Open browser DevTools (F12 or Cmd+Option+I)
2. Go to Console tab
3. Look for red error messages
4. Common issues:
   - CORS errors
   - API connection errors
   - React compilation errors

#### 3. Check Terminal Output

Look at the terminal where you ran `npm run dev`:
- Are there any **red error messages**?
- Does it say "Local: http://localhost:XXXX"?
- Does it say "ready in X ms"?

#### 4. Restart Frontend Cleanly

```bash
# Stop the current process (Ctrl+C)
# Then:

cd apps/frontend

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Start fresh
npm run dev
```

#### 5. Check if Backend is Running

The frontend needs the backend API:

```bash
# Check if backend is running
curl http://localhost:8000/health

# Should return: {"status":"healthy",...}
```

If backend isn't running:
```bash
cd apps/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Common Issues

#### Issue: Blank White Page

**Causes:**
- React app not mounting
- JavaScript errors
- Routing issues

**Fix:**
1. Check browser console (F12)
2. Check Network tab - are files loading?
3. Try accessing http://localhost:5173/login directly

#### Issue: "Cannot GET /"

**Cause:** Vite dev server not running properly

**Fix:**
```bash
cd apps/frontend
npm run dev
# Wait for "ready" message
# Note the actual port shown
```

#### Issue: CORS Errors

**Cause:** Backend CORS not configured correctly

**Fix:** Backend should allow `http://localhost:5173` (already configured)

#### Issue: Port Already in Use

**Error:** `Port 5173 is already in use`

**Fix:**
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or use a different port
# Edit vite.config.ts and change port
```

### Debug Steps

1. **Check Frontend Logs**
   ```bash
   cd apps/frontend
   npm run dev
   # Look for errors in terminal
   ```

2. **Check Browser Console**
   - Open http://localhost:5173
   - Press F12
   - Check Console tab for errors

3. **Check Network Tab**
   - Open DevTools → Network
   - Refresh page
   - Check if files are loading (200 status)

4. **Test API Connection**
   ```bash
   curl http://localhost:8000/api/v1/firms/
   ```

5. **Check Routes**
   - Try: http://localhost:5173/login
   - Try: http://localhost:5173/
   - Check if ProtectedRoute is redirecting

### Still Not Working?

1. **Check if files exist:**
   ```bash
   ls apps/frontend/src/
   ls apps/frontend/src/pages/
   ls apps/frontend/src/components/
   ```

2. **Verify dependencies:**
   ```bash
   cd apps/frontend
   cat package.json
   npm list --depth=0
   ```

3. **Try building instead of dev:**
   ```bash
   cd apps/frontend
   npm run build
   npm run preview
   ```

4. **Check React Router:**
   - Make sure `react-router-dom` is installed
   - Check if routes are correct

### Quick Test

Run this to see what's happening:

```bash
# Terminal 1 - Backend
cd apps/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend (watch for errors)
cd apps/frontend
npm run dev

# Terminal 3 - Test
curl http://localhost:8000/health
curl http://localhost:5173
```

### Expected Behavior

When frontend starts correctly, you should see:

```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

Then when you open http://localhost:5173:
- Should show login page OR redirect to login
- No blank white page
- No console errors

---

**Still stuck?** Share:
1. Terminal output from `npm run dev`
2. Browser console errors (F12)
3. What you see when accessing the URL

