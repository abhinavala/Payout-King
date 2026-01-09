"""
Mock Live Mode Simulator

Feeds fake PnL ticks every second to exercise trailing drawdown + daily loss.
This is your local dev simulator and will save time during API integration.

Usage:
    simulator = MockSimulator(account_id="test-1", starting_balance=10000)
    async for snapshot in simulator.run():
        # Feed snapshot to rules engine
        result = rule_engine.evaluate(snapshot)
"""

import asyncio
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import AsyncIterator

from rules_engine.interface import AccountSnapshot, PositionSnapshot
from decimal import Decimal


class MockSimulator:
    """
    Simulates a live trading account with realistic PnL movements.
    
    Features:
    - Random PnL ticks every second
    - Configurable volatility
    - Exercises trailing drawdown scenarios
    - Exercises daily loss scenarios
    - Can simulate winning/losing streaks
    """

    def __init__(
        self,
        account_id: str,
        starting_balance: Decimal = Decimal("10000"),
        volatility: Decimal = Decimal("50"),  # Max PnL change per tick
        tick_interval: float = 1.0,  # Seconds between ticks
    ):
        self.account_id = account_id
        self.starting_balance = starting_balance
        self.volatility = volatility
        self.tick_interval = tick_interval
        
        # State
        self.balance = starting_balance
        self.realized_pnl = Decimal("0")
        self.unrealized_pnl = Decimal("0")
        self.high_water_mark = starting_balance
        self.daily_pnl = Decimal("0")
        self.open_positions: list[PositionSnapshot] = []
        
        # Track daily reset
        self.last_reset_date = datetime.utcnow().date()
        
        # Simulation control
        self.running = False

    async def run(self) -> AsyncIterator[AccountSnapshot]:
        """
        Run the simulator, yielding AccountSnapshot every tick_interval seconds.
        
        Yields:
            AccountSnapshot with updated account state
        """
        self.running = True
        
        while self.running:
            # Update state
            await self._tick()
            
            # Build snapshot
            snapshot = self._build_snapshot()
            yield snapshot
            
            # Wait for next tick
            await asyncio.sleep(self.tick_interval)

    async def _tick(self):
        """Update account state for one tick."""
        # Random PnL change
        pnl_change = Decimal(str(random.uniform(
            -float(self.volatility),
            float(self.volatility)
        )))
        
        # Update unrealized PnL (simulating position movement)
        self.unrealized_pnl += pnl_change
        
        # Occasionally realize some PnL (close position)
        if random.random() < 0.1:  # 10% chance per tick
            realized = self.unrealized_pnl * Decimal("0.5")  # Realize half
            self.realized_pnl += realized
            self.balance += realized
            self.unrealized_pnl -= realized
            self.daily_pnl += realized
        
        # Update high water mark
        current_equity = self.balance + self.unrealized_pnl
        if current_equity > self.high_water_mark:
            self.high_water_mark = current_equity
        
        # Check daily reset (simplified: reset at midnight UTC)
        now = datetime.utcnow()
        if now.date() > self.last_reset_date:
            self.daily_pnl = Decimal("0")
            self.last_reset_date = now.date()
        
        # Simulate position opening/closing
        if not self.open_positions and random.random() < 0.2:  # 20% chance to open
            self._open_position()
        elif self.open_positions and random.random() < 0.15:  # 15% chance to close
            self._close_position()

    def _open_position(self):
        """Simulate opening a position."""
        symbols = ["ES", "NQ", "YM", "RTY"]
        symbol = random.choice(symbols)
        quantity = random.choice([1, -1, 2, -2])  # Long or short
        
        position = PositionSnapshot(
            symbol=symbol,
            quantity=quantity,
            avg_price=Decimal("4000"),  # Mock price
            current_price=Decimal("4000"),
            unrealized_pnl=Decimal("0"),
            opened_at=datetime.utcnow(),
        )
        self.open_positions.append(position)

    def _close_position(self):
        """Simulate closing a position."""
        if self.open_positions:
            position = self.open_positions.pop(0)
            # Realize the PnL
            self.realized_pnl += position.unrealized_pnl
            self.balance += position.unrealized_pnl
            self.daily_pnl += position.unrealized_pnl

    def _build_snapshot(self) -> AccountSnapshot:
        """Build AccountSnapshot from current state."""
        return AccountSnapshot(
            account_id=self.account_id,
            timestamp=datetime.utcnow(),
            equity=self.balance + self.unrealized_pnl,
            balance=self.balance,
            realized_pnl=self.realized_pnl,
            unrealized_pnl=self.unrealized_pnl,
            high_water_mark=self.high_water_mark,
            daily_pnl=self.daily_pnl,
            starting_balance=self.starting_balance,
            open_positions=self.open_positions.copy(),
        )

    def stop(self):
        """Stop the simulator."""
        self.running = False


class ScenarioSimulator:
    """
    Pre-configured scenarios to test specific rule behaviors.
    """

    @staticmethod
    async def trailing_drawdown_test() -> AsyncIterator[AccountSnapshot]:
        """
        Scenario: Account starts at $10k, makes profit to $10.5k,
        then loses money approaching trailing drawdown.
        """
        simulator = MockSimulator(
            account_id="scenario-trailing-dd",
            starting_balance=Decimal("10000"),
            volatility=Decimal("100"),
        )
        
        # Manually control for testing
        simulator.balance = Decimal("10000")
        simulator.high_water_mark = Decimal("10500")  # Made profit
        simulator.equity = Decimal("10200")  # Now losing
        
        async for snapshot in simulator.run():
            yield snapshot
            # Stop after 10 ticks for testing
            if snapshot.equity < Decimal("9500"):
                simulator.stop()
                break

    @staticmethod
    async def daily_loss_limit_test() -> AsyncIterator[AccountSnapshot]:
        """
        Scenario: Account loses money throughout the day, approaching daily limit.
        """
        simulator = MockSimulator(
            account_id="scenario-daily-loss",
            starting_balance=Decimal("10000"),
            volatility=Decimal("50"),
        )
        
        # Start losing
        simulator.daily_pnl = Decimal("-300")  # Already lost $300 today
        
        async for snapshot in simulator.run():
            yield snapshot
            # Stop when daily loss exceeds $500
            if snapshot.daily_pnl < Decimal("-500"):
                simulator.stop()
                break

