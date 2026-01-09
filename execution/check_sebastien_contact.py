"""
Verifier si Sebastien Vachon est dans Zoho Books
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

MCP_URL = os.getenv("MCP_ZOHO_BOOKS_URL")
MCP_KEY = os.getenv("MCP_ZOHO_BOOKS_KEY")
ORG_ID = os.getenv("ZOHO_BOOKS_ORGANIZATION_ID")


def call_tool(tool_name: str, arguments: dict):
    """Appelle un outil MCP Zoho Books."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
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
print("RECHERCHE DE SEBASTIEN VACHON - ZOHO BOOKS")
print("="*60)
print()

# D'abord, lister les outils disponibles
print("1. Liste des outils disponibles MCP...")
try:
    tools_result = call_tool("tools/list", {})
    print(f"Reponse: {tools_result}")
    print()
except Exception as e:
    print(f"Erreur: {e}")
    print()

# Essayer get_contact avec un nom de recherche
print("2. Recherche par get_contact...")
try:
    result = call_tool("get_contact", {
        "organization_id": ORG_ID,
        "contact_name": "Vachon"
    })
    print(f"Resultat: {result}")
except Exception as e:
    print(f"Erreur: {e}")

print()
print("="*60)
