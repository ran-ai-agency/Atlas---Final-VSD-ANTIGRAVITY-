#!/usr/bin/env python3
"""Recherche Patrick Kochanowski dans tous les comptes"""

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
print("RECHERCHE: Patrick Kochanowski")
print("=" * 70)

search_terms = ['Kochanowski', 'patrick.kochanowski', 'pkochanowski']
all_emails = []

for acc in accounts:
    acc_id = acc.get('accountId')
    acc_name = ACCOUNT_NAMES.get(acc_id, acc.get('accountDisplayName', 'Unknown'))
    
    print(f"\nCompte: {acc_name}")
    
    # List more emails (up to 200) and filter locally
    try:
        result = call_mcp('tools/call', {
            'name': 'ZohoMail_listEmails',
            'arguments': {
                'path_variables': {'accountId': acc_id},
                'query_params': {'limit': 200, 'start': 1}
            }
        })
        text = result.get('content', [{}])[0].get('text', '{}')
        
        if 'error' not in text.lower():
            emails = json.loads(text).get('data', [])
            print(f"  Emails scannes: {len(emails)}")
            
            for e in emails:
                subject = (e.get('subject') or '').lower()
                sender = (e.get('sender') or '').lower()
                from_addr = (e.get('fromAddress') or '').lower()
                to_addr = (e.get('toAddress') or '').lower()
                
                for term in search_terms:
                    term_lower = term.lower()
                    if (term_lower in subject or term_lower in sender or 
                        term_lower in from_addr or term_lower in to_addr):
                        e['_account'] = acc_name
                        e['_term'] = term
                        all_emails.append(e)
                        break
    except Exception as ex:
        print(f"  Erreur: {ex}")

# Also try sent emails
print("\n--- Verification des emails envoyes ---")
for acc in accounts:
    acc_id = acc.get('accountId')
    acc_name = ACCOUNT_NAMES.get(acc_id, 'Unknown')
    
    try:
        # Get sent folder
        result = call_mcp('tools/call', {
            'name': 'ZohoMail_listEmailFolders',
            'arguments': {
                'path_variables': {'accountId': acc_id}
            }
        })
        text = result.get('content', [{}])[0].get('text', '{}')
        folders = json.loads(text).get('data', [])
        
        sent_folder = None
        for f in folders:
            if 'sent' in f.get('folderName', '').lower():
                sent_folder = f.get('folderId')
                break
        
        if sent_folder:
            result = call_mcp('tools/call', {
                'name': 'ZohoMail_listEmails',
                'arguments': {
                    'path_variables': {'accountId': acc_id},
                    'query_params': {'limit': 100, 'start': 1, 'folderId': sent_folder}
                }
            })
            text = result.get('content', [{}])[0].get('text', '{}')
            
            if 'error' not in text.lower():
                emails = json.loads(text).get('data', [])
                print(f"  {acc_name} - Sent: {len(emails)} emails")
                
                for e in emails:
                    to_addr = (e.get('toAddress') or '').lower()
                    subject = (e.get('subject') or '').lower()
                    
                    for term in search_terms:
                        if term.lower() in to_addr or term.lower() in subject:
                            e['_account'] = acc_name + ' (Sent)'
                            e['_term'] = term
                            all_emails.append(e)
                            break
    except Exception as ex:
        pass

# Deduplicate
seen = set()
unique = []
for e in all_emails:
    mid = e.get('messageId')
    if mid and mid not in seen:
        seen.add(mid)
        unique.append(e)

print("\n" + "=" * 70)
print(f"RESULTATS: {len(unique)} courriel(s) trouve(s)")
print("=" * 70)

if unique:
    for i, e in enumerate(unique, 1):
        subject = e.get('subject', 'Sans sujet')[:60]
        sender = e.get('sender', e.get('fromAddress', 'Inconnu'))
        to_addr = e.get('toAddress', '')
        date_str = format_date(e.get('receivedTime') or e.get('sentDateInGMT'))
        account = e.get('_account', '')
        term = e.get('_term', '')
        msg_id = e.get('messageId', '')
        
        print(f"\n{i}. {subject}")
        print(f"   De: {sender}")
        print(f"   A: {to_addr}")
        print(f"   Date: {date_str} | Compte: {account}")
        print(f"   Terme: {term} | ID: {msg_id}")
else:
    print("\nAucun courriel trouve avec Patrick Kochanowski.")
    print("\nLes courriels peuvent etre:")
    print("- Dans un compte email non synchronise avec Zoho")
    print("- Archives ou supprimes")
    print("- Plus anciens que la limite de l'API")

print("\n" + "=" * 70)
