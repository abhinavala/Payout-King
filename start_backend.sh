#!/bin/bash
cd "$(dirname "$0")/apps/backend"
source venv/bin/activate
echo "🚀 Starting Backend on http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
uvicorn main:app --reload --port 8000
