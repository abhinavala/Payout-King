#!/bin/bash
cd "$(dirname "$0")"

echo "🚀 Starting Payout King Servers..."
echo ""

# Start backend
echo "📦 Starting Backend..."
cd apps/backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
echo $! > ../backend.pid
echo "✅ Backend started (PID: $(cat ../backend.pid))"
cd ../..

# Wait for backend
sleep 5

# Start frontend
echo "🎨 Starting Frontend..."
cd apps/frontend
nohup npm run dev > ../frontend.log 2>&1 &
echo $! > ../frontend.pid
echo "✅ Frontend started (PID: $(cat ../frontend.pid))"
cd ../..

echo ""
echo "✅ Both servers started!"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Check status: ./check_status.sh"
echo "View logs: tail -f apps/backend.log"
