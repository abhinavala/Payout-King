"""
Payout King Rules Engine

Core rule calculation logic for prop-firm compliance tracking.
"""

from .engine import RuleEngine
from .interface import AccountSnapshot, RuleEvaluationResult, PositionSnapshot
from .models import (
    FirmRules,
    RuleState,
    TrailingDrawdownRule,
    DailyLossLimitRule,
)

__all__ = [
    "RuleEngine",
    "AccountSnapshot",  # FROZEN INPUT INTERFACE
    "RuleEvaluationResult",  # FROZEN OUTPUT INTERFACE
    "PositionSnapshot",
    "FirmRules",
    "RuleState",
    "TrailingDrawdownRule",
    "DailyLossLimitRule",
]

