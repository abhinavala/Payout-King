"""
Account schemas.
"""

from typing import List
from pydantic import BaseModel


class AccountCreate(BaseModel):
    """Schema for creating a connected account."""

    platform: str  # 'tradovate', 'ninjatrader', 'rithmic'
    accountId: str
    accountName: str
    firm: str  # 'apex', 'topstep', etc.
    accountType: str  # 'eval', 'pa', 'funded'
    accountSize: float  # Starting balance in USD
    ruleSetVersion: str
    username: str  # Tradovate username (will be encrypted)
    password: str  # Tradovate password (will be encrypted)


class AccountResponse(BaseModel):
    """Schema for account response."""

    id: str
    userId: str
    platform: str
    accountId: str
    accountName: str
    firm: str
    accountType: str
    accountSize: float
    ruleSetVersion: str
    isActive: bool
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True


class AccountListResponse(BaseModel):
    """Schema for list of accounts."""

    accounts: List[AccountResponse]

