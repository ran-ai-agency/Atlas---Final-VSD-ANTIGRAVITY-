#!/usr/bin/env python3
"""
⚠️ DEPRECATED: Ce script est déprécié depuis le 8 janvier 2026.
Utiliser Google Calendar pour mettre à jour des événements.
Voir: execution/DEPRECATED_ZOHO_CALENDAR_SCRIPTS.md

Met a jour un evenement recurrent dans Zoho Calendar
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

    def _call(self, method: str, params: dict):
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

    def get_events_today(self, calendar_uid: str = "033c7928ba314969a0a0a6b5119ac590"):
        """Recupere les evenements d'aujourd'hui"""
        today = datetime.now()
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

        content = result.get('content', [])
        if content and isinstance(content, list):
            text = content[0].get('text', '')
            if text:
                events_obj = json.loads(text) if isinstance(text, str) else text
                return events_obj.get('events', [])
        return []

    def update_event(self, calendar_uid: str, event_uid: str, title: str, start: datetime, end: datetime, etag: int, description: str = ""):
        """Met a jour un evenement"""

        # Convertir en UTC (America/Toronto = UTC-5)
        start_utc = start + timedelta(hours=5)
        end_utc = end + timedelta(hours=5)

        start_str = start_utc.strftime('%Y%m%dT%H%M%S') + 'Z'
        end_str = end_utc.strftime('%Y%m%dT%H%M%S') + 'Z'

        result = self._call("tools/call", {
            "name": "ZohoCalendar_updateEvent",
            "arguments": {
                "body": {
                    "caluid": calendar_uid,
                    "uid": event_uid,
                    "title": title,
                    "dateandtime": {
                        "start": start_str,
                        "end": end_str,
                        "timezone": "America/Toronto"
                    },
                    "description": description,
                    "isallday": False,
                    "etag": etag
                }
            }
        })

        return result


def parse_zoho_datetime(dt_str: str) -> datetime:
    """Parse une date Zoho format 20260108T120000-0500"""
    if '-' in dt_str or '+' in dt_str[-5:]:
        dt_str = dt_str[:-5]
    dt_str = dt_str.rstrip('Z')
    return datetime.strptime(dt_str, '%Y%m%dT%H%M%S')


def main():
    """Fonction principale"""
    try:
        client = ZohoCalendarClient()

        print("=" * 70)
        print("CORRECTION GR INTERNATIONAL - RESEAUTAGE")
        print("=" * 70)
        print()

        # 1. Recuperer les evenements d'aujourd'hui
        print("Etape 1: Recherche de l'evenement GR International...")
        events = client.get_events_today()

        # Trouver l'evenement GR International
        gr_event = None
        for event in events:
            title = event.get('title', '').lower()
            if 'gr international' in title and 'reseautage' in title:
                gr_event = event
                break

        if not gr_event:
            print("[ERREUR] Evenement GR International non trouve")
            return 1

        print(f"[OK] Evenement trouve: {gr_event.get('title')}")

        # Afficher les details actuels
        dateandtime = gr_event.get('dateandtime', {})
        start_str = dateandtime.get('start', '')
        end_str = dateandtime.get('end', '')

        start_dt = parse_zoho_datetime(start_str)
        end_dt = parse_zoho_datetime(end_str)

        print(f"  Heure actuelle: {start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}")
        print()

        # 2. Calculer la nouvelle heure de fin (10h00 au lieu de 10h30)
        new_end_dt = start_dt.replace(hour=10, minute=0)

        print(f"Etape 2: Mise a jour de l'heure de fin...")
        print(f"  Nouvelle heure: {start_dt.strftime('%H:%M')} - {new_end_dt.strftime('%H:%M')}")
        print()

        # 3. Mettre a jour l'evenement
        calendar_uid = gr_event.get('caluid', '033c7928ba314969a0a0a6b5119ac590')
        event_uid = gr_event.get('uid')
        title = gr_event.get('title')
        description = gr_event.get('description', '')
        etag = gr_event.get('etag')

        if not event_uid or not etag:
            print("[ERREUR] Impossible de recuperer l'UID ou l'etag de l'evenement")
            return 1

        result = client.update_event(
            calendar_uid=calendar_uid,
            event_uid=event_uid,
            title=title,
            start=start_dt,
            end=new_end_dt,
            etag=int(etag),
            description=description
        )

        print("[OK] Evenement mis a jour!")
        print()
        print("=" * 70)
        print("IMPORTANT:")
        print("=" * 70)
        print("Cette mise a jour affecte UNIQUEMENT l'occurrence d'aujourd'hui.")
        print("Pour modifier TOUTES les recurrences futures, vous devez:")
        print("1. Ouvrir Zoho Calendar Web (calendar.zoho.com)")
        print("2. Ouvrir l'evenement GR International")
        print("3. Choisir 'Modifier tous les evenements' ou 'Modifier la serie'")
        print("4. Changer l'heure de fin a 10h00")
        print("5. Enregistrer")
        print()
        print("L'API Zoho Calendar MCP ne permet pas de modifier directement")
        print("toute une serie d'evenements recurrents.")
        print("=" * 70)

        return 0

    except Exception as e:
        print(f"[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
