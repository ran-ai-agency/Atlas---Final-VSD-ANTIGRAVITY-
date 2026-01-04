"""
Script de test pour decouvrir les methodes disponibles sur les MCP servers Zoho
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()


def test_mcp_server():
    """Teste la connexion au MCP server Zoho Books"""
    
    books_url = os.getenv("MCP_ZOHO_BOOKS_URL", "")
    books_key = os.getenv("MCP_ZOHO_BOOKS_KEY", "")
    
    print("=" * 70)
    print("TEST MCP SERVER ZOHO BOOKS")
    print("=" * 70)
    print()
    
    if not books_url or not books_key:
        print("❌ MCP_ZOHO_BOOKS_URL ou MCP_ZOHO_BOOKS_KEY non definis dans .env")
        return
    
    print(f"📡 URL: {books_url[:50]}...")
    print(f"🔑 Key: {books_key[:10]}...")
    print()
    
    # Test 1: Appel simple pour lister les methodes disponibles
    print("Test 1: Appel 'tools/list' pour decouvrir les methodes...")
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {books_key}"
    }
    
    try:
        response = requests.post(books_url, json=payload, headers=headers, timeout=10)
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Reponse recue")
            print(f"  Contenu: {result}")
            
            if "result" in result and "tools" in result["result"]:
                print()
                print("📋 Methodes disponibles:")
                for tool in result["result"]["tools"]:
                    print(f"  - {tool.get('name', 'N/A')}: {tool.get('description', 'N/A')}")
        else:
            print(f"  ❌ Erreur HTTP: {response.status_code}")
            print(f"  Reponse: {response.text[:500]}")
    
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    print()
    
    # Test 2: Essayer d'appeler une methode simple
    print("Test 2: Appel 'zoho_books_list_invoices'...")
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "zoho_books_list_invoices",
        "params": {"status": "all"}
    }
    
    try:
        response = requests.post(books_url, json=payload, headers=headers, timeout=10)
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Reponse recue")
            print(f"  Contenu: {str(result)[:300]}...")
        else:
            print(f"  ❌ Erreur HTTP: {response.status_code}")
            print(f"  Reponse: {response.text[:500]}")
    
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    test_mcp_server()
