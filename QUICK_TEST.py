#!/usr/bin/env python3
"""
Quick Test Script - Test Rules Engine Without Dependencies

This script tests the rules engine without needing pytest or any setup.
Just run: python3 QUICK_TEST.py
"""

import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "rules-engine"))

from decimal import Decimal
from datetime import datetime
from rules_engine.engine import RuleEngine
from rules_engine.interface import AccountSnapshot
from rules_engine.models import FirmRules, TrailingDrawdownRule, DailyLossLimitRule, RuleStatus


def test_trailing_drawdown_safe():
    """Test trailing drawdown when account is safe."""
    print("🧪 Test 1: Trailing Drawdown - Safe")
    
    rules = FirmRules(
        trailing_drawdown=TrailingDrawdownRule(
            enabled=True,
            max_drawdown_percent=Decimal("5"),
            include_unrealized_pnl=True,
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="test-1",
        timestamp=datetime.now(),
        equity=Decimal("10200"),
        balance=Decimal("10200"),
        high_water_mark=Decimal("10500"),
        starting_balance=Decimal("10000"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["trailing_drawdown"]

    assert rule_state.status == RuleStatus.SAFE, f"Expected SAFE, got {rule_state.status}"
    assert rule_state.current_value == Decimal("10200"), f"Expected 10200, got {rule_state.current_value}"
    assert rule_state.threshold == Decimal("9975"), f"Expected 9975, got {rule_state.threshold}"
    assert rule_state.remaining_buffer == Decimal("225"), f"Expected 225, got {rule_state.remaining_buffer}"
    
    print("   ✅ PASS: Account is safe, buffer is $225")
    return True


def test_trailing_drawdown_critical():
    """Test trailing drawdown when account is critical."""
    print("\n🧪 Test 2: Trailing Drawdown - Critical")
    
    rules = FirmRules(
        trailing_drawdown=TrailingDrawdownRule(
            enabled=True,
            max_drawdown_percent=Decimal("5"),
            include_unrealized_pnl=True,
        )
    )
    engine = RuleEngine(rules)

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

    assert rule_state.status == RuleStatus.CRITICAL, f"Expected CRITICAL, got {rule_state.status}"
    assert rule_state.remaining_buffer == Decimal("10"), f"Expected 10, got {rule_state.remaining_buffer}"
    assert rule_state.buffer_percent <= Decimal("10"), f"Expected <= 10%, got {rule_state.buffer_percent}%"
    
    print(f"   ✅ PASS: Account is critical, only ${rule_state.remaining_buffer} remaining")
    return True


def test_trailing_drawdown_violated():
    """Test trailing drawdown when account has violated the rule."""
    print("\n🧪 Test 3: Trailing Drawdown - Violated")
    
    rules = FirmRules(
        trailing_drawdown=TrailingDrawdownRule(
            enabled=True,
            max_drawdown_percent=Decimal("5"),
            include_unrealized_pnl=True,
        )
    )
    engine = RuleEngine(rules)

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

    assert rule_state.status == RuleStatus.VIOLATED, f"Expected VIOLATED, got {rule_state.status}"
    assert rule_state.remaining_buffer < 0, f"Expected negative buffer, got {rule_state.remaining_buffer}"
    
    print(f"   ✅ PASS: Account has violated trailing drawdown")
    return True


def test_daily_loss_limit():
    """Test daily loss limit."""
    print("\n🧪 Test 4: Daily Loss Limit")
    
    rules = FirmRules(
        daily_loss_limit=DailyLossLimitRule(
            enabled=True,
            max_loss_amount=Decimal("500"),
            reset_time="17:00",
            timezone="America/Chicago",
        )
    )
    engine = RuleEngine(rules)

    account_state = AccountSnapshot(
        account_id="test-4",
        timestamp=datetime.now(),
        equity=Decimal("10000"),
        balance=Decimal("10000"),
        high_water_mark=Decimal("10000"),
        daily_pnl=Decimal("-450"),  # Lost $450 today, only $50 remaining
        starting_balance=Decimal("10000"),
    )

    result = engine.evaluate(account_state)
    rule_state = result.rule_states["daily_loss_limit"]

    assert rule_state.status == RuleStatus.CRITICAL, f"Expected CRITICAL, got {rule_state.status}"
    assert rule_state.remaining_buffer == Decimal("50"), f"Expected 50, got {rule_state.remaining_buffer}"
    
    print(f"   ✅ PASS: Daily loss limit critical, ${rule_state.remaining_buffer} remaining")
    return True


def test_max_allowed_risk():
    """Test calculation of maximum allowed risk."""
    print("\n🧪 Test 5: Max Allowed Risk Calculation")
    
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
        account_id="test-5",
        timestamp=datetime.now(),
        equity=Decimal("10000"),
        balance=Decimal("10000"),
        high_water_mark=Decimal("10000"),
        daily_pnl=Decimal("-200"),
        starting_balance=Decimal("10000"),
    )

    result = engine.evaluate(account_state)
    max_allowed = result.max_allowed_risk

    assert "max_loss_allowed" in max_allowed, "max_loss_allowed not in result"
    # Trailing DD buffer = $500, Daily loss buffer = $300, so min is $300
    assert max_allowed["max_loss_allowed"] == Decimal("300"), f"Expected 300, got {max_allowed['max_loss_allowed']}"
    
    print(f"   ✅ PASS: Max loss allowed is ${max_allowed['max_loss_allowed']} (minimum of all buffers)")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Payout King - Rules Engine Quick Test")
    print("=" * 60)
    
    tests = [
        test_trailing_drawdown_safe,
        test_trailing_drawdown_critical,
        test_trailing_drawdown_violated,
        test_daily_loss_limit,
        test_max_allowed_risk,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"   ❌ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed! Rules engine is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

