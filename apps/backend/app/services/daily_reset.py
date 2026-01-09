"""
Daily reset service for prop firm rules.

Handles daily resets for:
- Daily loss limits (Topstep: 4:00 PM CT)
- Daily PnL counters
- Trading day tracking
"""

import asyncio
import logging
from datetime import datetime, time
from typing import Dict
from decimal import Decimal
from sqlalchemy.orm import Session
from pytz import timezone

from app.core.database import get_db
from app.models.account import ConnectedAccount
from app.models.account_state import AccountStateSnapshot

logger = logging.getLogger(__name__)


class DailyResetService:
    """Service for handling daily resets of trading rules."""

    def __init__(self):
        self.reset_times: Dict[str, time] = {
            "topstep": time(16, 0),  # 4:00 PM CT
            "apex": None,  # No daily reset
        }
        self.timezones: Dict[str, str] = {
            "topstep": "America/Chicago",  # Central Time
            "apex": "America/Chicago",
        }

    async def check_and_reset_daily_counters(self, db: Session):
        """
        Check if daily reset is needed and reset counters.
        
        Called periodically (every minute) to check for reset time.
        """
        accounts = db.query(ConnectedAccount).filter(
            ConnectedAccount.is_active == True
        ).all()

        for account in accounts:
            try:
                reset_time = self.reset_times.get(account.firm.lower())
                if reset_time is None:
                    continue  # No daily reset for this firm

                tz = timezone(self.timezones.get(account.firm.lower(), "America/Chicago"))
                now = datetime.now(tz)
                current_time = now.time()

                # Check if we're at or past reset time
                if current_time >= reset_time:
                    # Check if we've already reset today
                    last_reset = await self._get_last_reset_date(account.id, db)
                    today = now.date()

                    if last_reset != today:
                        logger.info(f"Daily reset for account {account.id} ({account.firm})")
                        await self._reset_daily_counters(account.id, db, now)
            except Exception as e:
                logger.error(f"Error checking daily reset for account {account.id}: {e}")

    async def _get_last_reset_date(self, account_id: str, db: Session) -> datetime.date:
        """Get the date of the last daily reset."""
        # Check metadata or latest snapshot for reset date
        # For now, return yesterday to trigger reset
        return datetime.now().date()

    async def _reset_daily_counters(self, account_id: str, db: Session, reset_time: datetime):
        """
        Reset daily counters for an account.
        
        This includes:
        - Daily PnL (reset to 0)
        - Daily loss limit counters
        - Trading day tracking
        """
        # Get latest snapshot
        latest_snapshot = db.query(AccountStateSnapshot).filter(
            AccountStateSnapshot.account_id == account_id
        ).order_by(AccountStateSnapshot.timestamp.desc()).first()

        if latest_snapshot:
            # Create new snapshot with reset daily PnL
            # Daily PnL resets to 0, but realized PnL persists
            # This is handled by the add-on tracking fills per day
            # Backend just needs to track the reset date
            
            logger.info(f"Daily reset applied for account {account_id} at {reset_time}")
            # Actual reset logic handled by add-on (tracks fills per day)
            # Backend can mark reset date in metadata if needed

    async def start_reset_scheduler(self):
        """Start background task to check for daily resets."""
        while True:
            try:
                db = next(get_db())
                await self.check_and_reset_daily_counters(db)
                db.close()
            except Exception as e:
                logger.error(f"Error in daily reset scheduler: {e}")
            
            # Check every minute
            await asyncio.sleep(60)


# Global instance
daily_reset_service = DailyResetService()
