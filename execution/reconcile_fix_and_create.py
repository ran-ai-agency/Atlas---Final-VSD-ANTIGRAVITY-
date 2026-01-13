#!/usr/bin/env python3
"""
Réconciliation Desjardins - Étapes 1 & 2:
1. Corriger les écarts de montant (Genspark)
2. Créer les 8 dépenses manquantes
"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

url = os.getenv('MCP_ZOHO_BOOKS_URL')
key = os.getenv('MCP_ZOHO_BOOKS_KEY')
org_id = os.getenv('ZOHO_BOOKS_ORGANIZATION_ID', '110002033190')

# IDs des comptes
ACCOUNT_IT = "89554000000000385"  # Dépenses informatiques et d'Internet
PAID_DESJARDINS = "89554000000117281"  # Desjardins Visa

def call_tool(tool_name, arguments):
    payload = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': tool_name, 'arguments': arguments}}
    response = requests.post(f'{url}?key={key}', json=payload, headers={'Content-Type': 'application/json'}, timeout=60)
    result = response.json()
    if 'error' in result:
        print(f"  Erreur MCP: {result['error']}")
        return None
    content = result.get('result', {}).get('content', [])
    for item in content:
        if item.get('type') == 'text':
            try:
                return json.loads(item.get('text', '{}'))
            except:
                return {'raw': item.get('text')}
    return None

print("=" * 70)
print("ÉTAPE 1: CORRECTION DES ÉCARTS DE MONTANT")
print("=" * 70)

# Corrections de montant
corrections = [
    {
        "expense_id": "89554000000156037",
        "description": "Genspark.ai - 19 déc 2025",
        "old_amount": 35.00,
        "new_amount": 35.34
    },
    {
        "expense_id": "89554000000117349",
        "description": "Genspark.ai - 4 déc 2025",
        "old_amount": 28.67,
        "new_amount": 28.66
    }
]

for corr in corrections:
    print(f"\n📝 {corr['description']}")
    print(f"   Ancien: {corr['old_amount']:.2f}$ → Nouveau: {corr['new_amount']:.2f}$")
    
    result = call_tool('ZohoBooks_update_expense', {
        'query_params': {'organization_id': org_id},
        'path_variables': {'expense_id': corr['expense_id']},
        'body': {
            'amount': corr['new_amount']
        }
    })
    
    if result and 'expense' in result:
        exp = result['expense']
        print(f"   ✅ Corrigé - Nouveau montant: {exp.get('total')}$")
    else:
        print(f"   ❌ Erreur: {result}")

print("\n" + "=" * 70)
print("ÉTAPE 2: CRÉATION DES 8 DÉPENSES MANQUANTES")
print("=" * 70)

# Dépenses à créer
new_expenses = [
    {
        "date": "2026-01-09",
        "amount": 14.94,
        "vendor_name": "Google Workspace",
        "description": "Abonnement Google Workspace - Janvier 2026",
        "reference_number": "GWORKSPACE-2026-01-09"
    },
    {
        "date": "2026-01-08",
        "amount": 44.00,
        "vendor_name": "DeepL",
        "description": "Abonnement DeepL Pro - Janvier 2026 (Tldx Solutions)",
        "reference_number": "DEEPL-2026-01-08"
    },
    {
        "date": "2026-01-08",
        "amount": 8.19,
        "vendor_name": "Perplexity AI",
        "description": "Abonnement Perplexity AI",
        "reference_number": "PERPLEXITY-2026-01-08"
    },
    {
        "date": "2026-01-02",
        "amount": 16.18,
        "vendor_name": "Anthropic",
        "description": "Anthropic API Usage - Janvier 2026",
        "reference_number": "ANTHROPIC-API-2026-01-02"
    },
    {
        "date": "2025-12-28",
        "amount": 42.11,
        "vendor_name": "Coursebox.ai",
        "description": "Abonnement Coursebox.ai",
        "reference_number": "COURSEBOX-2025-12-28"
    },
    {
        "date": "2025-12-21",
        "amount": 31.03,
        "vendor_name": "Google One",
        "description": "Abonnement Google One Storage",
        "reference_number": "GOOGLEONE-2025-12-21"
    },
    {
        "date": "2025-12-18",
        "amount": 15.20,
        "vendor_name": "PayPal",
        "description": "PayPal - Service professionnel",
        "reference_number": "PAYPAL-2025-12-18"
    },
    {
        "date": "2025-12-15",
        "amount": 459.61,
        "vendor_name": "SPT Publishing",
        "description": "SPT Publishing.com LLC - Achat",
        "reference_number": "SPTPUB-2025-12-15"
    }
]

created_count = 0
for exp in new_expenses:
    print(f"\n📝 Création: {exp['date']} | {exp['amount']:.2f}$ | {exp['vendor_name']}")
    
    result = call_tool('ZohoBooks_create_expense', {
        'query_params': {'organization_id': org_id},
        'body': {
            'account_id': ACCOUNT_IT,
            'paid_through_account_id': PAID_DESJARDINS,
            'date': exp['date'],
            'amount': exp['amount'],
            'vendor_name': exp['vendor_name'],
            'description': exp['description'],
            'reference_number': exp['reference_number']
        }
    })
    
    if result and 'expense' in result:
        expense = result['expense']
        print(f"   ✅ Créée - ID: {expense.get('expense_id')} | Total: {expense.get('total')}$")
        created_count += 1
    else:
        print(f"   ❌ Erreur: {result}")

print("\n" + "=" * 70)
print("RÉSUMÉ")
print("=" * 70)
print(f"Corrections de montant: {len(corrections)}")
print(f"Dépenses créées: {created_count}/{len(new_expenses)}")
