"""
Test script to fetch and display transaction data from Fineract API
"""
import requests
import json
from config import Config
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Setup
loan_id = 19130

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Authorization': Config.FINERACT_AUTH_TOKEN,
    'Fineract-Platform-TenantId': Config.FINERACT_TENANT_ID,
}

url = f"{Config.FINERACT_BASE_URL}/loans/{loan_id}?associations=all"

print(f"Fetching loan {loan_id} from: {url}")
print(f"Headers: {headers}")
print("-" * 80)

try:
    response = requests.get(url, headers=headers, verify=False, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Save full response to file for inspection
        with open('loan_response.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"\nFull response saved to: loan_response.json")
        
        # Display transaction info
        transactions = data.get('transactions', [])
        print(f"\nTotal transactions found: {len(transactions)}")
        
        if transactions:
            print("\nFirst few transactions:")
            for i, txn in enumerate(transactions[:3]):
                print(f"\n--- Transaction {i+1} ---")
                print(f"ID: {txn.get('id')}")
                print(f"Type: {txn.get('type')}")
                print(f"Date: {txn.get('date')}")
                print(f"Amount: {txn.get('amount')}")
                print(f"Reversed: {txn.get('reversed', False)}")
                print(f"Manually Reversed: {txn.get('manuallyReversed', False)}")
        else:
            print("\nNo transactions found in response!")
            print(f"\nAvailable fields in response: {list(data.keys())}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
