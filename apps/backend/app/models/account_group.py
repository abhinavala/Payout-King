"""
Account group model for multi-account management and copy-trade logic.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

# Association table for many-to-many relationship
account_group_members = Table(
    "account_group_members",
    Base.metadata,
    Column("group_id", String, ForeignKey("account_groups.id"), primary_key=True),
    Column("account_id", String, ForeignKey("connected_accounts.id"), primary_key=True),
)


class AccountGroup(Base):
    """Account group model for grouping accounts together."""

    __tablename__ = "account_groups"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    description = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="account_groups")
    accounts = relationship(
        "ConnectedAccount",
        secondary=account_group_members,
        back_populates="groups",
    )
    audit_logs = relationship("AuditLog", back_populates="group", cascade="all, delete-orphan")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
