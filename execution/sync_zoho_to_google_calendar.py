#!/usr/bin/env python3
"""
Synchronisation Zoho Calendar -> Google Calendar
Copie les evenements de Zoho Calendar vers Google Calendar
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv(Path(__file__).parent.parent / '.env')

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Paths
BASE_DIR = Path(__file__).parent.parent
CREDENTIALS_FILE = BASE_DIR / 'credentials.json'
TOKEN_FILE = BASE_DIR / 'token.json'


class ZohoCalendarClient:
    """Client pour Zoho Calendar via MCP"""

    def __init__(self):
        # Hardcoded values as fallback since MCP config may differ
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

    def get_events(self, start_date: str, end_date: str) -> list:
        """Recupere les evenements dans une plage de dates"""
        print(f"   DEBUG: Fetching events from {start_date} to {end_date}")
        print(f"   DEBUG: URL = {self.url[:50]}...")

        result = self._call("tools/call", {
            "name": "ZohoCalendar_getEventsInRange",
            "arguments": {
                "query_params": {
                    "start": start_date,
                    "end": end_date
                }
            }
        })

        print(f"   DEBUG: Result keys = {result.keys() if result else 'None'}")

        content = result.get("content", [])
        if content:
            text = content[0].get("text", "{}")
            data = json.loads(text)
            events = data.get("events", [])
            print(f"   DEBUG: Found {len(events)} events in response")
            return events
        else:
            print(f"   DEBUG: No content in result")
        return []


class GoogleCalendarClient:
    """Client pour Google Calendar API"""

    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authentification OAuth2 Google"""
        if TOKEN_FILE.exists():
            self.creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not CREDENTIALS_FILE.exists():
                    raise FileNotFoundError(f"Fichier credentials.json non trouve: {CREDENTIALS_FILE}")

                flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Sauvegarder le token
            with open(TOKEN_FILE, 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('calendar', 'v3', credentials=self.creds)

    def get_calendar_id(self, calendar_name: str = None) -> str:
        """Obtient l'ID du calendrier (primary par defaut)"""
        if not calendar_name:
            return 'primary'

        calendars = self.service.calendarList().list().execute()
        for cal in calendars.get('items', []):
            if calendar_name.lower() in cal.get('summary', '').lower():
                return cal['id']

        return 'primary'

    def event_exists(self, calendar_id: str, zoho_uid: str) -> tuple:
        """Verifie si un evenement existe deja (par extended properties)"""
        try:
            events = self.service.events().list(
                calendarId=calendar_id,
                privateExtendedProperty=f"zoho_uid={zoho_uid}",
                maxResults=1
            ).execute()

            items = events.get('items', [])
            if items:
                return True, items[0]['id']
        except HttpError:
            pass

        return False, None

    def create_event(self, calendar_id: str, event_data: dict) -> dict:
        """Cree un evenement dans Google Calendar"""
        return self.service.events().insert(
            calendarId=calendar_id,
            body=event_data
        ).execute()

    def update_event(self, calendar_id: str, event_id: str, event_data: dict) -> dict:
        """Met a jour un evenement"""
        return self.service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event_data
        ).execute()

    def delete_event(self, calendar_id: str, event_id: str):
        """Supprime un evenement"""
        self.service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()


def convert_zoho_to_google(zoho_event: dict) -> dict:
    """Convertit un evenement Zoho en format Google Calendar"""

    title = zoho_event.get('title', 'Sans titre')
    description = zoho_event.get('description', '')
    zoho_uid = zoho_event.get('uid', '')

    # Parser les dates Zoho (format: 20260106T120000-0500)
    date_info = zoho_event.get('dateandtime', {})
    start_str = date_info.get('start', '')
    end_str = date_info.get('end', '')
    timezone = date_info.get('timezone', 'America/Toronto')

    is_all_day = zoho_event.get('isallday', False)

    def parse_zoho_datetime(dt_str: str) -> str:
        """Parse Zoho datetime to ISO format"""
        # Format: 20260106T120000-0500 or 20260106T120000
        if not dt_str:
            return None

        # Remove timezone suffix if present
        if '-' in dt_str[8:] or '+' in dt_str[8:]:
            dt_str = dt_str[:15]

        try:
            dt = datetime.strptime(dt_str, '%Y%m%dT%H%M%S')
            return dt.isoformat()
        except:
            return None

    google_event = {
        'summary': title,
        'description': description,
        'extendedProperties': {
            'private': {
                'zoho_uid': zoho_uid,
                'synced_from': 'zoho_calendar'
            }
        }
    }

    if is_all_day:
        # All-day event
        start_date = start_str[:8] if start_str else None
        end_date = end_str[:8] if end_str else None

        if start_date:
            google_event['start'] = {
                'date': f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
            }
        if end_date:
            google_event['end'] = {
                'date': f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
            }
    else:
        # Timed event
        start_iso = parse_zoho_datetime(start_str)
        end_iso = parse_zoho_datetime(end_str)

        if start_iso:
            google_event['start'] = {
                'dateTime': start_iso,
                'timeZone': timezone
            }
        if end_iso:
            google_event['end'] = {
                'dateTime': end_iso,
                'timeZone': timezone
            }

    return google_event


def sync_calendars(days_ahead: int = 60, days_behind: int = 7):
    """Synchronise les evenements de Zoho vers Google"""

    print("=" * 60)
    print("  SYNCHRONISATION ZOHO CALENDAR -> GOOGLE CALENDAR")
    print("=" * 60)
    print()

    # Initialiser les clients
    print("1. Connexion a Zoho Calendar...")
    zoho = ZohoCalendarClient()
    print("   OK")

    print("2. Connexion a Google Calendar...")
    google = GoogleCalendarClient()
    print("   OK")
    print()

    # Definir la plage de dates - sync par tranches de 30 jours max
    today = datetime.now()

    # Collecter tous les evenements par tranches
    all_zoho_events = []

    # Tranche 1: Ce mois-ci
    start_date = today.strftime('%Y%m01')  # Premier du mois
    end_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    end_date = end_of_month.strftime('%Y%m%d')

    print(f"3. Recuperation des evenements Zoho...")
    print(f"   Tranche 1: {start_date} -> {end_date}")
    events1 = zoho.get_events(start_date, end_date)
    print(f"   -> {len(events1)} evenements")
    all_zoho_events.extend(events1)

    # Tranche 2: Mois prochain
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    start_date2 = next_month.strftime('%Y%m%d')
    end_of_next = (next_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    end_date2 = end_of_next.strftime('%Y%m%d')

    print(f"   Tranche 2: {start_date2} -> {end_date2}")
    events2 = zoho.get_events(start_date2, end_date2)
    print(f"   -> {len(events2)} evenements")
    all_zoho_events.extend(events2)

    # Tranche 3: Mois suivant (si days_ahead > 60)
    if days_ahead > 60:
        month_after = (next_month.replace(day=28) + timedelta(days=4)).replace(day=1)
        start_date3 = month_after.strftime('%Y%m%d')
        end_of_third = (month_after.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        end_date3 = end_of_third.strftime('%Y%m%d')

        print(f"   Tranche 3: {start_date3} -> {end_date3}")
        events3 = zoho.get_events(start_date3, end_date3)
        print(f"   -> {len(events3)} evenements")
        all_zoho_events.extend(events3)

    # Dedupliquer par uid
    seen_uids = set()
    zoho_events = []
    for e in all_zoho_events:
        uid = e.get('uid', '')
        if uid and uid not in seen_uids:
            seen_uids.add(uid)
            zoho_events.append(e)

    print(f"   Total: {len(zoho_events)} evenements uniques")
    print()

    # Synchroniser chaque evenement
    calendar_id = google.get_calendar_id()

    created = 0
    updated = 0
    skipped = 0
    errors = 0

    print("4. Synchronisation des evenements...")
    for event in zoho_events:
        title = event.get('title', 'Sans titre')[:40]
        zoho_uid = event.get('uid', '')

        try:
            # Verifier si l'evenement existe deja
            exists, google_event_id = google.event_exists(calendar_id, zoho_uid)

            # Convertir en format Google
            google_event = convert_zoho_to_google(event)

            if exists:
                # Mettre a jour
                google.update_event(calendar_id, google_event_id, google_event)
                updated += 1
                print(f"   [MAJ] {title.encode('ascii', 'replace').decode()}...")
            else:
                # Creer
                google.create_event(calendar_id, google_event)
                created += 1
                print(f"   [NEW] {title.encode('ascii', 'replace').decode()}...")

        except Exception as e:
            errors += 1
            print(f"   [ERR] {title.encode('ascii', 'replace').decode()}: {e}")

    print()
    print("=" * 60)
    print(f"  RESULTAT: {created} crees, {updated} maj, {errors} erreurs")
    print("=" * 60)

    return {
        'created': created,
        'updated': updated,
        'skipped': skipped,
        'errors': errors
    }


def main():
    """Fonction principale"""
    import argparse

    parser = argparse.ArgumentParser(description='Sync Zoho Calendar to Google Calendar')
    parser.add_argument('--days-ahead', type=int, default=60, help='Days ahead to sync')
    parser.add_argument('--days-behind', type=int, default=7, help='Days behind to sync')
    args = parser.parse_args()

    try:
        result = sync_calendars(
            days_ahead=args.days_ahead,
            days_behind=args.days_behind
        )
        return 0 if result['errors'] == 0 else 1

    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
