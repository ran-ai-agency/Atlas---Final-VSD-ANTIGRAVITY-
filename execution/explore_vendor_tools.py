#!/usr/bin/env python3
"""Lister les outils disponibles pour voir comment gérer les vendors"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

url = os.getenv('MCP_ZOHO_BOOKS_URL')
key = os.getenv('MCP_ZOHO_BOOKS_KEY')

# Lister les outils
payload = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list', 'params': {}}
response = requests.post(f'{url}?key={key}', json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
result = response.json()

tools = result.get('result', {}).get('tools', [])

# Chercher les outils liés aux vendors/contacts
print("=== Outils liés aux vendors/contacts ===")
for t in tools:
    name = t.get('name', '').lower()
    if 'vendor' in name or 'contact' in name:
        print(f"  - {t.get('name')}: {t.get('description', '')[:80]}")

print("\n=== Outils liés aux expenses ===")
for t in tools:
    name = t.get('name', '').lower()
    if 'expense' in name:
        # Afficher le schema complet
        print(f"\n{t.get('name')}:")
        schema = t.get('inputSchema', {})
        props = schema.get('properties', {})
        if 'body' in props:
            body_props = props['body'].get('properties', {})
            for key in body_props:
                print(f"    - {key}")
