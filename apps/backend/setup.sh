#!/bin/bash
# Setup script for backend

echo "Setting up Payout King Backend..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install rules-engine package
cd ../../packages/rules-engine
pip install -e .
cd ../../apps/backend

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/payoutking
ENCRYPTION_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
EOF
    echo ".env file created. Please review and update as needed."
fi

echo "Backend setup complete!"
echo "To start the server, run: uvicorn main:app --reload"

