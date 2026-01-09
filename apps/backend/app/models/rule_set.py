"""
Rule set model for prop firm rules.
"""

from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class RuleSet(Base):
    """Rule set model for prop firm rules."""

    __tablename__ = "rule_sets"

    id = Column(String, primary_key=True, index=True)
    firm = Column(String, nullable=False, index=True)  # 'apex', 'topstep', etc.
    account_type = Column(String, nullable=False)  # 'eval', 'pa', 'funded'
    version = Column(String, nullable=False)  # e.g., '1.0', '2024-01-01
    rules = Column(JSON, nullable=False)  # Serialized FirmRules
    effective_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        {"comment": "Versioned rule sets for different prop firms"},
    )

