"""
Audit log schemas.
"""

from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.models.audit_log import AuditEventType


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""

    id: str
    accountId: Optional[str]
    groupId: Optional[str]
    userId: str
    eventType: str
    ruleName: Optional[str]
    previousStatus: Optional[str]
    currentStatus: Optional[str]
    message: Optional[str]
    eventData: dict
    timestamp: str

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Schema for list of audit logs."""

    logs: List[AuditLogResponse]
    total: int


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs."""

    accountId: Optional[str] = None
    groupId: Optional[str] = None
    eventType: Optional[AuditEventType] = None
    ruleName: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    limit: int = 100
    offset: int = 0
