"""
Unit tests for Topstep Daily Loss Limit rule.

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
    DailyLossLimitRule,
    RuleStatus,
    RuleRecoverability,
    RuleSeverity,
)


def test_topstep_daily_loss_limit_safe_scenario():
    """
    Validation Scenario 1: Safe Case
    
    Setup:
    - Account size: $50,000
    - Daily loss limit: $1,000
    - Daily starting balance: $50,000
    - Daily realized PnL: -$300
    - Current balance: $49,700
    - Daily loss: $300
    
    Expected: Status SAFE, distance $700, buffer 70% remaining
    """
    rules = FirmRules(
        daily_loss_limit=DailyLossLimitRule(
            enabled=True,
            max_loss_amount=Decimal("1000"),  # $1,000 daily loss limit
            reset_time="16:00",  # 4:00 PM CT
            timezone="America/Chicago",
            recoverable=RuleRecoverability.NON_RECOVERABLE,
            severity=RuleSeverity.HARD_FAIL,
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-1",
        timestamp=datetime.now(),
        equity=Decimal("49700"),
        balance=Decimal("49700"),
        high_water_mark=Decimal("50000"),
        starting_balance=Decimal("50000"),
        daily_pnl=Decimal("-300"),  # Lost $300 today
        realized_pnl=Decimal("-300"),
        unrealized_pnl=Decimal("0"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["daily_loss_limit"]

    # Daily loss = $300
    assert rule_state.current_value == Decimal("300")
    # Remaining buffer = $1,000 - $300 = $700
    assert rule_state.remaining_buffer == Decimal("700")
    # Status should be SAFE (loss $300 < 80% of $1,000 = $800)
    assert rule_state.status == RuleStatus.SAFE
    # Buffer percent = (700 / 1000) * 100 = 70%
    assert rule_state.buffer_percent == Decimal("70")


def test_topstep_daily_loss_limit_boundary_scenario():
    """
    Validation Scenario 2: Boundary Case
    
    Setup:
    - Account size: $50,000
    - Daily loss limit: $1,000
    - Daily starting balance: $51,000 (had profit from previous day)
    - Daily realized PnL: -$950
    - Current balance: $50,050
    - Daily loss: $950
    
    Expected: Status CRITICAL, distance $50, buffer 5% remaining
    """
    rules = FirmRules(
        daily_loss_limit=DailyLossLimitRule(
            enabled=True,
            max_loss_amount=Decimal("1000"),
            reset_time="16:00",
            timezone="America/Chicago",
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-2",
        timestamp=datetime.now(),
        equity=Decimal("50050"),
        balance=Decimal("50050"),
        high_water_mark=Decimal("51000"),
        starting_balance=Decimal("50000"),
        daily_pnl=Decimal("-950"),  # Lost $950 today
        realized_pnl=Decimal("-950"),
        unrealized_pnl=Decimal("0"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["daily_loss_limit"]

    # Daily loss = $950
    assert rule_state.current_value == Decimal("950")
    # Remaining buffer = $1,000 - $950 = $50
    assert rule_state.remaining_buffer == Decimal("50")
    # Status should be CRITICAL (loss $950 >= 95% of $1,000 = $950)
    assert rule_state.status == RuleStatus.CRITICAL
    # Buffer percent = (50 / 1000) * 100 = 5%
    assert rule_state.buffer_percent == Decimal("5")


def test_topstep_daily_loss_limit_violation_scenario():
    """
    Validation Scenario 3: Violation Case
    
    Setup:
    - Account size: $50,000
    - Daily loss limit: $1,000
    - Daily starting balance: $50,000
    - Daily realized PnL: -$1,200
    - Current balance: $48,800
    - Daily loss: $1,200
    
    Expected: Status VIOLATED, distance -$200
    """
    rules = FirmRules(
        daily_loss_limit=DailyLossLimitRule(
            enabled=True,
            max_loss_amount=Decimal("1000"),
            reset_time="16:00",
            timezone="America/Chicago",
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-3",
        timestamp=datetime.now(),
        equity=Decimal("48800"),
        balance=Decimal("48800"),
        high_water_mark=Decimal("50000"),
        starting_balance=Decimal("50000"),
        daily_pnl=Decimal("-1200"),  # Lost $1,200 today, exceeded limit
        realized_pnl=Decimal("-1200"),
        unrealized_pnl=Decimal("0"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["daily_loss_limit"]

    # Daily loss = $1,200
    assert rule_state.current_value == Decimal("1200")
    # Remaining buffer = $1,000 - $1,200 = -$200 (negative = violation)
    assert rule_state.remaining_buffer == Decimal("-200")
    assert rule_state.status == RuleStatus.VIOLATED


def test_topstep_daily_loss_limit_exact_limit():
    """
    Edge Case: Daily loss exactly equals limit
    
    Expected: VIOLATED (daily_loss >= limit means violation)
    """
    rules = FirmRules(
        daily_loss_limit=DailyLossLimitRule(
            enabled=True,
            max_loss_amount=Decimal("1000"),
            reset_time="16:00",
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-exact",
        timestamp=datetime.now(),
        equity=Decimal("49000"),
        balance=Decimal("49000"),
        high_water_mark=Decimal("50000"),
        starting_balance=Decimal("50000"),
        daily_pnl=Decimal("-1000"),  # Exactly at limit
        realized_pnl=Decimal("-1000"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["daily_loss_limit"]

    assert rule_state.current_value == Decimal("1000")
    assert rule_state.remaining_buffer == Decimal("0")
    assert rule_state.status == RuleStatus.VIOLATED  # >= limit is violation


def test_topstep_daily_loss_limit_profitable_then_losing():
    """
    Validation Scenario 5: Profitable Then Losing
    
    Setup:
    - Daily starting balance: $50,000
    - Trade 1: +$500 (daily PnL: +$500)
    - Trade 2: -$1,200 (daily PnL: -$700)
    - Current balance: $49,300
    
    Expected: Net daily loss $700, status SAFE
    """
    rules = FirmRules(
        daily_loss_limit=DailyLossLimitRule(
            enabled=True,
            max_loss_amount=Decimal("1000"),
            reset_time="16:00",
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-profitable-then-losing",
        timestamp=datetime.now(),
        equity=Decimal("49300"),
        balance=Decimal("49300"),
        high_water_mark=Decimal("50000"),
        starting_balance=Decimal("50000"),
        daily_pnl=Decimal("-700"),  # Net daily loss: -$700
        realized_pnl=Decimal("-700"),
        unrealized_pnl=Decimal("0"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["daily_loss_limit"]

    # Daily loss = $700
    assert rule_state.current_value == Decimal("700")
    # Remaining buffer = $1,000 - $700 = $300
    assert rule_state.remaining_buffer == Decimal("300")
    # Status should be SAFE (loss $700 < 80% of $1,000 = $800)
    assert rule_state.status == RuleStatus.SAFE


def test_topstep_daily_loss_limit_unrealized_loss_excluded():
    """
    Edge Case: Unrealized losses do not count
    
    Expected: Only realized PnL counts toward daily loss
    """
    rules = FirmRules(
        daily_loss_limit=DailyLossLimitRule(
            enabled=True,
            max_loss_amount=Decimal("1000"),
            reset_time="16:00",
        )
    )
    engine = RuleEngine(rules)

    # Account with open losing position
    account_state = AccountSnapshot(
        account_id="topstep-eval-unrealized",
        timestamp=datetime.now(),
        equity=Decimal("48000"),  # Balance - unrealized loss
        balance=Decimal("50000"),  # Balance hasn't changed (no realized PnL)
        high_water_mark=Decimal("50000"),
        starting_balance=Decimal("50000"),
        daily_pnl=Decimal("0"),  # No realized PnL today
        realized_pnl=Decimal("0"),
        unrealized_pnl=Decimal("-2000"),  # Open position losing $2000
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["daily_loss_limit"]

    # Daily loss should be $0 (unrealized doesn't count)
    assert rule_state.current_value == Decimal("0")
    # Remaining buffer = $1,000 - $0 = $1,000
    assert rule_state.remaining_buffer == Decimal("1000")
    assert rule_state.status == RuleStatus.SAFE


def test_topstep_daily_loss_limit_caution_threshold():
    """
    Test CAUTION status threshold (80% of limit)
    """
    rules = FirmRules(
        daily_loss_limit=DailyLossLimitRule(
            enabled=True,
            max_loss_amount=Decimal("1000"),
            reset_time="16:00",
        )
    )
    engine = RuleEngine(rules)

    # Exactly at 80% threshold
    account_state = AccountSnapshot(
        account_id="topstep-eval-caution",
        timestamp=datetime.now(),
        equity=Decimal("49200"),
        balance=Decimal("49200"),
        high_water_mark=Decimal("50000"),
        starting_balance=Decimal("50000"),
        daily_pnl=Decimal("-800"),  # Exactly 80% of limit
        realized_pnl=Decimal("-800"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["daily_loss_limit"]

    assert rule_state.current_value == Decimal("800")
    assert rule_state.status == RuleStatus.CAUTION  # 80% <= loss < 95%


def test_topstep_daily_loss_limit_critical_threshold():
    """
    Test CRITICAL status threshold (95% of limit)
    """
    rules = FirmRules(
        daily_loss_limit=DailyLossLimitRule(
            enabled=True,
            max_loss_amount=Decimal("1000"),
            reset_time="16:00",
        )
    )
    engine = RuleEngine(rules)

    # Exactly at 95% threshold
    account_state = AccountSnapshot(
        account_id="topstep-eval-critical",
        timestamp=datetime.now(),
        equity=Decimal("49050"),
        balance=Decimal("49050"),
        high_water_mark=Decimal("50000"),
        starting_balance=Decimal("50000"),
        daily_pnl=Decimal("-950"),  # Exactly 95% of limit
        realized_pnl=Decimal("-950"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["daily_loss_limit"]

    assert rule_state.current_value == Decimal("950")
    assert rule_state.status == RuleStatus.CRITICAL  # 95% <= loss < 100%
