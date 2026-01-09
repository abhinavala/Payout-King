# Phase 0 & Phase 1 Execution Roadmap

## ✅ Phase 0: Foundation Locked (COMPLETE)

### 0.1 Rules Engine Interface Frozen ✅
- ✅ Created `AccountSnapshot` - single input object
- ✅ Created `RuleEvaluationResult` - single output object
- ✅ Updated `RuleEngine.evaluate()` as primary entry point
- ✅ All internal methods use `AccountSnapshot` instead of `AccountState`
- ✅ Interface is now stable and swappable

**Files Changed**:
- `packages/rules-engine/rules_engine/interface.py` - NEW
- `packages/rules-engine/rules_engine/engine.py` - Updated to use interface
- `packages/rules-engine/rules_engine/__init__.py` - Updated exports

### 0.2 Mock Live Mode ✅
- ✅ Created `MockSimulator` class
- ✅ Feeds fake PnL ticks every second
- ✅ Exercises trailing drawdown scenarios
- ✅ Exercises daily loss scenarios
- ✅ Test script included

**Files Created**:
- `apps/backend/app/services/mock_simulator.py`
- `apps/backend/scripts/test_mock_simulator.py`

**Usage**:
```python
from app.services.mock_simulator import MockSimulator
from rules_engine.engine import RuleEngine

simulator = MockSimulator(account_id="test-1", starting_balance=10000)
engine = RuleEngine(rules)

async for snapshot in simulator.run():
    result = engine.evaluate(snapshot)
    # Use result...
```

## 🚧 Phase 1: Tradovate Integration (IN PROGRESS)

### 1.1 Research Tradovate APIs ✅
- ✅ Created research document: `docs/TRADOVATE_API.md`
- ✅ Documented all questions to answer
- ✅ Created checklist for implementation phases
- ⚠️ **NEXT**: Actually research and fill in the document

**Action Items**:
1. Sign up for Tradovate API access (if required)
2. Test authentication endpoint with Postman/curl
3. Test each endpoint and document actual responses
4. Update `docs/TRADOVATE_API.md` with findings
5. Identify data gaps and workarounds

### 1.2 Read-Only Auth Flow ✅
- ✅ Created `TradovateAuthService`
- ✅ Implemented `verify_connection()` - fail fast check
- ✅ Implemented `connect_account()` - full flow
- ✅ Integrated into account creation endpoint
- ⚠️ **NEXT**: Test with real Tradovate API

**Files Created**:
- `apps/backend/app/services/tradovate_auth.py`
- Updated `apps/backend/app/api/v1/endpoints/accounts.py`

**What Works**:
- Verifies API credentials before saving
- Encrypts tokens before storage
- Returns clear error messages on failure

**What Needs Testing**:
- Actual Tradovate API endpoints (may differ from assumptions)
- Token refresh flow (if needed)
- Error handling for various failure modes

### 1.3 Account Polling/Streaming ⏳
- ⚠️ **NOT STARTED** - Waiting on Phase 1.1 research

**Planned Implementation**:
1. Update `TradovateClient` with actual endpoints
2. Implement polling loop (1-2 second interval)
3. Convert Tradovate responses to `AccountSnapshot`
4. Feed to rules engine
5. Store snapshots in database
6. Push updates via WebSocket

## 📋 Next Steps (Priority Order)

### Immediate (This Week)
1. **Research Tradovate API** (2-3 hours)
   - Get API access
   - Test endpoints
   - Update `docs/TRADOVATE_API.md`
   - Document actual responses

2. **Test Auth Flow** (1-2 hours)
   - Use real Tradovate credentials
   - Test `verify_connection()`
   - Fix any endpoint/auth issues
   - Verify encryption works

3. **Implement Account Polling** (4-6 hours)
   - Update `TradovateClient.get_account_state()`
   - Implement polling loop in `AccountTrackerService`
   - Test with real account
   - Verify data flows correctly

### Short Term (Next Week)
4. **Daily PnL from Fills** (Phase 2.1)
   - Implement fills endpoint
   - Calculate daily PnL correctly
   - Handle commissions
   - Test edge cases

5. **High Water Mark Persistence** (Phase 2.2)
   - Load from database
   - Update on equity increase
   - Persist to database
   - Test restart scenarios

### Medium Term (Week 3-4)
6. **Validate Against Real Apex** (Phase 2.3)
   - Run alongside real account
   - Compare calculations
   - Document divergences
   - Fix math issues

## 🎯 Success Criteria

### Phase 0 ✅
- [x] Rules engine has stable interface
- [x] Mock simulator works
- [x] Can swap between mock and real data

### Phase 1.1 (In Progress)
- [ ] `docs/TRADOVATE_API.md` fully filled out
- [ ] All endpoints documented
- [ ] Sample responses captured
- [ ] Data gaps identified

### Phase 1.2 (In Progress)
- [ ] Can verify Tradovate connection
- [ ] Credentials stored encrypted
- [ ] Error messages are clear
- [ ] Works with real API

### Phase 1.3 (Not Started)
- [ ] Can poll account data
- [ ] Data converts to `AccountSnapshot`
- [ ] Rules engine receives real data
- [ ] Dashboard shows live updates

## 🚨 Blockers

1. **Tradovate API Access**: Need to get actual API credentials
2. **API Documentation**: May need to reverse engineer if docs are poor
3. **Rate Limits**: Unknown - may need to adjust polling frequency

## 📝 Notes

- Mock simulator is ready for local dev - use it while API integration is in progress
- Interface is frozen - don't change `AccountSnapshot` or `RuleEvaluationResult` without careful consideration
- Auth flow is implemented but untested - will need real API to verify
- All code is structured to handle missing data gracefully

