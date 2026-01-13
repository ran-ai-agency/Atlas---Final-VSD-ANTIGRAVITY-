#!/usr/bin/env python3
"""
Vérifie les événements du 19 janvier 2026 dans Zoho Calendar
pour confirmer le RDV avec Marie Boudreau.
"""

import os
import sys
import json
import requests
from datetime import datetime
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

        try:
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
        except Exception as e:
            print(f"[ERROR] API Call failed: {e}")
            raise

    def get_events_for_date(self, target_date_str: str) -> dict:
        """Récupère les événements pour une date spécifique (YYYYMMDD)"""
        
        # Format Zoho pour getEventsInRange: YYYYMMDD
        # Pour une journée, start = end
        
        print(f"[INFO] Recherche des événements pour le {target_date_str}...")

        result = self._call("tools/call", {
            "name": "ZohoCalendar_getEventsInRange",
            "arguments": {
                "query_params": {
                    "start": target_date_str,
                    "end": target_date_str
                }
            }
        })

        return result


def parse_zoho_datetime(dt_str: str) -> datetime:
    """Parse une date Zoho format 20260108T120000-0500"""
    try:
        if '-' in dt_str[-5:] or '+' in dt_str[-5:]:
            dt_str = dt_str[:-5]
        dt_str = dt_str.rstrip('Z')
        return datetime.strptime(dt_str, '%Y%m%dT%H%M%S')
    except Exception as e:
        print(f"[WARN] Erreur parsing date {dt_str}: {e}")
        return datetime.now()


def format_event(event: dict) -> str:
    """Formate un événement pour l'affichage"""
    title = event.get('title', 'Sans titre')
    
    dateandtime = event.get('dateandtime', {})
    start_str = dateandtime.get('start', '')
    end_str = dateandtime.get('end', '')
    
    if start_str and end_str:
        start_dt = parse_zoho_datetime(start_str)
        end_dt = parse_zoho_datetime(end_str)
        time_range = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"
    else:
        time_range = "Heure non specifiee"
        
    return f"- {time_range} : {title}"


def main():
    client = ZohoCalendarClient()
    
    # Date cible : 19 Janvier 2026
    target_date = "20260119"
    
    try:
        result = client.get_events_for_date(target_date)
        
        events_data = result.get('content', [])
        events = []
        
        if isinstance(events_data, list) and len(events_data) > 0:
            events_content = events_data[0].get('text', '')
            if isinstance(events_content, str):
                try:
                    events_json = json.loads(events_content)
                    events = events_json.get('events', [])
                except:
                    print(f"[WARN] Impossible de parser le JSON: {events_content[:100]}...")
            elif isinstance(events_content, dict):
                events = events_content.get('events', [])
        
        if not events:
            print(f"Aucun événement trouvé pour le 19 Janvier 2026.")
            return 0
            
        print(f"\n=== Événements du 19 Janvier 2026 ===\n")
        
        found_marie = False
        for event in events:
            print(format_event(event))
            title = event.get('title', '').lower()
            if 'marie' in title or 'elia' in title or 'sans souci' in title:
                found_marie = True
                print("   >>> C'EST LE RDV AVEC MARIE ! <<<")
                
        if found_marie:
            print("\n[SUCCÈS] Le rendez-vous est confirmé présent dans l'agenda.")
        else:
            print("\n[ATTENTION] Aucun événement ne semble correspondre explicitement à Marie/ELIA.")
            
    except Exception as e:
        print(f"[ERREUR] {e}")
        return 1

if __name__ == "__main__":
    main()
