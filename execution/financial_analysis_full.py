#!/usr/bin/env python3
"""Analyse complète des dépenses (30 derniers jours) et prévisions (30 prochains jours)"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta
from collections import defaultdict

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

# Période d'analyse
today = datetime.now().date()
thirty_days_ago = today - timedelta(days=30)

print("=" * 70)
print(f"ANALYSE FINANCIÈRE - 30 DERNIERS JOURS")
print(f"Période: {thirty_days_ago} → {today}")
print("=" * 70)

# Récupérer les dépenses
result = call_tool('ZohoBooks_list_expenses', {'query_params': {'organization_id': org_id}})
all_expenses = result.get('expenses', []) if result else []

# Filtrer les 30 derniers jours
expenses = []
for exp in all_expenses:
    date_str = exp.get('date', '')
    if date_str:
        try:
            exp_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if thirty_days_ago <= exp_date <= today:
                expenses.append(exp)
        except:
            pass

# Trier par date
expenses.sort(key=lambda x: x.get('date', ''))

print(f"\nNombre de transactions: {len(expenses)}")

# Calculs
total = 0
by_category = defaultdict(float)
by_vendor = defaultdict(float)
by_card = defaultdict(float)
recurring_vendors = set()

# Identifier les vendeurs récurrents (abonnements)
recurring_keywords = ['openai', 'anthropic', 'zoho', 'google', 'deepl', 'genspark', 'perplexity', 
                      'manus', 'coursebox', 'flow', 'quickbooks']

print("\n" + "-" * 70)
print(f"{'DATE':<12} {'MONTANT':>10} {'FOURNISSEUR':<25} {'CARTE':<15}")
print("-" * 70)

for exp in expenses:
    date = exp.get('date', 'N/A')
    amount = float(exp.get('total', 0))
    vendor = exp.get('vendor_name', '') or 'N/A'
    account = exp.get('account_name', 'Non catégorisé')
    card = exp.get('paid_through_account_name', 'N/A')
    
    print(f"{date:<12} {amount:>10.2f}$ {vendor[:25]:<25} {card[:15]}")
    
    total += amount
    by_category[account] += amount
    by_vendor[vendor] += amount
    by_card[card] += amount
    
    # Identifier si récurrent
    for kw in recurring_keywords:
        if kw in vendor.lower():
            recurring_vendors.add(vendor)
            break

print("-" * 70)
print(f"{'TOTAL':<12} {total:>10.2f}$")

# Par catégorie
print("\n" + "=" * 70)
print("PAR CATÉGORIE")
print("=" * 70)
for cat, amt in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
    pct = (amt / total * 100) if total > 0 else 0
    print(f"  {cat[:40]:<40} {amt:>10.2f}$ ({pct:>5.1f}%)")

# Par fournisseur (top 10)
print("\n" + "=" * 70)
print("TOP 10 FOURNISSEURS")
print("=" * 70)
sorted_vendors = sorted(by_vendor.items(), key=lambda x: x[1], reverse=True)[:10]
for vendor, amt in sorted_vendors:
    pct = (amt / total * 100) if total > 0 else 0
    is_recurring = "🔁" if vendor in recurring_vendors else "  "
    print(f"{is_recurring} {vendor[:35]:<35} {amt:>10.2f}$ ({pct:>5.1f}%)")

# Par carte
print("\n" + "=" * 70)
print("PAR CARTE DE PAIEMENT")
print("=" * 70)
for card, amt in sorted(by_card.items(), key=lambda x: x[1], reverse=True):
    pct = (amt / total * 100) if total > 0 else 0
    print(f"  {card:<40} {amt:>10.2f}$ ({pct:>5.1f}%)")

# Calculer récurrents vs ponctuels
recurring_total = sum(by_vendor[v] for v in recurring_vendors)
one_time_total = total - recurring_total

print("\n" + "=" * 70)
print("ANALYSE RÉCURRENTS VS PONCTUELS")
print("=" * 70)
print(f"  Abonnements récurrents:  {recurring_total:>10.2f}$ ({recurring_total/total*100:.1f}%)")
print(f"  Dépenses ponctuelles:    {one_time_total:>10.2f}$ ({one_time_total/total*100:.1f}%)")

# ===== PRÉVISIONS =====
print("\n" + "=" * 70)
print("PRÉVISION - 30 PROCHAINS JOURS")
print("=" * 70)

# Abonnements mensuels attendus (basés sur les données actuelles)
# Note: OpenAI réduit à 20 USD (~28 CAD)
monthly_subscriptions = {
    "OpenAI (réduit à Plus)": 28.00,  # Était ~325$, maintenant 20 USD
    "Anthropic Claude Pro": 32.19,
    "Anthropic API": 16.18,
    "Zoho Canada": 17.25,
    "Google Workspace": 14.94,
    "Google One": 31.03,
    "DeepL Pro": 44.00,
    "Perplexity AI": 8.19,
    "Genspark AI": 35.34,
    "Manus AI": 60.19,
    "Flow Internet": 18.00,
    "QuickBooks": 16.10,
    "Coursebox.ai": 42.11,
}

print("\nABONNEMENTS RÉCURRENTS PRÉVUS:")
print("-" * 50)
recurring_forecast = 0
for name, amt in sorted(monthly_subscriptions.items(), key=lambda x: x[1], reverse=True):
    print(f"  {name:<30} {amt:>10.2f}$")
    recurring_forecast += amt

print("-" * 50)
print(f"  {'SOUS-TOTAL RÉCURRENT':<30} {recurring_forecast:>10.2f}$")

# Variables (repas, déplacements, etc.) - estimation basée sur l'historique
variable_estimate = one_time_total  # On estime similaire au mois passé

print(f"\nDÉPENSES VARIABLES ESTIMÉES:")
print("-" * 50)
print(f"  Repas et divertissements:     ~{one_time_total * 0.3:>8.2f}$")
print(f"  Déplacements:                 ~{one_time_total * 0.2:>8.2f}$")
print(f"  Autres:                       ~{one_time_total * 0.5:>8.2f}$")
print("-" * 50)
print(f"  {'SOUS-TOTAL VARIABLE':<30} ~{variable_estimate:>9.2f}$")

# Totaux
total_forecast = recurring_forecast + variable_estimate
savings_vs_last_month = total - total_forecast

print("\n" + "=" * 70)
print("RÉSUMÉ PRÉVISIONNEL")
print("=" * 70)
print(f"  Dépenses 30 derniers jours:     {total:>10.2f}$")
print(f"  Prévision 30 prochains jours:   {total_forecast:>10.2f}$")
print(f"  Différence:                     {savings_vs_last_month:>+10.2f}$")

if savings_vs_last_month > 0:
    print(f"\n  💰 ÉCONOMIES PRÉVUES: {savings_vs_last_month:.2f}$ (-{savings_vs_last_month/total*100:.1f}%)")
else:
    print(f"\n  ⚠️ HAUSSE PRÉVUE: {abs(savings_vs_last_month):.2f}$ (+{abs(savings_vs_last_month)/total*100:.1f}%)")
