"""
Service for tracking account states and calculating rule compliance.
"""

import asyncio
import uuid
import logging
import json
from typing import Dict, Optional, Any
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.account import ConnectedAccount
from app.models.account_state import AccountStateSnapshot
from app.services.tradovate_client import TradovateClient
from app.core.security import decrypt_api_token
from app.services.rule_loader import RuleLoaderService
from app.services.tradovate_auth import TradovateAuthService
from rules_engine.engine import RuleEngine
from rules_engine.interface import AccountSnapshot, RuleEvaluationResult, PositionSnapshot

logger = logging.getLogger(__name__)


def convert_decimals_to_float(obj: Any) -> Any:
    """Recursively convert Decimal objects to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals_to_float(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_decimals_to_float(item) for item in obj)
    else:
        return obj

# Import manager lazily to avoid circular import
def get_websocket_manager():
    from app.api.v1.endpoints.websocket import manager
    return manager


class AccountTrackerService:
    """Service for tracking accounts and calculating rule states."""

    def __init__(self):
        self.tracking_tasks: Dict[str, asyncio.Task] = {}
        self.rule_loader = RuleLoaderService()
        self.auth_service = TradovateAuthService()

    async def start_tracking(self, account_id: str, db: Session):
        """Start tracking an account."""
        if account_id in self.tracking_tasks:
            return  # Already tracking
        
        account = db.query(ConnectedAccount).filter(
            ConnectedAccount.id == account_id,
            ConnectedAccount.is_active == True,
        ).first()
        
        if not account:
            raise ValueError(f"Account {account_id} not found or inactive")
        
        # Start background task
        task = asyncio.create_task(self._track_account_loop(account_id, db))
        self.tracking_tasks[account_id] = task

    async def stop_tracking(self, account_id: str):
        """Stop tracking an account."""
        if account_id in self.tracking_tasks:
            self.tracking_tasks[account_id].cancel()
            del self.tracking_tasks[account_id]

    async def _track_account_loop(self, account_id: str, db: Session):
        """Background loop for tracking an account."""
        while True:
            try:
                await self._update_account_state(account_id, db, snapshot=None, result=None)
                await asyncio.sleep(5)  # Update every 5 seconds (only for polling platforms)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error tracking account {account_id}: {e}")
                await asyncio.sleep(10)  # Wait longer on error

    def _get_high_water_mark(self, account_id: str, db: Session, current_equity: Decimal) -> Decimal:
        """
        Get or update high-water mark for account.
        
        Backend is source of truth for HWM.
        Updates HWM if current equity exceeds it.
        """
        # Get latest snapshot to find current HWM
        latest_snapshot = db.query(AccountStateSnapshot).filter(
            AccountStateSnapshot.account_id == account_id
        ).order_by(AccountStateSnapshot.timestamp.desc()).first()
        
        if latest_snapshot:
            current_hwm = Decimal(str(latest_snapshot.high_water_mark))
        else:
            # First snapshot - use starting balance as initial HWM
            account = db.query(ConnectedAccount).filter(
                ConnectedAccount.id == account_id
            ).first()
            if account:
                current_hwm = Decimal(str(account.account_size)) / Decimal("100")
            else:
                current_hwm = current_equity
        
        # Update HWM if current equity exceeds it
        if current_equity > current_hwm:
            new_hwm = current_equity
        else:
            new_hwm = current_hwm
        
        return new_hwm

    def _get_daily_pnl_history(self, account_id: str, db: Session) -> Dict[str, Decimal]:
        """
        Get daily PnL history for account.
        
        Backend tracks this from snapshots or can use provided history from add-on.
        """
        # TODO: Build from historical snapshots or use provided history
        # For now, return empty - will be populated from add-on data
        return {}

    async def _update_account_state(
        self, account_id: str, db: Session, 
        snapshot: Optional[AccountSnapshot] = None,
        result: Optional[RuleEvaluationResult] = None,
        daily_pnl_history: Optional[Dict[str, Decimal]] = None
    ):
        """
        Update account state and calculate rule compliance.
        
        Backend is source of truth for:
        - High-water mark (tracks and updates)
        - Daily PnL history (tracks from snapshots)
        - Starting balance (from account metadata)
        
        Can be called with pre-computed snapshot (from NinjaTrader) or fetch from platform.
        """
        account = db.query(ConnectedAccount).filter(
            ConnectedAccount.id == account_id
        ).first()
        
        if not account or not account.is_active:
            await self.stop_tracking(account_id)
            return
        
        # If snapshot provided (from NinjaTrader), use it but update HWM
        if snapshot is not None and result is not None:
            # Backend tracks HWM - update if equity exceeds current HWM
            current_hwm = self._get_high_water_mark(account_id, db, snapshot.equity)
            
            # Update snapshot with backend-tracked HWM
            snapshot.high_water_mark = current_hwm
            
            # Use provided daily PnL history or get from backend
            if daily_pnl_history:
                snapshot.daily_pnl_history = daily_pnl_history
            else:
                snapshot.daily_pnl_history = self._get_daily_pnl_history(account_id, db)
            
            engine_state = snapshot
            rule_states = result.rule_states
        else:
            # Otherwise, fetch from platform (Tradovate, etc.)
            if account.platform == "tradovate":
                username, password = self.auth_service.get_decrypted_credentials(account)
                access_token = await self.auth_service.get_access_token_for_account(account)
                client = TradovateClient(access_token)
            else:
                raise ValueError(f"Unsupported platform: {account.platform}")
            
            # Fetch account state from platform
            state_data = await client.get_account_state(account.account_id)
            
            # Get HWM from backend (source of truth)
            current_equity = Decimal(str(state_data["equity"]))
            current_hwm = self._get_high_water_mark(account_id, db, current_equity)
            
            # Get daily PnL history
            daily_pnl_history = self._get_daily_pnl_history(account_id, db)
            
            # Convert to AccountSnapshot
            engine_state = AccountSnapshot(
                account_id=account_id,
                timestamp=state_data["timestamp"],
                equity=current_equity,
                balance=state_data["balance"],
                realized_pnl=state_data["realized_pnl"],
                unrealized_pnl=state_data["unrealized_pnl"],
                high_water_mark=current_hwm,  # Backend-tracked HWM
                daily_pnl=state_data["daily_pnl"],
                starting_balance=Decimal(str(account.account_size)) / Decimal("100"),
                open_positions=[
                    PositionSnapshot(
                        symbol=pos["symbol"],
                        quantity=pos["quantity"],
                        avg_price=pos["avg_price"],
                        current_price=pos["current_price"],
                        unrealized_pnl=pos["unrealized_pnl"],
                        opened_at=pos["opened_at"],
                        peak_unrealized_loss=pos.get("peak_unrealized_loss", Decimal("0")),
                    )
                    for pos in state_data["open_positions"]
                ],
                daily_pnl_history=daily_pnl_history,
            )
            
            # Load rule set and evaluate
            rules = await self.rule_loader.get_rules(account.firm, account.account_type, account.rule_set_version)
            rule_engine = RuleEngine(rules)
            result = rule_engine.evaluate(engine_state)
            rule_states = result.rule_states
        
        # Get previous snapshot for comparison
        previous_snapshot = (
            db.query(AccountStateSnapshot)
            .filter(AccountStateSnapshot.account_id == account_id)
            .order_by(AccountStateSnapshot.timestamp.desc())
            .first()
        )
        previous_rule_states = previous_snapshot.rule_states if previous_snapshot else {}
        
        # Convert rule states and positions to dict, then convert Decimals to float for JSON serialization
        rule_states_dict = {k: v.dict() for k, v in rule_states.items()}
        rule_states_dict = convert_decimals_to_float(rule_states_dict)
        
        open_positions_list = [pos.dict() for pos in engine_state.open_positions]
        open_positions_list = convert_decimals_to_float(open_positions_list)
        
        # Save snapshot with backend-tracked HWM
        snapshot_db = AccountStateSnapshot(
            id=str(uuid.uuid4()),
            account_id=account_id,
            timestamp=engine_state.timestamp,
            equity=float(engine_state.equity),
            balance=float(engine_state.balance),
            realized_pnl=float(engine_state.realized_pnl),
            unrealized_pnl=float(engine_state.unrealized_pnl),
            high_water_mark=float(engine_state.high_water_mark),  # Backend-tracked HWM
            daily_pnl=float(engine_state.daily_pnl),
            open_positions=open_positions_list,
            rule_states=rule_states_dict,
        )
        db.add(snapshot_db)
        db.commit()
        
        # Audit logging: Log warnings, violations, and state changes
        from app.services.audit_logger import audit_logger
        
        # Log HWM update if it changed
        if engine_state.equity > Decimal(str(snapshot_db.high_water_mark)):
            logger.info(f"HWM updated for account {account_id}: {float(engine_state.high_water_mark)}")
            audit_logger.log_account_update(
                db,
                account,
                f"High-water mark updated to ${float(engine_state.high_water_mark):.2f}",
                {"new_hwm": float(engine_state.high_water_mark), "equity": float(engine_state.equity)},
            )
        
        # Log rule state changes, warnings, and violations
        for rule_name, rule_state in rule_states.items():
            # Handle both Pydantic model and dict formats
            if hasattr(rule_state, 'status'):
                current_status = rule_state.status.value if hasattr(rule_state.status, 'value') else str(rule_state.status)
                remaining_buffer = float(rule_state.remaining_buffer) if hasattr(rule_state, 'remaining_buffer') else 0
                buffer_percent = float(rule_state.buffer_percent) if hasattr(rule_state, 'buffer_percent') else 0
                warnings = rule_state.warnings if hasattr(rule_state, 'warnings') else []
            else:
                # Dict format from JSON
                current_status = rule_state.get("status", "safe")
                remaining_buffer = float(rule_state.get("remainingBuffer", 0))
                buffer_percent = float(rule_state.get("bufferPercent", 0))
                warnings = rule_state.get("warnings", [])
            
            previous_rule_state = previous_rule_states.get(rule_name, {})
            previous_status = previous_rule_state.get("status") if previous_rule_state else None
            
            # Log rule evaluation
            audit_logger.log_rule_evaluation(
                db,
                account,
                rule_name,
                current_status,
                {
                    "remainingBuffer": remaining_buffer,
                    "bufferPercent": buffer_percent,
                    "warnings": warnings,
                },
            )
            
            # Log state change if status changed
            if previous_status and previous_status != current_status:
                audit_logger.log_state_change(
                    db,
                    account,
                    rule_name,
                    previous_status,
                    current_status,
                    f"Rule {rule_name} status changed from {previous_status} to {current_status}",
                    {
                        "previousStatus": previous_status,
                        "currentStatus": current_status,
                        "remainingBuffer": remaining_buffer,
                        "bufferPercent": buffer_percent,
                    },
                )
            
            # Log warnings (caution/critical)
            if current_status in ["caution", "critical"]:
                warning_msg = f"Rule {rule_name} in {current_status} status. Buffer: ${remaining_buffer:.2f} ({buffer_percent:.1f}%)"
                if warnings:
                    warning_msg += f". {warnings[0]}"
                audit_logger.log_warning(
                    db,
                    account,
                    rule_name,
                    previous_status,
                    current_status,
                    warning_msg,
                    {
                        "remainingBuffer": remaining_buffer,
                        "bufferPercent": buffer_percent,
                        "warnings": warnings,
                    },
                )
            
            # Log violations
            if current_status == "violated":
                violation_msg = f"Rule {rule_name} VIOLATED. Buffer: ${remaining_buffer:.2f}"
                if warnings:
                    violation_msg += f". {warnings[0]}"
                audit_logger.log_violation(
                    db,
                    account,
                    rule_name,
                    previous_status,
                    violation_msg,
                    {
                        "remainingBuffer": remaining_buffer,
                        "bufferPercent": buffer_percent,
                        "warnings": warnings,
                    },
                )
        
        # Send WebSocket update
        manager = get_websocket_manager()
        await manager.send_to_account(
            account_id,
            {
                "type": "account_state_update",
                "accountId": account_id,
                "data": {
                    "equity": float(engine_state.equity),
                    "balance": float(engine_state.balance),
                    "ruleStates": {k: v.dict() for k, v in rule_states.items()},
                },
                "timestamp": engine_state.timestamp.isoformat(),
            }
        )
        
        # Send group updates for all groups containing this account
        from app.models.account_group import AccountGroup
        from app.api.v1.endpoints.groups import get_group_risk_evaluation
        
        groups = db.query(AccountGroup).filter(
            AccountGroup.accounts.any(ConnectedAccount.id == account_id)
        ).all()
        
        for group in groups:
            try:
                evaluation = get_group_risk_evaluation(group, db)
                evaluation.timestamp = engine_state.timestamp.isoformat()
                await manager.send_to_group(
                    group.id,
                    {
                        "type": "group_risk_update",
                        "groupId": group.id,
                        "data": evaluation.dict(),
                        "timestamp": engine_state.timestamp.isoformat(),
                    }
                )
            except Exception as e:
                logger.error(f"Error sending group update for group {group.id}: {e}")


# Global instance
account_tracker = AccountTrackerService()

