"""
Service for loading prop firm rule sets.

Supports multiple prop firms with firm-specific rules:
- Apex Trader Funding
- Topstep
- My Funded Futures (MFF)
- Bulenox
- TakeProfitTrader

Each firm has different rules for eval, PA, and funded account types.
Includes recovery path information for each rule.
"""

from typing import Optional
from decimal import Decimal
from rules_engine.models import (
    FirmRules,
    TrailingDrawdownRule,
    DailyLossLimitRule,
    OverallMaxLossRule,
    MaxPositionSizeRule,
    MAERule,
    ConsistencyRule,
    TradingHoursRule,
    MinimumTradingDaysRule,
    ProfitTargetRule,
    RuleRecoverability,
    RuleSeverity,
    RuleType,
)


class RuleLoaderService:
    """Service for loading rule sets for different prop firms."""

    def __init__(self):
        self._cache: dict = {}

    async def get_rules(
        self, firm: str, account_type: str, version: str = "1.0"
    ) -> FirmRules:
        """
        Get rule set for a firm/account type/version.
        
        Args:
            firm: Prop firm name ('apex', 'topstep', 'mff', 'bulenox', 'takeprofit')
            account_type: Account type ('eval', 'pa', 'funded')
            version: Rule set version (default: '1.0')
            
        Returns:
            FirmRules with firm-specific rules
            
        Raises:
            ValueError: If firm is not supported
        """
        cache_key = f"{firm}:{account_type}:{version}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Load rules based on firm
        firm_lower = firm.lower()
        if firm_lower == "apex":
            rules = self._get_apex_rules(account_type)
        elif firm_lower == "topstep":
            rules = self._get_topstep_rules(account_type)
        elif firm_lower == "mff" or firm_lower == "myfundedfutures":
            rules = self._get_mff_rules(account_type)
        elif firm_lower == "bulenox":
            rules = self._get_bulenox_rules(account_type)
        elif firm_lower == "takeprofit" or firm_lower == "takeprofitrader":
            rules = self._get_takeprofit_rules(account_type)
        else:
            raise ValueError(
                f"Unknown firm: {firm}. Supported firms: apex, topstep, mff, bulenox, takeprofit"
            )
        
        self._cache[cache_key] = rules
        return rules

    def _get_apex_rules(self, account_type: str) -> FirmRules:
        """
        Get Apex Trader Funding rules.
        
        EVALUATION:
        - 5% trailing drawdown (intraday, includes unrealized PnL) - NON-RECOVERABLE
        - MAE rule (max adverse excursion) - NON-RECOVERABLE
        - No daily loss limit
        - Profit target - RECOVERABLE
        - Minimum 7 trading days - RECOVERABLE
        - Trading hours: Close by 4:59 PM ET - NON-RECOVERABLE
        - Contract limits - NON-RECOVERABLE
        
        PERFORMANCE ACCOUNT (PA):
        - Same trailing drawdown - NON-RECOVERABLE
        - MAE rule still applies - NON-RECOVERABLE
        - 30% consistency rule (at payout) - RECOVERABLE
        - Max loss per trade (soft rule) - SOMETIMES
        """
        # Base rules for all account types
        rules = FirmRules(
            trailing_drawdown=TrailingDrawdownRule(
                enabled=True,
                max_drawdown_percent=Decimal("5"),
                include_unrealized_pnl=True,  # Intraday equity-based
                recoverable=RuleRecoverability.NON_RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
            ),
            mae_rule=MAERule(
                enabled=True,
                max_adverse_excursion_percent=Decimal("5"),  # Same as drawdown
                recoverable=RuleRecoverability.NON_RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
            ),
            trading_hours=TradingHoursRule(
                enabled=True,
                forced_close_time="16:59",  # 4:59 PM ET
                timezone="America/New_York",
                recoverable=RuleRecoverability.NON_RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
                auto_liquidate=True,
            ),
        )

        if account_type == "eval":
            # Evaluation account rules
            rules.profit_target = ProfitTargetRule(
                enabled=True,
                target_amount=Decimal("3000"),  # Example for $50k account
                recoverable=RuleRecoverability.RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
            )
            rules.minimum_trading_days = MinimumTradingDaysRule(
                enabled=True,
                min_days=7,
                min_profit_per_day=Decimal("50"),
                recoverable=RuleRecoverability.RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
            )
            # Contract limits vary by account size - would need account_size parameter
            # For now, disabled - would be set per account
            rules.max_position_size = None

        elif account_type == "pa":
            # Performance Account rules
            rules.consistency_rule = ConsistencyRule(
                enabled=True,
                max_single_day_percent=Decimal("30"),
                recoverable=RuleRecoverability.RECOVERABLE,
                severity=RuleSeverity.PAYOUT_BLOCK,
                rule_type=RuleType.OBJECTIVE,
                applies_at_payout=True,
            )
            # Max loss per trade is subjective/soft rule - not implemented as objective

        return rules

    def _get_topstep_rules(self, account_type: str) -> FirmRules:
        """
        Get Topstep rules.
        
        TRADING COMBINE (EVAL):
        - Maximum Loss Limit (MLL): End-of-day drawdown - NON-RECOVERABLE
        - Daily Loss Limit (DLL): $1000 for $50k account - RECOVERABLE (day-based)
        - Profit target - RECOVERABLE
        - Consistency: 50% during evaluation - RECOVERABLE
        - Trading hours: Flatten before close - NON-RECOVERABLE
        - Scaling plan (contract limits increase) - NON-RECOVERABLE
        
        FUNDED:
        - Same MLL and DLL
        - Prohibited trading practices (subjective)
        """
        # Base rules
        rules = FirmRules(
            trailing_drawdown=TrailingDrawdownRule(
                enabled=True,
                max_drawdown_percent=Decimal("4"),  # End-of-day drawdown
                include_unrealized_pnl=False,  # Balance only, not intraday equity
                recoverable=RuleRecoverability.NON_RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
            ),
            daily_loss_limit=DailyLossLimitRule(
                enabled=True,
                max_loss_amount=Decimal("1000"),  # For $50k account
                reset_time="16:00",  # End of trading day
                timezone="America/Chicago",
                recoverable=RuleRecoverability.RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
                liquidates_positions=True,
            ),
            trading_hours=TradingHoursRule(
                enabled=True,
                forced_close_time="15:10",  # 3:10 PM CT or market close
                timezone="America/Chicago",
                recoverable=RuleRecoverability.NON_RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
                auto_liquidate=True,
            ),
        )

        if account_type == "eval":
            rules.profit_target = ProfitTargetRule(
                enabled=True,
                target_amount=Decimal("3000"),  # Example for $50k account
                recoverable=RuleRecoverability.RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
            )
            rules.consistency_rule = ConsistencyRule(
                enabled=True,
                max_single_day_percent=Decimal("50"),
                recoverable=RuleRecoverability.RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
                applies_at_payout=False,  # Checked when profit target reached
            )
            rules.minimum_trading_days = MinimumTradingDaysRule(
                enabled=True,
                min_days=2,
                min_profit_per_day=Decimal("0"),  # Losing days still count
                recoverable=RuleRecoverability.RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
            )

        return rules

    def _get_mff_rules(self, account_type: str) -> FirmRules:
        """
        Get My Funded Futures (MFF) rules.
        
        EVALUATION:
        - Trailing drawdown - NON-RECOVERABLE
        - Profit target - RECOVERABLE
        - Contract limits - NON-RECOVERABLE
        - Trading hours - NON-RECOVERABLE
        
        FUNDED:
        - Consistency rule: 40% - RECOVERABLE
        - Minimum trading days: 5-10 days - RECOVERABLE
        - Daily loss limits (less strict than Topstep) - RECOVERABLE
        """
        rules = FirmRules(
            trailing_drawdown=TrailingDrawdownRule(
                enabled=True,
                max_drawdown_percent=Decimal("5"),
                include_unrealized_pnl=True,
                recoverable=RuleRecoverability.NON_RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
            ),
        )

        if account_type == "eval":
            rules.profit_target = ProfitTargetRule(
                enabled=True,
                target_amount=Decimal("3000"),  # Example
                recoverable=RuleRecoverability.RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
            )
        elif account_type == "funded":
            rules.consistency_rule = ConsistencyRule(
                enabled=True,
                max_single_day_percent=Decimal("40"),
                recoverable=RuleRecoverability.RECOVERABLE,
                severity=RuleSeverity.PAYOUT_BLOCK,
                rule_type=RuleType.OBJECTIVE,
                applies_at_payout=True,
            )
            rules.minimum_trading_days = MinimumTradingDaysRule(
                enabled=True,
                min_days=5,  # Typically 5-10 days
                min_profit_per_day=Decimal("0"),
                recoverable=RuleRecoverability.RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
            )
            rules.daily_loss_limit = DailyLossLimitRule(
                enabled=True,
                max_loss_amount=Decimal("2500"),  # ~5% of $50k, less strict
                reset_time="17:00",
                timezone="America/Chicago",
                recoverable=RuleRecoverability.RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
            )

        return rules

    def _get_bulenox_rules(self, account_type: str) -> FirmRules:
        """
        Get Bulenox rules.
        
        QUALIFICATION (EVAL):
        - Max drawdown: Trailing - NON-RECOVERABLE
        - Profit target - RECOVERABLE
        - No minimum days (unique advantage)
        - Trading hours - NON-RECOVERABLE
        
        FUNDED:
        - 40% performance rule - RECOVERABLE
        - Safety net balance - NON-RECOVERABLE
        - Payout lockups
        """
        rules = FirmRules(
            trailing_drawdown=TrailingDrawdownRule(
                enabled=True,
                max_drawdown_percent=Decimal("5"),
                include_unrealized_pnl=True,
                recoverable=RuleRecoverability.NON_RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
            ),
        )

        if account_type == "eval":
            rules.profit_target = ProfitTargetRule(
                enabled=True,
                target_amount=Decimal("3000"),  # Example
                recoverable=RuleRecoverability.RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
            )
            # No minimum trading days - unique advantage
        elif account_type == "funded":
            rules.consistency_rule = ConsistencyRule(
                enabled=True,
                max_single_day_percent=Decimal("40"),
                recoverable=RuleRecoverability.RECOVERABLE,
                severity=RuleSeverity.PAYOUT_BLOCK,
                rule_type=RuleType.OBJECTIVE,
                applies_at_payout=True,
            )
            rules.daily_loss_limit = DailyLossLimitRule(
                enabled=True,
                max_loss_amount=Decimal("2000"),  # 4% of $50k account
                reset_time="17:00",
                timezone="America/Chicago",
                recoverable=RuleRecoverability.RECOVERABLE,
                severity=RuleSeverity.HARD_FAIL,
                rule_type=RuleType.OBJECTIVE,
            )

        return rules

    def _get_takeprofit_rules(self, account_type: str) -> FirmRules:
        """
        Get TakeProfitTrader rules.
        
        TEST (EVAL):
        - End-of-day drawdown - NON-RECOVERABLE
        - Profit target - RECOVERABLE
        - Trading hours - NON-RECOVERABLE
        
        PRO / PRO+ (FUNDED):
        - Trailing drawdown (intraday) - NON-RECOVERABLE
        - Immediate payout eligibility (subject to consistency review)
        - Max 5 active funded accounts
        """
        if account_type == "eval":
            return FirmRules(
                trailing_drawdown=TrailingDrawdownRule(
                    enabled=True,
                    max_drawdown_percent=Decimal("5"),
                    include_unrealized_pnl=False,  # End-of-day
                    recoverable=RuleRecoverability.NON_RECOVERABLE,
                    severity=RuleSeverity.HARD_FAIL,
                    rule_type=RuleType.OBJECTIVE,
                ),
                profit_target=ProfitTargetRule(
                    enabled=True,
                    target_amount=Decimal("3000"),  # Example
                    recoverable=RuleRecoverability.RECOVERABLE,
                    severity=RuleSeverity.HARD_FAIL,
                    rule_type=RuleType.OBJECTIVE,
                ),
                trading_hours=TradingHoursRule(
                    enabled=True,
                    forced_close_time="16:00",
                    timezone="America/Chicago",
                    recoverable=RuleRecoverability.NON_RECOVERABLE,
                    severity=RuleSeverity.HARD_FAIL,
                    rule_type=RuleType.OBJECTIVE,
                ),
                minimum_trading_days=MinimumTradingDaysRule(
                    enabled=True,
                    min_days=5,
                    min_profit_per_day=Decimal("0"),
                    recoverable=RuleRecoverability.RECOVERABLE,
                    severity=RuleSeverity.HARD_FAIL,
                    rule_type=RuleType.OBJECTIVE,
                ),
            )
        else:
            # Funded accounts
            return FirmRules(
                trailing_drawdown=TrailingDrawdownRule(
                    enabled=True,
                    max_drawdown_percent=Decimal("5"),
                    include_unrealized_pnl=True,  # Trailing intraday
                    recoverable=RuleRecoverability.NON_RECOVERABLE,
                    severity=RuleSeverity.HARD_FAIL,
                    rule_type=RuleType.OBJECTIVE,
                ),
                consistency_rule=ConsistencyRule(
                    enabled=True,
                    max_single_day_percent=Decimal("50"),  # During eval, none when funded
                    recoverable=RuleRecoverability.RECOVERABLE,
                    severity=RuleSeverity.PAYOUT_BLOCK,
                    rule_type=RuleType.OBJECTIVE,
                    applies_at_payout=True,
                ),
            )

    def get_supported_firms(self) -> list:
        """Get list of supported prop firms."""
        return ["apex", "topstep", "mff", "bulenox", "takeprofit"]

    def get_supported_account_types(self) -> list:
        """Get list of supported account types."""
        return ["eval", "pa", "funded"]
