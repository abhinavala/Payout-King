"""
Account management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.models.user import User
from app.models.account import ConnectedAccount
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.account import AccountCreate, AccountResponse, AccountListResponse

router = APIRouter()


@router.get("/", response_model=AccountListResponse)
async def list_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all connected accounts for the current user."""
    accounts = db.query(ConnectedAccount).filter(
        ConnectedAccount.user_id == current_user.id,
        ConnectedAccount.is_active == True,
    ).all()
    
    return AccountListResponse(
        accounts=[
            AccountResponse(
                id=acc.id,
                userId=acc.user_id,
                platform=acc.platform,
                accountId=acc.account_id,
                accountName=acc.account_name,
                firm=acc.firm,
                accountType=acc.account_type,
                accountSize=acc.account_size / 100,  # Convert cents to dollars
                ruleSetVersion=acc.rule_set_version,
                isActive=acc.is_active,
                createdAt=acc.created_at.isoformat(),
                updatedAt=acc.updated_at.isoformat() if acc.updated_at else acc.created_at.isoformat(),
            )
            for acc in accounts
        ]
    )


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Connect a new trading account.
    
    This endpoint:
    1. For Tradovate: Verifies API credentials with the platform
    2. For NinjaTrader: Creates account record (Add-On handles auth)
    3. Encrypts and stores credentials (if needed)
    4. Creates the ConnectedAccount record
    """
    # Check if platform is supported
    supported_platforms = ["ninjatrader", "tradovate", "rithmic"]
    if account_data.platform not in supported_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform {account_data.platform} not supported. Supported: {', '.join(supported_platforms)}",
        )
    
    # Handle different platforms
    if account_data.platform == "ninjatrader":
        # NinjaTrader: No API credentials needed, Add-On handles authentication
        # Just create the account record
        account = ConnectedAccount(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            platform="ninjatrader",
            account_id=account_data.accountId,
            account_name=account_data.accountName or account_data.accountId,
            firm=account_data.firm,
            account_type=account_data.accountType,
            account_size=int(account_data.accountSize * 100),  # Convert to cents
            rule_set_version=account_data.ruleSetVersion,
            encrypted_api_token=None,  # Not needed for NinjaTrader
            encrypted_api_secret=None,
            is_active=True,
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        
    elif account_data.platform == "tradovate":
        # Tradovate: Verify credentials and connect
        from app.services.tradovate_auth import TradovateAuthService, TradovateAuthError
        
        auth_service = TradovateAuthService()
        
        try:
            account = await auth_service.connect_account(
                user_id=current_user.id,
                account_data={
                    "accountId": account_data.accountId,
                    "accountName": account_data.accountName,
                    "firm": account_data.firm,
                    "accountType": account_data.accountType,
                    "accountSize": account_data.accountSize,
                    "ruleSetVersion": account_data.ruleSetVersion,
                },
                username=account_data.username,
                password=account_data.password,
                db=db,
            )
        except TradovateAuthError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
    else:
        # Rithmic or other platforms - not yet implemented
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform {account_data.platform} integration not yet implemented.",
        )
    
    return AccountResponse(
        id=account.id,
        userId=account.user_id,
        platform=account.platform,
        accountId=account.account_id,
        accountName=account.account_name,
        firm=account.firm,
        accountType=account.account_type,
        accountSize=account.account_size / 100,
        ruleSetVersion=account.rule_set_version,
        isActive=account.is_active,
        createdAt=account.created_at.isoformat(),
        updatedAt=account.updated_at.isoformat() if account.updated_at else account.created_at.isoformat(),
    )


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific account."""
    account = db.query(ConnectedAccount).filter(
        ConnectedAccount.id == account_id,
        ConnectedAccount.user_id == current_user.id,
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    return AccountResponse(
        id=account.id,
        userId=account.user_id,
        platform=account.platform,
        accountId=account.account_id,
        accountName=account.account_name,
        firm=account.firm,
        accountType=account.account_type,
        accountSize=account.account_size / 100,
        ruleSetVersion=account.rule_set_version,
        isActive=account.is_active,
        createdAt=account.created_at.isoformat(),
        updatedAt=account.updated_at.isoformat() if account.updated_at else account.created_at.isoformat(),
    )


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Disconnect an account."""
    account = db.query(ConnectedAccount).filter(
        ConnectedAccount.id == account_id,
        ConnectedAccount.user_id == current_user.id,
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )
    
    account.is_active = False
    db.commit()
    
    return None

