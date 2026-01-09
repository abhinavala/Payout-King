# Test Scenarios - Detailed Testing

## Scenario 1: New Account - Safe Status

**Setup:**
- Account: $50,000 starting balance
- Current equity: $51,000
- High-water mark: $51,000
- No open positions

**Expected:**
- Status: SAFE (green)
- Trailing drawdown: $0 (equity = HWM)
- All rules: SAFE
- No warnings

**Test Command:**
```bash
curl -X POST http://localhost:8000/api/v1/test/account-data \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "TEST-001",
    "equity": 51000,
    "balance": 50000,
    "highWaterMark": 51000,
    "startingBalance": 50000,
    "openPositions": [],
    "dailyPnLHistory": {}
  }'
```

## Scenario 2: Approaching Drawdown - CAUTION

**Setup:**
- Account: $50,000 starting balance
- High-water mark: $55,000 (was profitable)
- Current equity: $52,500
- Drawdown: $2,500 (4.5% of HWM)

**Expected:**
- Status: CAUTION (yellow)
- Trailing drawdown: Close to limit
- Buffer: Low
- Warnings: "Approaching drawdown limit"

**Test Command:**
```bash
curl -X POST http://localhost:8000/api/v1/test/account-data \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "TEST-001",
    "equity": 52500,
    "balance": 50000,
    "highWaterMark": 55000,
    "startingBalance": 50000,
    "openPositions": [],
    "dailyPnLHistory": {}
  }'
```

## Scenario 3: Rule Violation - VIOLATED

**Setup:**
- Account: $50,000 starting balance
- High-water mark: $55,000
- Current equity: $52,000
- Drawdown: $3,000 (5.45% of HWM) - EXCEEDS 5% limit

**Expected:**
- Status: VIOLATED (red)
- Trailing drawdown: EXCEEDED
- Buffer: Negative
- Warnings: "Trailing drawdown rule violated"
- Audit log: Violation entry created

**Test Command:**
```bash
curl -X POST http://localhost:8000/api/v1/test/account-data \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "TEST-001",
    "equity": 52000,
    "balance": 50000,
    "highWaterMark": 55000,
    "startingBalance": 50000,
    "openPositions": [],
    "dailyPnLHistory": {}
  }'
```

## Scenario 4: High-Water Mark Update

**Setup:**
- Account equity increases above current HWM
- HWM should update automatically

**Test Command:**
```bash
# First, set HWM to 51000
curl -X POST http://localhost:8000/api/v1/test/account-data \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "TEST-001",
    "equity": 51000,
    "highWaterMark": 51000,
    "startingBalance": 50000,
    "openPositions": [],
    "dailyPnLHistory": {}
  }'

# Then, send higher equity
curl -X POST http://localhost:8000/api/v1/test/account-data \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "TEST-001",
    "equity": 53000,
    "highWaterMark": 51000,  # Backend will update this
    "startingBalance": 50000,
    "openPositions": [],
    "dailyPnLHistory": {}
  }'
```

**Expected:**
- Backend updates HWM to 53000
- Audit log: "High-water mark updated"
- Status: SAFE (more buffer now)

## Scenario 5: Multiple Accounts - Group Risk

**Setup:**
- Create 2 accounts
- Add to group
- Test group risk evaluation

**Test Commands:**
```bash
# Create second account (via frontend or API)
# Then create group
curl -X POST http://localhost:8000/api/v1/groups \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Group",
    "account_ids": ["TEST-001", "TEST-002"]
  }'

# Get group risk
curl -X GET "http://localhost:8000/api/v1/groups/{group_id}/risk" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:**
- Group status = worst account status
- Weakest account identified
- Per-rule summaries

## Scenario 6: Daily PnL History - Consistency Rule

**Setup:**
- Account with trading history
- Test consistency rule calculation

**Test Command:**
```bash
curl -X POST http://localhost:8000/api/v1/test/account-data \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "TEST-001",
    "equity": 51000,
    "balance": 50000,
    "highWaterMark": 51000,
    "startingBalance": 50000,
    "realizedPnL": 1000,
    "openPositions": [],
    "dailyPnLHistory": {
      "2024-01-10": 500,
      "2024-01-11": 300,
      "2024-01-12": 200
    }
  }'
```

**Expected:**
- Consistency rule evaluated
- Status based on largest day percentage
- Warnings if > 50% threshold

## Scenario 7: Position Size Rule

**Setup:**
- Account with open positions
- Test max position size rule

**Test Command:**
```bash
curl -X POST http://localhost:8000/api/v1/test/account-data \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "accountId": "TEST-001",
    "equity": 51000,
    "balance": 50000,
    "highWaterMark": 51000,
    "startingBalance": 50000,
    "openPositions": [
      {
        "symbol": "ES",
        "quantity": 5,
        "avgPrice": 4500,
        "currentPrice": 4510,
        "unrealizedPnL": 50,
        "openedAt": "2024-01-15T09:00:00Z",
        "peakUnrealizedLoss": 0
      }
    ],
    "dailyPnLHistory": {}
  }'
```

**Expected:**
- Position size rule evaluated
- Status based on total contracts
- Warnings if approaching limit

## 🎯 Testing Checklist

- [ ] Scenario 1: Safe status
- [ ] Scenario 2: Caution status
- [ ] Scenario 3: Violation status
- [ ] Scenario 4: HWM update
- [ ] Scenario 5: Group risk
- [ ] Scenario 6: Consistency rule
- [ ] Scenario 7: Position size rule
- [ ] WebSocket real-time updates
- [ ] Audit log creation
- [ ] Frontend visualization
- [ ] Alert feed

---

**Run through these scenarios to test all functionality!**
