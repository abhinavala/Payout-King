"""
NinjaTrader Add-On endpoint for receiving account data.

This endpoint receives data from the NinjaTrader Add-On and processes it.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from decimal import Decimal
import logging

from app.core.database import get_db
from app.models.account import ConnectedAccount
from app.services.account_tracker import account_tracker
from rules_engine.interface import AccountSnapshot, PositionSnapshot
from rules_engine.engine import RuleEngine
from app.services.rule_loader import RuleLoaderService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/account-update")
async def receive_ninjatrader_account_update(
    data: dict,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Receive account update from NinjaTrader Add-On.
    
    Matches AccountUpdateMessage schema from add-on.
    
    This endpoint:
    1. Receives AccountUpdateMessage from NinjaTrader
    2. Converts to AccountSnapshot format
    3. Backend tracks HWM (updates if equity exceeds current HWM)
    4. Evaluates rules
    5. Stores snapshot
    6. Pushes updates via WebSocket
    
    Backend is source of truth for HWM and daily PnL history.
    """
    try:
        # Extract account ID
        account_id = data.get("accountId")
        if not account_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing accountId",
            )

        logger.info(f"Received data from NinjaTrader account: {account_id}")

        # Find connected account
        # Try exact match first
        connected_account = db.query(ConnectedAccount).filter(
            ConnectedAccount.account_id == account_id,
            ConnectedAccount.platform == "ninjatrader",
            ConnectedAccount.is_active == True,
        ).first()

        # If not found, try case-insensitive match
        if not connected_account:
            connected_account = db.query(ConnectedAccount).filter(
                ConnectedAccount.account_id.ilike(account_id),
                ConnectedAccount.platform == "ninjatrader",
                ConnectedAccount.is_active == True,
            ).first()

        if not connected_account:
            # Log available accounts for debugging
            available_accounts = db.query(ConnectedAccount).filter(
                ConnectedAccount.platform == "ninjatrader",
                ConnectedAccount.is_active == True,
            ).all()
            available_ids = [acc.account_id for acc in available_accounts]
            
            logger.warning(f"Account '{account_id}' not found. Available: {available_ids}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account '{account_id}' not found. Available accounts: {available_ids}",
            )

        logger.info(f"Found connected account: {connected_account.id} ({connected_account.account_name})")

        # Convert to AccountSnapshot
        try:
            timestamp_str = data.get("timestamp", "")
            if timestamp_str.endswith("Z"):
                timestamp_str = timestamp_str.replace("Z", "+00:00")
            
            # Parse timestamp (can be Unix milliseconds or ISO string)
            timestamp_value = data.get("timestamp", 0)
            if isinstance(timestamp_value, (int, float)):
                # Unix timestamp in milliseconds
                timestamp = datetime.utcfromtimestamp(timestamp_value / 1000.0)
            else:
                # ISO string
                timestamp_str = str(timestamp_value)
                if timestamp_str.endswith("Z"):
                    timestamp_str = timestamp_str.replace("Z", "+00:00")
                timestamp = datetime.fromisoformat(timestamp_str)
            
            # Convert daily PnL history from add-on
            daily_pnl_history = {}
            if "dailyPnlHistory" in data and data["dailyPnlHistory"]:
                daily_pnl_history = {
                    str(k): Decimal(str(v))
                    for k, v in data["dailyPnlHistory"].items()
                }
            
            snapshot = AccountSnapshot(
                account_id=connected_account.id,  # Use internal ID
                timestamp=timestamp,
                equity=Decimal(str(data.get("equity", 0))),
                balance=Decimal(str(data.get("balance", data.get("equity", 0)))),
                realized_pnl=Decimal(str(data.get("realizedPnl", data.get("realizedPnL", 0)))),
                unrealized_pnl=Decimal(str(data.get("unrealizedPnl", data.get("unrealizedPnL", 0)))),
                # HWM will be updated by backend (source of truth)
                high_water_mark=Decimal(str(data.get("highWaterMark", data.get("equity", 0)))),
                daily_pnl=Decimal(str(data.get("dailyPnl", data.get("dailyPnL", 0)))),
                starting_balance=Decimal(str(connected_account.account_size)) / Decimal("100"),
                open_positions=[
                    PositionSnapshot(
                        symbol=pos.get("symbol", "UNKNOWN"),
                        quantity=int(pos.get("quantity", 0)),
                        avg_price=Decimal(str(pos.get("avgPrice", 0))),
                        current_price=Decimal(str(pos.get("currentPrice", pos.get("avgPrice", 0)))),
                        unrealized_pnl=Decimal(str(pos.get("unrealizedPnl", pos.get("unrealizedPnL", 0)))),
                        opened_at=datetime.fromtimestamp(
                            pos.get("openedAt", int(datetime.utcnow().timestamp() * 1000)) / 1000.0
                        ) if isinstance(pos.get("openedAt"), (int, float)) else datetime.fromisoformat(
                            pos.get("openedAt", datetime.utcnow().isoformat()).replace("Z", "+00:00")
                        ),
                        peak_unrealized_loss=Decimal(str(pos.get("peakUnrealizedLoss", 0))),
                    )
                    for pos in data.get("openPositions", [])
                ],
                daily_pnl_history=daily_pnl_history,
            )
        except Exception as e:
            logger.error(f"Error converting to AccountSnapshot: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error parsing account data: {str(e)}",
            )

        # Load rules and evaluate
        rule_loader = RuleLoaderService()
        rules = await rule_loader.get_rules(
            connected_account.firm,
            connected_account.account_type,
            connected_account.rule_set_version,
        )
        engine = RuleEngine(rules)
        result = engine.evaluate(snapshot)

        logger.info(f"Rule evaluation complete. Risk level: {result.overall_risk_level}")

        # Store snapshot (via account tracker service)
        # Backend tracks HWM and daily PnL history
        await account_tracker._update_account_state(
            connected_account.id, 
            db, 
            snapshot=snapshot, 
            result=result,
            daily_pnl_history=daily_pnl_history
        )

        return {
            "success": True,
            "riskLevel": result.overall_risk_level,
            "ruleStates": {
                name: {
                    "status": state.status,
                    "remainingBuffer": float(state.remaining_buffer),
                    "bufferPercent": float(state.buffer_percent),
                }
                for name, state in result.rule_states.items()
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing account data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing account data: {str(e)}",
        )


@router.get("/health")
async def health_check():
    """Health check for NinjaTrader endpoint."""
    return {"status": "ok", "service": "ninjatrader-endpoint"}


@router.get("/debug/accounts")
async def debug_accounts(
    db: Session = Depends(get_db),
):
    """Debug endpoint to list all connected NinjaTrader accounts."""
    accounts = db.query(ConnectedAccount).filter(
        ConnectedAccount.platform == "ninjatrader",
        ConnectedAccount.is_active == True,
    ).all()
    
    return {
        "accounts": [
            {
                "id": acc.id,
                "account_id": acc.account_id,
                "account_name": acc.account_name,
                "firm": acc.firm,
                "account_type": acc.account_type,
                "is_active": acc.is_active,
            }
            for acc in accounts
        ]
    }
