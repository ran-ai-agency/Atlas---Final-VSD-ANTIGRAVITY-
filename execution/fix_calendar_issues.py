#!/usr/bin/env python3
"""
⚠️ DEPRECATED: Ce script est déprécié depuis le 8 janvier 2026.
Utiliser Google Calendar pour mettre à jour/supprimer des événements.
Voir: execution/DEPRECATED_ZOHO_CALENDAR_SCRIPTS.md

Corrige les problemes du calendrier:
1. Met a jour GR International (8h30-10h00 au lieu de 10h30)
2. Supprime les doublons
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

    def get_events_today(self):
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

    def delete_event(self, calendar_uid: str, event_uid: str, etag: int):
        """Supprime un evenement"""
        result = self._call("tools/call", {
            "name": "ZohoCalendar_deleteEvent",
            "arguments": {
                "body": {
                    "caluid": calendar_uid,
                    "uid": event_uid,
                    "etag": etag
                }
            }
        })
        return result

    def update_event(self, calendar_uid: str, event_uid: str, title: str, start: datetime, end: datetime, etag: int, description: str = ""):
        """Met a jour un evenement"""
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
    """Parse une date Zoho"""
    if '-' in dt_str or '+' in dt_str[-5:]:
        dt_str = dt_str[:-5]
    dt_str = dt_str.rstrip('Z')
    return datetime.strptime(dt_str, '%Y%m%dT%H%M%S')


def main():
    """Fonction principale"""
    try:
        client = ZohoCalendarClient()

        print("=" * 80)
        print("NETTOYAGE DU CALENDRIER")
        print("=" * 80)
        print()

        # Recuperer tous les evenements
        events = client.get_events_today()
        print(f"Total evenements aujourd'hui: {len(events)}\n")

        # Grouper par titre pour trouver les doublons
        events_by_title = {}
        for event in events:
            title = event.get('title', '').strip()
            if title not in events_by_title:
                events_by_title[title] = []
            events_by_title[title].append(event)

        # 1. Traiter les doublons
        print("Etape 1: Suppression des doublons")
        print("-" * 80)

        deleted_count = 0
        for title, event_list in events_by_title.items():
            if len(event_list) > 1:
                print(f"\n[DOUBLON] '{title}' ({len(event_list)} occurrences)")

                # Garder le premier, supprimer les autres
                for i, event in enumerate(event_list[1:], 1):
                    try:
                        calendar_uid = event.get('caluid')
                        event_uid = event.get('uid')
                        etag = int(event.get('etag', 0))

                        print(f"  Suppression occurrence #{i+1}...")

                        client.delete_event(calendar_uid, event_uid, etag)
                        deleted_count += 1
                        print(f"  [OK] Supprime")

                    except Exception as e:
                        print(f"  [ERREUR] {e}")

        print(f"\n[RESUME] {deleted_count} doublon(s) supprime(s)\n")

        # 2. Corriger GR International
        print("Etape 2: Correction GR International")
        print("-" * 80)

        gr_events = [e for e in events if 'gr international' in e.get('title', '').lower()]

        if gr_events:
            gr_event = gr_events[0]
            print(f"\n[TROUVE] {gr_event.get('title')}")

            dateandtime = gr_event.get('dateandtime', {})
            start_dt = parse_zoho_datetime(dateandtime.get('start', ''))
            end_dt = parse_zoho_datetime(dateandtime.get('end', ''))

            print(f"  Heure actuelle: {start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}")

            # Verifier si correction necessaire
            if end_dt.hour == 10 and end_dt.minute == 30:
                new_end_dt = start_dt.replace(hour=10, minute=0)
                print(f"  Nouvelle heure: {start_dt.strftime('%H:%M')} - {new_end_dt.strftime('%H:%M')}")

                try:
                    client.update_event(
                        calendar_uid=gr_event.get('caluid'),
                        event_uid=gr_event.get('uid'),
                        title=gr_event.get('title'),
                        start=start_dt,
                        end=new_end_dt,
                        etag=int(gr_event.get('etag')),
                        description=gr_event.get('description', '')
                    )
                    print(f"  [OK] Mis a jour\n")
                except Exception as e:
                    print(f"  [ERREUR] {e}\n")
            else:
                print(f"  [INFO] Deja a la bonne heure\n")
        else:
            print("[INFO] Evenement GR International non trouve aujourd'hui\n")

        print("=" * 80)
        print("NETTOYAGE TERMINE")
        print("=" * 80)
        print()
        print("NOTE: Pour modifier TOUTES les recurrences futures de GR International:")
        print("1. Ouvrir calendar.zoho.com")
        print("2. Ouvrir l'evenement GR International")
        print("3. Choisir 'Modifier la serie complete'")
        print("4. Changer l'heure de fin a 10h00")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
