#!/bin/bash

# Payout King Quick Start Script
# Starts both backend and frontend

set -e

echo "🚀 Starting Payout King..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "apps/backend" ] || [ ! -d "apps/frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "${YELLOW}⚠️  Port $1 is already in use${NC}"
        return 1
    fi
    return 0
}

# Check ports
echo "Checking ports..."
check_port 8000 || echo "  Backend port 8000 is in use - will try anyway"
check_port 5173 || echo "  Frontend port 5173 is in use - will try anyway"
echo ""

# Start backend
echo "${BLUE}📦 Starting Backend...${NC}"
cd apps/backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies if needed
if [ ! -f ".deps_installed" ]; then
    echo "${YELLOW}Installing backend dependencies...${NC}"
    pip install -r requirements.txt
    
    # Install rules engine
    cd ../../packages/rules-engine
    pip install -e .
    cd ../../apps/backend
    
    touch .deps_installed
fi

# Start backend in background
echo "${GREEN}✅ Starting backend server on http://localhost:8000${NC}"
echo "   API docs: http://localhost:8000/docs"
uvicorn main:app --reload --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
echo ""
echo "${BLUE}🎨 Starting Frontend...${NC}"
cd ../frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "${YELLOW}Installing frontend dependencies (this may take a minute)...${NC}"
    npm install
fi

# Start frontend
echo "${GREEN}✅ Starting frontend server on http://localhost:5173${NC}"
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo ""
echo "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo "${GREEN}  ✅ Payout King is running!${NC}"
echo "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "📍 Backend:  http://localhost:8000"
echo "📍 Frontend: http://localhost:5173"
echo "📍 API Docs:  http://localhost:8000/docs"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f apps/backend.log"
echo "   Frontend: tail -f apps/frontend.log"
echo ""
echo "🛑 To stop:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop both servers..."

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait

