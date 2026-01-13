#!/usr/bin/env python3
"""Corriger le nom du fournisseur pour les dépenses Anthropic"""

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

# IDs des dépenses à corriger
expenses_to_fix = [
    ('89554000000158001', '2025-12-17'),
    ('89554000000156003', '2026-01-02')
]

for expense_id, date in expenses_to_fix:
    print(f"Mise à jour de la dépense {expense_id} ({date})...")
    
    result = call_tool('ZohoBooks_update_expense', {
        'query_params': {'organization_id': org_id},
        'path_variables': {'expense_id': expense_id},
        'body': {
            'vendor_name': 'Anthropic'
        }
    })
    
    if result:
        expense = result.get('expense', {})
        if expense:
            print(f"  [OK] Fournisseur mis à jour: {expense.get('vendor_name')}")
        else:
            print(f"  Réponse: {result}")
    else:
        print("  [ERREUR] Échec de mise à jour")

print("\n=== Vérification ===")
result = call_tool('ZohoBooks_list_expenses', {'query_params': {'organization_id': org_id}})
expenses = result.get('expenses', []) if result else []

target_ids = ['89554000000158001', '89554000000156003']
for exp in expenses:
    if exp.get('expense_id') in target_ids:
        print(f"{exp.get('date')} | {exp.get('total')}$ | Fournisseur: {exp.get('vendor_name', 'VIDE')}")
