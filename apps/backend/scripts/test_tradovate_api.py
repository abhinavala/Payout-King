#!/usr/bin/env python3
"""
Test Tradovate API Integration

This script tests the Tradovate API endpoints with a real API key.
Use this to verify authentication and endpoint responses.

Usage:
    python3 scripts/test_tradovate_api.py --api-key YOUR_API_KEY
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "rules-engine"))

import httpx
from app.core.config import settings


async def test_account_list(api_key: str):
    """Test getting account list."""
    print("=" * 70)
    print("TEST 1: Get Account List")
    print("=" * 70)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.TRADOVATE_API_URL}/account/listitem",
                headers=headers,
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                accounts = response.json()
                print(f"\n✅ Success! Found {len(accounts)} account(s):")
                for i, account in enumerate(accounts, 1):
                    print(f"\n  Account {i}:")
                    for key, value in account.items():
                        print(f"    {key}: {value}")
                return accounts
            else:
                print(f"\n❌ Failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


async def test_account_balance(api_key: str, account_id: str):
    """Test getting account balance."""
    print("\n" + "=" * 70)
    print("TEST 2: Get Account Balance")
    print("=" * 70)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try different endpoint variations
            endpoints = [
                f"{settings.TRADOVATE_API_URL}/account/account",
                f"{settings.TRADOVATE_API_URL}/account/{account_id}",
            ]
            
            for endpoint in endpoints:
                print(f"\nTrying: {endpoint}")
                response = await client.get(
                    endpoint,
                    headers=headers,
                    params={"accountId": account_id} if "account" in endpoint else None,
                )
                
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"\n✅ Success!")
                    print(f"Response keys: {list(data.keys())}")
                    for key, value in data.items():
                        if isinstance(value, (int, float, str)):
                            print(f"  {key}: {value}")
                    return data
                else:
                    print(f"Response: {response.text[:200]}")
            
            print("\n❌ All endpoint variations failed")
            return None
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


async def test_positions(api_key: str, account_id: str):
    """Test getting open positions."""
    print("\n" + "=" * 70)
    print("TEST 3: Get Open Positions")
    print("=" * 70)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            endpoints = [
                f"{settings.TRADOVATE_API_URL}/position/list",
                f"{settings.TRADOVATE_API_URL}/position/{account_id}",
            ]
            
            for endpoint in endpoints:
                print(f"\nTrying: {endpoint}")
                response = await client.get(
                    endpoint,
                    headers=headers,
                    params={"accountId": account_id} if "list" in endpoint else None,
                )
                
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    positions = response.json()
                    print(f"\n✅ Success! Found {len(positions)} position(s)")
                    if positions:
                        print(f"Sample position keys: {list(positions[0].keys())}")
                        for key, value in positions[0].items():
                            if isinstance(value, (int, float, str)):
                                print(f"  {key}: {value}")
                    return positions
                else:
                    print(f"Response: {response.text[:200]}")
            
            print("\n❌ All endpoint variations failed")
            return None
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


async def test_fills(api_key: str, account_id: str):
    """Test getting fills."""
    print("\n" + "=" * 70)
    print("TEST 4: Get Fills (for daily PnL)")
    print("=" * 70)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            endpoints = [
                f"{settings.TRADOVATE_API_URL}/fill/list",
                f"{settings.TRADOVATE_API_URL}/fill/{account_id}",
            ]
            
            for endpoint in endpoints:
                print(f"\nTrying: {endpoint}")
                response = await client.get(
                    endpoint,
                    headers=headers,
                    params={"accountId": account_id} if "list" in endpoint else None,
                )
                
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    fills = response.json()
                    print(f"\n✅ Success! Found {len(fills)} fill(s)")
                    if fills:
                        print(f"Sample fill keys: {list(fills[0].keys())}")
                        # Show recent fills
                        for fill in fills[:3]:
                            print(f"\n  Fill:")
                            for key, value in fill.items():
                                if isinstance(value, (int, float, str)):
                                    print(f"    {key}: {value}")
                    return fills
                else:
                    print(f"Response: {response.text[:200]}")
            
            print("\n❌ All endpoint variations failed")
            return None
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


async def main():
    """Run all API tests."""
    parser = argparse.ArgumentParser(description="Test Tradovate API")
    parser.add_argument(
        "--api-key",
        required=True,
        help="Tradovate API key",
    )
    parser.add_argument(
        "--account-id",
        help="Account ID to test (optional, will use first account from list)",
    )
    
    args = parser.parse_args()
    
    print("═══════════════════════════════════════════════════════════════")
    print("  TRADOVATE API TEST SUITE")
    print("═══════════════════════════════════════════════════════════════")
    print(f"\nAPI URL: {settings.TRADOVATE_API_URL}")
    print(f"API Key: {args.api_key[:10]}...{args.api_key[-4:]}")
    print()
    
    # Test 1: Get account list
    accounts = await test_account_list(args.api_key)
    
    if not accounts:
        print("\n❌ Cannot proceed - failed to get account list")
        return 1
    
    # Use provided account ID or first account
    account_id = args.account_id or accounts[0].get("accountId")
    
    if not account_id:
        print("\n❌ No account ID available")
        return 1
    
    print(f"\nUsing Account ID: {account_id}")
    
    # Test 2: Get account balance
    balance = await test_account_balance(args.api_key, str(account_id))
    
    # Test 3: Get positions
    positions = await test_positions(args.api_key, str(account_id))
    
    # Test 4: Get fills
    fills = await test_fills(args.api_key, str(account_id))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Account List: {'PASS' if accounts else 'FAIL'}")
    print(f"✅ Account Balance: {'PASS' if balance else 'FAIL'}")
    print(f"✅ Positions: {'PASS' if positions is not None else 'FAIL'}")
    print(f"✅ Fills: {'PASS' if fills is not None else 'FAIL'}")
    print()
    print("Next Steps:")
    print("1. Update TradovateClient with actual endpoint responses")
    print("2. Update docs/TRADOVATE_API.md with real response formats")
    print("3. Implement polling loop")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

