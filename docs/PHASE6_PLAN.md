# PHASE 6 - Multi-Account & Copy-Trade Logic

## Current Phase: PHASE 6 - Multi-Account & Copy-Trade Logic

## Master Plan Requirements

### 6.1 Account Grouping
Define:
- Group ID
- Member accounts
- Weakest account logic

### 6.2 Group Risk Evaluation
Rules:
- Lowest buffer dominates
- One account can invalidate group safety
- Surface this clearly

## Implementation Strategy

### 1. Database Models
- `AccountGroup` model
  - Group ID (UUID)
  - Group name
  - Owner (user)
  - Created/updated timestamps
  - Member accounts (many-to-many relationship)

### 2. Group Risk Evaluation Logic
- Calculate group-level risk from member accounts
- Weakest account logic:
  - Find account with lowest buffer across all rules
  - Group status = weakest account status
  - Group buffer = minimum buffer across all accounts
- One violation invalidates group

### 3. API Endpoints
- `POST /api/v1/groups` - Create group
- `GET /api/v1/groups` - List user's groups
- `GET /api/v1/groups/{group_id}` - Get group details
- `PUT /api/v1/groups/{group_id}` - Update group
- `DELETE /api/v1/groups/{group_id}` - Delete group
- `POST /api/v1/groups/{group_id}/accounts` - Add account to group
- `DELETE /api/v1/groups/{group_id}/accounts/{account_id}` - Remove account
- `GET /api/v1/groups/{group_id}/risk` - Get group risk evaluation

### 4. Group Risk Calculation
- For each rule type:
  - Find minimum buffer across all accounts
  - Find minimum buffer percent
  - Determine group status (weakest account status)
- Overall group risk = worst status across all rules

### 5. Copy-Trade Logic (Future)
- Track which accounts are copy-trading
- Ensure all copy-trade accounts follow same rules
- Group-level risk applies to all copy-trade accounts

## Data Structures

### AccountGroup Model
```python
class AccountGroup:
    id: UUID
    name: str
    user_id: UUID
    account_ids: List[UUID]
    created_at: datetime
    updated_at: datetime
```

### GroupRiskEvaluation
```python
class GroupRiskEvaluation:
    group_id: UUID
    overall_status: str  # safe, caution, critical, violated
    weakest_account_id: UUID
    rule_states: Dict[str, RuleState]
    timestamp: datetime
```

## Implementation Steps

1. Create AccountGroup database model
2. Create group schemas (Pydantic)
3. Create group endpoints
4. Implement group risk evaluation logic
5. Add WebSocket support for group updates
6. Update frontend to show groups
7. Add weakest account highlighting

## Key Principles

1. **Weakest Account Dominates**
   - Group status = worst account status
   - Group buffer = minimum buffer
   - One violation = group violation

2. **Clear Surface**
   - Show which account is weakest
   - Show group-level buffers
   - Show group-level status

3. **Real-time Updates**
   - Group risk updates when any member account updates
   - WebSocket notifications for group changes

## Next Steps

1. Review existing account models
2. Create AccountGroup model
3. Implement group risk evaluation
4. Create API endpoints
5. Add WebSocket support
6. Update frontend
