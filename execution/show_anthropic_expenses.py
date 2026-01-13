#!/usr/bin/env python3
"""Afficher les détails des dépenses Anthropic créées"""

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
    content = result.get('result', {}).get('content', [])
    for item in content:
        if item.get('type') == 'text':
            try:
                return json.loads(item.get('text', '{}'))
            except:
                return None
    return None

# Récupérer les dépenses récentes
result = call_tool('ZohoBooks_list_expenses', {'query_params': {'organization_id': org_id}})
expenses = result.get('expenses', []) if result else []

# Filtrer les deux dépenses Anthropic récemment créées
target_ids = ['89554000000158001', '89554000000156003']
for exp in expenses:
    if exp.get('expense_id') in target_ids:
        print('=' * 60)
        print(f"DÉPENSE: {exp.get('expense_id')}")
        print('=' * 60)
        print(f"Date:          {exp.get('date')}")
        print(f"Fournisseur:   {exp.get('vendor_name')}")
        print(f"Montant:       {exp.get('total')} CAD")
        print(f"Compte:        {exp.get('account_name')}")
        print(f"Payé via:      {exp.get('paid_through_account_name')}")
        print(f"Référence:     {exp.get('reference_number')}")
        print(f"Description:   {exp.get('description')}")
        print(f"Statut:        {exp.get('status')}")
        print()
