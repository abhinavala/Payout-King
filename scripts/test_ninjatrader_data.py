#!/usr/bin/env python3
"""
Test script to simulate NinjaTrader data and verify the connection works.
This helps verify the backend is ready before connecting the real Add-On.
"""

import json
import sys
from datetime import datetime

# Try to use httpx (FastAPI uses it), fallback to urllib
try:
    import httpx
    USE_HTTPX = True
except ImportError:
    try:
        import urllib.request
        import urllib.parse
        USE_HTTPX = False
    except ImportError:
        print("❌ Need httpx or urllib. Install: pip install httpx")
        sys.exit(1)

BACKEND_URL = "http://localhost:8000"

def test_ninjatrader_endpoint():
    """Test the NinjaTrader endpoint with sample data."""
    
    print("═══════════════════════════════════════════════════════════════")
    print("  🧪 Testing NinjaTrader Endpoint")
    print("═══════════════════════════════════════════════════════════════")
    print()
    
    # Check health
    print("1. Checking endpoint health...")
    try:
        if USE_HTTPX:
            response = httpx.get(f"{BACKEND_URL}/api/v1/ninjatrader/health", timeout=5.0)
            if response.status_code == 200:
                print(f"   ✅ Endpoint is healthy: {response.json()}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
        else:
            req = urllib.request.Request(f"{BACKEND_URL}/api/v1/ninjatrader/health")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    print(f"   ✅ Endpoint is healthy: {data}")
                else:
                    print(f"   ❌ Health check failed: {response.status}")
                    return False
    except Exception as e:
        print(f"   ❌ Cannot reach backend: {e}")
        print(f"   Make sure backend is running: http://localhost:8000")
        return False
    
    print()
    
    # Check connected accounts
    print("2. Checking connected accounts...")
    try:
        if USE_HTTPX:
            response = httpx.get(f"{BACKEND_URL}/api/v1/ninjatrader/debug/accounts", timeout=5.0)
            if response.status_code == 200:
                accounts = response.json().get("accounts", [])
            else:
                print(f"   ❌ Failed to get accounts: {response.status_code}")
                return False
        else:
            req = urllib.request.Request(f"{BACKEND_URL}/api/v1/ninjatrader/debug/accounts")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    accounts = json.loads(response.read().decode()).get("accounts", [])
                else:
                    print(f"   ❌ Failed to get accounts: {response.status}")
                    return False
        
        if accounts:
            print(f"   ✅ Found {len(accounts)} connected account(s):")
            for acc in accounts:
                print(f"      - {acc['account_name']} (ID: {acc['account_id']})")
        else:
            print("   ⚠️  No accounts connected yet")
            print("   Connect an account in the dashboard first!")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print()
    
    # Test with sample data (if account exists)
    if accounts:
        test_account = accounts[0]
        print(f"3. Testing with account: {test_account['account_id']}")
        
        sample_data = {
            "accountId": test_account["account_id"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "equity": 50000.0,
            "balance": 50000.0,
            "realizedPnL": 0.0,
            "unrealizedPnL": 0.0,
            "highWaterMark": 50000.0,
            "dailyPnL": 0.0,
            "openPositions": []
        }
        
        try:
            json_data = json.dumps(sample_data).encode('utf-8')
            
            if USE_HTTPX:
                response = httpx.post(
                    f"{BACKEND_URL}/api/v1/ninjatrader/account-data",
                    content=json_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Data accepted successfully!")
                    print(f"   Risk Level: {result.get('riskLevel', 'unknown')}")
                    print(f"   Rule States: {len(result.get('ruleStates', {}))} rules evaluated")
                    return True
                else:
                    print(f"   ❌ Failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
            else:
                req = urllib.request.Request(
                    f"{BACKEND_URL}/api/v1/ninjatrader/account-data",
                    data=json_data,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        result = json.loads(response.read().decode())
                        print(f"   ✅ Data accepted successfully!")
                        print(f"   Risk Level: {result.get('riskLevel', 'unknown')}")
                        print(f"   Rule States: {len(result.get('ruleStates', {}))} rules evaluated")
                        return True
                    else:
                        print(f"   ❌ Failed: {response.status}")
                        return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    else:
        print("3. ⚠️  Skipping data test (no accounts connected)")
        return False

if __name__ == "__main__":
    success = test_ninjatrader_endpoint()
    print()
    if success:
        print("═══════════════════════════════════════════════════════════════")
        print("  ✅ Backend is ready for NinjaTrader connection!")
        print("═══════════════════════════════════════════════════════════════")
        print()
        print("Next steps:")
        print("1. Build the Add-On in Visual Studio")
        print("2. Create config file on Windows")
        print("3. Enable Add-On in NinjaTrader")
        print("4. Connect account in dashboard")
        print("5. Verify data is flowing!")
    else:
        print("═══════════════════════════════════════════════════════════════")
        print("  ⚠️  Some checks failed - see above for details")
        print("═══════════════════════════════════════════════════════════════")

