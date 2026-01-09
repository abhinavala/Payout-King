"""
Audit log model for tracking all warnings, state changes, and violations.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class AuditEventType(str, enum.Enum):
    """Types of audit events."""
    
    WARNING = "warning"  # Rule warning (caution/critical status)
    STATE_CHANGE = "state_change"  # Account state changed
    VIOLATION = "violation"  # Rule violated
    RULE_EVALUATION = "rule_evaluation"  # Rule evaluation performed
    ACCOUNT_UPDATE = "account_update"  # Account data updated
    GROUP_UPDATE = "group_update"  # Group risk updated


class AuditLog(Base):
    """Audit log entry for tracking all system events."""

    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    account_id = Column(String, ForeignKey("connected_accounts.id"), nullable=True, index=True)
    group_id = Column(String, ForeignKey("account_groups.id"), nullable=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    event_type = Column(Enum(AuditEventType), nullable=False, index=True)
    event_data = Column(JSON, default=dict)  # Event-specific data
    
    # Event details
    rule_name = Column(String, nullable=True)  # Rule that triggered event
    previous_status = Column(String, nullable=True)  # Previous rule status
    current_status = Column(String, nullable=True)  # Current rule status
    message = Column(String, nullable=True)  # Human-readable message
    
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, server_default=func.now())
    
    # Relationships
    account = relationship("ConnectedAccount", back_populates="audit_logs")
    group = relationship("AccountGroup", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
