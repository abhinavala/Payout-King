#!/bin/bash
echo "🔍 Checking Server Status..."
echo ""
echo "Backend (port 8000):"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✅ Running - http://localhost:8000"
    echo "  📚 API Docs: http://localhost:8000/docs"
else
    echo "  ❌ Not running"
fi
echo ""
echo "Frontend (port 5173):"
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "  ✅ Running - http://localhost:5173"
else
    echo "  ❌ Not running"
fi
echo ""
echo "Processes:"
ps aux | grep -E "(uvicorn|vite)" | grep -v grep | awk '{print "  PID:", $2, "|", $11, $12, $13}'
