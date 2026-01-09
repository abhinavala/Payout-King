#!/usr/bin/env python3
"""
Test Tradovate OAuth-Style Authentication and API

This script:
1. Authenticates with Tradovate using username/password
2. Retrieves an access token
3. Uses that token to call read-only endpoints
4. Prints raw responses for schema inspection

Usage:
    python3 scripts/test_tradovate_auth.py --username YOUR_USERNAME --password YOUR_PASSWORD

Important:
- Credentials are NOT stored or logged
- Read-only usage only
- Development/testing only
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path
from typing import Dict, Optional

import httpx


# Tradovate API Configuration
# Try different possible endpoints
TRADOVATE_AUTH_ENDPOINTS = [
    "https://www.tradovate.com/auth/accesstokenrequest",
    "https://live.tradovate.com/auth/accesstokenrequest",
    "https://api.tradovate.com/auth/accesstokenrequest",
    "https://www.tradovate.com/api/v1/auth/accesstokenrequest",
    "https://live.tradovate.com/api/v1/auth/accesstokenrequest",
]
TRADOVATE_API_BASE = "https://www.tradovate.com"  # or https://demo.tradovate.com for demo


async def authenticate(
    username: str, password: str, app_id: str = "PayoutKing", app_version: str = "0.1"
) -> Optional[Dict]:
    """
    Authenticate with Tradovate and get access token.
    
    Args:
        username: Tradovate username
        password: Tradovate password
        app_id: Application identifier
        app_version: Application version
        
    Returns:
        Dict with access token and user info, or None if failed
    """
    print("=" * 70)
    print("STEP 1: Authentication")
    print("=" * 70)
    print(f"Username: {username}")
    print(f"App ID: {app_id}")
    print()
    
    payload = {
        "name": username,
        "password": password,
        "appId": app_id,
        "appVersion": app_version,
        "cid": "scalper",  # Known public client ID
        "sec": "",  # Empty if not required
    }
    
    # Try different possible endpoints
    last_error = None
    for auth_url in TRADOVATE_AUTH_ENDPOINTS:
        print(f"Trying: {auth_url}")
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.post(
                    auth_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print("✅ Authentication Successful!")
                        print(f"\nResponse Keys: {list(data.keys())}")
                        
                        # Extract token (field name may vary)
                        access_token = data.get("accessToken") or data.get("access_token") or data.get("token")
                        
                        if access_token:
                            print(f"\n✅ Access Token Retrieved from: {auth_url}")
                            print(f"Token (first 20 chars): {access_token[:20]}...")
                            return {
                                "access_token": access_token,
                                "user_id": data.get("userId") or data.get("user_id"),
                                "full_response": data,
                                "auth_url": auth_url,  # Remember which URL worked
                            }
                        else:
                            print("\n⚠️  Warning: No access token found in response")
                            print(f"Full response: {json.dumps(data, indent=2)}")
                            return {"full_response": data, "auth_url": auth_url}
                    except json.JSONDecodeError:
                        print(f"⚠️  Response is not JSON: {response.text[:200]}")
                        continue
                elif response.status_code in [301, 302, 307, 308]:
                    print(f"⚠️  Redirect ({response.status_code}), trying next endpoint...")
                    continue
                elif response.status_code == 404:
                    print(f"⚠️  Not found (404), trying next endpoint...")
                    last_error = f"404: {response.text[:100]}"
                    continue
                else:
                    print(f"⚠️  Status {response.status_code}, trying next endpoint...")
                    last_error = f"{response.status_code}: {response.text[:100]}"
                    continue
        except httpx.TimeoutException:
            print(f"⚠️  Timeout, trying next endpoint...")
            continue
        except httpx.RequestError as e:
            print(f"⚠️  Request error: {e}, trying next endpoint...")
            last_error = str(e)
            continue
        except Exception as e:
            print(f"⚠️  Error: {e}, trying next endpoint...")
            last_error = str(e)
            continue
    
    # If we get here, all endpoints failed
    print(f"\n❌ All authentication endpoints failed!")
    if last_error:
        print(f"Last error: {last_error}")
    print("\nPossible issues:")
    print("1. Endpoint path may be different")
    print("2. May need different base URL (demo.tradovate.com?)")
    print("3. May require different authentication method")
    return None


async def test_endpoint(
    endpoint: str,
    access_token: str,
    method: str = "GET",
    params: Optional[Dict] = None,
    description: str = "",
) -> Optional[Dict]:
    """
    Test an API endpoint with the access token.
    
    Args:
        endpoint: API endpoint path (e.g., "/account/list")
        access_token: Access token from authentication
        method: HTTP method (GET, POST, etc.)
        params: Query parameters
        description: Human-readable description
        
    Returns:
        Response data as dict, or None if failed
    """
    url = f"{TRADOVATE_API_BASE}{endpoint}"
    
    print("\n" + "=" * 70)
    print(f"Testing: {description or endpoint}")
    print("=" * 70)
    print(f"URL: {url}")
    if params:
        print(f"Params: {params}")
    print()
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=params)
            else:
                print(f"❌ Unsupported method: {method}")
                return None
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print()
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("✅ Success!")
                    print(f"\nResponse Type: {type(data)}")
                    
                    if isinstance(data, list):
                        print(f"Array Length: {len(data)}")
                        if data:
                            print(f"\nFirst Item Keys: {list(data[0].keys())}")
                            print(f"\nFirst Item Sample:")
                            print(json.dumps(data[0], indent=2))
                    elif isinstance(data, dict):
                        print(f"Response Keys: {list(data.keys())}")
                        print(f"\nFull Response:")
                        print(json.dumps(data, indent=2))
                    else:
                        print(f"Response: {data}")
                    
                    return data
                except json.JSONDecodeError:
                    print(f"⚠️  Response is not JSON:")
                    print(response.text[:500])
                    return {"raw": response.text}
            elif response.status_code == 401:
                print("❌ Unauthorized - Token may be invalid or expired")
                print(f"Response: {response.text}")
                return None
            elif response.status_code == 403:
                print("❌ Forbidden - Insufficient permissions")
                print(f"Response: {response.text}")
                return None
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return None
                
    except httpx.TimeoutException:
        print("❌ Error: Connection timeout")
        return None
    except httpx.RequestError as e:
        print(f"❌ Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


async def main():
    """Run authentication and endpoint tests."""
    parser = argparse.ArgumentParser(
        description="Test Tradovate OAuth authentication and API endpoints"
    )
    parser.add_argument(
        "--username",
        required=True,
        help="Tradovate username",
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Tradovate password",
    )
    parser.add_argument(
        "--account-id",
        help="Account ID to test (optional, will use first account from list)",
    )
    parser.add_argument(
        "--app-id",
        default="PayoutKing",
        help="Application ID (default: PayoutKing)",
    )
    parser.add_argument(
        "--app-version",
        default="0.1",
        help="Application version (default: 0.1)",
    )
    
    args = parser.parse_args()
    
    print("═══════════════════════════════════════════════════════════════")
    print("  TRADOVATE API AUTHENTICATION TEST")
    print("═══════════════════════════════════════════════════════════════")
    print()
    print("⚠️  WARNING: This script uses credentials for testing only.")
    print("   Credentials are NOT stored or logged permanently.")
    print()
    
    # Step 1: Authenticate
    auth_result = await authenticate(
        args.username, args.password, args.app_id, args.app_version
    )
    
    if not auth_result or "access_token" not in auth_result:
        print("\n❌ Cannot proceed - authentication failed")
        return 1
    
    access_token = auth_result["access_token"]
    user_id = auth_result.get("user_id")
    
    print(f"\n✅ Authentication successful!")
    if user_id:
        print(f"User ID: {user_id}")
    
    # Step 2: Test endpoints
    results = {}
    
    # Test account list
    account_list = await test_endpoint(
        "/account/list",
        access_token,
        description="Get Account List",
    )
    results["account_list"] = account_list
    
    # Get account ID if not provided
    account_id = args.account_id
    if not account_id and account_list and isinstance(account_list, list) and account_list:
        account_id = account_list[0].get("id") or account_list[0].get("accountId")
        print(f"\n📝 Using first account ID: {account_id}")
    
    if account_id:
        # Test account details
        account_details = await test_endpoint(
            f"/account/{account_id}",
            access_token,
            description=f"Get Account Details (ID: {account_id})",
        )
        results["account_details"] = account_details
        
        # Test positions
        positions = await test_endpoint(
            "/position/list",
            access_token,
            params={"accountId": account_id},
            description="Get Open Positions",
        )
        results["positions"] = positions
        
        # Test orders
        orders = await test_endpoint(
            "/order/list",
            access_token,
            params={"accountId": account_id},
            description="Get Orders",
        )
        results["orders"] = orders
        
        # Test fills
        fills = await test_endpoint(
            "/fill/list",
            access_token,
            params={"accountId": account_id},
            description="Get Fills (for daily PnL)",
        )
        results["fills"] = fills
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Authentication: {'PASS' if auth_result else 'FAIL'}")
    print(f"✅ Account List: {'PASS' if account_list else 'FAIL'}")
    if account_id:
        print(f"✅ Account Details: {'PASS' if results.get('account_details') else 'FAIL'}")
        print(f"✅ Positions: {'PASS' if results.get('positions') is not None else 'FAIL'}")
        print(f"✅ Orders: {'PASS' if results.get('orders') is not None else 'FAIL'}")
        print(f"✅ Fills: {'PASS' if results.get('fills') is not None else 'FAIL'}")
    print()
    print("Next Steps:")
    print("1. Review the response formats above")
    print("2. Update docs/TRADOVATE_API.md with actual schemas")
    print("3. Update TradovateClient with real endpoints")
    print("4. Implement polling loop")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

