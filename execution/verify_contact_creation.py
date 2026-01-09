"""
Verifier que Sebastien Vachon a ete ajoute a Zoho Books
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
ORG_ID = os.getenv("ZOHO_BOOKS_ORGANIZATION_ID")
MCP_URL = os.getenv("MCP_ZOHO_BOOKS_URL")
MCP_KEY = os.getenv("MCP_ZOHO_BOOKS_KEY")


def call_mcp(method: str, params: dict):
    """Appelle le MCP server Zoho Books."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }

    headers = {"Content-Type": "application/json"}
    url_with_key = f"{MCP_URL}?key={MCP_KEY}"

    response = requests.post(url_with_key, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    result = response.json()

    if "error" in result:
        raise Exception(f"Erreur MCP: {result['error']}")

    return result.get("result", {})


print("="*60)
print("VERIFICATION DES CONTACTS - ZOHO BOOKS")
print("="*60)
print()

# Lister tous les contacts
print("Liste des contacts recents...")
print()

try:
    result = call_mcp("tools/call", {
        "name": "list_contacts",
        "arguments": {
            "organization_id": ORG_ID
        }
    })

    # Le resultat peut etre structure differemment
    print("Reponse MCP:")
    print(result)
    print()

    # Chercher Sebastien Vachon
    if isinstance(result, dict):
        contacts = result.get("contacts", [])
        if contacts:
            print(f"Nombre de contacts: {len(contacts)}")
            print()
            for contact in contacts[:10]:  # Premiers 10
                name = contact.get("contact_name", "")
                if "Vachon" in name or "Sebastien" in name:
                    print(f"TROUVE: {name}")
                    print(f"  ID: {contact.get('contact_id')}")
                    print(f"  Email: {contact.get('email')}")
                    print(f"  Phone: {contact.get('phone')}")
                    print()
        else:
            print("Aucun contact trouve")
    else:
        print(f"Format inattendu: {type(result)}")

except Exception as e:
    print(f"Erreur: {e}")

print("="*60)
