#!/usr/bin/env python3
"""
Analyse des dépenses des 30 derniers jours via Zoho Books
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

# Organisation ID
ORGANIZATION_ID = os.getenv("ZOHO_BOOKS_ORGANIZATION_ID", "110002033190")

def call_mcp(method: str, params: dict = None):
    """Appelle le MCP server Zoho Books."""
    url = os.getenv("MCP_ZOHO_BOOKS_URL")
    key = os.getenv("MCP_ZOHO_BOOKS_KEY")

    if not url or not key:
        print("Erreur: MCP_ZOHO_BOOKS_URL ou MCP_ZOHO_BOOKS_KEY manquant dans .env")
        return None

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(f"{url}?key={key}", json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"Erreur MCP: {result['error']}")
            return None

        return result.get("result", {})
    except Exception as e:
        print(f"Exception lors de l'appel MCP: {e}")
        return None

def call_tool(tool_name: str, query_params: dict = None, body: dict = None, path_variables: dict = None):
    """Appelle un outil spécifique avec le bon format de paramètres."""
    arguments = {}

    if query_params:
        arguments["query_params"] = query_params
    if body:
        arguments["body"] = body
    if path_variables:
        arguments["path_variables"] = path_variables

    result = call_mcp("tools/call", {
        "name": tool_name,
        "arguments": arguments
    })

    if result:
        content = result.get("content", [])
        for item in content:
            if item.get("type") == "text":
                text = item.get("text", "{}")
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    # Parfois le texte n'est pas du JSON valide ou est juste un message
                    return {"raw_text": text}
    return None

def list_expenses(org_id: str, from_date: str, to_date: str):
    """Liste les dépenses pour une période donnée."""
    # Note: L'outil 'list expenses' semble supporter des filtres dans query_params
    # On essaie de passer filter_by ou date_start/end si supporté, sinon on filtrera côté client
    # D'après la doc standard Zoho Books API, c'est 'date_start' et 'date_end' mais le tool MCP mapping peut varier
    # On va récupérer tout et filtrer si nécessaire, mais on tente les params
    
    params = {"organization_id": org_id}
    # On retire les filtres de date pour tester si c'est la cause de l'erreur
    # params["date_start"] = from_date
    # params["date_end"] = to_date
    
    print(f"Appel de 'list expenses' avec params: {params}")
    result = call_tool("list expenses", query_params=params)

    if result:
        expenses = result.get("expenses", [])
        return expenses
    return []

def main():
    try:
        # Test de connexion
        print("Test de la connexion MCP (get organization)...")
        org = call_tool("getOrganization", query_params={}) # Trying camelCase based on client
        if not org or "error" in str(org):
            print("Tentative avec 'get organization' (espace)...")
            org = call_tool("get organization", query_params={})
            
        if org:
            print(f"Connexion OK: {org.get('name')} (ID: {org.get('organization_id')})")
        else:
            print("Échec du test de connexion.")
            # On continue quand même pour voir

        # Période: 30 derniers jours
        today = datetime.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        print(f"Récupération des dépenses du {thirty_days_ago} au {today}...")
        
        expenses = list_expenses(
            org_id=ORGANIZATION_ID,
            from_date=thirty_days_ago.isoformat(),
            to_date=today.isoformat()
        )
        
        # Filtrage manuel si l'API n'a pas filtré
        filtered_expenses = []
        for exp in expenses:
            exp_date = exp.get('date', '')
            if exp_date:
                d = datetime.strptime(exp_date, "%Y-%m-%d").date()
                if thirty_days_ago <= d <= today:
                    filtered_expenses.append(exp)
        
        expenses = filtered_expenses
        
        print(f"Nombre de dépenses trouvées: {len(expenses)}")
        
        total_amount = 0
        categories = {}
        
        print("\nDétail des dépenses (30 derniers jours):")
        print("-" * 60)
        for expense in expenses:
            date = expense.get('date', 'N/A')
            amount = float(expense.get('total', 0))
            # Essayer de trouver le nom du compte ou category
            # Souvent 'account_name' dans l'objet expense
            account_name = expense.get('account_name', 'Non catégorisé')
            vendor_name = expense.get('vendor_name', 'Inconnu')
            description = expense.get('description', '')
            
            print(f"{date} | {amount:>8.2f} $ | {vendor_name[:20]:<20} | {account_name}")
            
            total_amount += amount
            
            if account_name not in categories:
                categories[account_name] = 0
            categories[account_name] += amount
            
        print("-" * 60)
        print(f"Total des dépenses: {total_amount:.2f} $")
        
        print("\nPar catégorie:")
        for cat, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {cat:<30}: {amount:>8.2f} $")

    except Exception as e:
        print(f"Erreur globale: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    main()
