#!/usr/bin/env python3
"""Test direct MCP calls to discover available tools"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

def main():
    url = os.getenv("MCP_ZOHO_BOOKS_URL")
    key = os.getenv("MCP_ZOHO_BOOKS_KEY")
    
    print(f"URL: {url}")
    print(f"Key: {'*' * 10 if key else 'MISSING'}")
    
    if not url or not key:
        print("Configuration MCP manquante!")
        return
    
    # Test 1: tools/list
    print("\n=== Test tools/list ===")
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        response = requests.post(f"{url}?key={key}", json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        result = response.json()
        
        if "error" in result:
            print(f"Erreur: {result['error']}")
        else:
            tools = result.get("result", {}).get("tools", [])
            print(f"Nombre d'outils disponibles: {len(tools)}")
            
            # Chercher les outils liés aux expenses
            expense_tools = [t for t in tools if "expense" in t.get("name", "").lower()]
            print(f"\nOutils relatifs aux dépenses ({len(expense_tools)}):")
            for t in expense_tools:
                print(f"  - {t.get('name')}: {t.get('description', '')[:80]}")
                
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()
