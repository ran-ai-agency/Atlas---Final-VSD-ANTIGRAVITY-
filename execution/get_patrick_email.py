#!/usr/bin/env python3
"""Obtenir les details complets de l'email de Patrick Kochanowski"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

mail_url = os.getenv('MCP_ZOHO_MAIL_URL', '')
mail_key = os.getenv('MCP_ZOHO_MAIL_KEY', '')
url = f'{mail_url}?key={mail_key}'

def call_mcp(method, params):
    response = requests.post(url, json={'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}, timeout=60)
    return response.json().get('result', {})

# Account Sympatico et message ID
account_id = '219196000000029010'
message_id = '1767828635917000700'

# D'abord, obtenir le folder ID
result = call_mcp('tools/call', {
    'name': 'ZohoMail_listEmails',
    'arguments': {
        'path_variables': {'accountId': account_id},
        'query_params': {'limit': 200, 'start': 1}
    }
})

text = result.get('content', [{}])[0].get('text', '{}')
emails = json.loads(text).get('data', [])

target_email = None
for e in emails:
    if e.get('messageId') == message_id:
        target_email = e
        break

if target_email:
    print("=" * 70)
    print("DETAILS DE L'EMAIL DE PATRICK KOCHANOWSKI")
    print("=" * 70)
    print(f"\nSujet: {target_email.get('subject', 'N/A')}")
    print(f"\nExpéditeur (sender): {target_email.get('sender', 'N/A')}")
    print(f"Adresse email (fromAddress): {target_email.get('fromAddress', 'N/A')}")
    print(f"\nDestinataire: {target_email.get('toAddress', 'N/A')}")
    print(f"Message ID: {target_email.get('messageId', 'N/A')}")
    print(f"Folder ID: {target_email.get('folderId', 'N/A')}")
    
    # Essayer de lire le contenu complet
    folder_id = target_email.get('folderId')
    if folder_id:
        result = call_mcp('tools/call', {
            'name': 'ZohoMail_getMessageContent',
            'arguments': {
                'path_variables': {
                    'accountId': account_id,
                    'folderId': folder_id,
                    'messageId': message_id
                },
                'query_params': {'includeBlockContent': True}
            }
        })
        text = result.get('content', [{}])[0].get('text', '{}')
        full_email = json.loads(text).get('data', {})
        
        if full_email:
            print(f"\n--- Détails supplémentaires ---")
            print(f"From (complet): {full_email.get('fromAddress', 'N/A')}")
            print(f"Reply-To: {full_email.get('replyTo', 'N/A')}")
    
    print("\n" + "=" * 70)
else:
    print("Email non trouve dans les 200 derniers messages.")
