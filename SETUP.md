# Payout King - Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- npm or yarn

## Quick Start

### 1. Database Setup

```bash
# Create PostgreSQL database
createdb payoutking

# Or using psql:
psql -U postgres -c "CREATE DATABASE payoutking;"
```

### 2. Backend Setup

```bash
cd apps/backend

# Run setup script (creates venv, installs dependencies)
chmod +x setup.sh
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ../../packages/rules-engine
pip install -e .
cd ../../apps/backend

# Create .env file (see apps/backend/.env.example)
# Then run database migrations:
alembic upgrade head

# Start the server
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd apps/frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Project Structure

```
payout-king/
├── apps/
│   ├── backend/          # FastAPI backend
│   │   ├── app/
│   │   │   ├── api/      # API routes
│   │   │   ├── core/     # Config, database, security
│   │   │   ├── models/   # SQLAlchemy models
│   │   │   ├── schemas/ # Pydantic schemas
│   │   │   └── services/ # Business logic
│   │   └── main.py
│   └── frontend/         # React frontend
│       └── src/
│           ├── components/
│           ├── pages/
│           ├── services/
│           └── hooks/
├── packages/
│   ├── rules-engine/     # Core rule calculation engine
│   │   ├── rules_engine/
│   │   └── tests/
│   └── shared-types/     # Shared TypeScript types
```

## Environment Variables

### Backend (.env)

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/payoutking
ENCRYPTION_KEY=your-encryption-key-32-chars-long
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
TRADOVATE_API_URL=https://demo.tradovate.com/api/v1
TRADOVATE_WS_URL=wss://demo.tradovate.com/ws
```

## Running Tests

### Rules Engine Tests

```bash
cd packages/rules-engine
pytest
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development Workflow

1. **Backend changes**: The server auto-reloads on file changes (--reload flag)
2. **Frontend changes**: Vite HMR automatically updates the browser
3. **Database changes**: Create a new Alembic migration:
   ```bash
   alembic revision --autogenerate -m "description"
   alembic upgrade head
   ```

## Next Steps

1. Set up Tradovate API credentials
2. Connect your first account
3. Configure prop firm rules (Apex/Topstep)
4. Start tracking account states

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify database exists: `psql -l | grep payoutking`

### Import Errors
- Ensure rules-engine package is installed: `pip install -e ../../packages/rules-engine`
- Check Python path and virtual environment activation

### WebSocket Connection Issues
- Ensure backend is running on port 8000
- Check CORS settings in backend config
- Verify WebSocket URL in frontend (should be `ws://localhost:8000/api/v1/ws/{account_id}`)

