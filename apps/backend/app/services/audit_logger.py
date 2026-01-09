"""
Audit logging service for tracking all warnings, state changes, and violations.
"""

import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog, AuditEventType
from app.models.account import ConnectedAccount


class AuditLoggerService:
    """Service for logging audit events."""

    @staticmethod
    def log_warning(
        db: Session,
        account: ConnectedAccount,
        rule_name: str,
        previous_status: Optional[str],
        current_status: str,
        message: str,
        event_data: Optional[Dict[str, Any]] = None,
    ):
        """Log a rule warning (caution/critical status)."""
        log = AuditLog(
            id=str(uuid.uuid4()),
            account_id=account.id,
            user_id=account.user_id,
            event_type=AuditEventType.WARNING,
            rule_name=rule_name,
            previous_status=previous_status,
            current_status=current_status,
            message=message,
            event_data=event_data or {},
            timestamp=datetime.utcnow(),
        )
        db.add(log)
        db.commit()

    @staticmethod
    def log_violation(
        db: Session,
        account: ConnectedAccount,
        rule_name: str,
        previous_status: Optional[str],
        message: str,
        event_data: Optional[Dict[str, Any]] = None,
    ):
        """Log a rule violation."""
        log = AuditLog(
            id=str(uuid.uuid4()),
            account_id=account.id,
            user_id=account.user_id,
            event_type=AuditEventType.VIOLATION,
            rule_name=rule_name,
            previous_status=previous_status,
            current_status="violated",
            message=message,
            event_data=event_data or {},
            timestamp=datetime.utcnow(),
        )
        db.add(log)
        db.commit()

    @staticmethod
    def log_state_change(
        db: Session,
        account: ConnectedAccount,
        rule_name: Optional[str],
        previous_status: Optional[str],
        current_status: str,
        message: str,
        event_data: Optional[Dict[str, Any]] = None,
    ):
        """Log an account state change."""
        log = AuditLog(
            id=str(uuid.uuid4()),
            account_id=account.id,
            user_id=account.user_id,
            event_type=AuditEventType.STATE_CHANGE,
            rule_name=rule_name,
            previous_status=previous_status,
            current_status=current_status,
            message=message,
            event_data=event_data or {},
            timestamp=datetime.utcnow(),
        )
        db.add(log)
        db.commit()

    @staticmethod
    def log_rule_evaluation(
        db: Session,
        account: ConnectedAccount,
        rule_name: str,
        status: str,
        event_data: Optional[Dict[str, Any]] = None,
    ):
        """Log a rule evaluation."""
        log = AuditLog(
            id=str(uuid.uuid4()),
            account_id=account.id,
            user_id=account.user_id,
            event_type=AuditEventType.RULE_EVALUATION,
            rule_name=rule_name,
            current_status=status,
            message=f"Rule {rule_name} evaluated: {status}",
            event_data=event_data or {},
            timestamp=datetime.utcnow(),
        )
        db.add(log)
        db.commit()

    @staticmethod
    def log_account_update(
        db: Session,
        account: ConnectedAccount,
        message: str,
        event_data: Optional[Dict[str, Any]] = None,
    ):
        """Log an account data update."""
        log = AuditLog(
            id=str(uuid.uuid4()),
            account_id=account.id,
            user_id=account.user_id,
            event_type=AuditEventType.ACCOUNT_UPDATE,
            message=message,
            event_data=event_data or {},
            timestamp=datetime.utcnow(),
        )
        db.add(log)
        db.commit()

    @staticmethod
    def log_group_update(
        db: Session,
        group_id: str,
        user_id: str,
        message: str,
        event_data: Optional[Dict[str, Any]] = None,
    ):
        """Log a group risk update."""
        log = AuditLog(
            id=str(uuid.uuid4()),
            group_id=group_id,
            user_id=user_id,
            event_type=AuditEventType.GROUP_UPDATE,
            message=message,
            event_data=event_data or {},
            timestamp=datetime.utcnow(),
        )
        db.add(log)
        db.commit()


# Global instance
audit_logger = AuditLoggerService()
