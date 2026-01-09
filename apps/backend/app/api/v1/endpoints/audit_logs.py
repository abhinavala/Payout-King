"""
Audit log endpoints for querying audit trail.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.audit_log import AuditLog, AuditEventType
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.audit_log import AuditLogResponse, AuditLogListResponse, AuditLogFilter

router = APIRouter()


@router.get("/", response_model=AuditLogListResponse)
async def list_audit_logs(
    account_id: Optional[str] = Query(None),
    group_id: Optional[str] = Query(None),
    event_type: Optional[AuditEventType] = Query(None),
    rule_name: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Query audit logs.
    
    Only returns logs for accounts/groups owned by the current user.
    """
    query = db.query(AuditLog).filter(AuditLog.user_id == current_user.id)
    
    if account_id:
        query = query.filter(AuditLog.account_id == account_id)
    
    if group_id:
        query = query.filter(AuditLog.group_id == group_id)
    
    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    
    if rule_name:
        query = query.filter(AuditLog.rule_name == rule_name)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
    
    return AuditLogListResponse(
        logs=[
            AuditLogResponse(
                id=log.id,
                accountId=log.account_id,
                groupId=log.group_id,
                userId=log.user_id,
                eventType=log.event_type.value,
                ruleName=log.rule_name,
                previousStatus=log.previous_status,
                currentStatus=log.current_status,
                message=log.message,
                eventData=log.event_data or {},
                timestamp=log.timestamp.isoformat(),
            )
            for log in logs
        ],
        total=total,
    )


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific audit log entry."""
    log = db.query(AuditLog).filter(
        AuditLog.id == log_id,
        AuditLog.user_id == current_user.id,
    ).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )
    
    return AuditLogResponse(
        id=log.id,
        accountId=log.account_id,
        groupId=log.group_id,
        userId=log.user_id,
        eventType=log.event_type.value,
        ruleName=log.rule_name,
        previousStatus=log.previous_status,
        currentStatus=log.current_status,
        message=log.message,
        eventData=log.event_data or {},
        timestamp=log.timestamp.isoformat(),
    )
