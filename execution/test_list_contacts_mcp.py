"""
Test de listing des contacts pour verifier les permissions MCP
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

MCP_URL = os.getenv("MCP_ZOHO_BOOKS_URL")
MCP_KEY = os.getenv("MCP_ZOHO_BOOKS_KEY")

print("="*60)
print("TEST LECTURE CONTACTS VIA MCP")
print("="*60)
print()

# Test avec "list contacts" (avec espace comme dans le screenshot)
tools_to_try = [
    "list contacts",
    "get contact",
    "update contact"
]

headers = {"Content-Type": "application/json"}
url_with_key = f"{MCP_URL}?key={MCP_KEY}"

for tool_name in tools_to_try:
    print(f"Test: {tool_name}")
    print("-" * 60)

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": {}
        }
    }

    try:
        response = requests.post(url_with_key, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"  ERREUR: {result['error']['message']}")
        else:
            res = result.get("result", {})
            content = res.get("content", [])
            if content:
                for item in content[:3]:  # Premiers 3 items
                    if item.get("type") == "text":
                        text = item.get("text", "")
                        print(f"  {text[:200]}")  # Premiers 200 chars

    except Exception as e:
        print(f"  EXCEPTION: {e}")

    print()

print("="*60)
