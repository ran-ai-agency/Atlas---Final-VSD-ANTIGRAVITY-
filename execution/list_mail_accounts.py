#!/usr/bin/env python3
"""Liste tous les comptes de messagerie Zoho Mail"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

mail_url = os.getenv('MCP_ZOHO_MAIL_URL', '')
mail_key = os.getenv('MCP_ZOHO_MAIL_KEY', '')
url = f'{mail_url}?key={mail_key}'

response = requests.post(url, json={
    'jsonrpc': '2.0', 
    'id': 1, 
    'method': 'tools/call', 
    'params': {'name': 'ZohoMail_getMailAccounts', 'arguments': {}}
}, timeout=60)

data = json.loads(response.json().get('result', {}).get('content', [{}])[0].get('text', '{}'))
accounts = data.get('data', [])

print("=" * 60)
print("COMPTES DE MESSAGERIE ZOHO MAIL DISPONIBLES")
print("=" * 60)

for i, acc in enumerate(accounts, 1):
    email = acc.get('emailAddress', 'N/A')
    acc_id = acc.get('accountId', 'N/A')
    display = acc.get('accountDisplayName', 'N/A')
    print(f"\n{i}. {email}")
    print(f"   Nom affiché: {display}")
    print(f"   Account ID: {acc_id}")

print(f"\n{'=' * 60}")
print(f"Total: {len(accounts)} compte(s)")
