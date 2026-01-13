#!/usr/bin/env python3
"""Trouver ou créer le vendor Anthropic et lier aux dépenses"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

url = os.getenv('MCP_ZOHO_BOOKS_URL')
key = os.getenv('MCP_ZOHO_BOOKS_KEY')
org_id = os.getenv('ZOHO_BOOKS_ORGANIZATION_ID', '110002033190')

def call_tool(tool_name, arguments):
    payload = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': tool_name, 'arguments': arguments}}
    response = requests.post(f'{url}?key={key}', json=payload, headers={'Content-Type': 'application/json'}, timeout=60)
    result = response.json()
    if 'error' in result:
        print(f"Erreur MCP: {result['error']}")
        return None
    content = result.get('result', {}).get('content', [])
    for item in content:
        if item.get('type') == 'text':
            try:
                return json.loads(item.get('text', '{}'))
            except:
                return {'raw': item.get('text')}
    return None

# 1. Chercher le contact Anthropic existant
print("=== Recherche du contact Anthropic ===")
result = call_tool('ZohoBooks_list_contacts', {'query_params': {'organization_id': org_id}})

anthropic_id = None
if result and 'contacts' in result:
    contacts = result.get('contacts', [])
    for c in contacts:
        if 'anthropic' in c.get('contact_name', '').lower():
            anthropic_id = c.get('contact_id')
            print(f"Trouvé: {c.get('contact_name')} - ID: {anthropic_id}")
            break

# 2. Si pas trouvé, créer le contact
if not anthropic_id:
    print("Contact non trouvé, création...")
    result = call_tool('ZohoBooks_create_contact', {
        'query_params': {'organization_id': org_id},
        'body': {
            'contact_name': 'Anthropic',
            'contact_type': 'vendor',
            'company_name': 'Anthropic PBC',
            'website': 'https://anthropic.com'
        }
    })
    if result and 'contact' in result:
        anthropic_id = result['contact'].get('contact_id')
        print(f"Contact créé - ID: {anthropic_id}")
    else:
        print(f"Erreur création: {result}")

if not anthropic_id:
    print("Impossible de trouver ou créer le contact Anthropic")
    exit(1)

# 3. Mettre à jour les dépenses avec le vendor_id
print(f"\n=== Mise à jour des dépenses avec vendor_id: {anthropic_id} ===")

expenses_to_fix = ['89554000000158001', '89554000000156003']

for expense_id in expenses_to_fix:
    print(f"Mise à jour {expense_id}...")
    result = call_tool('ZohoBooks_update_expense', {
        'query_params': {'organization_id': org_id},
        'path_variables': {'expense_id': expense_id},
        'body': {
            'vendor_id': anthropic_id
        }
    })
    if result and 'expense' in result:
        exp = result['expense']
        print(f"  [OK] Fournisseur: {exp.get('vendor_name', 'N/A')} (ID: {exp.get('vendor_id', 'N/A')})")
    else:
        print(f"  Réponse: {result}")

print("\n=== Vérification finale ===")
result = call_tool('ZohoBooks_list_expenses', {'query_params': {'organization_id': org_id}})
expenses = result.get('expenses', []) if result else []

for exp in expenses:
    if exp.get('expense_id') in expenses_to_fix:
        print(f"{exp.get('date')} | {exp.get('total')}$ | Fournisseur: {exp.get('vendor_name', 'VIDE')}")
