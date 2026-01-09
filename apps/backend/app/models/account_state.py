"""
Account state snapshot model.
"""

from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class AccountStateSnapshot(Base):
    """Snapshot of account state at a point in time."""

    __tablename__ = "account_state_snapshots"

    id = Column(String, primary_key=True, index=True)
    account_id = Column(String, ForeignKey("connected_accounts.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Account metrics
    equity = Column(Numeric(20, 2), nullable=False)
    balance = Column(Numeric(20, 2), nullable=False)
    realized_pnl = Column(Numeric(20, 2), default=0)
    unrealized_pnl = Column(Numeric(20, 2), default=0)
    high_water_mark = Column(Numeric(20, 2), nullable=False)
    daily_pnl = Column(Numeric(20, 2), default=0)
    
    # Serialized data
    open_positions = Column(JSON, default=list)
    rule_states = Column(JSON, default=dict)  # Calculated rule states
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    account = relationship("ConnectedAccount", back_populates="state_snapshots")

