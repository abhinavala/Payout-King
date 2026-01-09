"""
Tradovate Authentication Service

Handles read-only auth flow:
1. Verify connection by fetching account list and balance
2. Store API credentials encrypted
3. Handle token refresh (if needed)

This is Phase 1.2 implementation.
"""

from typing import Dict, Optional
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import encrypt_api_token, decrypt_api_token
from app.models.account import ConnectedAccount


class TradovateAuthError(Exception):
    """Raised when Tradovate authentication fails."""
    pass


class TradovateAuthService:
    """
    Service for authenticating and verifying Tradovate API access.
    """

    def __init__(self):
        self.base_url = settings.TRADOVATE_API_URL

    async def get_access_token(
        self, username: str, password: str, app_id: str = "PayoutKing", app_version: str = "0.1"
    ) -> str:
        """
        Authenticate with Tradovate and get access token.
        
        Args:
            username: Tradovate username
            password: Tradovate password
            app_id: Application identifier
            app_version: Application version
            
        Returns:
            Access token string
            
        Raises:
            TradovateAuthError: If authentication fails
        """
        auth_url = "https://www.tradovate.com/auth/accesstokenrequest"
        
        payload = {
            "name": username,
            "password": password,
            "appId": app_id,
            "appVersion": app_version,
            "cid": "scalper",  # Known public client ID
            "sec": "",  # Empty if not required
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    auth_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                
                if response.status_code != 200:
                    raise TradovateAuthError(
                        f"Authentication failed: {response.status_code} - {response.text}"
                    )
                
                data = response.json()
                access_token = data.get("accessToken") or data.get("access_token") or data.get("token")
                
                if not access_token:
                    raise TradovateAuthError(
                        "No access token in authentication response"
                    )
                
                return access_token
                
        except httpx.TimeoutException:
            raise TradovateAuthError(
                "Connection timeout. Please check your internet connection."
            )
        except httpx.RequestError as e:
            raise TradovateAuthError(
                f"Network error: {str(e)}"
            )

    async def verify_connection(
        self, username: str, password: str
    ) -> Dict:
        """
        Verify that credentials work by authenticating and fetching account data.
        
        This is the "fail fast" check - if this fails, don't save credentials.
        
        Args:
            username: Tradovate username
            password: Tradovate password
            
        Returns:
            Dict with account information if successful
            
        Raises:
            TradovateAuthError: If authentication fails
        """
        # Step 1: Get access token
        access_token = await self.get_access_token(username, password)
        
        # Step 2: Verify by fetching account list
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try to fetch account list (this verifies auth works)
                response = await client.get(
                    f"{self.base_url}/account/list",
                    headers=headers,
                )
                
                if response.status_code == 401:
                    raise TradovateAuthError(
                        "Invalid credentials or expired token. Please check your username and password."
                    )
                elif response.status_code == 403:
                    raise TradovateAuthError(
                        "Account does not have required permissions."
                    )
                elif response.status_code != 200:
                    raise TradovateAuthError(
                        f"Failed to verify connection: {response.status_code} - {response.text}"
                    )
                
                accounts = response.json()
                
                if not accounts or (isinstance(accounts, list) and len(accounts) == 0):
                    raise TradovateAuthError(
                        "No accounts found. Please ensure your account has access."
                    )
                
                return {
                    "success": True,
                    "accounts": accounts,
                    "message": "Connection verified successfully",
                }
                
        except httpx.TimeoutException:
            raise TradovateAuthError(
                "Connection timeout. Please check your internet connection."
            )
        except httpx.RequestError as e:
            raise TradovateAuthError(
                f"Network error: {str(e)}"
            )

    async def connect_account(
        self,
        user_id: str,
        account_data: Dict,
        username: str,
        password: str,
        db: Session = None,
    ) -> ConnectedAccount:
        """
        Connect a Tradovate account after verifying credentials.
        
        This method:
        1. Verifies the credentials work (authenticates and fetches accounts)
        2. Encrypts and stores the credentials
        3. Creates a ConnectedAccount record
        
        Args:
            user_id: User ID who owns this account
            account_data: Account information (accountId, accountName, etc.)
            username: Tradovate username
            password: Tradovate password
            db: Database session
            
        Returns:
            ConnectedAccount record
            
        Raises:
            TradovateAuthError: If verification fails
        """
        # Step 1: Verify connection
        verification = await self.verify_connection(username, password)
        
        if not verification["success"]:
            raise TradovateAuthError("Connection verification failed")
        
        # Step 2: Encrypt credentials (store username/password, not token)
        encrypted_username = encrypt_api_token(username)
        encrypted_password = encrypt_api_token(password)
        
        # Step 3: Create ConnectedAccount
        # TODO: Extract account info from verification response
        account = ConnectedAccount(
            user_id=user_id,
            platform="tradovate",
            account_id=str(account_data.get("accountId")),
            account_name=account_data.get("accountName", "Tradovate Account"),
            firm=account_data.get("firm", "other"),
            account_type=account_data.get("accountType", "funded"),
            account_size=int(account_data.get("accountSize", 0) * 100),  # Convert to cents
            rule_set_version=account_data.get("ruleSetVersion", "1.0"),
            encrypted_api_token=encrypted_username,  # Store username
            encrypted_api_secret=encrypted_password,  # Store password
            is_active=True,
        )
        
        db.add(account)
        db.commit()
        db.refresh(account)
        
        return account

    async def get_access_token_for_account(self, account: ConnectedAccount) -> str:
        """
        Get access token for an account by authenticating with stored credentials.
        
        Args:
            account: ConnectedAccount with encrypted credentials
            
        Returns:
            Access token string
            
        Raises:
            TradovateAuthError: If authentication fails
        """
        username = decrypt_api_token(account.encrypted_api_token)
        password = decrypt_api_token(account.encrypted_api_secret)
        return await self.get_access_token(username, password)
    
    def get_decrypted_credentials(self, account: ConnectedAccount) -> tuple[str, str]:
        """
        Get decrypted credentials for an account.
        
        Args:
            account: ConnectedAccount with encrypted credentials
            
        Returns:
            Tuple of (username, password)
        """
        username = decrypt_api_token(account.encrypted_api_token)
        password = decrypt_api_token(account.encrypted_api_secret)
        return username, password

