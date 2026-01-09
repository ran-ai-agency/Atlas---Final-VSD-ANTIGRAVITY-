#!/usr/bin/env python3
"""
⚠️ DEPRECATED: Ce script est déprécié depuis le 8 janvier 2026.
Utiliser Google Calendar pour créer des événements.
Voir: execution/DEPRECATED_ZOHO_CALENDAR_SCRIPTS.md

Ajoute l'événement "Elections de C.A." au calendrier Zoho
"""

import os
import sys
import json
import requests
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

    def get_all_calendars(self) -> list:
        """Récupère tous les calendriers"""
        result = self._call("tools/call", {
            "name": "ZohoCalendar_getAllCalendar",
            "arguments": {}
        })

        # Parser le résultat
        content = result.get('content', [])
        if isinstance(content, list) and len(content) > 0:
            text = content[0].get('text', '')
            if text:
                try:
                    data = json.loads(text) if isinstance(text, str) else text
                    return data.get('calendars', [])
                except json.JSONDecodeError:
                    return []
        return []

    def add_event(self, caluid: str, title: str, description: str, start: str, end: str, timezone: str = "America/Toronto") -> dict:
        """Ajoute un événement au calendrier"""
        result = self._call("tools/call", {
            "name": "ZohoCalendar_addEvent",
            "arguments": {
                "body": {
                    "caluid": caluid,
                    "title": title,
                    "description": description,
                    "dateandtime": {
                        "start": start,
                        "end": end,
                        "timezone": timezone
                    },
                    "isallday": False
                }
            }
        })

        return result


def main():
    """Fonction principale"""
    client = ZohoCalendarClient()

    print("=== Ajout de l'evenement 'Elections de C.A.' ===\n")

    try:
        # Étape 1: Récupérer le calendrier principal
        print("1. Recherche du calendrier principal...")
        calendars = client.get_all_calendars()

        if not calendars:
            print("[ERREUR] Aucun calendrier trouve")
            return 1

        # Chercher le calendrier principal ou personnel
        caluid = None
        for cal in calendars:
            if cal.get('isprimary') or cal.get('name') == 'Personal':
                caluid = cal.get('uid')
                print(f"   Calendrier trouve: {cal.get('name')} ({caluid})")
                break

        if not caluid:
            # Utiliser le premier calendrier disponible
            caluid = calendars[0].get('uid')
            print(f"   Utilisation du premier calendrier: {calendars[0].get('name')} ({caluid})")

        # Étape 2: Ajouter l'événement
        print("\n2. Ajout de l'evenement...")
        print("   Titre: Elections de C.A.")
        print("   Date: 12 fevrier 2026")
        print("   Heure: 8h30 - 10h00 (heure de l'Est)")

        result = client.add_event(
            caluid=caluid,
            title="Elections de C.A.",
            description="Elections du Conseil d'Administration - GR International Vaudreuil-Dorion",
            start="20260212T083000",  # 12 février 2026, 8h30
            end="20260212T100000",    # 12 février 2026, 10h00
            timezone="America/Toronto"
        )

        print("\n[SUCCES] Evenement ajoute au calendrier!")

        # Afficher le résultat si disponible
        content = result.get('content', [])
        if content:
            text = content[0].get('text', '')
            if text:
                try:
                    data = json.loads(text) if isinstance(text, str) else text
                    events = data.get('events', [])
                    if events:
                        event_uid = events[0].get('uid', 'N/A')
                        print(f"   UID de l'evenement: {event_uid}")
                except json.JSONDecodeError:
                    pass

        return 0

    except Exception as e:
        print(f"\n[ERREUR] Impossible d'ajouter l'evenement: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
