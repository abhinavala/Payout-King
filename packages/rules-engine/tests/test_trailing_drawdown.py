"""
Unit tests for trailing drawdown calculations.

These tests are CRITICAL - rule math must be exact.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from rules_engine.engine import RuleEngine
from rules_engine.interface import AccountSnapshot
from rules_engine.models import (
    FirmRules,
    TrailingDrawdownRule,
    DailyLossLimitRule,
    RuleStatus,
)


def test_trailing_drawdown_safe():
    """Test trailing drawdown when account is safe."""
    rules = FirmRules(
        trailing_drawdown=TrailingDrawdownRule(
            enabled=True,
            max_drawdown_percent=Decimal("5"),  # 5% max drawdown
            include_unrealized_pnl=True,
        )
    )
    engine = RuleEngine(rules)

    # Account with $10,000 starting, high water mark at $10,500, current equity $10,200
    account_state = AccountSnapshot(
        account_id="test-1",
        timestamp=datetime.now(),
        equity=Decimal("10200"),
        balance=Decimal("10200"),
        high_water_mark=Decimal("10500"),
        starting_balance=Decimal("10000"),
    )

    rule_state = engine._calculate_trailing_drawdown(account_state)

    assert rule_state.status == RuleStatus.SAFE
    assert rule_state.current_value == Decimal("10200")
    # Threshold = 10500 - (10500 * 0.05) = 9975
    assert rule_state.threshold == Decimal("9975")
    # Remaining buffer = 10200 - 9975 = 225
    assert rule_state.remaining_buffer == Decimal("225")
    assert rule_state.buffer_percent > Decimal("30")


def test_trailing_drawdown_critical():
    """Test trailing drawdown when account is critical."""
    rules = FirmRules(
        trailing_drawdown=TrailingDrawdownRule(
            enabled=True,
            max_drawdown_percent=Decimal("5"),
            include_unrealized_pnl=True,
        )
    )
    engine = RuleEngine(rules)

    # High water mark at $10,000, current equity at $9,510 (only $10 above threshold)
    account_state = AccountSnapshot(
        account_id="test-2",
        timestamp=datetime.now(),
        equity=Decimal("9510"),
        balance=Decimal("9510"),
        high_water_mark=Decimal("10000"),
        starting_balance=Decimal("10000"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["trailing_drawdown"]

    # Threshold = 9500, current = 9510, remaining = 10
    # buffer_percent = (10 / 500) * 100 = 2%, which is <= 10%, so CRITICAL
    assert rule_state.status == RuleStatus.CRITICAL
    assert rule_state.remaining_buffer == Decimal("10")
    assert rule_state.buffer_percent <= Decimal("10")


def test_trailing_drawdown_violated():
    """Test trailing drawdown when account has violated the rule."""
    rules = FirmRules(
        trailing_drawdown=TrailingDrawdownRule(
            enabled=True,
            max_drawdown_percent=Decimal("5"),
            include_unrealized_pnl=True,
        )
    )
    engine = RuleEngine(rules)

    # Current equity below threshold
    account_state = AccountSnapshot(
        account_id="test-3",
        timestamp=datetime.now(),
        equity=Decimal("9400"),
        balance=Decimal("9400"),
        high_water_mark=Decimal("10000"),
        starting_balance=Decimal("10000"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["trailing_drawdown"]

    assert rule_state.status == RuleStatus.VIOLATED
    assert rule_state.remaining_buffer < 0


def test_trailing_drawdown_without_unrealized():
    """Test trailing drawdown using balance instead of equity."""
    rules = FirmRules(
        trailing_drawdown=TrailingDrawdownRule(
            enabled=True,
            max_drawdown_percent=Decimal("5"),
            include_unrealized_pnl=False,  # Use balance, not equity
        )
    )
    engine = RuleEngine(rules)

    # Equity is lower due to unrealized loss, but balance is higher
    account_state = AccountSnapshot(
        account_id="test-4",
        timestamp=datetime.now(),
        equity=Decimal("9800"),  # Lower due to unrealized loss
        balance=Decimal("10000"),  # Balance is still at starting
        high_water_mark=Decimal("10000"),
        starting_balance=Decimal("10000"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["trailing_drawdown"]

    # Should use balance (10000) not equity (9800)
    assert rule_state.current_value == Decimal("10000")
    assert rule_state.status == RuleStatus.SAFE


def test_daily_loss_limit_safe():
    """Test daily loss limit when safe."""
    rules = FirmRules(
        daily_loss_limit=DailyLossLimitRule(
            enabled=True,
            max_loss_amount=Decimal("500"),  # $500 max daily loss
            reset_time="17:00",
            timezone="America/Chicago",
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="test-5",
        timestamp=datetime.now(),
        equity=Decimal("10000"),
        balance=Decimal("10000"),
        high_water_mark=Decimal("10000"),
        daily_pnl=Decimal("-100"),  # Lost $100 today
        starting_balance=Decimal("10000"),
    )

    rule_state = engine._calculate_daily_loss_limit(account_state)

    assert rule_state.status == RuleStatus.SAFE
    assert rule_state.current_value == Decimal("100")  # Daily loss
    assert rule_state.remaining_buffer == Decimal("400")  # $500 - $100
    assert rule_state.buffer_percent > Decimal("30")


def test_daily_loss_limit_critical():
    """Test daily loss limit when critical."""
    rules = FirmRules(
        daily_loss_limit=DailyLossLimitRule(
            enabled=True,
            max_loss_amount=Decimal("500"),
            reset_time="17:00",
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="test-6",
        timestamp=datetime.now(),
        equity=Decimal("10000"),
        balance=Decimal("10000"),
        high_water_mark=Decimal("10000"),
        daily_pnl=Decimal("-450"),  # Lost $450 today, only $50 remaining
        starting_balance=Decimal("10000"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["daily_loss_limit"]

    assert rule_state.status == RuleStatus.CRITICAL
    assert rule_state.remaining_buffer == Decimal("50")
    assert rule_state.buffer_percent <= Decimal("10")  # 50/500 = 10%


def test_daily_loss_limit_violated():
    """Test daily loss limit when violated."""
    rules = FirmRules(
        daily_loss_limit=DailyLossLimitRule(
            enabled=True,
            max_loss_amount=Decimal("500"),
            reset_time="17:00",
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="test-7",
        timestamp=datetime.now(),
        equity=Decimal("10000"),
        balance=Decimal("10000"),
        high_water_mark=Decimal("10000"),
        daily_pnl=Decimal("-600"),  # Lost $600, exceeded limit
        starting_balance=Decimal("10000"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["daily_loss_limit"]

    assert rule_state.status == RuleStatus.VIOLATED
    assert rule_state.remaining_buffer < 0


def test_max_allowed_risk_calculation():
    """Test calculation of maximum allowed risk."""
    rules = FirmRules(
        trailing_drawdown=TrailingDrawdownRule(
            enabled=True,
            max_drawdown_percent=Decimal("5"),
            include_unrealized_pnl=True,
        ),
        daily_loss_limit=DailyLossLimitRule(
            enabled=True,
            max_loss_amount=Decimal("500"),
            reset_time="17:00",
        ),
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="test-8",
        timestamp=datetime.now(),
        equity=Decimal("10000"),
        balance=Decimal("10000"),
        high_water_mark=Decimal("10000"),
        daily_pnl=Decimal("-200"),
        starting_balance=Decimal("10000"),
    )

    result = engine.evaluate(account_state)
    max_allowed = result.max_allowed_risk

    # Max loss should be the minimum of trailing DD buffer and daily loss buffer
    assert "max_loss_allowed" in max_allowed
    # Trailing DD buffer = $500 (5% of $10,000)
    # Daily loss buffer = $300 ($500 - $200)
    # So max_loss_allowed should be $300 (the smaller one)
    assert max_allowed["max_loss_allowed"] == Decimal("300")

