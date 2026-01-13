#!/usr/bin/env python3
"""Recherche courriels Patrick RBC"""

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

def call_mcp(method, params):
    response = requests.post(url, json={'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}, timeout=60)
    return response.json().get('result', {})

# Get accounts
result = call_mcp('tools/call', {'name': 'ZohoMail_getMailAccounts', 'arguments': {}})
accounts_data = json.loads(result.get('content', [{}])[0].get('text', '{}'))
accounts = accounts_data.get('data', [])

search_terms = ['Patrick', 'patrick@rbc', 'banque royale', 'RBC Patrick']
all_results = []

print("Recherche de courriels avec Patrick de RBC...")
print("=" * 60)

for term in search_terms:
    print(f"Terme: {term}")
    for acc in accounts:
        acc_id = acc.get('accountId')
        acc_email = acc.get('emailAddress', 'Unknown')
        
        try:
            result = call_mcp('tools/call', {
                'name': 'ZohoMail_searchEmails',
                'arguments': {
                    'path_variables': {'accountId': acc_id},
                    'query_params': {'searchKey': term, 'limit': 50}
                }
            })
            text = result.get('content', [{}])[0].get('text', '{}')
            
            if 'error' not in text.lower() and 'mandatory' not in text.lower():
                emails = json.loads(text).get('data', [])
                for e in emails:
                    all_results.append({
                        'account': acc_email,
                        'subject': e.get('subject', 'Sans sujet'),
                        'sender': e.get('sender', e.get('fromAddress', 'Inconnu')),
                        'date': e.get('receivedTime'),
                        'msgId': e.get('messageId'),
                        'accId': acc_id,
                        'term': term
                    })
        except Exception as ex:
            print(f"  Erreur {acc_email}: {ex}")

print("=" * 60)

# Deduplicate by messageId
seen = set()
unique = []
for r in all_results:
    if r['msgId'] not in seen:
        seen.add(r['msgId'])
        unique.append(r)

if unique:
    print(f"\n{len(unique)} email(s) trouve(s):\n")
    for i, r in enumerate(unique[:20], 1):
        subj = r['subject'][:60] if r['subject'] else 'Sans sujet'
        print(f"{i}. {subj}")
        print(f"   De: {r['sender']}")
        print(f"   Compte: {r['account']}")
        print(f"   Terme trouve: {r['term']}")
        print(f"   Message ID: {r['msgId']}")
        print()
else:
    print("\nAucun email trouve avec ces termes de recherche.")
    print("\nSuggestions:")
    print("- Verifiez le nom exact de Patrick")
    print("- Les emails peuvent etre archives ou supprimes")
    print("- Essayez de chercher directement dans Zoho Mail")
