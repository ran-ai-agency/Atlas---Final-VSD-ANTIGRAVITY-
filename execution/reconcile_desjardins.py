#!/usr/bin/env python3
"""Réconciliation: Comparer les dépenses Zoho Books avec l'état de compte Desjardins"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

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

# Récupérer toutes les dépenses Zoho
print("=== Récupération des dépenses Zoho Books ===\n")
result = call_tool('ZohoBooks_list_expenses', {'query_params': {'organization_id': org_id}})
zoho_expenses = result.get('expenses', []) if result else []

# Filtrer pour décembre 2025 et janvier 2026
filtered_zoho = []
for exp in zoho_expenses:
    date_str = exp.get('date', '')
    if date_str.startswith('2025-12') or date_str.startswith('2026-01'):
        filtered_zoho.append(exp)

# Trier par date
filtered_zoho.sort(key=lambda x: x.get('date', ''))

print(f"Dépenses Zoho (déc 2025 - jan 2026): {len(filtered_zoho)}\n")

# Afficher les dépenses Zoho
print("=" * 80)
print("DÉPENSES DANS ZOHO BOOKS")
print("=" * 80)
for exp in filtered_zoho:
    date = exp.get('date', 'N/A')
    amount = float(exp.get('total', 0))
    vendor = exp.get('vendor_name', '') or 'N/A'
    account = exp.get('account_name', '')
    paid_through = exp.get('paid_through_account_name', '')
    ref = exp.get('reference_number', '')
    desc = exp.get('description', '')[:40] if exp.get('description') else ''
    
    print(f"{date} | {amount:>8.2f} $ | {vendor[:25]:<25} | {paid_through[:15]} | {desc}")

print()

# État de compte Desjardins (données fournies par l'utilisateur)
desjardins_transactions = [
    # Janvier 2026
    {"date": "2026-01-09", "description": "Google Workspace", "amount": 14.94, "status": "autorisée"},
    {"date": "2026-01-08", "description": "Www.perplexity.ai", "amount": 0.00, "status": "autorisée"},
    {"date": "2026-01-08", "description": "Tldx Solutions Gmbh", "amount": 44.00, "status": "facturée"},
    {"date": "2026-01-08", "description": "Www.perplexity.ai", "amount": 8.19, "status": "facturée"},
    {"date": "2026-01-02", "description": "Claude.ai Subscription", "amount": 243.45, "status": "facturée"},
    {"date": "2026-01-02", "description": "Anthropic", "amount": 16.18, "status": "facturée"},
    # Décembre 2025
    {"date": "2025-12-28", "description": "Www.coursebox.ai", "amount": 42.11, "status": "facturée"},
    {"date": "2025-12-28", "description": "PayPal (Zoho)", "amount": 17.25, "status": "facturée"},
    {"date": "2025-12-21", "description": "Google One", "amount": 31.03, "status": "facturée"},
    {"date": "2025-12-19", "description": "Genspark.ai", "amount": 35.34, "status": "facturée"},
    {"date": "2025-12-18", "description": "PayPal", "amount": 15.20, "status": "facturée"},
    {"date": "2025-12-17", "description": "Claude.ai Subscription", "amount": 130.65, "status": "facturée"},
    {"date": "2025-12-15", "description": "Claude.ai Subscription", "amount": 32.19, "status": "facturée"},
    {"date": "2025-12-15", "description": "Spt Publishing.com Llc", "amount": 459.61, "status": "facturée"},
    {"date": "2025-12-13", "description": "Openai Chatgpt Subscr", "amount": 325.19, "status": "facturée"},
    {"date": "2025-12-09", "description": "Google Workspace", "amount": 14.94, "status": "facturée"},
    {"date": "2025-12-08", "description": "Tldx Solutions Gmbh", "amount": 44.00, "status": "facturée"},
    {"date": "2025-12-05", "description": "Manus Ai", "amount": 60.19, "status": "facturée"},
    {"date": "2025-12-04", "description": "Genspark.ai", "amount": 28.66, "status": "facturée"},
    {"date": "2025-12-03", "description": "PayPal", "amount": 16.10, "status": "facturée"},
]

print("=" * 80)
print("ÉTAT DE COMPTE DESJARDINS VISA")
print("=" * 80)
for tx in desjardins_transactions:
    print(f"{tx['date']} | {tx['amount']:>8.2f} $ | {tx['description']:<30} | {tx['status']}")

print()

# Réconciliation
print("=" * 80)
print("RÉCONCILIATION: ASSOCIATIONS")
print("=" * 80)
print()

def find_zoho_match(date, amount, description):
    """Cherche une correspondance dans Zoho"""
    matches = []
    for exp in filtered_zoho:
        zoho_date = exp.get('date', '')
        zoho_amount = float(exp.get('total', 0))
        zoho_vendor = (exp.get('vendor_name', '') or '').lower()
        zoho_desc = (exp.get('description', '') or '').lower()
        
        # Correspondance par date et montant approximatif
        if zoho_date == date and abs(zoho_amount - amount) < 1.0:
            matches.append(exp)
        # Correspondance par montant exact même si date différente
        elif abs(zoho_amount - amount) < 0.01:
            matches.append(exp)
    return matches

for tx in desjardins_transactions:
    date = tx['date']
    amount = tx['amount']
    desc = tx['description']
    
    matches = find_zoho_match(date, amount, desc)
    
    print(f"📋 DESJARDINS: {date} | {amount:.2f}$ | {desc}")
    
    if matches:
        for m in matches:
            zoho_date = m.get('date')
            zoho_amount = float(m.get('total', 0))
            zoho_vendor = m.get('vendor_name', '') or 'N/A'
            zoho_id = m.get('expense_id')
            
            # Vérifier si les montants correspondent
            if abs(zoho_amount - amount) < 0.01:
                status = "✅ CORRESPONDANCE EXACTE"
            else:
                status = f"⚠️ ÉCART: Zoho={zoho_amount:.2f}$ vs Relevé={amount:.2f}$"
            
            print(f"   └─ ZOHO: {zoho_date} | {zoho_amount:.2f}$ | {zoho_vendor} | ID: {zoho_id}")
            print(f"      {status}")
    else:
        print(f"   └─ ❌ AUCUNE CORRESPONDANCE DANS ZOHO")
    
    print()
