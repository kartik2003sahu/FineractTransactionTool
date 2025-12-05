"""
Test script to check if transaction 439700 really exists and if it was undone
"""
import requests
import json
from config import Config
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

loan_id = 19130
transaction_id = 439700

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': Config.FINERACT_AUTH_TOKEN,
    'Fineract-Platform-TenantId': Config.FINERACT_TENANT_ID,
}

# Fetch loan details with transactions
url = f"{Config.FINERACT_BASE_URL}/loans/{loan_id}?associations=transactions"

print(f"Checking if transaction {transaction_id} exists and its status...")
print(f"URL: {url}")
print("-" * 80)

try:
    response = requests.get(url, headers=headers, verify=False, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        transactions = data.get('transactions', [])
        
        # Find transaction 439700
        txn = next((t for t in transactions if t.get('id') == transaction_id), None)
        
        if txn:
            print(f"✓ Transaction {transaction_id} FOUND!")
            print(f"\nTransaction Details:")
            print(f"  ID: {txn.get('id')}")
            print(f"  Type: {txn.get('type', {}).get('value')}")
            print(f"  Code: {txn.get('type', {}).get('code')}")
            print(f"  Date: {txn.get('date')}")
            print(f"  Amount: {txn.get('amount')}")
            print(f"  Manually Reversed: {txn.get('manuallyReversed')}")
            print(f"  Reversed: {txn.get('reversed', False)}")
            
            if txn.get('manuallyReversed') or txn.get('reversed'):
                print("\n✅ Transaction IS REVERSED/UNDONE on server!")
            else:
                print("\n❌ Transaction is NOT reversed on server (still active)")
        else:
            print(f"✗ Transaction {transaction_id} NOT FOUND in loan {loan_id}")
            print(f"\nAll transaction IDs: {[t.get('id') for t in transactions]}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
