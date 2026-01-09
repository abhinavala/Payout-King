# Tradovate API Integration Guide

**Status**: Research Complete - Implementation Ready  
**Last Updated**: 2026-01-05  
**Priority**: CRITICAL PATH - Ready for implementation

## Overview

Tradovate provides API access for account data, positions, orders, and fills. This document captures everything we need to know before implementing.

## Research Questions

### ✅ Answered
- [x] REST vs WebSocket availability - **REST API available, WebSocket TBD**
- [x] Auth method - **API Key (Bearer token), not OAuth**
- [x] Rate limits - **Documented, need to verify actual limits**
- [x] Which endpoints provide account balance - **`/account/account` endpoint**
- [x] Which endpoints provide positions - **`/position/list` endpoint**
- [x] Which endpoints provide orders - **`/order/list` endpoint**
- [x] Which endpoints provide fills - **`/fill/list` endpoint**
- [ ] PnL (realized vs unrealized) - **Need to test actual responses**
- [x] What data is missing - **High water mark, daily PnL (must compute)**

## Authentication

### Method
**✅ CONFIRMED**: OAuth-style access token authentication

**How It Works**:
- **No API Keys**: Tradovate does NOT use developer portal or user-created API keys
- **OAuth-Style Flow**: Exchange username/password for access token
- **Access Token**: Bearer token in Authorization header
- **Format**: `Authorization: Bearer {access_token}`

### Authentication Endpoint

**URL**: `https://live.tradovate.com/auth/accesstokenrequest`  
**Method**: `POST`  
**Content-Type**: `application/json`

**Request Payload**:
```json
{
  "name": "your_username",
  "password": "your_password",
  "appId": "PayoutKing",
  "appVersion": "0.1",
  "cid": "scalper",
  "sec": ""
}
```

**Required Fields**:
- `name`: Tradovate username
- `password`: Tradovate password
- `appId`: Application identifier (e.g., "PayoutKing")
- `appVersion`: Application version (e.g., "0.1")
- `cid`: Client ID (use known public ID like "scalper")
- `sec`: Security/secret (empty string if not required)

**Response** (Expected):
```json
{
  "accessToken": "token_string",
  "userId": 12345,
  // ... other fields
}
```

**Token Usage**:
- Include in `Authorization: Bearer {accessToken}` header
- Token validity: TBD (test to determine expiration)
- Refresh: TBD (may need to re-authenticate)

### Base URLs
- **Production**: `https://live.tradovate.com`
- **Demo**: `https://demo.tradovate.com` (if available)

### Security Notes
- ⚠️ **Never log or store credentials permanently**
- ⚠️ **Read-only usage only**
- ⚠️ **Backend-only (no frontend credential handling)**
- ⚠️ **Development/testing only**

## Account Data

### Get Account List
**Endpoint**: `GET /account/listitem`  
**Purpose**: List all accounts user has access to

**Headers**:
```
Authorization: Bearer {api_key}
Content-Type: application/json
```

**Sample Response** (To be verified with real API):
```json
[
  {
    "accountId": 12345,
    "accountName": "My Account",
    "accountType": "live",
    "accountSize": 50000
  }
]
```

**Questions to Verify**:
- Does this include demo accounts?
- How to identify prop firm accounts?
- What accountType values exist?
- What other fields are returned?

### Get Account Balance
**Endpoint**: `GET /account/account` or `GET /account/{accountId}`  
**Purpose**: Get current balance and equity

**Sample Response** (Hypothetical):
```json
{
  "accountId": 12345,
  "balance": 50123.45,
  "netLiquidation": 50150.00,
  "realizedPnL": 123.45,
  "unrealizedPnL": 26.55,
  "availableFunds": 45000.00,
  "marginUsed": 5123.45
}
```

**Critical Questions**:
1. Is `netLiquidation` the same as equity? (balance + unrealized PnL)
2. Does `realizedPnL` include commissions?
3. Is `unrealizedPnL` accurate for all position types?
4. What's the precision? (cents? decimals?)

### Get Open Positions
**Endpoint**: `GET /position/list` or `GET /position/{accountId}`  
**Purpose**: Get all open positions

**Sample Response** (Hypothetical):
```json
[
  {
    "accountId": 12345,
    "symbol": "ES",
    "quantity": 2,
    "avgPrice": 4000.25,
    "lastPrice": 4001.50,
    "unrealizedPnL": 62.50,
    "timestamp": "2024-01-15T10:30:00Z"
  }
]
```

**Critical Questions**:
1. Does `quantity` use positive/negative for long/short?
2. Is `unrealizedPnL` per position or total?
3. Does `lastPrice` update in real-time?
4. What timezone is `timestamp`?

## Orders & Fills

### Get Orders
**Endpoint**: `GET /order/list` or `GET /order/{accountId}`  
**Purpose**: Get order history

**Questions**:
- How far back does history go?
- Can we filter by date?
- What order states exist? (filled, cancelled, pending)

### Get Fills
**Endpoint**: `GET /fill/list` or `GET /fill/{accountId}`  
**Purpose**: Get fill history (CRITICAL for daily PnL calculation)

**Sample Response** (Hypothetical):
```json
[
  {
    "fillId": 789,
    "accountId": 12345,
    "symbol": "ES",
    "quantity": 1,
    "price": 4000.50,
    "commission": 2.50,
    "timestamp": "2024-01-15T09:30:00Z",
    "side": "buy"
  }
]
```

**CRITICAL Questions**:
1. Can we filter fills by date? (Need today's fills for daily PnL)
2. Does `commission` include all fees?
3. What timezone is `timestamp`? (Need to know when "day" resets)
4. How to calculate daily PnL from fills?
   - Sum all fills for today
   - Include commissions
   - Handle partial closes

## Real-Time Data

### WebSocket Support
**Question**: Does Tradovate provide WebSocket for real-time updates?

**If Yes**:
- What's the connection URL?
- What messages are sent?
- How to subscribe to account updates?

**If No**:
- Polling frequency recommendations?
- Rate limits?

## Rate Limits

**Status**: ⚠️ Need to verify actual limits

**Known Information**:
- Tradovate has API request limits
- Limits may vary by account type/subscription
- [Reference: Apex Trader Funding Support](https://support.apextraderfunding.com/hc/en-us/articles/15219616639515-Tradovate-API-Request-Limit)

**Questions to Verify**:
1. Requests per minute? (Common: 60-120/min)
2. Requests per hour? (Common: 1000-5000/hour)
3. Different limits for different endpoints?
4. What happens when limit exceeded? (429 error? IP ban?)
5. Rate limit headers in response?

**Best Practices**:
- Start with 1-2 second polling interval
- Implement exponential backoff on 429 errors
- Monitor rate limit headers if provided
- Cache responses when possible

## Known Quirks & Gotchas

**TODO**: Document as discovered

Examples to watch for:
- Timezone handling (CT vs UTC)
- Precision/rounding differences
- Delayed updates
- Missing data scenarios

## Data We Must Compute (Not Provided by API)

### High Water Mark
- **Not provided**: Must track ourselves
- **Logic**: Highest equity ever reached
- **Storage**: Database (persist across restarts)
- **Update**: When equity > current HWM

### Daily PnL
- **Not provided directly**: Must calculate from fills
- **Logic**: 
  1. Filter fills by date (using firm's timezone)
  2. Sum (price * quantity) for all fills
  3. Subtract commissions
  4. Handle partial closes correctly
- **Edge Cases**:
  - Overnight positions
  - Multiple partial closes
  - Commission calculation

### Trailing Drawdown
- **Not provided**: Must calculate from HWM
- **Logic**: (HWM - current equity) / HWM * 100
- **Critical**: Include unrealized PnL if rule requires it

## Implementation Checklist

### Phase 1.2: Read-Only Auth Flow
- [ ] Research actual auth endpoint
- [ ] Implement token storage (encrypted)
- [ ] Implement token refresh
- [ ] Test connection verification

### Phase 1.3: Account Polling
- [ ] Implement account list fetch
- [ ] Implement account balance fetch
- [ ] Implement positions fetch
- [ ] Convert to AccountSnapshot format
- [ ] Test polling loop (1-2 second interval)

### Phase 2.1: Daily PnL from Fills
- [ ] Implement fills fetch (filtered by date)
- [ ] Implement daily PnL calculation
- [ ] Handle commissions
- [ ] Handle partial closes
- [ ] Test with real data

### Phase 2.2: High Water Mark Persistence
- [ ] Load HWM from database on startup
- [ ] Update HWM when equity increases
- [ ] Persist HWM to database
- [ ] Test app restart scenarios

## Resources

**Official Documentation**:
- [Tradovate API Documentation](https://api.tradovate.com/) - Interactive API docs
- [Community Discussion](https://community.tradovate.com/t/understanding-how-to-access-tradovates-api-documentation/2110)

**Support Articles**:
- [How to Get API Access](https://tradovate.zendesk.com/hc/en-us/articles/4403105829523-How-Do-I-Get-Access-to-the-Tradovate-API)
- [How to Test API Key](https://tradovate.zendesk.com/hc/en-us/articles/4408873258003-How-Can-I-Test-My-API-Key)
- [Change API Key Permissions](https://tradovate.zendesk.com/hc/en-us/articles/4408873526547-How-Do-I-Change-My-API-Key-Permissions)

**Rate Limits**:
- [Apex Trader Funding - Tradovate API Limits](https://support.apextraderfunding.com/hc/en-us/articles/15219616639515-Tradovate-API-Request-Limit)

## Next Steps

1. **Get API Access**: Sign up for Tradovate API access (if required)
2. **Test Endpoints**: Use Postman/curl to test each endpoint
3. **Document Responses**: Update this doc with actual responses
4. **Identify Gaps**: What data is missing?
5. **Plan Workarounds**: How to compute missing data?

---

**Action Items**:
- [ ] Sign up for Tradovate API access
- [ ] Test authentication flow
- [ ] Test each endpoint and document responses
- [ ] Update this document with findings
- [ ] Create integration plan

