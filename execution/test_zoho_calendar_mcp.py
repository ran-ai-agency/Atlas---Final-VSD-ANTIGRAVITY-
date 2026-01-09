#!/usr/bin/env python3
"""
Test des différents appels Zoho Calendar MCP pour comprendre la structure
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')


class ZohoCalendarClient:
    """Client pour Zoho Calendar via MCP"""

    def __init__(self):
        self.base_url = os.getenv('MCP_ZOHO_CALENDAR_URL')
        self.key = os.getenv('MCP_ZOHO_CALENDAR_KEY')
        self.url = f"{self.base_url}?key={self.key}"

    def _call(self, method: str, params: dict) -> dict:
        """Appelle le MCP Zoho Calendar"""
        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": method,
            "params": params
        }

        print(f"\n[REQUEST] {method}")
        print(json.dumps(payload, indent=2))

        response = requests.post(
            self.url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        response.raise_for_status()

        result = response.json()
        print(f"\n[RESPONSE]")
        print(json.dumps(result, indent=2, default=str))

        if "error" in result:
            raise Exception(f"MCP Error: {result['error']}")

        return result.get("result", {})


def main():
    client = ZohoCalendarClient()

    print("=" * 60)
    print("TEST 1: Liste des outils disponibles")
    print("=" * 60)

    try:
        result = client._call("tools/list", {})
        tools = result.get("tools", [])
        print(f"\n✓ {len(tools)} outils trouvés")

        for tool in tools:
            if "getEvents" in tool.get("name", ""):
                print(f"\nOutil: {tool.get('name')}")
                print(f"Description: {tool.get('description', 'N/A')}")
                print(f"Input Schema:")
                print(json.dumps(tool.get('inputSchema', {}), indent=2))

    except Exception as e:
        print(f"\n✗ Erreur: {e}")

    print("\n" + "=" * 60)
    print("TEST 2: Obtenir tous les calendriers")
    print("=" * 60)

    try:
        result = client._call("tools/call", {
            "name": "ZohoCalendar_getAllCalendar",
            "arguments": {}
        })
        print(f"\n✓ Calendriers récupérés")

    except Exception as e:
        print(f"\n✗ Erreur: {e}")

    print("\n" + "=" * 60)
    print("TEST 3: Tester getEventsInRange avec différentes structures")
    print("=" * 60)

    # Aujourd'hui
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1) - timedelta(seconds=1)

    # UTC
    today_start_utc = today_start + timedelta(hours=5)
    today_end_utc = today_end + timedelta(hours=5)

    start_str = today_start_utc.strftime('%Y%m%dT%H%M%S') + 'Z'
    end_str = today_end_utc.strftime('%Y%m%dT%H%M%S') + 'Z'

    calendar_uid = "033c7928ba314969a0a0a6b5119ac590"

    # Test 1: Avec body
    print("\n--- Tentative 1: arguments.body ---")
    try:
        result = client._call("tools/call", {
            "name": "ZohoCalendar_getEventsInRange",
            "arguments": {
                "body": {
                    "caluid": calendar_uid,
                    "start": start_str,
                    "end": end_str,
                    "timezone": "America/Toronto"
                }
            }
        })
        print(f"\n✓ SUCCESS avec body!")
    except Exception as e:
        print(f"\n✗ Échec: {e}")

    # Test 2: Sans body, paramètres directs
    print("\n--- Tentative 2: arguments directs ---")
    try:
        result = client._call("tools/call", {
            "name": "ZohoCalendar_getEventsInRange",
            "arguments": {
                "caluid": calendar_uid,
                "start": start_str,
                "end": end_str,
                "timezone": "America/Toronto"
            }
        })
        print(f"\n✓ SUCCESS avec arguments directs!")
    except Exception as e:
        print(f"\n✗ Échec: {e}")

    # Test 3: Avec range au lieu de start/end
    print("\n--- Tentative 3: avec range ---")
    try:
        result = client._call("tools/call", {
            "name": "ZohoCalendar_getEventsInRange",
            "arguments": {
                "caluid": calendar_uid,
                "range": {
                    "start": start_str,
                    "end": end_str
                },
                "timezone": "America/Toronto"
            }
        })
        print(f"\n✓ SUCCESS avec range!")
    except Exception as e:
        print(f"\n✗ Échec: {e}")


if __name__ == "__main__":
    main()
