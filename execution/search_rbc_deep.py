#!/usr/bin/env python3
"""Recherche approfondie RBC dans tous les comptes"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(Path(__file__).parent.parent / '.env')

mail_url = os.getenv('MCP_ZOHO_MAIL_URL', '')
mail_key = os.getenv('MCP_ZOHO_MAIL_KEY', '')
url = f'{mail_url}?key={mail_key}'

ACCOUNT_NAMES = {
    '219196000000002002': 'Ran.AI Agency',
    '219196000000029010': 'Sympatico',
    '219196000000034010': 'Bell Net',
    '219196000000072002': 'Gmail'
}

def call_mcp(method, params):
    response = requests.post(url, json={'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}, timeout=120)
    return response.json().get('result', {})

def format_date(timestamp_ms):
    if timestamp_ms:
        try:
            ts = int(timestamp_ms) if isinstance(timestamp_ms, str) else timestamp_ms
            dt = datetime.fromtimestamp(ts / 1000)
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return str(timestamp_ms)
    return "N/A"

# Get accounts
result = call_mcp('tools/call', {'name': 'ZohoMail_getMailAccounts', 'arguments': {}})
accounts_data = json.loads(result.get('content', [{}])[0].get('text', '{}'))
accounts = accounts_data.get('data', [])

print("=" * 70)
print("RECHERCHE APPROFONDIE: RBC (Banque Royale)")
print("=" * 70)

all_emails = []

for acc in accounts:
    acc_id = acc.get('accountId')
    acc_name = ACCOUNT_NAMES.get(acc_id, acc.get('accountDisplayName', 'Unknown'))
    
    print(f"\nRecherche dans: {acc_name}...")
    
    # Use searchEmails API for deeper search
    try:
        result = call_mcp('tools/call', {
            'name': 'ZohoMail_searchEmails',
            'arguments': {
                'path_variables': {'accountId': acc_id},
                'query_params': {'searchKey': 'RBC', 'limit': 100}
            }
        })
        text = result.get('content', [{}])[0].get('text', '{}')
        
        if 'error' not in text.lower() and 'mandatory' not in text.lower():
            emails = json.loads(text).get('data', [])
            for e in emails:
                e['_account'] = acc_name
                e['_acc_id'] = acc_id
                all_emails.append(e)
            print(f"  -> {len(emails)} email(s) trouve(s)")
        else:
            print(f"  -> Erreur API: {text[:100]}")
    except Exception as ex:
        print(f"  -> Erreur: {ex}")

# Deduplicate
seen = set()
unique = []
for e in all_emails:
    mid = e.get('messageId')
    if mid and mid not in seen:
        seen.add(mid)
        unique.append(e)

# Sort by date
unique.sort(key=lambda x: x.get('receivedTime', 0), reverse=True)

print("\n" + "=" * 70)
print(f"RESULTATS: {len(unique)} courriel(s) RBC trouve(s)")
print("=" * 70)

if unique:
    for i, e in enumerate(unique, 1):
        subject = e.get('subject', 'Sans sujet')
        sender = e.get('sender', e.get('fromAddress', 'Inconnu'))
        date_str = format_date(e.get('receivedTime'))
        account = e.get('_account', '')
        msg_id = e.get('messageId', '')
        
        # Clean for Windows console
        try:
            subject = subject.encode('cp1252', 'replace').decode('cp1252')[:65]
            sender = sender.encode('cp1252', 'replace').decode('cp1252')
        except:
            subject = subject[:65]
        
        print(f"\n{i}. {subject}")
        print(f"   De: {sender}")
        print(f"   Date: {date_str} | Compte: {account}")
        print(f"   ID: {msg_id}")
else:
    print("\nAucun courriel RBC trouve dans l'historique accessible via l'API.")

print("\n" + "=" * 70)
