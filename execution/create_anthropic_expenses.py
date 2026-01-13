#!/usr/bin/env python3
"""Vérifier et créer les dépenses Anthropic manquantes"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

url = os.getenv('MCP_ZOHO_BOOKS_URL')
key = os.getenv('MCP_ZOHO_BOOKS_KEY')
org_id = os.getenv('ZOHO_BOOKS_ORGANIZATION_ID', '110002033190')

# IDs des comptes depuis la directive
ACCOUNT_IT = "89554000000000385"  # Dépenses informatiques et d'Internet
PAID_THROUGH_RBC = "89554000000057009"  # RBC MasterCard

def call_tool(tool_name, arguments):
    payload = {
        'jsonrpc': '2.0', 
        'id': 1, 
        'method': 'tools/call', 
        'params': {'name': tool_name, 'arguments': arguments}
    }
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

def main():
    # Vérifier les dépenses Anthropic existantes
    print('=== Vérification des dépenses Anthropic ===')
    result = call_tool('ZohoBooks_list_expenses', {'query_params': {'organization_id': org_id}})
    
    if not result or 'expenses' not in result:
        print("Erreur lors de la récupération des dépenses")
        return
    
    expenses = result.get('expenses', [])
    anthropic_expenses = [e for e in expenses if 'anthropic' in e.get('vendor_name', '').lower()]
    
    print(f'Dépenses Anthropic trouvées: {len(anthropic_expenses)}')
    for e in anthropic_expenses:
        print(f"  - {e.get('date')} | {e.get('total')} $ | Ref: {e.get('reference_number', 'N/A')}")
    
    # Vérifier si les dates spécifiques existent
    dates_to_create = []
    
    if not any(e.get('date') == '2025-12-17' for e in anthropic_expenses):
        print("Date 2025-12-17: MANQUANT - À créer")
        dates_to_create.append(('2025-12-17', 130.65, 'Anthropic Max - Décembre 2025'))
    else:
        print("Date 2025-12-17: EXISTE")
    
    if not any(e.get('date') == '2026-01-02' for e in anthropic_expenses):
        print("Date 2026-01-02: MANQUANT - À créer")
        dates_to_create.append(('2026-01-02', 243.45, 'Anthropic Max - Janvier 2026'))
    else:
        print("Date 2026-01-02: EXISTE")
    
    if not dates_to_create:
        print("\nToutes les dépenses sont déjà enregistrées!")
        return
    
    # Créer les dépenses manquantes
    print(f"\n=== Création de {len(dates_to_create)} dépense(s) ===")
    
    for date, amount, description in dates_to_create:
        print(f"\nCréation: {date} - {amount}$ - {description}")
        
        result = call_tool('ZohoBooks_create_expense', {
            'query_params': {'organization_id': org_id},
            'body': {
                'account_id': ACCOUNT_IT,
                'paid_through_account_id': PAID_THROUGH_RBC,
                'date': date,
                'amount': amount,
                'vendor_name': 'Anthropic',
                'description': description,
                'reference_number': f"ANTHROPIC-{date}"
            }
        })
        
        if result:
            expense = result.get('expense', {})
            if expense:
                print(f"  [OK] Créée - ID: {expense.get('expense_id')}")
            else:
                print(f"  Réponse: {result}")
        else:
            print("  [ERREUR] Échec de création")

if __name__ == "__main__":
    main()
