"""
Unit tests for Topstep Consistency Rule.

These tests match the exact validation scenarios from the rule specification.
Tests are CRITICAL - rule math must be exact.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from rules_engine.engine import RuleEngine
from rules_engine.interface import AccountSnapshot
from rules_engine.models import (
    FirmRules,
    ConsistencyRule,
    RuleStatus,
    RuleRecoverability,
    RuleSeverity,
)


def test_consistency_rule_safe_scenario():
    """
    Validation Scenario 1: Safe Case
    
    Setup:
    - Day 1: +$300
    - Day 2: +$400
    - Day 3: +$300
    - Total realized PnL: $1,000
    - Max single-day profit: $400
    - Percentage: 40%
    
    Expected: Status SAFE, distance $100, requirement met
    """
    rules = FirmRules(
        consistency_rule=ConsistencyRule(
            enabled=True,
            max_single_day_percent=Decimal("50"),  # 50% max
            recoverable=RuleRecoverability.RECOVERABLE,
            severity=RuleSeverity.PAYOUT_BLOCK,
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-consistency-1",
        timestamp=datetime.now(),
        equity=Decimal("51000"),
        balance=Decimal("51000"),
        high_water_mark=Decimal("51000"),
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("1000"),  # Total profit
        unrealized_pnl=Decimal("0"),
        daily_pnl_history={
            "2024-01-01": Decimal("300"),  # Day 1
            "2024-01-02": Decimal("400"),  # Day 2 (max)
            "2024-01-03": Decimal("300"),  # Day 3
        },
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["consistency"]

    # Max single day = $400
    # Total = $1,000
    # Percentage = 400 / 1000 * 100 = 40%
    # Max allowed = 50% of $1,000 = $500
    # Distance = $500 - $400 = $100
    assert rule_state.current_value == Decimal("40")  # 40%
    assert rule_state.threshold == Decimal("50")  # 50% threshold
    assert rule_state.remaining_buffer == Decimal("100")  # $100 buffer
    assert rule_state.status == RuleStatus.SAFE  # 40% <= 40% threshold for SAFE


def test_consistency_rule_boundary_scenario():
    """
    Validation Scenario 2: Boundary Case
    
    Setup:
    - Day 1: +$500
    - Day 2: +$300
    - Day 3: +$200
    - Total realized PnL: $1,000
    - Max single-day profit: $500
    - Percentage: 50%
    
    Expected: Status SAFE (50% is allowed, violation is > 50%), distance $0
    """
    rules = FirmRules(
        consistency_rule=ConsistencyRule(
            enabled=True,
            max_single_day_percent=Decimal("50"),
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-consistency-2",
        timestamp=datetime.now(),
        equity=Decimal("51000"),
        balance=Decimal("51000"),
        high_water_mark=Decimal("51000"),
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("1000"),
        unrealized_pnl=Decimal("0"),
        daily_pnl_history={
            "2024-01-01": Decimal("500"),  # Day 1 (max, exactly 50%)
            "2024-01-02": Decimal("300"),
            "2024-01-03": Decimal("200"),
        },
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["consistency"]

    # Max single day = $500
    # Total = $1,000
    # Percentage = 500 / 1000 * 100 = 50%
    # Max allowed = 50% of $1,000 = $500
    # Distance = $500 - $500 = $0
    assert rule_state.current_value == Decimal("50")  # 50%
    assert rule_state.remaining_buffer == Decimal("0")  # At the limit
    assert rule_state.status == RuleStatus.SAFE  # Exactly 50% is allowed (not > 50%)


def test_consistency_rule_violation_scenario():
    """
    Validation Scenario 3: Violation Case
    
    Setup:
    - Day 1: +$600
    - Day 2: +$200
    - Day 3: +$200
    - Total realized PnL: $1,000
    - Max single-day profit: $600
    - Percentage: 60%
    
    Expected: Status VIOLATED, distance -$100
    """
    rules = FirmRules(
        consistency_rule=ConsistencyRule(
            enabled=True,
            max_single_day_percent=Decimal("50"),
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-consistency-3",
        timestamp=datetime.now(),
        equity=Decimal("51000"),
        balance=Decimal("51000"),
        high_water_mark=Decimal("51000"),
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("1000"),
        unrealized_pnl=Decimal("0"),
        daily_pnl_history={
            "2024-01-01": Decimal("600"),  # Day 1 (max, 60% of total)
            "2024-01-02": Decimal("200"),
            "2024-01-03": Decimal("200"),
        },
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["consistency"]

    # Max single day = $600
    # Total = $1,000
    # Percentage = 600 / 1000 * 100 = 60%
    # Max allowed = 50% of $1,000 = $500
    # Distance = $500 - $600 = -$100 (violation)
    assert rule_state.current_value == Decimal("60")  # 60%
    assert rule_state.remaining_buffer == Decimal("-100")  # Negative = violation
    assert rule_state.status == RuleStatus.VIOLATED  # 60% > 50%


def test_consistency_rule_recovery_scenario():
    """
    Validation Scenario 4: Recovery Case
    
    Setup:
    - Initial: Day 1: +$600, Day 2: +$200, Day 3: +$200 (Total: $1,000, Max: $600, 60% - VIOLATED)
    - Add Day 4: +$300
    
    Expected: New total $1,300, max day $600, new percentage 46.2%, status CRITICAL → CAUTION
    """
    rules = FirmRules(
        consistency_rule=ConsistencyRule(
            enabled=True,
            max_single_day_percent=Decimal("50"),
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-consistency-4",
        timestamp=datetime.now(),
        equity=Decimal("51300"),
        balance=Decimal("51300"),
        high_water_mark=Decimal("51300"),
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("1300"),  # New total after Day 4
        unrealized_pnl=Decimal("0"),
        daily_pnl_history={
            "2024-01-01": Decimal("600"),  # Day 1 (max)
            "2024-01-02": Decimal("200"),
            "2024-01-03": Decimal("200"),
            "2024-01-04": Decimal("300"),  # Added day
        },
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["consistency"]

    # Max single day = $600
    # Total = $1,300
    # Percentage = 600 / 1300 * 100 = 46.15% (approximately)
    # Max allowed = 50% of $1,300 = $650
    # Distance = $650 - $600 = $50
    # Status should be CRITICAL (45% < 46.15% <= 50%)
    assert rule_state.current_value > Decimal("45")  # Between 45% and 50%
    assert rule_state.current_value <= Decimal("50")
    assert rule_state.remaining_buffer > Decimal("0")  # Positive buffer
    assert rule_state.status == RuleStatus.CRITICAL  # Between 45% and 50%


def test_consistency_rule_negative_total():
    """
    Edge Case: Total PnL is negative
    
    Expected: Rule doesn't apply, status SAFE
    """
    rules = FirmRules(
        consistency_rule=ConsistencyRule(
            enabled=True,
            max_single_day_percent=Decimal("50"),
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-consistency-negative",
        timestamp=datetime.now(),
        equity=Decimal("48000"),
        balance=Decimal("48000"),
        high_water_mark=Decimal("50000"),
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("-2000"),  # Negative total
        unrealized_pnl=Decimal("0"),
        daily_pnl_history={
            "2024-01-01": Decimal("-500"),
            "2024-01-02": Decimal("-1500"),
        },
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["consistency"]

    # Rule doesn't apply when total <= 0
    assert rule_state.status == RuleStatus.SAFE
    assert rule_state.current_value == Decimal("0")
    assert len(rule_state.warnings) == 0  # No warnings when rule doesn't apply


def test_consistency_rule_no_history():
    """
    Edge Case: No daily PnL history provided
    
    Expected: Placeholder state with warning
    """
    rules = FirmRules(
        consistency_rule=ConsistencyRule(
            enabled=True,
            max_single_day_percent=Decimal("50"),
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-consistency-no-history",
        timestamp=datetime.now(),
        equity=Decimal("50000"),
        balance=Decimal("50000"),
        high_water_mark=Decimal("50000"),
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("0"),
        unrealized_pnl=Decimal("0"),
        daily_pnl_history=None,  # No history
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["consistency"]

    # Should return placeholder state
    assert rule_state.status == RuleStatus.SAFE  # Placeholder assumes safe
    assert "Daily PnL history required" in rule_state.warnings[0]
