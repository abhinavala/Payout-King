"""
Data models for the rules engine.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RuleStatus(str, Enum):
    """Status of a rule check."""

    SAFE = "safe"
    CAUTION = "caution"
    CRITICAL = "critical"
    VIOLATED = "violated"


class RuleSeverity(str, Enum):
    """Severity of rule violation."""

    HARD_FAIL = "hard_fail"  # Account fails immediately
    PAYOUT_BLOCK = "payout_block"  # Blocks payout but account continues
    SOFT_RULE = "soft_rule"  # May trigger review


class RuleRecoverability(str, Enum):
    """Whether a rule violation can be recovered from."""

    NON_RECOVERABLE = "non_recoverable"  # ❌ Cannot be fixed, account fails
    RECOVERABLE = "recoverable"  # ✅ Can be fixed
    SOMETIMES = "sometimes"  # ⚠️ May be recoverable depending on context


class RuleType(str, Enum):
    """Type of rule."""

    OBJECTIVE = "objective"  # Clear, mathematical rule
    SUBJECTIVE = "subjective"  # Advisory, judgment-based
    SEMI_OBJECTIVE = "semi_objective"  # Mostly objective but may have subjective elements


class Position(BaseModel):
    """Open trading position."""

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


class AccountState(BaseModel):
    """Current state of a trading account."""

    account_id: str
    timestamp: datetime
    equity: Decimal = Field(..., description="Current account equity")
    balance: Decimal = Field(..., description="Account balance")
    realized_pnl: Decimal = Field(default=Decimal("0"))
    unrealized_pnl: Decimal = Field(default=Decimal("0"))
    high_water_mark: Decimal = Field(
        ..., description="Highest equity reached (for trailing drawdown)"
    )
    open_positions: List[Position] = Field(default_factory=list)
    daily_pnl: Decimal = Field(default=Decimal("0"))
    starting_balance: Decimal = Field(..., description="Initial account balance")


class TrailingDrawdownRule(BaseModel):
    """Trailing drawdown rule configuration."""

    enabled: bool = True
    max_drawdown_percent: Decimal = Field(
        ..., description="Maximum drawdown as percentage (e.g., 5 for 5%)"
    )
    include_unrealized_pnl: bool = True
    reset_on_profit_target: bool = False
    profit_target_percent: Optional[Decimal] = None
    recoverable: RuleRecoverability = RuleRecoverability.NON_RECOVERABLE
    severity: RuleSeverity = RuleSeverity.HARD_FAIL
    rule_type: RuleType = RuleType.OBJECTIVE


class DailyLossLimitRule(BaseModel):
    """Daily loss limit rule configuration."""

    enabled: bool = True
    max_loss_amount: Decimal = Field(..., description="Maximum daily loss in USD")
    reset_time: str = Field(
        ..., description="Time when daily limit resets (e.g., '17:00')"
    )
    timezone: str = Field(default="America/Chicago", description="Timezone for reset")
    recoverable: RuleRecoverability = RuleRecoverability.RECOVERABLE
    severity: RuleSeverity = RuleSeverity.HARD_FAIL
    rule_type: RuleType = RuleType.OBJECTIVE
    liquidates_positions: bool = Field(
        default=True, description="Whether positions are liquidated on violation"
    )


class OverallMaxLossRule(BaseModel):
    """Overall maximum loss rule."""

    enabled: bool = True
    max_loss_amount: Decimal
    from_starting_balance: bool = True


class MaxPositionSizeRule(BaseModel):
    """Maximum position size rule."""

    enabled: bool = True
    max_contracts: int
    max_risk_per_trade: Optional[Decimal] = None
    recoverable: RuleRecoverability = RuleRecoverability.NON_RECOVERABLE
    severity: RuleSeverity = RuleSeverity.HARD_FAIL
    rule_type: RuleType = RuleType.OBJECTIVE


class MAERule(BaseModel):
    """Maximum Adverse Excursion (MAE) rule.
    
    Tracks peak unrealized loss on any trade, even if trade later recovers.
    """

    enabled: bool = True
    max_adverse_excursion_percent: Decimal = Field(
        ..., description="Max MAE as percentage of account"
    )
    recoverable: RuleRecoverability = RuleRecoverability.NON_RECOVERABLE
    severity: RuleSeverity = RuleSeverity.HARD_FAIL
    rule_type: RuleType = RuleType.OBJECTIVE


class ConsistencyRule(BaseModel):
    """Consistency rule - limits largest winning day as % of total profit."""

    enabled: bool = True
    max_single_day_percent: Decimal = Field(
        ..., description="Max % of total profit from single day (e.g., 30 for 30%)"
    )
    recoverable: RuleRecoverability = RuleRecoverability.RECOVERABLE
    severity: RuleSeverity = RuleSeverity.PAYOUT_BLOCK
    rule_type: RuleType = RuleType.OBJECTIVE
    applies_at_payout: bool = Field(
        default=True, description="Only checked when requesting payout"
    )


class TradingHoursRule(BaseModel):
    """Trading hours restriction rule."""

    enabled: bool = True
    forced_close_time: str = Field(
        ..., description="Time when all positions must be closed (e.g., '16:59')"
    )
    timezone: str = Field(default="America/New_York", description="Timezone")
    recoverable: RuleRecoverability = RuleRecoverability.NON_RECOVERABLE
    severity: RuleSeverity = RuleSeverity.HARD_FAIL
    rule_type: RuleType = RuleType.OBJECTIVE
    auto_liquidate: bool = Field(
        default=True, description="Whether positions are auto-liquidated"
    )


class MinimumTradingDaysRule(BaseModel):
    """Minimum trading days requirement."""

    enabled: bool = True
    min_days: int = Field(..., description="Minimum number of trading days")
    min_profit_per_day: Decimal = Field(
        default=Decimal("50"),
        description="Minimum profit to count as trading day"
    )
    recoverable: RuleRecoverability = RuleRecoverability.RECOVERABLE
    severity: RuleSeverity = RuleSeverity.HARD_FAIL
    rule_type: RuleType = RuleType.OBJECTIVE


class ProfitTargetRule(BaseModel):
    """Profit target rule."""

    enabled: bool = True
    target_amount: Decimal = Field(..., description="Profit target in USD")
    recoverable: RuleRecoverability = RuleRecoverability.RECOVERABLE
    severity: RuleSeverity = RuleSeverity.HARD_FAIL
    rule_type: RuleType = RuleType.OBJECTIVE


class FirmRules(BaseModel):
    """Complete set of rules for a prop firm."""

    trailing_drawdown: Optional[TrailingDrawdownRule] = None
    daily_loss_limit: Optional[DailyLossLimitRule] = None
    overall_max_loss: Optional[OverallMaxLossRule] = None
    max_position_size: Optional[MaxPositionSizeRule] = None
    mae_rule: Optional[MAERule] = None
    consistency_rule: Optional[ConsistencyRule] = None
    trading_hours: Optional[TradingHoursRule] = None
    minimum_trading_days: Optional[MinimumTradingDaysRule] = None
    profit_target: Optional[ProfitTargetRule] = None


class DistanceMetric(BaseModel):
    """Distance to violation in various units."""

    dollars: Optional[Decimal] = None
    ticks: Optional[Decimal] = None
    contracts: Optional[int] = None
    percent: Optional[Decimal] = None


class RuleState(BaseModel):
    """Current state of a specific rule."""

    rule_name: str
    current_value: Decimal
    threshold: Decimal
    remaining_buffer: Decimal = Field(
        ..., description="How much room until violation"
    )
    buffer_percent: Decimal = Field(
        ..., description="0-100, how close to violation"
    )
    status: RuleStatus
    distance_to_violation: DistanceMetric
    warnings: List[str] = Field(default_factory=list)
    recoverable: RuleRecoverability = Field(
        default=RuleRecoverability.NON_RECOVERABLE,
        description="Whether violation can be recovered from"
    )
    severity: RuleSeverity = Field(
        default=RuleSeverity.HARD_FAIL,
        description="Severity of violation"
    )
    rule_type: RuleType = Field(
        default=RuleType.OBJECTIVE,
        description="Type of rule"
    )
    recovery_path: Optional[str] = Field(
        default=None,
        description="How to recover if violated (if recoverable)"
    )
