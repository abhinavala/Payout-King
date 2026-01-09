"""
Account group schemas.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class GroupCreate(BaseModel):
    """Schema for creating an account group."""

    name: str
    description: Optional[str] = None
    account_ids: List[str] = []  # List of account IDs to add to group


class GroupUpdate(BaseModel):
    """Schema for updating an account group."""

    name: Optional[str] = None
    description: Optional[str] = None


class GroupMember(BaseModel):
    """Schema for a group member account."""

    id: str
    accountName: str
    firm: str
    accountType: str
    accountSize: float
    platform: str

    class Config:
        from_attributes = True


class GroupResponse(BaseModel):
    """Schema for group response."""

    id: str
    name: str
    description: Optional[str]
    userId: str
    accountIds: List[str]
    accounts: List[GroupMember]
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True


class GroupListResponse(BaseModel):
    """Schema for list of groups."""

    groups: List[GroupResponse]


class RuleStateSummary(BaseModel):
    """Summary of a rule state for group evaluation."""

    status: str  # safe, caution, critical, violated
    remainingBuffer: float
    bufferPercent: float
    weakestAccountId: str
    weakestAccountName: str


class GroupRiskEvaluation(BaseModel):
    """Group risk evaluation result."""

    groupId: str
    groupName: str
    overallStatus: str  # safe, caution, critical, violated
    weakestAccountId: str
    weakestAccountName: str
    ruleStates: Dict[str, RuleStateSummary]
    timestamp: str
