# Payout King

**Real-time risk, rule-compliance, and trade-guard platform for futures prop-firm traders.**

## Core Principle

> **Desktop-native integration is the primary data source.**

This is a **stateful compliance engine** that sits alongside a trader's execution platform and acts as a safety system. It prevents traders from violating prop-firm rules *before* violations occur by continuously monitoring live account state and modeling firm rules exactly.

## Architecture

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

## Repository Structure

```
/apps
  /backend        (FastAPI)
  /frontend       (React + TypeScript)
  /ninjatrader-addon
/packages
  /rules-engine
```

## Development Philosophy

- **Exact math > heuristics**
- **Real-time correctness > convenience**
- **Desktop truth > API snapshots**

## Non-Goals

- No guaranteed payouts
- No signal generation
- No broker impersonation
- No stealth rule bypassing

## Product Positioning

> "We model objective prop-firm rules in real time and warn you before a mathematical violation becomes possible."

Never promise immunity from discretionary enforcement.

## Development Status

Following the [Master Execution Plan](./docs/MASTER_PLAN.md). Currently in **PHASE 1: Rule Specification**.
