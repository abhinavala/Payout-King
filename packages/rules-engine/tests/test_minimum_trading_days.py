"""
Unit tests for Minimum Trading Days rule.

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
    MinimumTradingDaysRule,
    RuleStatus,
    RuleRecoverability,
    RuleSeverity,
)


def test_apex_minimum_trading_days_requirement_met():
    """
    Validation Scenario 1: Requirement Met (Apex - 1 day)
    
    Setup:
    - Account start date: 2024-01-01
    - Current date: 2024-01-05
    - Trading days count: 2 (traded on Jan 2 and Jan 4)
    - Requirement: 1 day
    
    Expected: Status SAFE, requirement met
    """
    rules = FirmRules(
        minimum_trading_days=MinimumTradingDaysRule(
            enabled=True,
            min_days=1,  # Apex requires 1 day
            min_profit_per_day=Decimal("0"),  # Any closed trade counts
            recoverable=RuleRecoverability.RECOVERABLE,
            severity=RuleSeverity.HARD_FAIL,
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="apex-eval-min-days-1",
        timestamp=datetime.now(),
        equity=Decimal("50000"),
        balance=Decimal("50000"),
        high_water_mark=Decimal("50000"),
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("0"),
        unrealized_pnl=Decimal("0"),
        daily_pnl_history={
            "2024-01-02": Decimal("100"),  # Day 1 with trades
            "2024-01-04": Decimal("200"),  # Day 2 with trades
        },
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["minimum_trading_days"]

    # Trading days counted = 2 (both days have PnL >= min_profit_per_day = 0)
    assert rule_state.current_value == Decimal("2")
    # Remaining days = 1 - 2 = 0 (requirement met)
    assert rule_state.remaining_buffer == Decimal("0")
    assert rule_state.status == RuleStatus.SAFE  # Requirement met


def test_topstep_minimum_trading_days_requirement_met():
    """
    Validation Scenario 1: Requirement Met (Topstep - 2 days)
    
    Setup:
    - Account start date: 2024-01-01
    - Current date: 2024-01-05
    - Trading days count: 3 (traded on Jan 2, Jan 3, and Jan 4)
    - Requirement: 2 days
    
    Expected: Status SAFE, requirement met
    """
    rules = FirmRules(
        minimum_trading_days=MinimumTradingDaysRule(
            enabled=True,
            min_days=2,  # Topstep requires 2 days
            min_profit_per_day=Decimal("0"),  # Any closed trade counts
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-min-days-1",
        timestamp=datetime.now(),
        equity=Decimal("50000"),
        balance=Decimal("50000"),
        high_water_mark=Decimal("50000"),
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("0"),
        unrealized_pnl=Decimal("0"),
        daily_pnl_history={
            "2024-01-02": Decimal("100"),  # Day 1
            "2024-01-03": Decimal("200"),  # Day 2
            "2024-01-04": Decimal("150"),  # Day 3
        },
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["minimum_trading_days"]

    # Trading days counted = 3
    assert rule_state.current_value == Decimal("3")
    # Remaining days = 2 - 3 = 0 (requirement met)
    assert rule_state.remaining_buffer == Decimal("0")
    assert rule_state.status == RuleStatus.SAFE


def test_minimum_trading_days_partially_met():
    """
    Validation Scenario 2: Partially Met (Topstep)
    
    Setup:
    - Account start date: 2024-01-01
    - Current date: 2024-01-03
    - Trading days count: 1 (traded on Jan 2 only)
    - Requirement: 2 days
    
    Expected: Status CAUTION, 1 day remaining
    """
    rules = FirmRules(
        minimum_trading_days=MinimumTradingDaysRule(
            enabled=True,
            min_days=2,
            min_profit_per_day=Decimal("0"),
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-min-days-2",
        timestamp=datetime.now(),
        equity=Decimal("50000"),
        balance=Decimal("50000"),
        high_water_mark=Decimal("50000"),
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("0"),
        unrealized_pnl=Decimal("0"),
        daily_pnl_history={
            "2024-01-02": Decimal("100"),  # Only 1 day
        },
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["minimum_trading_days"]

    # Trading days counted = 1
    assert rule_state.current_value == Decimal("1")
    # Remaining days = 2 - 1 = 1
    assert rule_state.remaining_buffer == Decimal("1")
    assert rule_state.status == RuleStatus.CAUTION  # Close to requirement


def test_minimum_trading_days_not_met():
    """
    Validation Scenario 3: Not Met (New Account)
    
    Setup:
    - Account start date: 2024-01-01
    - Current date: 2024-01-01 (same day)
    - Trading days count: 0
    
    Expected: Status CAUTION, 2 days remaining
    """
    rules = FirmRules(
        minimum_trading_days=MinimumTradingDaysRule(
            enabled=True,
            min_days=2,
            min_profit_per_day=Decimal("0"),
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-min-days-3",
        timestamp=datetime.now(),
        equity=Decimal("50000"),
        balance=Decimal("50000"),
        high_water_mark=Decimal("50000"),
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("0"),
        unrealized_pnl=Decimal("0"),
        daily_pnl_history={},  # No trading days yet
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["minimum_trading_days"]

    # Trading days counted = 0
    assert rule_state.current_value == Decimal("0")
    # Remaining days = 2 - 0 = 2
    assert rule_state.remaining_buffer == Decimal("2")
    assert rule_state.status == RuleStatus.CAUTION


def test_minimum_trading_days_with_min_profit_requirement():
    """
    Test minimum profit per day requirement
    
    Setup:
    - Requirement: 2 days, min $50 profit per day
    - Day 1: +$100 (meets requirement)
    - Day 2: +$30 (does NOT meet requirement)
    
    Expected: Only 1 day counted
    """
    rules = FirmRules(
        minimum_trading_days=MinimumTradingDaysRule(
            enabled=True,
            min_days=2,
            min_profit_per_day=Decimal("50"),  # Must make at least $50 per day
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-min-days-profit",
        timestamp=datetime.now(),
        equity=Decimal("50130"),
        balance=Decimal("50130"),
        high_water_mark=Decimal("50130"),
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("130"),
        unrealized_pnl=Decimal("0"),
        daily_pnl_history={
            "2024-01-02": Decimal("100"),  # Meets $50 requirement
            "2024-01-03": Decimal("30"),  # Does NOT meet $50 requirement
        },
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["minimum_trading_days"]

    # Only day 1 counts (day 2 has $30 < $50 minimum)
    assert rule_state.current_value == Decimal("1")
    # Remaining days = 2 - 1 = 1
    assert rule_state.remaining_buffer == Decimal("1")
    assert rule_state.status == RuleStatus.CAUTION


def test_minimum_trading_days_no_history():
    """
    Edge Case: No daily PnL history provided
    
    Expected: Placeholder state with warning
    """
    rules = FirmRules(
        minimum_trading_days=MinimumTradingDaysRule(
            enabled=True,
            min_days=2,
            min_profit_per_day=Decimal("0"),
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-min-days-no-history",
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
    rule_state = result.rule_states["minimum_trading_days"]

    # Should return placeholder state
    assert rule_state.status == RuleStatus.CAUTION
    assert "Daily PnL history required" in rule_state.warnings[0]


def test_minimum_trading_days_loss_days_dont_count():
    """
    Edge Case: Loss days don't count if they don't meet minimum profit
    
    Setup:
    - Requirement: 2 days, min $50 profit per day
    - Day 1: -$100 (loss, doesn't meet $50 profit requirement)
    - Day 2: +$200 (profit, meets requirement)
    
    Expected: Only 1 day counted
    """
    rules = FirmRules(
        minimum_trading_days=MinimumTradingDaysRule(
            enabled=True,
            min_days=2,
            min_profit_per_day=Decimal("50"),
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="topstep-eval-min-days-loss",
        timestamp=datetime.now(),
        equity=Decimal("50100"),
        balance=Decimal("50100"),
        high_water_mark=Decimal("50100"),
        starting_balance=Decimal("50000"),
        realized_pnl=Decimal("100"),  # Net: -100 + 200 = 100
        unrealized_pnl=Decimal("0"),
        daily_pnl_history={
            "2024-01-02": Decimal("-100"),  # Loss, doesn't meet $50 profit requirement
            "2024-01-03": Decimal("200"),  # Profit, meets requirement
        },
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["minimum_trading_days"]

    # Only day 2 counts (day 1 is a loss, doesn't meet $50 profit requirement)
    assert rule_state.current_value == Decimal("1")
    # Remaining days = 2 - 1 = 1
    assert rule_state.remaining_buffer == Decimal("1")
