"""
Test direct de creation de contact via MCP Zoho Books
Utilise la syntaxe exacte du protocole MCP
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

MCP_URL = os.getenv("MCP_ZOHO_BOOKS_URL")
MCP_KEY = os.getenv("MCP_ZOHO_BOOKS_KEY")
ORG_ID = os.getenv("ZOHO_BOOKS_ORGANIZATION_ID")

print("="*60)
print("TEST CREATION CONTACT VIA MCP")
print("="*60)
print()

# Methode 1: Appel direct tools/call
# IMPORTANT: Nom d'outil corrigé selon MCP officiel (espaces, minuscules, pas de préfixe)
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "create contact",
        "arguments": {
            "query_params": {
                "organization_id": ORG_ID
            },
            "body": {
                "contact_name": "Solution Comptabilite - Sebastien Vachon",
                "contact_type": "vendor",
                "email": "info@solutioncomptabilite.com",
                "phone": "(514) 880-2776",
                "website": "solutioncomptabilite.com",
                "billing_address": {
                    "street": "9500, rue de Limoilou",
                    "city": "Quebec",
                    "state": "QC",
                    "zip": "H1K 0J6",
                    "country": "Canada"
                },
                "notes": "President / Solution Comptabilite"
            }
        }
    }
}

print("Envoi de la requete MCP...")
print(f"URL: {MCP_URL}")
print(f"Methode: tools/call")
print(f"Tool: create_contact")
print()

headers = {"Content-Type": "application/json"}
url_with_key = f"{MCP_URL}?key={MCP_KEY}"

try:
    response = requests.post(url_with_key, json=payload, headers=headers, timeout=30)
    response.raise_for_status()

    result = response.json()

    print("REPONSE MCP:")
    print(json.dumps(result, indent=2))
    print()

    if "error" in result:
        print(f"ERREUR: {result['error']}")
    elif "result" in result:
        print("SUCCES!")
        res_content = result.get("result", {})
        print(f"Contenu: {res_content}")

        # Analyser le contenu
        if isinstance(res_content, dict):
            content = res_content.get("content", [])
            if content:
                for item in content:
                    if item.get("type") == "text":
                        print(f"Message: {item.get('text')}")

except requests.exceptions.RequestException as e:
    print(f"ERREUR REQUETE: {e}")
except Exception as e:
    print(f"ERREUR: {e}")

print()
print("="*60)
