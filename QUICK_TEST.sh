#!/bin/bash
# Quick test script for Payout King

echo "🧪 Payout King Quick Test"
echo ""

# Get token (you'll need to replace with your actual email/password)
read -p "Enter your email: " EMAIL
read -sp "Enter your password: " PASSWORD
echo ""

echo "1. Logging in..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ] || [ "$TOKEN" == "None" ]; then
  echo "❌ Login failed! Check your credentials."
  exit 1
fi

echo "✅ Login successful!"
echo ""

echo "2. Testing backend health..."
HEALTH=$(curl -s http://localhost:8000/health)
echo "$HEALTH"
echo ""

echo "3. Sending test account data..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/test/account-data \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "TEST-001",
    "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
    "equity": 51000,
    "balance": 50000,
    "realizedPnL": 0,
    "unrealizedPnL": 1000,
    "highWaterMark": 51000,
    "dailyPnL": 0,
    "startingBalance": 50000,
    "openPositions": [],
    "dailyPnLHistory": {},
    "orders": []
  }')

if echo "$RESPONSE" | grep -q "error\|Error\|failed"; then
  echo "❌ Failed to send test data"
  echo "$RESPONSE"
else
  echo "✅ Test data sent successfully!"
fi
echo ""

echo "4. Checking audit logs..."
LOGS=$(curl -s -X GET "http://localhost:8000/api/v1/audit-logs?limit=5" \
  -H "Authorization: Bearer $TOKEN")
echo "$LOGS" | python3 -m json.tool 2>/dev/null || echo "$LOGS"
echo ""

echo "✅ Test complete!"
echo ""
echo "Now check your frontend at http://localhost:5173"
echo "You should see the account with updated data!"
