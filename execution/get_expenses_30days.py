#!/usr/bin/env python3
"""Retrieve expenses using correct tool name"""

import os
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

def call_tool(tool_name: str, arguments: dict = None):
    url = os.getenv("MCP_ZOHO_BOOKS_URL")
    key = os.getenv("MCP_ZOHO_BOOKS_KEY")
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }
    
    response = requests.post(f"{url}?key={key}", json=payload, headers={"Content-Type": "application/json"}, timeout=60)
    result = response.json()
    
    if "error" in result:
        print(f"Erreur MCP: {result['error']}")
        return None
    
    content = result.get("result", {}).get("content", [])
    for item in content:
        if item.get("type") == "text":
            try:
                return json.loads(item.get("text", "{}"))
            except:
                return {"raw": item.get("text")}
    return None

def main():
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    print(f"Récupération des dépenses du {thirty_days_ago} au {today}...")
    
    org_id = os.getenv("ZOHO_BOOKS_ORGANIZATION_ID", "110002033190")
    
    # Appel avec le bon nom d'outil
    result = call_tool("ZohoBooks_list_expenses", {
        "query_params": {
            "organization_id": org_id,
            "date_start": thirty_days_ago.isoformat(),
            "date_end": today.isoformat()
        }
    })
    
    if not result or "raw" in result:
        # Essayer sans filtres de date
        print("Tentative sans filtres de date...")
        result = call_tool("ZohoBooks_list_expenses", {
            "query_params": {
                "organization_id": org_id
            }
        })
    
    if not result:
        print("Échec de la récupération des dépenses.")
        return
    
    print(f"\n[DEBUG] Clés dans le résultat: {list(result.keys())}")
    if "expenses" in result:
        print(f"[DEBUG] Nombre d'expenses dans la réponse brute: {len(result.get('expenses', []))}")
    else:
        print(f"[DEBUG] Réponse brute (premiers 500 chars): {str(result)[:500]}")
    
    expenses = result.get("expenses", [])
    
    # Filtrer par date si nécessaire
    filtered = []
    for exp in expenses:
        exp_date_str = exp.get("date", "")
        if exp_date_str:
            try:
                exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
                if thirty_days_ago <= exp_date <= today:
                    filtered.append(exp)
            except:
                pass
    
    print(f"\nDépenses des 30 derniers jours: {len(filtered)}")
    print("-" * 70)
    
    total = 0
    categories = {}
    recurring = {}
    
    for exp in filtered:
        date = exp.get("date", "N/A")
        amount = float(exp.get("total", 0))
        vendor = exp.get("vendor_name", "Inconnu")
        account = exp.get("account_name", "Non catégorisé")
        
        print(f"{date} | {amount:>8.2f} $ | {vendor[:25]:<25} | {account}")
        
        total += amount
        categories[account] = categories.get(account, 0) + amount
        
        # Tracker les vendeurs récurrents
        recurring[vendor] = recurring.get(vendor, 0) + amount
    
    print("-" * 70)
    print(f"TOTAL: {total:.2f} $")
    
    print("\n=== PAR CATÉGORIE ===")
    for cat, amt in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat:<35}: {amt:>8.2f} $")
    
    print("\n=== PAR FOURNISSEUR ===")
    for vendor, amt in sorted(recurring.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {vendor:<35}: {amt:>8.2f} $")
    
    # Prévision pour les 30 prochains jours
    print("\n" + "=" * 70)
    print("PRÉVISION POUR LES 30 PROCHAINS JOURS")
    print("=" * 70)
    print(f"Basé sur les dépenses des 30 derniers jours: {total:.2f} $")
    print(f"Projection linéaire: ~{total:.2f} $ pour les 30 prochains jours")
    
    # Sauvegarder les données pour analyse
    with open(Path(__file__).parent.parent / ".tmp" / "expenses_30days.json", "w", encoding="utf-8") as f:
        json.dump({
            "period": {"from": thirty_days_ago.isoformat(), "to": today.isoformat()},
            "total": total,
            "count": len(filtered),
            "by_category": categories,
            "by_vendor": recurring,
            "expenses": filtered
        }, f, indent=2, ensure_ascii=False)
    print("\nDonnées sauvegardées dans .tmp/expenses_30days.json")

if __name__ == "__main__":
    main()
