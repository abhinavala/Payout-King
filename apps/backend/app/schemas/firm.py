"""
Schemas for prop firm information.
"""

from typing import List, Dict
from pydantic import BaseModel


class FirmInfo(BaseModel):
    """Information about a prop firm."""

    id: str
    name: str
    display_name: str
    supported_account_types: List[str]
    description: str
    rules_summary: Dict[str, str]


class FirmListResponse(BaseModel):
    """Response with list of supported firms."""

    firms: List[FirmInfo]


class AccountTypeInfo(BaseModel):
    """Information about account types."""

    id: str
    name: str
    display_name: str
    description: str


class AccountTypeListResponse(BaseModel):
    """Response with list of account types."""

    account_types: List[AccountTypeInfo]

