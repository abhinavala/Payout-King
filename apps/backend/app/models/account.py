"""
Connected account model.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class ConnectedAccount(Base):
    """Connected trading account model."""

    __tablename__ = "connected_accounts"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    platform = Column(String, nullable=False)  # 'tradovate', 'ninjatrader', 'rithmic'
    account_id = Column(String, nullable=False)  # Platform-specific account ID
    account_name = Column(String, nullable=False)
    firm = Column(String, nullable=False)  # 'apex', 'topstep', etc.
    account_type = Column(String, nullable=False)  # 'eval', 'pa', 'funded'
    account_size = Column(Integer, nullable=False)  # Starting balance in cents
    rule_set_version = Column(String, nullable=False)
    
    # Encrypted API credentials
    encrypted_api_token = Column(String, nullable=True)
    encrypted_api_secret = Column(String, nullable=True)
    
    # Account metadata
    is_active = Column(Boolean, default=True)
    account_metadata = Column(JSON, default=dict)  # Additional platform-specific data (renamed from 'metadata' - reserved word)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="accounts")
    state_snapshots = relationship("AccountStateSnapshot", back_populates="account", cascade="all, delete-orphan")
    groups = relationship("AccountGroup", secondary="account_group_members", back_populates="accounts")
    audit_logs = relationship("AuditLog", back_populates="account", cascade="all, delete-orphan")

