#!/usr/bin/env python3
"""
Liste les outils disponibles dans Zoho Mail MCP
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')


def main():
    mail_url = os.getenv("MCP_ZOHO_MAIL_URL", "")
    mail_key = os.getenv("MCP_ZOHO_MAIL_KEY", "")

    if not mail_url or not mail_key:
        print("MCP_ZOHO_MAIL_URL et MCP_ZOHO_MAIL_KEY requis dans .env")
        return 1

    url = f"{mail_url}?key={mail_key}"

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }

    response = requests.post(
        url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=60
    )

    result = response.json()
    tools = result.get("result", {}).get("tools", [])

    print("=== OUTILS ZOHO MAIL MCP ===\n")

    for tool in tools:
        print(f"Nom: {tool.get('name')}")
        print(f"Description: {tool.get('description', 'N/A')}")
        print(f"Schema:")
        print(json.dumps(tool.get('inputSchema', {}), indent=2))
        print()
        print("-" * 70)
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
