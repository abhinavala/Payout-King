#!/usr/bin/env python3
"""
Test script for Mock Live Mode Simulator

Run this to verify the simulator works and exercises rule scenarios.

Usage:
    python scripts/test_mock_simulator.py
"""

import asyncio
from decimal import Decimal
from rules_engine.engine import RuleEngine
from rules_engine.models import FirmRules, TrailingDrawdownRule, DailyLossLimitRule
from app.services.mock_simulator import MockSimulator


async def test_basic_simulator():
    """Test basic simulator functionality."""
    print("=" * 60)
    print("Testing Basic Mock Simulator")
    print("=" * 60)
    
    simulator = MockSimulator(
        account_id="test-1",
        starting_balance=Decimal("10000"),
        volatility=Decimal("50"),
        tick_interval=0.5,  # Faster for testing
    )
    
    # Set up rules
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
            timezone="America/Chicago",
        ),
    )
    engine = RuleEngine(rules)
    
    print("\nStarting simulation...")
    print("Press Ctrl+C to stop\n")
    
    tick_count = 0
    try:
        async for snapshot in simulator.run():
            tick_count += 1
            
            # Evaluate rules
            result = engine.evaluate(snapshot)
            
            # Print status every 5 ticks
            if tick_count % 5 == 0:
                print(f"\n[Tick {tick_count}]")
                print(f"  Equity: ${snapshot.equity:.2f}")
                print(f"  Balance: ${snapshot.balance:.2f}")
                print(f"  Unrealized PnL: ${snapshot.unrealized_pnl:.2f}")
                print(f"  Daily PnL: ${snapshot.daily_pnl:.2f}")
                print(f"  High Water Mark: ${snapshot.high_water_mark:.2f}")
                print(f"  Risk Level: {result.overall_risk_level.upper()}")
                
                for rule_name, rule_state in result.rule_states.items():
                    print(f"  {rule_name}: {rule_state.status} "
                          f"(Buffer: ${rule_state.remaining_buffer:.2f}, "
                          f"{rule_state.buffer_percent:.1f}%)")
            
            # Stop after 20 ticks for testing
            if tick_count >= 20:
                simulator.stop()
                break
                
    except KeyboardInterrupt:
        simulator.stop()
        print("\n\nSimulation stopped by user")
    
    print(f"\nSimulation complete. Total ticks: {tick_count}")


async def test_trailing_drawdown_scenario():
    """Test trailing drawdown scenario."""
    print("\n" + "=" * 60)
    print("Testing Trailing Drawdown Scenario")
    print("=" * 60)
    
    simulator = MockSimulator(
        account_id="scenario-dd",
        starting_balance=Decimal("10000"),
        volatility=Decimal("100"),
        tick_interval=0.5,
    )
    
    # Manually set up scenario: made profit, now losing
    simulator.balance = Decimal("10000")
    simulator.high_water_mark = Decimal("10500")  # Made $500 profit
    simulator.equity = Decimal("10200")  # Now at $10,200 (losing)
    simulator.unrealized_pnl = Decimal("200")
    
    rules = FirmRules(
        trailing_drawdown=TrailingDrawdownRule(
            enabled=True,
            max_drawdown_percent=Decimal("5"),  # 5% = $525 max drawdown from $10,500
            include_unrealized_pnl=True,
        ),
    )
    engine = RuleEngine(rules)
    
    print("\nScenario: Account made profit to $10,500, now at $10,200")
    print("Trailing drawdown threshold: $9,975 (5% of $10,500)")
    print("Current buffer: $225\n")
    
    tick_count = 0
    async for snapshot in simulator.run():
        tick_count += 1
        result = engine.evaluate(snapshot)
        
        if "trailing_drawdown" in result.rule_states:
            td_state = result.rule_states["trailing_drawdown"]
            print(f"[Tick {tick_count}] Equity: ${snapshot.equity:.2f} | "
                  f"Status: {td_state.status} | "
                  f"Buffer: ${td_state.remaining_buffer:.2f}")
        
        if tick_count >= 10:
            simulator.stop()
            break


if __name__ == "__main__":
    print("Payout King - Mock Simulator Test")
    print("=" * 60)
    
    asyncio.run(test_basic_simulator())
    asyncio.run(test_trailing_drawdown_scenario())
    
    print("\n" + "=" * 60)
    print("All tests complete!")
    print("=" * 60)

