#!/bin/bash

# Test script to verify NinjaTrader connection

echo "═══════════════════════════════════════════════════════════════"
echo "  🧪 Testing NinjaTrader Connection"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check backend is running
echo "1. Checking backend health..."
BACKEND_HEALTH=$(curl -s http://localhost:8000/health 2>&1)
if [[ $? -eq 0 ]]; then
    echo "   ✅ Backend is running"
    echo "   Response: $BACKEND_HEALTH"
else
    echo "   ❌ Backend is not running!"
    echo "   Start it with: cd apps/backend && source venv/bin/activate && uvicorn main:app --reload"
    exit 1
fi

echo ""

# Check NinjaTrader endpoint
echo "2. Checking NinjaTrader endpoint..."
NINJA_HEALTH=$(curl -s http://localhost:8000/api/v1/ninjatrader/health 2>&1)
if [[ $? -eq 0 ]]; then
    echo "   ✅ NinjaTrader endpoint is accessible"
    echo "   Response: $NINJA_HEALTH"
else
    echo "   ❌ NinjaTrader endpoint not accessible!"
    exit 1
fi

echo ""

# Check if any accounts are connected
echo "3. Checking connected accounts..."
echo "   (You need to be logged in to check this)"
echo "   Go to: http://localhost:5173"
echo "   Login and check your dashboard for connected accounts"

echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ Connection Test Complete"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Make sure NinjaTrader is running with the Add-On enabled"
echo "2. Check NinjaTrader log (Tools → Log) for:"
echo "   ✅ 'Connected to account: [YourAccount]'"
echo "   ✅ 'Data sent successfully'"
echo "3. Check backend logs: tail -f apps/backend.log"
echo "4. Check dashboard: http://localhost:5173"
echo ""

