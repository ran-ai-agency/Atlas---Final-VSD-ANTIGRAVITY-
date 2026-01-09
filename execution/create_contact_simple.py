"""
Creation de contact Zoho Books - Version simplifiee
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
print("CREATION CONTACT - SEBASTIEN VACHON")
print("="*60)
print()

# Version simple avec parametres minimaux
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "create contact",
        "arguments": {
            "contact_name": "Solution Comptabilite - Sebastien Vachon",
            "contact_type": "vendor"
        }
    }
}

print("Tentative 1: Parametres minimaux")
print("-" * 60)

headers = {"Content-Type": "application/json"}
url_with_key = f"{MCP_URL}?key={MCP_KEY}"

try:
    response = requests.post(url_with_key, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    result = response.json()

    print(json.dumps(result, indent=2))

    if "error" in result:
        print(f"\nERREUR: {result['error']['message']}")

        # Tentative 2: Avec plus de details
        print("\nTentative 2: Avec email et phone")
        print("-" * 60)

        payload["params"]["arguments"] = {
            "contact_name": "Solution Comptabilite - Sebastien Vachon",
            "contact_type": "vendor",
            "email": "info@solutioncomptabilite.com",
            "phone": "(514) 880-2776"
        }

        response = requests.post(url_with_key, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()

        print(json.dumps(result, indent=2))

    if "result" in result and not result.get("error"):
        print("\nSUCCES - Contact cree!")
        res = result.get("result", {})
        if "content" in res:
            for item in res["content"]:
                if item.get("type") == "text":
                    print(f"\n{item.get('text')}")

except Exception as e:
    print(f"ERREUR: {e}")

print()
print("="*60)
