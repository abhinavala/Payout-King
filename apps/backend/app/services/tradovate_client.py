"""
Tradovate API client for account data ingestion.
"""

import httpx
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime

from app.core.config import settings


class TradovateClient:
    """Client for interacting with Tradovate API."""

    def __init__(self, access_token: str):
        """
        Initialize Tradovate client.
        
        Args:
            access_token: Tradovate access token (from OAuth authentication)
        """
        self.access_token = access_token
        self.base_url = settings.TRADOVATE_API_URL
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def get_account_list(self) -> List[Dict]:
        """Get list of all accounts."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/account/list",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_account_balance(self, account_id: str) -> Dict:
        """Get current account balance and equity."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/account/{account_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            data = response.json()
            # Extract balance and equity (field names TBD based on actual response)
            return {
                "balance": Decimal(str(data.get("balance", data.get("accountBalance", 0)))),
                "equity": Decimal(str(data.get("netLiquidation", data.get("equity", data.get("accountEquity", 0))))),
                "realized_pnl": Decimal(str(data.get("realizedPnL", data.get("realizedPnl", 0)))),
            }

    async def get_open_positions(self, account_id: str) -> List[Dict]:
        """Get open positions."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/position/list",
                headers=self.headers,
                params={"accountId": account_id},
            )
            response.raise_for_status()
            return response.json()

    async def get_daily_pnl(self, account_id: str, date: Optional[datetime] = None) -> Decimal:
        """Get daily PnL for a specific date (defaults to today)."""
        # TODO: Implement daily PnL calculation from fills/orders
        # This is a placeholder
        return Decimal("0")

    async def get_account_state(self, account_id: str) -> Dict:
        """
        Get complete account state for rule engine.
        
        Returns a dictionary compatible with AccountState model.
        """
        balance_data = await self.get_account_balance(account_id)
        positions = await self.get_open_positions(account_id)
        daily_pnl = await self.get_daily_pnl(account_id)
        
        # Calculate unrealized PnL from positions
        unrealized_pnl = sum(
            Decimal(str(pos.get("unrealizedPnL", 0))) for pos in positions
        )
        
        # Calculate equity
        equity = balance_data["balance"] + unrealized_pnl
        
        return {
            "account_id": account_id,
            "timestamp": datetime.utcnow(),
            "equity": equity,
            "balance": balance_data["balance"],
            "realized_pnl": balance_data["realized_pnl"],
            "unrealized_pnl": unrealized_pnl,
            "high_water_mark": equity,  # TODO: Track this over time
            "daily_pnl": daily_pnl,
            "open_positions": [
                {
                    "symbol": pos.get("symbol"),
                    "quantity": pos.get("quantity", 0),
                    "avg_price": Decimal(str(pos.get("avgPrice", 0))),
                    "current_price": Decimal(str(pos.get("lastPrice", 0))),
                    "unrealized_pnl": Decimal(str(pos.get("unrealizedPnL", 0))),
                    "opened_at": datetime.fromisoformat(pos.get("timestamp", datetime.utcnow().isoformat())),
                }
                for pos in positions
            ],
        }

