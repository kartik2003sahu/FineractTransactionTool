import requests
from config import Config
import urllib3
from datetime import datetime

urllib3.disable_warnings()

r = requests.get(
    f'{Config.FINERACT_BASE_URL}/loans/19130?associations=transactions',
    headers={
        'Authorization': Config.FINERACT_AUTH_TOKEN,
        'Fineract-Platform-TenantId': Config.FINERACT_TENANT_ID
    },
    verify=False
)

def parse_date(date_data):
    if isinstance(date_data, list):
        return datetime(*date_data[:6])
    return None

txns = r.json().get('transactions', [])
repayments = [t for t in txns if 
              t.get('type', {}).get('code') == 'loanTransactionType.repayment' and
              not t.get('manuallyReversed')]

print(f'Total active repayment transactions: {len(repayments)}\n')

# Sort by date descending
sorted_txns = sorted(repayments, key=lambda x: parse_date(x.get('date')), reverse=True)

print('Latest 10 transactions (sorted newest first):')
for i, t in enumerate(sorted_txns[:10], 1):
    date = t.get('date')
    dt = parse_date(date)
    print(f"{i}. ID: {t.get('id'):6d} | Date: {dt.strftime('%Y-%m-%d') if dt else 'Unknown'}")

print(f'\nThe LATEST transaction is ID: {sorted_txns[0].get("id")}')
