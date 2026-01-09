#!/bin/bash
# Start Payout King Services
# Run this script to start both backend and frontend

echo "🚀 Starting Payout King Services..."

# Start Backend
echo "📦 Starting Backend on http://localhost:8000..."
cd /Users/abhinavala/payout-king/apps/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait a moment
sleep 2

# Start Frontend
echo "🎨 Starting Frontend on http://localhost:5173..."
cd /Users/abhinavala/payout-king/apps/frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ Services starting..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "To stop services, run:"
echo "kill $BACKEND_PID $FRONTEND_PID"
