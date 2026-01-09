"""
Core rule engine that calculates rule states and distances to violation.
"""

from decimal import Decimal
from typing import Dict, List, Optional

from .models import (
    DistanceMetric,
    FirmRules,
    RuleState,
    RuleStatus,
    RuleRecoverability,
    RuleSeverity,
    RuleType,
)
from .interface import AccountSnapshot, RuleEvaluationResult


class RuleEngine:
    """
    Calculates rule compliance states and distances to violation.

    This is the core intellectual property of Payout King.
    """

    def __init__(self, rules: FirmRules):
        self.rules = rules

    def evaluate(self, snapshot: AccountSnapshot) -> RuleEvaluationResult:
        """
        FROZEN INTERFACE METHOD
        
        Evaluate rules against an account snapshot.
        This is the primary entry point - all other methods are internal.
        
        Args:
            snapshot: AccountSnapshot with current account state
            
        Returns:
            RuleEvaluationResult with all rule states and risk metrics
        """
        rule_states = self.calculate_all_rule_states(snapshot)
        max_allowed_risk = self.get_max_allowed_risk(snapshot, rule_states)
        overall_risk_level = self._calculate_overall_risk_level(rule_states)
        
        return RuleEvaluationResult(
            account_id=snapshot.account_id,
            timestamp=snapshot.timestamp,
            rule_states=rule_states,
            max_allowed_risk=max_allowed_risk,
            overall_risk_level=overall_risk_level,
        )

    def calculate_all_rule_states(
        self, account_state: AccountSnapshot
    ) -> Dict[str, RuleState]:
        """
        Calculate the state of all enabled rules.

        Returns a dictionary mapping rule names to their states.
        """
        rule_states = {}

        if self.rules.trailing_drawdown and self.rules.trailing_drawdown.enabled:
            rule_states["trailing_drawdown"] = self._calculate_trailing_drawdown(
                account_state
            )

        if self.rules.daily_loss_limit and self.rules.daily_loss_limit.enabled:
            rule_states["daily_loss_limit"] = self._calculate_daily_loss_limit(
                account_state
            )

        if self.rules.overall_max_loss and self.rules.overall_max_loss.enabled:
            rule_states["overall_max_loss"] = self._calculate_overall_max_loss(
                account_state
            )

        if self.rules.max_position_size and self.rules.max_position_size.enabled:
            rule_states["max_position_size"] = self._calculate_max_position_size(
                account_state
            )

        if self.rules.mae_rule and self.rules.mae_rule.enabled:
            rule_states["mae"] = self._calculate_mae(account_state)

        if self.rules.consistency_rule and self.rules.consistency_rule.enabled:
            rule_states["consistency"] = self._calculate_consistency(
                account_state, 
                daily_pnl_history=account_state.daily_pnl_history
            )

        if self.rules.trading_hours and self.rules.trading_hours.enabled:
            rule_states["trading_hours"] = self._calculate_trading_hours(account_state)

        if self.rules.minimum_trading_days and self.rules.minimum_trading_days.enabled:
            rule_states["minimum_trading_days"] = self._calculate_minimum_trading_days(
                account_state
            )

        if self.rules.profit_target and self.rules.profit_target.enabled:
            rule_states["profit_target"] = self._calculate_profit_target(account_state)

        return rule_states

    def _calculate_overall_risk_level(
        self, rule_states: Dict[str, RuleState]
    ) -> str:
        """
        Calculate overall risk level from individual rule states.
        
        Priority: violated > critical > caution > safe
        """
        if any(state.status == RuleStatus.VIOLATED for state in rule_states.values()):
            return "violated"
        if any(state.status == RuleStatus.CRITICAL for state in rule_states.values()):
            return "critical"
        if any(state.status == RuleStatus.CAUTION for state in rule_states.values()):
            return "caution"
        return "safe"

    def _calculate_trailing_drawdown(
        self, account_state: AccountSnapshot
    ) -> RuleState:
        """
        Calculate trailing drawdown state.

        Trailing drawdown is calculated from the high-water mark.
        If include_unrealized_pnl is True, we use equity. Otherwise, use balance.
        
        Status levels per specification:
        - SAFE: More than 20% buffer above threshold
        - CAUTION: Within 20% of threshold
        - CRITICAL: Within 5% of threshold
        - VIOLATED: At or below threshold
        """
        rule = self.rules.trailing_drawdown
        assert rule is not None

        # Use equity if unrealized PnL is included, otherwise use balance
        current_value = (
            account_state.equity
            if rule.include_unrealized_pnl
            else account_state.balance
        )

        # Calculate maximum allowed drawdown threshold
        max_drawdown_threshold = (
            account_state.high_water_mark * Decimal(str(rule.max_drawdown_percent)) / Decimal("100")
        )
        min_allowed_value = account_state.high_water_mark - max_drawdown_threshold

        # Remaining buffer is how much more we can lose before violation
        # Formula: distance_to_violation = current_equity - (high_water_mark * 0.95)
        remaining_buffer = current_value - min_allowed_value

        # Calculate status levels per specification
        # SAFE: current_equity > (high_water_mark * 0.95) + (threshold * 0.20)
        # CAUTION: within 20% of threshold
        # CRITICAL: within 5% of threshold
        safe_threshold = min_allowed_value + (max_drawdown_threshold * Decimal("0.20"))
        caution_threshold = min_allowed_value + (max_drawdown_threshold * Decimal("0.20"))
        critical_threshold = min_allowed_value + (max_drawdown_threshold * Decimal("0.05"))

        # Determine status
        if remaining_buffer <= 0:
            status = RuleStatus.VIOLATED
        elif current_value <= critical_threshold:
            status = RuleStatus.CRITICAL
        elif current_value <= caution_threshold:
            status = RuleStatus.CAUTION
        else:
            status = RuleStatus.SAFE

        # Buffer as percentage of max_drawdown_threshold (0-100)
        buffer_percent = (
            (remaining_buffer / max_drawdown_threshold) * Decimal("100")
            if max_drawdown_threshold > 0
            else Decimal("100")
        )

        # Distance to violation
        distance = DistanceMetric(
            dollars=remaining_buffer,
            percent=buffer_percent,
        )

        warnings = []
        if status == RuleStatus.VIOLATED:
            warnings.append(
                f"Trailing drawdown VIOLATED: Account has breached drawdown limit"
            )
        elif status == RuleStatus.CRITICAL:
            warnings.append(
                f"Trailing drawdown critical: ${remaining_buffer:.2f} remaining (within 5% of threshold)"
            )
        elif status == RuleStatus.CAUTION:
            warnings.append(
                f"Trailing drawdown caution: ${remaining_buffer:.2f} remaining (within 20% of threshold)"
            )

        return RuleState(
            rule_name="trailing_drawdown",
            current_value=current_value,
            threshold=min_allowed_value,
            remaining_buffer=remaining_buffer,
            buffer_percent=buffer_percent,
            status=status,
            distance_to_violation=distance,
            warnings=warnings,
            recoverable=rule.recoverable,
            severity=rule.severity,
            rule_type=rule.rule_type,
            recovery_path=None if rule.recoverable == RuleRecoverability.NON_RECOVERABLE else "Cannot recover - account fails immediately",
        )

    def _calculate_daily_loss_limit(
        self, account_state: AccountSnapshot
    ) -> RuleState:
        """
        Calculate daily loss limit state.

        Daily loss is tracked from the start of the trading day.
        Only realized PnL counts (unrealized PnL excluded).
        
        Status levels per specification:
        - SAFE: daily_loss < (daily_loss_limit * 0.80) - Less than 80% of limit used
        - CAUTION: (daily_loss_limit * 0.80) <= daily_loss < (daily_loss_limit * 0.95)
        - CRITICAL: (daily_loss_limit * 0.95) <= daily_loss < daily_loss_limit
        - VIOLATED: daily_loss >= daily_loss_limit
        """
        rule = self.rules.daily_loss_limit
        assert rule is not None

        # Daily loss = -daily_realized_pnl (only realized PnL counts, unrealized excluded)
        # daily_pnl in account_state should already be daily realized PnL
        daily_loss = -account_state.daily_pnl if account_state.daily_pnl < 0 else Decimal("0")

        # Remaining buffer is how much more we can lose today
        # Formula: distance_to_violation = daily_loss_limit - daily_loss
        max_loss_decimal = Decimal(str(rule.max_loss_amount))
        remaining_buffer = max_loss_decimal - daily_loss

        # Buffer as percentage of limit remaining
        buffer_percent = (
            (remaining_buffer / max_loss_decimal) * Decimal("100")
            if max_loss_decimal > 0
            else Decimal("0")
        )

        # Determine status based on percentage of limit used
        # SAFE: loss < 80% of limit
        # CAUTION: 80% <= loss < 95%
        # CRITICAL: 95% <= loss < 100%
        # VIOLATED: loss >= 100%
        if daily_loss >= max_loss_decimal:
            status = RuleStatus.VIOLATED
        elif daily_loss >= (max_loss_decimal * Decimal("0.95")):
            status = RuleStatus.CRITICAL
        elif daily_loss >= (max_loss_decimal * Decimal("0.80")):
            status = RuleStatus.CAUTION
        else:
            status = RuleStatus.SAFE

        distance = DistanceMetric(
            dollars=remaining_buffer,
            percent=buffer_percent,
        )

        warnings = []
        if status == RuleStatus.VIOLATED:
            warnings.append(
                f"Daily loss limit VIOLATED: ${daily_loss:.2f} loss exceeds limit of ${max_loss_decimal:.2f}"
            )
        elif status == RuleStatus.CRITICAL:
            warnings.append(
                f"Daily loss limit critical: ${remaining_buffer:.2f} remaining (95%+ of limit used)"
            )
        elif status == RuleStatus.CAUTION:
            warnings.append(
                f"Daily loss limit caution: ${remaining_buffer:.2f} remaining (80%+ of limit used)"
            )

        recovery_path = None
        if rule.recoverable == RuleRecoverability.RECOVERABLE:
            recovery_path = f"Trading disabled until next session (resets at {rule.reset_time}). Account does not fail unless repeated abuse."
        elif rule.recoverable == RuleRecoverability.NON_RECOVERABLE:
            recovery_path = "Cannot recover - account fails immediately"
        
        return RuleState(
            rule_name="daily_loss_limit",
            current_value=daily_loss,
            threshold=rule.max_loss_amount,
            remaining_buffer=remaining_buffer,
            buffer_percent=buffer_percent,
            status=status,
            distance_to_violation=distance,
            warnings=warnings,
            recoverable=rule.recoverable,
            severity=rule.severity,
            rule_type=rule.rule_type,
            recovery_path=recovery_path,
        )

    def _calculate_overall_max_loss(
        self, account_state: AccountSnapshot
    ) -> RuleState:
        """
        Calculate overall maximum loss state.
        """
        rule = self.rules.overall_max_loss
        assert rule is not None

        # Calculate total loss from starting balance or absolute
        if rule.from_starting_balance:
            total_loss = account_state.starting_balance - account_state.equity
        else:
            total_loss = -account_state.realized_pnl if account_state.realized_pnl < 0 else Decimal("0")

        # Remaining buffer
        remaining_buffer = rule.max_loss_amount - total_loss

        # Buffer as percentage
        buffer_percent = (
            (remaining_buffer / rule.max_loss_amount) * Decimal("100")
            if rule.max_loss_amount > 0
            else Decimal("0")
        )

        # Determine status
        if remaining_buffer <= 0:
            status = RuleStatus.VIOLATED
        elif buffer_percent <= Decimal("10"):
            status = RuleStatus.CRITICAL
        elif buffer_percent <= Decimal("30"):
            status = RuleStatus.CAUTION
        else:
            status = RuleStatus.SAFE

        distance = DistanceMetric(
            dollars=remaining_buffer,
            percent=buffer_percent,
        )

        warnings = []
        if status == RuleStatus.CRITICAL:
            warnings.append(
                f"Overall max loss critical: ${remaining_buffer:.2f} remaining"
            )
        elif status == RuleStatus.CAUTION:
            warnings.append(
                f"Overall max loss caution: ${remaining_buffer:.2f} remaining"
            )

        return RuleState(
            rule_name="overall_max_loss",
            current_value=total_loss,
            threshold=rule.max_loss_amount,
            remaining_buffer=remaining_buffer,
            buffer_percent=buffer_percent,
            status=status,
            distance_to_violation=distance,
            warnings=warnings,
        )

    def _calculate_max_position_size(
        self, account_state: AccountSnapshot
    ) -> RuleState:
        """
        Calculate maximum position size state.
        
        Status levels per specification:
        - SAFE: current_position_size <= (max_position_size * 0.80) - Less than 80% of limit
        - CAUTION: (max_position_size * 0.80) < current_position_size <= (max_position_size * 0.95)
        - CRITICAL: (max_position_size * 0.95) < current_position_size < max_position_size
        - VIOLATED: current_position_size > max_position_size
        """
        rule = self.rules.max_position_size
        assert rule is not None

        # Calculate current total position size (sum of absolute quantities)
        # This is gross position size across all instruments
        current_position_size = sum(abs(pos.quantity) for pos in account_state.open_positions)

        # Remaining buffer: how many more contracts can be opened
        # Formula: distance_to_violation = max_position_size - current_position_size
        remaining_buffer = rule.max_contracts - current_position_size

        # Buffer as percentage of limit remaining
        buffer_percent = (
            (remaining_buffer / rule.max_contracts) * Decimal("100")
            if rule.max_contracts > 0
            else Decimal("0")
        )

        # Determine status based on percentage of limit used
        # SAFE: position <= 80% of limit
        # CAUTION: 80% < position <= 95%
        # CRITICAL: 95% < position < 100%
        # VIOLATED: position >= 100%
        if current_position_size > rule.max_contracts:
            status = RuleStatus.VIOLATED
        elif current_position_size > (rule.max_contracts * Decimal("0.95")):
            status = RuleStatus.CRITICAL
        elif current_position_size > (rule.max_contracts * Decimal("0.80")):
            status = RuleStatus.CAUTION
        else:
            status = RuleStatus.SAFE

        distance = DistanceMetric(
            contracts=int(remaining_buffer) if remaining_buffer >= 0 else 0,
            percent=buffer_percent,
        )

        warnings = []
        if status == RuleStatus.VIOLATED:
            warnings.append(
                f"Max position size VIOLATED: {current_position_size} contracts exceeds limit of {rule.max_contracts}"
            )
        elif status == RuleStatus.CRITICAL:
            warnings.append(
                f"Max position size critical: {int(remaining_buffer)} contracts remaining (95%+ of limit used)"
            )
        elif status == RuleStatus.CAUTION:
            warnings.append(
                f"Max position size caution: {int(remaining_buffer)} contracts remaining (80%+ of limit used)"
            )

        return RuleState(
            rule_name="max_position_size",
            current_value=Decimal(current_position_size),
            threshold=Decimal(rule.max_contracts),
            remaining_buffer=Decimal(remaining_buffer),
            buffer_percent=buffer_percent,
            status=status,
            distance_to_violation=distance,
            warnings=warnings,
            recoverable=rule.recoverable,
            severity=rule.severity,
            rule_type=rule.rule_type,
            recovery_path="Cannot recover - account fails immediately" if rule.recoverable == RuleRecoverability.NON_RECOVERABLE else None,
        )

    def get_max_allowed_risk(
        self, account_state: AccountSnapshot, rule_states: Dict[str, RuleState]
    ) -> Dict[str, Decimal]:
        """
        Calculate maximum allowed values for various risk metrics.

        Returns a dictionary with keys like:
        - max_loss_allowed: Maximum loss that can be taken right now
        - max_profit_allowed: Maximum profit allowed today (if consistency rule)
        - max_contracts_allowed: Maximum contracts that can be opened
        """
        max_allowed = {}

        # Max loss allowed = minimum of all loss-related buffers
        loss_buffers = []
        if "trailing_drawdown" in rule_states:
            loss_buffers.append(rule_states["trailing_drawdown"].remaining_buffer)
        if "daily_loss_limit" in rule_states:
            loss_buffers.append(rule_states["daily_loss_limit"].remaining_buffer)
        if "overall_max_loss" in rule_states:
            loss_buffers.append(rule_states["overall_max_loss"].remaining_buffer)

        if loss_buffers:
            max_allowed["max_loss_allowed"] = min(loss_buffers)

        # Max contracts allowed
        if "max_position_size" in rule_states:
            max_allowed["max_contracts_allowed"] = Decimal(
                rule_states["max_position_size"].distance_to_violation.contracts or 0
            )

        return max_allowed

    def _calculate_mae(self, account_state: AccountSnapshot) -> RuleState:
        """
        Calculate Maximum Adverse Excursion (MAE) rule state.
        
        MAE tracks peak unrealized loss on any trade, even if trade later recovers.
        Uses peak_unrealized_loss from positions.
        """
        rule = self.rules.mae_rule
        assert rule is not None

        # Find maximum peak unrealized loss across all positions
        max_mae = Decimal("0")
        for pos in account_state.open_positions:
            if pos.peak_unrealized_loss < max_mae:
                max_mae = pos.peak_unrealized_loss

        # Calculate MAE as percentage of account
        mae_percent = (
            (abs(max_mae) / account_state.starting_balance) * Decimal("100")
            if account_state.starting_balance > 0
            else Decimal("0")
        )

        # Calculate threshold
        threshold_percent = rule.max_adverse_excursion_percent
        threshold_amount = (
            account_state.starting_balance * threshold_percent / Decimal("100")
        )

        # Remaining buffer
        remaining_buffer = threshold_amount - abs(max_mae)

        # Buffer as percentage
        buffer_percent = (
            (remaining_buffer / threshold_amount) * Decimal("100")
            if threshold_amount > 0
            else Decimal("100")
        )

        # Determine status
        if remaining_buffer <= 0:
            status = RuleStatus.VIOLATED
        elif buffer_percent <= Decimal("10"):
            status = RuleStatus.CRITICAL
        elif buffer_percent <= Decimal("30"):
            status = RuleStatus.CAUTION
        else:
            status = RuleStatus.SAFE

        distance = DistanceMetric(
            dollars=remaining_buffer,
            percent=buffer_percent,
        )

        warnings = []
        if status == RuleStatus.CRITICAL:
            warnings.append(
                f"MAE critical: ${remaining_buffer:.2f} remaining before violation"
            )
        elif status == RuleStatus.CAUTION:
            warnings.append(
                f"MAE caution: ${remaining_buffer:.2f} remaining before violation"
            )

        return RuleState(
            rule_name="mae",
            current_value=abs(max_mae),
            threshold=threshold_amount,
            remaining_buffer=remaining_buffer,
            buffer_percent=buffer_percent,
            status=status,
            distance_to_violation=distance,
            warnings=warnings,
            recoverable=rule.recoverable,
            severity=rule.severity,
            rule_type=rule.rule_type,
            recovery_path="Cannot recover - account fails immediately",
        )

    def _calculate_consistency(
        self, account_state: AccountSnapshot, daily_pnl_history: Optional[Dict[str, Decimal]] = None
    ) -> RuleState:
        """
        Calculate consistency rule state.
        
        Consistency rule limits largest winning day as % of total profit.
        Only applies when total profit is positive.
        
        Status levels per specification:
        - SAFE: max_single_day_profit <= (total_realized_pnl * 0.40)
        - CAUTION: (total_realized_pnl * 0.40) < max_single_day_profit <= (total_realized_pnl * 0.45)
        - CRITICAL: (total_realized_pnl * 0.45) < max_single_day_profit <= (total_realized_pnl * 0.50)
        - VIOLATED: max_single_day_profit > (total_realized_pnl * 0.50)
        
        Note: This requires daily PnL history. If not provided, returns placeholder state.
        daily_pnl_history should be a dict mapping date strings (YYYY-MM-DD) to daily realized PnL.
        """
        rule = self.rules.consistency_rule
        assert rule is not None

        # Total realized PnL (net profit across all days)
        total_realized_pnl = account_state.realized_pnl
        
        # If no daily PnL history provided, return placeholder
        if daily_pnl_history is None or len(daily_pnl_history) == 0:
            # Placeholder: cannot calculate without daily history
            return RuleState(
                rule_name="consistency",
                current_value=Decimal("0"),
                threshold=rule.max_single_day_percent,
                remaining_buffer=rule.max_single_day_percent,
                buffer_percent=Decimal("100"),
                status=RuleStatus.SAFE,  # Assume safe if we can't calculate
                distance_to_violation=DistanceMetric(percent=Decimal("100")),
                warnings=["Daily PnL history required for consistency rule calculation"],
                recoverable=rule.recoverable,
                severity=rule.severity,
                rule_type=rule.rule_type,
                recovery_path=None,
            )
        
        # Find maximum single-day profit
        max_single_day_profit = max(daily_pnl_history.values()) if daily_pnl_history.values() else Decimal("0")
        
        # Rule only applies when total profit is positive
        if total_realized_pnl <= 0:
            # No profit yet, rule doesn't apply
            return RuleState(
                rule_name="consistency",
                current_value=Decimal("0"),
                threshold=rule.max_single_day_percent,
                remaining_buffer=rule.max_single_day_percent,
                buffer_percent=Decimal("100"),
                status=RuleStatus.SAFE,  # Rule doesn't apply when total <= 0
                distance_to_violation=DistanceMetric(percent=Decimal("100")),
                warnings=[],
                recoverable=rule.recoverable,
                severity=rule.severity,
                rule_type=rule.rule_type,
                recovery_path=None,
            )
        
        # Calculate percentage: max_single_day_profit / total_realized_pnl * 100
        largest_day_percent = (max_single_day_profit / total_realized_pnl) * Decimal("100")
        
        # Calculate max allowed single day (50% of total)
        max_allowed_single_day = total_realized_pnl * (rule.max_single_day_percent / Decimal("100"))
        
        # Distance to violation: how much more can the max day be before violation
        distance_to_violation = max_allowed_single_day - max_single_day_profit
        
        # Determine status based on percentage thresholds
        # SAFE: <= 40% of total
        # CAUTION: 40% < x <= 45%
        # CRITICAL: 45% < x <= 50%
        # VIOLATED: > 50%
        if largest_day_percent > rule.max_single_day_percent:
            status = RuleStatus.VIOLATED
        elif largest_day_percent > Decimal("45"):
            status = RuleStatus.CRITICAL
        elif largest_day_percent > Decimal("40"):
            status = RuleStatus.CAUTION
        else:
            status = RuleStatus.SAFE
        
        # Buffer as percentage of threshold
        buffer_percent = (
            (distance_to_violation / max_allowed_single_day) * Decimal("100")
            if max_allowed_single_day > 0
            else Decimal("0")
        )

        distance = DistanceMetric(
            dollars=distance_to_violation,
            percent=buffer_percent,
        )

        warnings = []
        if status == RuleStatus.VIOLATED:
            warnings.append(
                f"Consistency rule VIOLATED: {largest_day_percent:.1f}% of profit from single day (max {rule.max_single_day_percent}%)"
            )
        elif status == RuleStatus.CRITICAL:
            warnings.append(
                f"Consistency rule critical: {largest_day_percent:.1f}% of profit from single day (max {rule.max_single_day_percent}%)"
            )
        elif status == RuleStatus.CAUTION:
            warnings.append(
                f"Consistency rule caution: {largest_day_percent:.1f}% of profit from single day"
            )

        recovery_path = None
        if rule.recoverable == RuleRecoverability.RECOVERABLE:
            recovery_path = "Add more trading days or increase total profit to reduce single-day percentage"

        return RuleState(
            rule_name="consistency",
            current_value=largest_day_percent,
            threshold=rule.max_single_day_percent,
            remaining_buffer=distance_to_violation,
            buffer_percent=buffer_percent,
            status=status,
            distance_to_violation=distance,
            warnings=warnings,
            recoverable=rule.recoverable,
            severity=rule.severity,
            rule_type=rule.rule_type,
            recovery_path=recovery_path,
        )

    def _calculate_trading_hours(self, account_state: AccountSnapshot) -> RuleState:
        """
        Calculate trading hours rule state.
        
        Checks if current time is before forced close time.
        Positions must be closed by the deadline (e.g., 3:10 PM CT for Topstep).
        
        Status levels per specification:
        - SAFE: current_time < (trading_day_end - 30 minutes) AND open_positions_count == 0
        - CAUTION: (trading_day_end - 30 minutes) <= current_time < (trading_day_end - 10 minutes) AND open_positions_count > 0
        - CRITICAL: (trading_day_end - 10 minutes) <= current_time < trading_day_end AND open_positions_count > 0
        - VIOLATED: current_time >= trading_day_end AND open_positions_count > 0
        """
        rule = self.rules.trading_hours
        assert rule is not None

        from datetime import datetime
        import pytz

        # Get current time in rule's timezone
        tz = pytz.timezone(rule.timezone)
        now = datetime.now(tz)
        
        # Parse forced close time (e.g., "15:10" for 3:10 PM CT)
        close_hour, close_minute = map(int, rule.forced_close_time.split(":"))
        close_time = now.replace(hour=close_hour, minute=close_minute, second=0, microsecond=0)

        # Check if we have open positions
        has_open_positions = len(account_state.open_positions) > 0

        # Calculate time until deadline
        seconds_until_deadline = (close_time - now).total_seconds() if now < close_time else 0
        minutes_until_deadline = seconds_until_deadline / 60

        # Determine status per specification
        if has_open_positions and now >= close_time:
            # At or after deadline with open positions = VIOLATED
            status = RuleStatus.VIOLATED
        elif has_open_positions and seconds_until_deadline <= 600:  # 10 minutes = 600 seconds
            # Less than 10 minutes before deadline with open positions = CRITICAL
            status = RuleStatus.CRITICAL
        elif has_open_positions and seconds_until_deadline <= 1800:  # 30 minutes = 1800 seconds
            # Between 10 and 30 minutes before deadline with open positions = CAUTION
            status = RuleStatus.CAUTION
        elif not has_open_positions:
            # No open positions = SAFE (requirement satisfied)
            status = RuleStatus.SAFE
        else:
            # More than 30 minutes before deadline = SAFE
            status = RuleStatus.SAFE

        distance = DistanceMetric(
            percent=Decimal(str((seconds_until_deadline / 3600) * 100)) if seconds_until_deadline > 0 else Decimal("0"),
        )

        warnings = []
        if status == RuleStatus.VIOLATED:
            warnings.append(
                f"Trading hours VIOLATION: Positions must be closed by {rule.forced_close_time}. Account failed."
            )
        elif status == RuleStatus.CRITICAL:
            warnings.append(
                f"Trading hours critical: {int(minutes_until_deadline)} minutes until forced close at {rule.forced_close_time}"
            )
        elif status == RuleStatus.CAUTION:
            warnings.append(
                f"Trading hours caution: {int(minutes_until_deadline)} minutes until forced close at {rule.forced_close_time}"
            )

        return RuleState(
            rule_name="trading_hours",
            current_value=Decimal(str(minutes_until_deadline)),
            threshold=Decimal("0"),  # Must close before this time
            remaining_buffer=Decimal(str(minutes_until_deadline)),
            buffer_percent=Decimal("100") if seconds_until_deadline > 0 else Decimal("0"),
            status=status,
            distance_to_violation=distance,
            warnings=warnings,
            recoverable=rule.recoverable,
            severity=rule.severity,
            rule_type=rule.rule_type,
            recovery_path="Cannot recover - account fails immediately" if rule.recoverable == RuleRecoverability.NON_RECOVERABLE else None,
        )

    def _calculate_minimum_trading_days(self, account_state: AccountSnapshot) -> RuleState:
        """
        Calculate minimum trading days rule state.
        
        Requires tracking daily PnL history to count trading days.
        A trading day is a day where at least one trade was closed.
        """
        rule = self.rules.minimum_trading_days
        assert rule is not None

        # Count trading days from daily PnL history
        # A trading day is a day where at least one trade was closed (daily PnL != 0)
        # OR where daily PnL meets minimum profit requirement
        if account_state.daily_pnl_history is None or len(account_state.daily_pnl_history) == 0:
            # No history provided, return placeholder
            return RuleState(
                rule_name="minimum_trading_days",
                current_value=Decimal("0"),
                threshold=Decimal(str(rule.min_days)),
                remaining_buffer=Decimal(str(rule.min_days)),
                buffer_percent=Decimal("0"),
                status=RuleStatus.CAUTION,
                distance_to_violation=DistanceMetric(percent=Decimal("0")),
                warnings=["Daily PnL history required for minimum trading days calculation"],
                recoverable=rule.recoverable,
                severity=rule.severity,
                rule_type=rule.rule_type,
                recovery_path=None,
            )
        
        # Count days where daily PnL meets minimum requirement
        # For most firms, any day with closed trades counts (PnL != 0)
        # Some firms require minimum profit per day
        trading_days_counted = 0
        for date, daily_pnl in account_state.daily_pnl_history.items():
            # Count as trading day if PnL meets minimum requirement
            if daily_pnl >= rule.min_profit_per_day:
                trading_days_counted += 1
        
        remaining_days = Decimal(str(max(0, rule.min_days - trading_days_counted)))
        min_days_decimal = Decimal(str(rule.min_days))
        buffer_percent = (
            (remaining_days / min_days_decimal) * Decimal("100")
            if min_days_decimal > 0
            else Decimal("100")
        )

        # Determine status
        # SAFE: Requirement met (trading_days_counted >= min_days)
        # CAUTION: Close to requirement (1-2 days remaining)
        # CRITICAL: Far from requirement (many days remaining)
        if remaining_days <= Decimal("0"):
            status = RuleStatus.SAFE  # Requirement met
        elif remaining_days <= Decimal("2"):
            status = RuleStatus.CAUTION
        else:
            status = RuleStatus.CAUTION  # Still need more days

        distance = DistanceMetric(
            percent=buffer_percent,
        )

        warnings = []
        if remaining_days > 0:
            warnings.append(
                f"Minimum trading days: {int(remaining_days)} more days required (min ${rule.min_profit_per_day} profit per day)"
            )
        else:
            warnings.append(
                f"Minimum trading days requirement met: {trading_days_counted} trading days"
            )

        recovery_path = None
        if rule.recoverable == RuleRecoverability.RECOVERABLE:
            if remaining_days > 0:
                recovery_path = f"Trade {int(remaining_days)} more days with at least ${rule.min_profit_per_day} profit each day"
            else:
                recovery_path = "Requirement met - no action needed"

        return RuleState(
            rule_name="minimum_trading_days",
            current_value=Decimal(str(trading_days_counted)),
            threshold=Decimal(str(rule.min_days)),
            remaining_buffer=remaining_days,
            buffer_percent=buffer_percent,
            status=status,
            distance_to_violation=distance,
            warnings=warnings,
            recoverable=rule.recoverable,
            severity=rule.severity,
            rule_type=rule.rule_type,
            recovery_path=recovery_path,
        )

    def _calculate_profit_target(self, account_state: AccountSnapshot) -> RuleState:
        """
        Calculate profit target rule state.
        """
        rule = self.rules.profit_target
        assert rule is not None

        current_profit = account_state.realized_pnl + account_state.unrealized_pnl
        remaining_to_target = rule.target_amount - current_profit

        buffer_percent = (
            (current_profit / rule.target_amount) * Decimal("100")
            if rule.target_amount > 0
            else Decimal("100")
        )

        # Determine status
        if remaining_to_target <= 0:
            status = RuleStatus.SAFE  # Target reached
        elif buffer_percent >= Decimal("90"):
            status = RuleStatus.SAFE
        elif buffer_percent >= Decimal("70"):
            status = RuleStatus.CAUTION
        else:
            status = RuleStatus.SAFE

        distance = DistanceMetric(
            dollars=remaining_to_target,
            percent=buffer_percent,
        )

        warnings = []
        if remaining_to_target > 0:
            warnings.append(
                f"Profit target: ${remaining_to_target:.2f} remaining to reach ${rule.target_amount}"
            )

        recovery_path = None
        if rule.recoverable == RuleRecoverability.RECOVERABLE:
            recovery_path = f"Continue trading to reach ${rule.target_amount} profit target"

        return RuleState(
            rule_name="profit_target",
            current_value=current_profit,
            threshold=rule.target_amount,
            remaining_buffer=remaining_to_target,
            buffer_percent=buffer_percent,
            status=status,
            distance_to_violation=distance,
            warnings=warnings,
            recoverable=rule.recoverable,
            severity=rule.severity,
            rule_type=rule.rule_type,
            recovery_path=recovery_path,
        )

