#!/bin/bash
# Test registration endpoint

echo "Testing registration endpoint..."
echo ""

# Test 1: Health check
echo "1. Testing backend health..."
curl -s http://localhost:8000/health
echo ""
echo ""

# Test 2: Registration
echo "2. Testing registration..."
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser'$(date +%s)'@example.com","password":"test123456"}' \
  -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "Done!"
