# Payout King Architecture

## Core Principle

> **Desktop-native integration is the primary data source.**

Broker APIs (OAuth) are optional and secondary, used only for analytics or account verification — not enforcement.

## Primary Data Path (Mandatory)

```
[Trading Platform Desktop App]
        ↓
[Local Add-On / Plugin]
        ↓  (WebSocket / HTTPS)
[Payout King Backend]
        ↓
[Rule Engine + State Tracker]
        ↓
[Web Dashboard + Alerts]
```

This is the **only architecture** capable of:
- Tick-level monitoring
- Intratrade drawdown detection
- MAE/MFE calculations
- Trailing high-water mark tracking
- Pre-trade warnings

## Secondary Data Path (Optional)

```
[Broker API / OAuth]
        ↓
[Backend Analytics Layer]
```

Used for:
- Historical analysis
- Read-only dashboards
- Mobile views

Never relied upon for enforcement.

## Component Responsibilities

### Desktop Add-On
- Subscribe to account events
- Capture order submissions, fills, position changes
- Track per-tick state
- Send state updates to backend every 100–500ms
- **Must not place trades by default**

### Backend (FastAPI)
- User authentication (JWT)
- Device / add-on authentication
- Account state persistence
- Rule evaluation
- High-water mark storage
- Daily reset logic
- WebSocket broadcasting

### Rule Engine
- Deterministic and versioned
- Each account assigned: Firm, Account type, Account size, Rule version
- Computes distance-to-violation for every rule
- Assigns status: SAFE, CAUTION, CRITICAL, VIOLATED

### Frontend (React)
- Informational only
- Reflects backend truth
- Never computes rules
- Never infers state

## Data Contract

### AccountUpdate Message Schema

```typescript
interface AccountUpdate {
  accountId: string;
  timestamp: number; // Unix timestamp in milliseconds
  realizedPnl: number;
  unrealizedPnl: number;
  equity: number;
  positions: Position[];
  openOrders: Order[];
}

interface Position {
  instrument: string;
  quantity: number;
  avgPrice: number;
  unrealizedPnl: number;
}

interface Order {
  orderId: string;
  instrument: string;
  quantity: number;
  orderType: string;
  status: string;
}
```

**This schema is sacred.** Changes require spec updates.

## Security Model

- Desktop add-on authenticates via device token
- Backend issues scoped JWTs
- No broker credentials stored
- No trade placement permissions by default

## Multi-Account Support

- Users may connect many accounts
- Unified dashboard
- Per-account rule state
- Grouping (copy-traded sets)
- Weakest-account detection
