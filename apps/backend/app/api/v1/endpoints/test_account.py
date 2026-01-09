"""
Test endpoint for simulating account data and rule violations.

This allows testing the full flow without a real NinjaTrader connection.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from app.core.database import get_db
from app.models.user import User
from app.models.account import ConnectedAccount
from app.api.v1.endpoints.auth import get_current_user
from app.services.account_tracker import account_tracker
from rules_engine.interface import AccountSnapshot, PositionSnapshot
from rules_engine.engine import RuleEngine
from app.services.rule_loader import RuleLoaderService

router = APIRouter()


@router.post("/simulate-account-data/{account_id}")
async def simulate_account_data(
    account_id: str,
    scenario: str = "normal",  # normal, near_drawdown, near_daily_limit, violated
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Simulate account data for testing.
    
    Scenarios:
    - normal: Account in good standing
    - near_drawdown: Close to trailing drawdown violation
    - near_daily_limit: Close to daily loss limit
    - violated: Account has violated a rule
    - high_profit: Account with good profit, far from limits
    """
    # Get the account
    account = db.query(ConnectedAccount).filter(
        ConnectedAccount.id == account_id,
        ConnectedAccount.user_id == current_user.id,
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    # Load rules
    rule_loader = RuleLoaderService()
    rules = await rule_loader.get_rules(account.firm, account.account_type, account.rule_set_version)
    
    # Calculate scenario values
    starting_balance = Decimal(account.account_size) / Decimal("100")
    high_water_mark = starting_balance
    
    if scenario == "normal":
        equity = starting_balance * Decimal("0.98")  # 2% down
        daily_pnl = Decimal("-500")
        unrealized_pnl = Decimal("0")
        high_water_mark = starting_balance
        
    elif scenario == "near_drawdown":
        # Close to drawdown violation (e.g., 4.8% down when limit is 5%)
        drawdown_percent = Decimal("4.8")
        equity = starting_balance * (Decimal("1") - drawdown_percent / Decimal("100"))
        daily_pnl = Decimal("-2000")
        unrealized_pnl = Decimal("-400")
        high_water_mark = starting_balance
        
    elif scenario == "near_daily_limit":
        # Close to daily loss limit
        if rules.daily_loss_limit:
            daily_pnl = -rules.daily_loss_limit.max_loss_amount * Decimal("0.95")  # 95% of limit
        else:
            daily_pnl = Decimal("-1000")
        equity = starting_balance + daily_pnl
        unrealized_pnl = Decimal("0")
        high_water_mark = starting_balance
        
    elif scenario == "violated":
        # Account has violated a rule
        equity = starting_balance * Decimal("0.94")  # 6% down (violated 5% limit)
        daily_pnl = Decimal("-3000")
        unrealized_pnl = Decimal("-500")
        high_water_mark = starting_balance
        
    elif scenario == "high_profit":
        # Account with good profit
        equity = starting_balance * Decimal("1.10")  # 10% profit
        daily_pnl = Decimal("2000")
        unrealized_pnl = Decimal("500")
        high_water_mark = equity
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown scenario: {scenario}. Use: normal, near_drawdown, near_daily_limit, violated, high_profit",
        )
    
    # Create account snapshot
    snapshot = AccountSnapshot(
        account_id=account.id,
        timestamp=datetime.utcnow(),
        equity=equity,
        balance=equity - unrealized_pnl,
        realized_pnl=daily_pnl - unrealized_pnl,
        unrealized_pnl=unrealized_pnl,
        high_water_mark=high_water_mark,
        daily_pnl=daily_pnl,
        starting_balance=starting_balance,
        open_positions=[
            PositionSnapshot(
                symbol="ES 03-26",
                quantity=2,
                avg_price=Decimal("4000.00"),
                current_price=Decimal("4001.00") if unrealized_pnl > 0 else Decimal("3999.00"),
                unrealized_pnl=unrealized_pnl,
                opened_at=datetime.utcnow() - timedelta(hours=1),
                peak_unrealized_loss=Decimal("-200") if unrealized_pnl < 0 else Decimal("0"),
            )
        ] if abs(unrealized_pnl) > 0 else [],
    )
    
    # Evaluate rules
    engine = RuleEngine(rules)
    result = engine.evaluate(snapshot)
    
    # Update account state
    await account_tracker._update_account_state(account.id, db, snapshot=snapshot, result=result)
    
    return {
        "success": True,
        "scenario": scenario,
        "account_state": {
            "equity": float(snapshot.equity),
            "balance": float(snapshot.balance),
            "daily_pnl": float(snapshot.daily_pnl),
            "unrealized_pnl": float(snapshot.unrealized_pnl),
            "high_water_mark": float(snapshot.high_water_mark),
        },
        "rule_states": {
            name: {
                "status": state.status.value if hasattr(state.status, 'value') else str(state.status),
                "remaining_buffer": float(state.remaining_buffer),
                "buffer_percent": float(state.buffer_percent),
                "recoverable": state.recoverable.value if hasattr(state.recoverable, 'value') else str(state.recoverable),
                "severity": state.severity.value if hasattr(state.severity, 'value') else str(state.severity),
                "warnings": state.warnings,
                "recovery_path": state.recovery_path if hasattr(state, 'recovery_path') else None,
            }
            for name, state in result.rule_states.items()
        },
        "overall_risk_level": result.overall_risk_level,
        "max_allowed_risk": {k: float(v) for k, v in result.max_allowed_risk.items()},
    }


@router.get("/test-scenarios")
async def get_test_scenarios():
    """Get list of available test scenarios."""
    return {
        "scenarios": [
            {
                "id": "normal",
                "name": "Normal Trading",
                "description": "Account in good standing, 2% down from starting balance",
            },
            {
                "id": "near_drawdown",
                "name": "Near Drawdown Violation",
                "description": "Close to trailing drawdown limit (4.8% down, limit is 5%)",
            },
            {
                "id": "near_daily_limit",
                "name": "Near Daily Loss Limit",
                "description": "Close to daily loss limit (95% of limit used)",
            },
            {
                "id": "violated",
                "name": "Rule Violated",
                "description": "Account has violated a rule (6% down, limit is 5%)",
            },
            {
                "id": "high_profit",
                "name": "High Profit",
                "description": "Account with good profit, far from limits",
            },
        ]
    }

