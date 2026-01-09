"""
Unit tests for Apex Trailing Drawdown rule.

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
    TrailingDrawdownRule,
    RuleStatus,
    RuleRecoverability,
    RuleSeverity,
)


def test_apex_trailing_drawdown_safe_scenario():
    """
    Validation Scenario 1: Safe Case
    
    Setup:
    - Starting balance: $50,000
    - High-water mark: $50,000 (no profit yet)
    - Current equity: $49,000
    - Threshold: $2,500 (5% of $50,000)
    - Min allowed equity: $47,500
    
    Expected: Status SAFE, distance $1,500
    """
    rules = FirmRules(
        trailing_drawdown=TrailingDrawdownRule(
            enabled=True,
            max_drawdown_percent=Decimal("5"),  # 5% max drawdown
            include_unrealized_pnl=True,
            recoverable=RuleRecoverability.NON_RECOVERABLE,
            severity=RuleSeverity.HARD_FAIL,
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="apex-eval-1",
        timestamp=datetime.now(),
        equity=Decimal("49000"),  # Current equity
        balance=Decimal("49000"),
        high_water_mark=Decimal("50000"),  # HWM = starting balance
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("-1000"),
        unrealized_pnl=Decimal("0"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["trailing_drawdown"]

    # Threshold = 50000 - (50000 * 0.05) = 50000 - 2500 = 47500
    assert rule_state.threshold == Decimal("47500")
    # Remaining buffer = 49000 - 47500 = 1500
    assert rule_state.remaining_buffer == Decimal("1500")
    # Status should be SAFE (more than 20% buffer: 1500 > 2500 * 0.20 = 500)
    assert rule_state.status == RuleStatus.SAFE
    assert rule_state.current_value == Decimal("49000")


def test_apex_trailing_drawdown_boundary_scenario():
    """
    Validation Scenario 2: Boundary Case
    
    Setup:
    - Starting balance: $50,000
    - High-water mark: $52,500 (reached after $2,500 profit)
    - Current equity: $50,000
    - Threshold: $2,625 (5% of $52,500)
    - Min allowed equity: $49,875
    
    Expected: Status CRITICAL, distance $125 (5% buffer)
    """
    rules = FirmRules(
        trailing_drawdown=TrailingDrawdownRule(
            enabled=True,
            max_drawdown_percent=Decimal("5"),
            include_unrealized_pnl=True,
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="apex-eval-2",
        timestamp=datetime.now(),
        equity=Decimal("50000"),
        balance=Decimal("50000"),
        high_water_mark=Decimal("52500"),  # HWM increased after profit
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("0"),
        unrealized_pnl=Decimal("0"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["trailing_drawdown"]

    # Threshold = 52500 - (52500 * 0.05) = 52500 - 2625 = 49875
    assert rule_state.threshold == Decimal("49875")
    # Remaining buffer = 50000 - 49875 = 125
    assert rule_state.remaining_buffer == Decimal("125")
    # Status should be CRITICAL (within 5% of threshold: 125 <= 2625 * 0.05 = 131.25)
    assert rule_state.status == RuleStatus.CRITICAL
    assert rule_state.current_value == Decimal("50000")


def test_apex_trailing_drawdown_violation_scenario():
    """
    Validation Scenario 3: Violation Case
    
    Setup:
    - Starting balance: $50,000
    - High-water mark: $52,500
    - Current equity: $49,800
    - Threshold: $2,625
    - Min allowed equity: $49,875
    
    Expected: Status VIOLATED, distance -$75
    """
    rules = FirmRules(
        trailing_drawdown=TrailingDrawdownRule(
            enabled=True,
            max_drawdown_percent=Decimal("5"),
            include_unrealized_pnl=True,
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="apex-eval-3",
        timestamp=datetime.now(),
        equity=Decimal("49800"),  # Below threshold
        balance=Decimal("49800"),
        high_water_mark=Decimal("52500"),
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("-200"),
        unrealized_pnl=Decimal("0"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["trailing_drawdown"]

    # Threshold = 49875
    assert rule_state.threshold == Decimal("49875")
    # Remaining buffer = 49800 - 49875 = -75 (negative = violation)
    assert rule_state.remaining_buffer == Decimal("-75")
    assert rule_state.status == RuleStatus.VIOLATED
    assert rule_state.current_value == Decimal("49800")


def test_apex_trailing_drawdown_hwm_update_during_trade():
    """
    Validation Scenario 4: HWM Update During Trade
    
    Setup:
    - Starting balance: $50,000
    - High-water mark: $50,000
    - Current equity: $51,000 (open position with +$1,000 unrealized)
    
    Expected: HWM updates to $51,000, new threshold $2,550, status SAFE
    """
    rules = FirmRules(
        trailing_drawdown=TrailingDrawdownRule(
            enabled=True,
            max_drawdown_percent=Decimal("5"),
            include_unrealized_pnl=True,
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="apex-eval-4",
        timestamp=datetime.now(),
        equity=Decimal("51000"),  # Equity exceeds HWM
        balance=Decimal("50000"),
        high_water_mark=Decimal("50000"),  # Will be updated by caller
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("0"),
        unrealized_pnl=Decimal("1000"),  # Open position profit
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["trailing_drawdown"]

    # Note: HWM update happens outside the rule engine (in state tracker)
    # Rule engine uses the HWM provided in snapshot
    # If HWM were updated to 51000, new threshold would be 51000 - 2550 = 48450
    # For this test, HWM is still 50000, so threshold is 47500
    # But equity 51000 > 47500, so SAFE
    
    # Current calculation with HWM=50000:
    assert rule_state.threshold == Decimal("47500")
    assert rule_state.remaining_buffer == Decimal("3500")  # 51000 - 47500
    assert rule_state.status == RuleStatus.SAFE
    
    # If HWM were updated to 51000 (simulate by changing input):
    account_state_updated = AccountSnapshot(
        account_id="apex-eval-4-updated",
        timestamp=datetime.now(),
        equity=Decimal("51000"),
        balance=Decimal("50000"),
        high_water_mark=Decimal("51000"),  # Updated HWM
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("0"),
        unrealized_pnl=Decimal("1000"),
    )
    
    result_updated = engine.evaluate(account_state_updated)
    rule_state_updated = result_updated.rule_states["trailing_drawdown"]
    
    # New threshold = 51000 - (51000 * 0.05) = 51000 - 2550 = 48450
    assert rule_state_updated.threshold == Decimal("48450")
    # Remaining buffer = 51000 - 48450 = 2550
    assert rule_state_updated.remaining_buffer == Decimal("2550")
    assert rule_state_updated.status == RuleStatus.SAFE


def test_apex_trailing_drawdown_exact_threshold():
    """
    Edge Case: Equity exactly equals threshold
    
    Expected: VIOLATED (equity <= threshold means violation)
    """
    rules = FirmRules(
        trailing_drawdown=TrailingDrawdownRule(
            enabled=True,
            max_drawdown_percent=Decimal("5"),
            include_unrealized_pnl=True,
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="apex-eval-exact",
        timestamp=datetime.now(),
        equity=Decimal("47500"),  # Exactly at threshold
        balance=Decimal("47500"),
        high_water_mark=Decimal("50000"),
        starting_balance=Decimal("50000"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["trailing_drawdown"]

    assert rule_state.threshold == Decimal("47500")
    assert rule_state.remaining_buffer == Decimal("0")
    assert rule_state.status == RuleStatus.VIOLATED  # <= threshold is violation


def test_apex_trailing_drawdown_with_unrealized_pnl():
    """
    Test that unrealized PnL is included in equity calculation
    """
    rules = FirmRules(
        trailing_drawdown=TrailingDrawdownRule(
            enabled=True,
            max_drawdown_percent=Decimal("5"),
            include_unrealized_pnl=True,  # Include unrealized
        )
    )
    engine = RuleEngine(rules)

    # Account with open losing position
    account_state = AccountSnapshot(
        account_id="apex-eval-unrealized",
        timestamp=datetime.now(),
        equity=Decimal("48000"),  # Balance - unrealized loss
        balance=Decimal("50000"),  # Balance hasn't changed
        high_water_mark=Decimal("50000"),
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("0"),
        unrealized_pnl=Decimal("-2000"),  # Open position losing $2000
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["trailing_drawdown"]

    # Should use equity (48000) not balance (50000)
    assert rule_state.current_value == Decimal("48000")
    # Threshold = 47500, buffer = 48000 - 47500 = 500
    assert rule_state.remaining_buffer == Decimal("500")
    assert rule_state.status == RuleStatus.CAUTION  # Within 20% of threshold (500 <= 2500 * 0.20 = 500)
