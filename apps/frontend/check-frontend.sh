#!/bin/bash

echo "🔍 Checking Frontend Status..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ node_modules not found - need to run: npm install"
    exit 1
fi

# Check if src directory exists
if [ ! -d "src" ]; then
    echo "❌ src directory not found"
    exit 1
fi

# Check required files
echo "Checking required files..."
[ -f "src/main.tsx" ] && echo "✅ src/main.tsx" || echo "❌ Missing src/main.tsx"
[ -f "src/App.tsx" ] && echo "✅ src/App.tsx" || echo "❌ Missing src/App.tsx"
[ -f "index.html" ] && echo "✅ index.html" || echo "❌ Missing index.html"
[ -f "vite.config.ts" ] && echo "✅ vite.config.ts" || echo "❌ Missing vite.config.ts"

echo ""
echo "Checking ports..."
lsof -ti:5173 > /dev/null 2>&1 && echo "✅ Port 5173 is in use" || echo "⚠️  Port 5173 is free"
lsof -ti:3000 > /dev/null 2>&1 && echo "⚠️  Port 3000 is in use" || echo "✅ Port 3000 is free"

echo ""
echo "Checking backend..."
curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "✅ Backend is running" || echo "❌ Backend is NOT running"

echo ""
echo "To start frontend:"
echo "  npm run dev"
echo ""
echo "Then try accessing:"
echo "  http://localhost:5173"
echo "  http://localhost:5173/login"
