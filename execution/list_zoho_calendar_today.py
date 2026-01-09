#!/usr/bin/env python3
"""
Liste les événements du jour dans Zoho Calendar
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

    def get_events_today(self) -> dict:
        """Récupère les événements d'aujourd'hui"""

        # Aujourd'hui
        today = datetime.now()

        # Format Zoho pour getEventsInRange: YYYYMMDD (date seulement, pas d'heure)
        start_str = today.strftime('%Y%m%d')
        end_str = today.strftime('%Y%m%d')

        result = self._call("tools/call", {
            "name": "ZohoCalendar_getEventsInRange",
            "arguments": {
                "query_params": {
                    "start": start_str,
                    "end": end_str
                }
            }
        })

        return result


def parse_zoho_datetime(dt_str: str) -> datetime:
    """Parse une date Zoho format 20260108T120000-0500"""
    # Enlever le timezone offset (-0500 ou +0000)
    if '-' in dt_str or '+' in dt_str[-5:]:
        dt_str = dt_str[:-5]
    # Enlever le Z final si présent
    dt_str = dt_str.rstrip('Z')
    return datetime.strptime(dt_str, '%Y%m%dT%H%M%S')


def format_event(event: dict) -> str:
    """Formate un événement pour l'affichage"""
    title = event.get('title', 'Sans titre')

    # Extraire les dates
    dateandtime = event.get('dateandtime', {})
    start_str = dateandtime.get('start', '')
    end_str = dateandtime.get('end', '')

    if start_str and end_str:
        # Parser les dates (déjà en heure locale America/Toronto)
        start_dt = parse_zoho_datetime(start_str)
        end_dt = parse_zoho_datetime(end_str)

        # Format: HH:MM - HH:MM
        time_range = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"
    else:
        time_range = "Heure non specifiee"

    location = event.get('location', '')
    description = event.get('description', '')

    output = f"- {time_range} - {title}"
    if location:
        output += f"\n  Lieu: {location}"
    if description:
        output += f"\n  Description: {description}"

    return output


def main():
    """Fonction principale"""
    client = ZohoCalendarClient()

    today = datetime.now()
    print(f"=== Agenda du {today.strftime('%A %d %B %Y')} ===\n")

    try:
        result = client.get_events_today()


        # Extraire les événements
        events_data = result.get('content', [])
        if isinstance(events_data, list) and len(events_data) > 0:
            events_json = events_data[0].get('text', '')
            if events_json:
                try:
                    events_obj = json.loads(events_json) if isinstance(events_json, str) else events_json
                    events = events_obj.get('events', [])
                except json.JSONDecodeError:
                    # Peut-être que c'est déjà un dict
                    events = events_json.get('events', []) if isinstance(events_json, dict) else []
            else:
                events = []
        else:
            events = []

        if not events:
            print("Aucun evenement prevu aujourd'hui.\n")
            return 0

        # Trier par heure de début
        sorted_events = sorted(events, key=lambda e: e.get('dateandtime', {}).get('start', ''))

        for event in sorted_events:
            print(format_event(event))
            print()

        print(f"Total: {len(events)} evenement(s)\n")
        return 0

    except Exception as e:
        print(f"[ERREUR] Impossible de récupérer l'agenda: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
