# PHASE 6 Progress - Multi-Account & Copy-Trade Logic

## Status: 🚧 IN PROGRESS

**Current Phase**: PHASE 6 - Multi-Account & Copy-Trade Logic

## Master Plan Compliance

### ✅ 6.1 Account Grouping
- ✅ Group ID (UUID)
- ✅ Member accounts (many-to-many relationship)
- ✅ Weakest account logic (implemented in risk evaluation)

### ✅ 6.2 Group Risk Evaluation
- ✅ Lowest buffer dominates
- ✅ One account can invalidate group safety
- ✅ Surface this clearly (API endpoint + WebSocket)

## Completed ✅

### 1. Database Models ✅
- Created `AccountGroup` model
- Many-to-many relationship with `ConnectedAccount`
- User ownership
- Timestamps

### 2. Group Risk Evaluation Logic ✅
- Implemented `get_group_risk_evaluation()` function
- Weakest account logic:
  - Finds account with lowest buffer per rule
  - Group status = worst account status
  - Group buffer = minimum buffer
- One violation invalidates group

### 3. API Endpoints ✅
- `GET /api/v1/groups` - List user's groups
- `POST /api/v1/groups` - Create group
- `GET /api/v1/groups/{group_id}` - Get group details
- `PUT /api/v1/groups/{group_id}` - Update group
- `DELETE /api/v1/groups/{group_id}` - Delete group
- `POST /api/v1/groups/{group_id}/accounts/{account_id}` - Add account
- `DELETE /api/v1/groups/{group_id}/accounts/{account_id}` - Remove account
- `GET /api/v1/groups/{group_id}/risk` - Get group risk evaluation

### 4. WebSocket Support ✅
- Added group WebSocket endpoint `/ws/group/{group_id}`
- Group updates sent when any member account updates
- Real-time group risk evaluation

### 5. Schemas ✅
- `GroupCreate` - Create group
- `GroupUpdate` - Update group
- `GroupResponse` - Group response
- `GroupRiskEvaluation` - Risk evaluation result
- `RuleStateSummary` - Rule state summary

## Files Created

### New Files
- `models/account_group.py` - AccountGroup database model
- `schemas/group.py` - Group schemas
- `api/v1/endpoints/groups.py` - Group endpoints
- `docs/PHASE6_PLAN.md` - Implementation plan
- `docs/PHASE6_PROGRESS.md` - This file

### Modified Files
- `models/user.py` - Added account_groups relationship
- `models/account.py` - Added groups relationship
- `models/__init__.py` - Export AccountGroup
- `api/v1/api.py` - Include groups router
- `api/v1/endpoints/websocket.py` - Group WebSocket support
- `services/account_tracker.py` - Group update notifications

## Implementation Details

### Group Risk Evaluation Algorithm

1. **Collect Account States**
   - Get latest state snapshot for each account in group
   - Extract rule states from snapshots

2. **Find Weakest Account Per Rule**
   - For each rule type:
     - Compare status priority (violated > critical > caution > safe)
     - If same status, compare buffer (lower = weaker)
     - Track weakest account per rule

3. **Determine Overall Group Status**
   - Overall status = worst status across all rules
   - Overall weakest account = account with worst status

4. **Return Group Risk Evaluation**
   - Overall status
   - Weakest account ID and name
   - Per-rule summaries with weakest account info

### WebSocket Updates

When an account state changes:
1. Send account update to account WebSocket subscribers
2. Find all groups containing this account
3. Calculate group risk evaluation
4. Send group update to group WebSocket subscribers

## Key Principles

✅ **Weakest Account Dominates**
- Group status = worst account status
- Group buffer = minimum buffer
- One violation = group violation

✅ **Clear Surface**
- API endpoint shows group risk
- WebSocket provides real-time updates
- Weakest account clearly identified

✅ **Real-time Updates**
- Group risk updates when any member account updates
- WebSocket notifications for group changes

## Remaining Tasks

### Database Migration
- [ ] Create migration for `account_groups` table
- [ ] Create migration for `account_group_members` association table

### Frontend Integration
- [ ] Create group management UI
- [ ] Display group risk evaluation
- [ ] Show weakest account
- [ ] Group WebSocket integration

### Testing
- [ ] Test group creation
- [ ] Test group risk evaluation
- [ ] Test WebSocket updates
- [ ] Test weakest account logic

## Validation

### ✅ Master Plan Requirements Met
- ✅ Account grouping implemented
- ✅ Weakest account logic
- ✅ Group risk evaluation
- ✅ Lowest buffer dominates
- ✅ One violation invalidates group
- ✅ Clear API surface

## Next Steps

1. **Database Migration**
   - Create Alembic migration
   - Test migration

2. **Frontend Integration**
   - Group management UI
   - Group risk display
   - WebSocket integration

3. **Testing**
   - Unit tests for group logic
   - Integration tests for endpoints
   - WebSocket tests

---

**PHASE 6: ~85% Complete** - Backend complete, needs migration and frontend
