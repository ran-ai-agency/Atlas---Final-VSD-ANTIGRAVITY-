#!/usr/bin/env python3
"""
Crée un événement dans Zoho Calendar via MCP
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
        self.base_url = os.getenv('MCP_ZOHO_CALENDAR_URL', 'https://zohocalendar-110002203871.zohomcp.ca/mcp/message')
        self.key = os.getenv('MCP_ZOHO_CALENDAR_KEY', 'e8e366a6a3e982cf1e21fbd9dcb5ee97')
        self.url = f"{self.base_url}?key={self.key}"

    def _call(self, method: str, params: dict) -> dict:
        """Appelle le MCP Zoho Calendar"""
        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": method,
            "params": params
        }

        response = requests.post(
            self.url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        response.raise_for_status()

        result = response.json()
        if "error" in result:
            raise Exception(f"MCP Error: {result['error']}")

        return result.get("result", {})

    def list_tools(self) -> list:
        """Liste les outils disponibles"""
        result = self._call("tools/list", {})
        return result.get("tools", [])

    def get_calendars(self) -> list:
        """Liste les calendriers disponibles"""
        result = self._call("tools/call", {
            "name": "ZohoCalendar_getAllCalendar",
            "arguments": {}
        })
        return result

    def create_event(self, title: str, start: datetime, end: datetime,
                     description: str = "", location: str = "",
                     calendar_uid: str = "033c7928ba314969a0a0a6b5119ac590") -> dict:
        """Crée un événement dans Zoho Calendar"""

        # Format Zoho: YYYYMMDDTHHMMSSZ (UTC)
        # Convertir l'heure locale (America/Toronto = UTC-5) en UTC
        from datetime import timedelta
        start_utc = start + timedelta(hours=5)
        end_utc = end + timedelta(hours=5)

        start_str = start_utc.strftime('%Y%m%dT%H%M%S') + 'Z'
        end_str = end_utc.strftime('%Y%m%dT%H%M%S') + 'Z'

        result = self._call("tools/call", {
            "name": "ZohoCalendar_addEvent",
            "arguments": {
                "body": {
                    "caluid": calendar_uid,
                    "title": title,
                    "dateandtime": {
                        "start": start_str,
                        "end": end_str,
                        "timezone": "America/Toronto"
                    },
                    "description": description,
                    "isallday": False
                }
            }
        })

        return result


def main():
    """Fonction principale"""
    import argparse

    parser = argparse.ArgumentParser(description='Créer un événement Zoho Calendar')
    parser.add_argument('--title', help='Titre de l\'événement')
    parser.add_argument('--date', help='Date (YYYY-MM-DD)')
    parser.add_argument('--start-time', help='Heure de début (HH:MM)')
    parser.add_argument('--end-time', help='Heure de fin (HH:MM)')
    parser.add_argument('--description', default='', help='Description')
    parser.add_argument('--location', default='', help='Lieu')
    parser.add_argument('--list-tools', action='store_true', help='Lister les outils disponibles')

    args = parser.parse_args()

    client = ZohoCalendarClient()

    if args.list_tools:
        print("Outils disponibles:")
        tools = client.list_tools()
        for tool in tools:
            print(f"  - {tool.get('name')}: {tool.get('description', '')[:80]}")
        return 0

    # Parser les dates
    date_str = args.date
    start_time = args.start_time
    end_time = args.end_time

    start_dt = datetime.strptime(f"{date_str} {start_time}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{date_str} {end_time}", "%Y-%m-%d %H:%M")

    print(f"Création de l'événement:")
    print(f"  Titre: {args.title}")
    print(f"  Date: {date_str}")
    print(f"  Heure: {start_time} - {end_time}")
    if args.description:
        print(f"  Description: {args.description}")
    print()

    try:
        result = client.create_event(
            title=args.title,
            start=start_dt,
            end=end_dt,
            description=args.description,
            location=args.location
        )
        print("[OK] Evenement cree avec succes!")
        print(json.dumps(result, indent=2, default=str))
        return 0
    except Exception as e:
        print(f"[ERREUR] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
