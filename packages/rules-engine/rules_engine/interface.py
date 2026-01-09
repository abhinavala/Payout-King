"""
Frozen interface for the Rules Engine.

This module defines the stable input/output contracts that will not change.
This allows swapping between mock data, Tradovate data, and other brokers.

DO NOT MODIFY THESE INTERFACES WITHOUT CAREFUL CONSIDERATION.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from .models import RuleState


class AccountSnapshot(BaseModel):
    """
    FROZEN INPUT INTERFACE
    
    This is the single input object for the rules engine.
    All data sources (mock, Tradovate, other brokers) must convert to this format.
    
    Fields:
    - account_id: Unique identifier for the account
    - timestamp: When this snapshot was taken
    - equity: Current account equity (balance + unrealized PnL)
    - balance: Account balance (realized PnL only)
    - realized_pnl: Total realized PnL
    - unrealized_pnl: Total unrealized PnL from open positions
    - high_water_mark: Highest equity ever reached (for trailing drawdown)
    - daily_pnl: PnL for the current trading day (must be calculated from fills)
    - starting_balance: Initial account balance when account was created
    - open_positions: List of currently open positions
    """
    
    account_id: str
    timestamp: datetime
    equity: Decimal = Field(..., description="Current account equity")
    balance: Decimal = Field(..., description="Account balance")
    realized_pnl: Decimal = Field(default=Decimal("0"))
    unrealized_pnl: Decimal = Field(default=Decimal("0"))
    high_water_mark: Decimal = Field(
        ..., description="Highest equity reached (for trailing drawdown)"
    )
    daily_pnl: Decimal = Field(
        default=Decimal("0"),
        description="PnL for current trading day (calculated from fills)"
    )
    starting_balance: Decimal = Field(..., description="Initial account balance")
    
    # Daily PnL history for consistency rule and minimum trading days
    # Key: Date string (YYYY-MM-DD), Value: Daily realized PnL for that date
    daily_pnl_history: Optional[Dict[str, Decimal]] = Field(
        default=None,
        description="Historical daily PnL by date. Required for consistency rule and minimum trading days."
    )
    
    # Open positions
    open_positions: List["PositionSnapshot"] = Field(default_factory=list)


class PositionSnapshot(BaseModel):
    """
    Snapshot of an open position.
    """
    
    symbol: str
    quantity: int  # Positive = long, negative = short
    avg_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal
    opened_at: datetime
    peak_unrealized_loss: Decimal = Field(
        default=Decimal("0"),
        description="Peak unrealized loss for MAE tracking"
    )


# Forward reference resolution (Pydantic v2)
# Note: Pydantic v2 handles forward references automatically, but we keep this for clarity


class RuleEvaluationResult(BaseModel):
    """
    FROZEN OUTPUT INTERFACE
    
    This is the single output object from the rules engine.
    Contains all rule states and calculated metrics.
    
    Fields:
    - account_id: Account this evaluation is for
    - timestamp: When evaluation was performed
    - rule_states: Dictionary of rule_name -> RuleState
    - max_allowed_risk: Calculated safe limits (max loss, max contracts, etc.)
    - overall_risk_level: Aggregated risk level (safe/caution/critical/violated)
    """
    
    account_id: str
    timestamp: datetime
    rule_states: Dict[str, RuleState] = Field(
        ..., description="Rule name -> RuleState mapping"
    )
    max_allowed_risk: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Safe limits: max_loss_allowed, max_contracts_allowed, etc."
    )
    overall_risk_level: str = Field(
        ..., description="Aggregated: 'safe', 'caution', 'critical', or 'violated'"
    )

