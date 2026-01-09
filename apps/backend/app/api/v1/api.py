"""
API v1 router.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, accounts, websocket, ninjatrader, firms, test_account, groups, audit_logs

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
api_router.include_router(ninjatrader.router, prefix="/ninjatrader", tags=["ninjatrader"])
api_router.include_router(firms.router, prefix="/firms", tags=["firms"])
api_router.include_router(test_account.router, prefix="/test", tags=["testing"])
api_router.include_router(groups.router, prefix="/groups", tags=["groups"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit"])

