"""
Account group management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from decimal import Decimal

from app.core.database import get_db
from app.models.user import User
from app.models.account import ConnectedAccount
from app.models.account_group import AccountGroup
from app.models.account_state import AccountStateSnapshot
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.group import (
    GroupCreate,
    GroupUpdate,
    GroupResponse,
    GroupListResponse,
    GroupRiskEvaluation,
    RuleStateSummary,
    GroupMember,
)
from app.services.account_tracker import account_tracker

router = APIRouter()


def get_group_risk_evaluation(
    group: AccountGroup,
    db: Session,
) -> GroupRiskEvaluation:
    """
    Calculate group risk evaluation.
    
    Per Master Plan:
    - Lowest buffer dominates
    - One account can invalidate group safety
    - Weakest account logic
    """
    if not group.accounts:
        # Empty group - return safe status
        return GroupRiskEvaluation(
            groupId=group.id,
            groupName=group.name,
            overallStatus="safe",
            weakestAccountId="",
            weakestAccountName="",
            ruleStates={},
            timestamp="",
        )

    # Get latest state for each account
    account_states = {}
    for account in group.accounts:
        # Get latest snapshot
        latest_snapshot = (
            db.query(AccountStateSnapshot)
            .filter(AccountStateSnapshot.account_id == account.id)
            .order_by(AccountStateSnapshot.timestamp.desc())
            .first()
        )
        
        if latest_snapshot and latest_snapshot.rule_states:
            account_states[account.id] = {
                "account": account,
                "rule_states": latest_snapshot.rule_states,
            }

    if not account_states:
        # No states available
        return GroupRiskEvaluation(
            groupId=group.id,
            groupName=group.name,
            overallStatus="disconnected",
            weakestAccountId="",
            weakestAccountName="",
            ruleStates={},
            timestamp="",
        )

    # For each rule, find the weakest account (lowest buffer)
    group_rule_states = {}
    overall_worst_status = "safe"
    overall_weakest_account_id = None
    overall_weakest_account_name = None

    # Collect all rule names from all accounts
    all_rule_names = set()
    for account_data in account_states.values():
        if account_data["rule_states"]:
            all_rule_names.update(account_data["rule_states"].keys())

    # For each rule, find the account with the worst status/buffer
    for rule_name in all_rule_names:
        worst_buffer = Decimal("999999999")  # Start with very high buffer
        worst_buffer_percent = Decimal("100")
        worst_status = "safe"
        weakest_account_id = None
        weakest_account_name = None

        for account_id, account_data in account_states.items():
            rule_state = account_data["rule_states"].get(rule_name)
            if not rule_state:
                continue

            status_val = rule_state.get("status", "safe")
            buffer = Decimal(str(rule_state.get("remainingBuffer", 0)))
            buffer_percent = Decimal(str(rule_state.get("bufferPercent", 100)))

            # Status priority: violated > critical > caution > safe
            status_priority = {
                "violated": 4,
                "critical": 3,
                "caution": 2,
                "safe": 1,
            }

            current_priority = status_priority.get(status_val, 1)
            worst_priority = status_priority.get(worst_status, 1)

            # If this account has worse status, or same status but lower buffer
            if (
                current_priority > worst_priority
                or (current_priority == worst_priority and buffer < worst_buffer)
            ):
                worst_status = status_val
                worst_buffer = buffer
                worst_buffer_percent = buffer_percent
                weakest_account_id = account_id
                weakest_account_name = account_data["account"].account_name

        # Update overall worst status
        worst_priority = status_priority.get(worst_status, 1)
        overall_worst_priority = status_priority.get(overall_worst_status, 1)
        if worst_priority > overall_worst_priority:
            overall_worst_status = worst_status
            overall_weakest_account_id = weakest_account_id
            overall_weakest_account_name = weakest_account_name

        group_rule_states[rule_name] = RuleStateSummary(
            status=worst_status,
            remainingBuffer=float(worst_buffer),
            bufferPercent=float(worst_buffer_percent),
            weakestAccountId=weakest_account_id or "",
            weakestAccountName=weakest_account_name or "",
        )

    # If no overall weakest found, use first account
    if not overall_weakest_account_id and account_states:
        first_account = list(account_states.values())[0]["account"]
        overall_weakest_account_id = first_account.id
        overall_weakest_account_name = first_account.account_name

    return GroupRiskEvaluation(
        groupId=group.id,
        groupName=group.name,
        overallStatus=overall_worst_status,
        weakestAccountId=overall_weakest_account_id or "",
        weakestAccountName=overall_weakest_account_name or "",
        ruleStates={rule_name: state.dict() for rule_name, state in group_rule_states.items()},
        timestamp="",  # Will be set by caller
    )


@router.get("/", response_model=GroupListResponse)
async def list_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all account groups for the current user."""
    groups = (
        db.query(AccountGroup)
        .filter(AccountGroup.user_id == current_user.id)
        .all()
    )

    group_responses = []
    for group in groups:
        group_responses.append(
            GroupResponse(
                id=group.id,
                name=group.name,
                description=group.description,
                userId=group.user_id,
                accountIds=[acc.id for acc in group.accounts],
                accounts=[
                    GroupMember(
                        id=acc.id,
                        accountName=acc.account_name,
                        firm=acc.firm,
                        accountType=acc.account_type,
                        accountSize=acc.account_size / 100,  # Convert cents to dollars
                        platform=acc.platform,
                    )
                    for acc in group.accounts
                ],
                createdAt=group.created_at.isoformat(),
                updatedAt=group.updated_at.isoformat()
                if group.updated_at
                else group.created_at.isoformat(),
            )
        )

    return GroupListResponse(groups=group_responses)


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new account group."""
    # Verify all accounts belong to user
    if group_data.account_ids:
        accounts = (
            db.query(ConnectedAccount)
            .filter(
                ConnectedAccount.id.in_(group_data.account_ids),
                ConnectedAccount.user_id == current_user.id,
            )
            .all()
        )
        if len(accounts) != len(group_data.account_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more accounts not found or do not belong to user",
            )
    else:
        accounts = []

    group = AccountGroup(
        id=str(uuid.uuid4()),
        name=group_data.name,
        description=group_data.description,
        user_id=current_user.id,
    )
    group.accounts = accounts

    db.add(group)
    db.commit()
    db.refresh(group)

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        userId=group.user_id,
        accountIds=[acc.id for acc in group.accounts],
        accounts=[
            GroupMember(
                id=acc.id,
                accountName=acc.account_name,
                firm=acc.firm,
                accountType=acc.account_type,
                accountSize=acc.account_size / 100,
                platform=acc.platform,
            )
            for acc in group.accounts
        ],
        createdAt=group.created_at.isoformat(),
        updatedAt=group.updated_at.isoformat()
        if group.updated_at
        else group.created_at.isoformat(),
    )


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific account group."""
    group = (
        db.query(AccountGroup)
        .filter(AccountGroup.id == group_id, AccountGroup.user_id == current_user.id)
        .first()
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
        )

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        userId=group.user_id,
        accountIds=[acc.id for acc in group.accounts],
        accounts=[
            GroupMember(
                id=acc.id,
                accountName=acc.account_name,
                firm=acc.firm,
                accountType=acc.account_type,
                accountSize=acc.account_size / 100,
                platform=acc.platform,
            )
            for acc in group.accounts
        ],
        createdAt=group.created_at.isoformat(),
        updatedAt=group.updated_at.isoformat()
        if group.updated_at
        else group.created_at.isoformat(),
    )


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: str,
    group_data: GroupUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an account group."""
    group = (
        db.query(AccountGroup)
        .filter(AccountGroup.id == group_id, AccountGroup.user_id == current_user.id)
        .first()
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
        )

    if group_data.name is not None:
        group.name = group_data.name
    if group_data.description is not None:
        group.description = group_data.description

    db.commit()
    db.refresh(group)

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        userId=group.user_id,
        accountIds=[acc.id for acc in group.accounts],
        accounts=[
            GroupMember(
                id=acc.id,
                accountName=acc.account_name,
                firm=acc.firm,
                accountType=acc.account_type,
                accountSize=acc.account_size / 100,
                platform=acc.platform,
            )
            for acc in group.accounts
        ],
        createdAt=group.created_at.isoformat(),
        updatedAt=group.updated_at.isoformat()
        if group.updated_at
        else group.created_at.isoformat(),
    )


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an account group."""
    group = (
        db.query(AccountGroup)
        .filter(AccountGroup.id == group_id, AccountGroup.user_id == current_user.id)
        .first()
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
        )

    db.delete(group)
    db.commit()

    return None


@router.post("/{group_id}/accounts/{account_id}", response_model=GroupResponse)
async def add_account_to_group(
    group_id: str,
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add an account to a group."""
    group = (
        db.query(AccountGroup)
        .filter(AccountGroup.id == group_id, AccountGroup.user_id == current_user.id)
        .first()
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
        )

    account = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.id == account_id, ConnectedAccount.user_id == current_user.id
        )
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    if account not in group.accounts:
        group.accounts.append(account)
        db.commit()
        db.refresh(group)

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        userId=group.user_id,
        accountIds=[acc.id for acc in group.accounts],
        accounts=[
            GroupMember(
                id=acc.id,
                accountName=acc.account_name,
                firm=acc.firm,
                accountType=acc.account_type,
                accountSize=acc.account_size / 100,
                platform=acc.platform,
            )
            for acc in group.accounts
        ],
        createdAt=group.created_at.isoformat(),
        updatedAt=group.updated_at.isoformat()
        if group.updated_at
        else group.created_at.isoformat(),
    )


@router.delete("/{group_id}/accounts/{account_id}", response_model=GroupResponse)
async def remove_account_from_group(
    group_id: str,
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove an account from a group."""
    group = (
        db.query(AccountGroup)
        .filter(AccountGroup.id == group_id, AccountGroup.user_id == current_user.id)
        .first()
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
        )

    account = (
        db.query(ConnectedAccount)
        .filter(ConnectedAccount.id == account_id)
        .first()
    )

    if account and account in group.accounts:
        group.accounts.remove(account)
        db.commit()
        db.refresh(group)

    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        userId=group.user_id,
        accountIds=[acc.id for acc in group.accounts],
        accounts=[
            GroupMember(
                id=acc.id,
                accountName=acc.account_name,
                firm=acc.firm,
                accountType=acc.account_type,
                accountSize=acc.account_size / 100,
                platform=acc.platform,
            )
            for acc in group.accounts
        ],
        createdAt=group.created_at.isoformat(),
        updatedAt=group.updated_at.isoformat()
        if group.updated_at
        else group.created_at.isoformat(),
    )


@router.get("/{group_id}/risk", response_model=GroupRiskEvaluation)
async def get_group_risk(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get group risk evaluation.
    
    Per Master Plan:
    - Lowest buffer dominates
    - One account can invalidate group safety
    - Weakest account logic
    """
    group = (
        db.query(AccountGroup)
        .filter(AccountGroup.id == group_id, AccountGroup.user_id == current_user.id)
        .first()
    )

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
        )

    evaluation = get_group_risk_evaluation(group, db)
    evaluation.timestamp = group.updated_at.isoformat() if group.updated_at else group.created_at.isoformat()

    return evaluation
