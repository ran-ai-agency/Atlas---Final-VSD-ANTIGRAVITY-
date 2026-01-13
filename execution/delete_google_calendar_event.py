#!/usr/bin/env python3
"""
Supprimer un événement dans Google Calendar
Usage: python delete_google_calendar_event.py --event-id <ID>
Ou:    python delete_google_calendar_event.py --search "Titre" --date "YYYY-MM-DD"
"""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime

load_dotenv(Path(__file__).parent.parent / '.env')

SCOPES = ['https://www.googleapis.com/auth/calendar']
BASE_DIR = Path(__file__).parent.parent
CREDENTIALS_FILE = BASE_DIR / 'credentials.json'
TOKEN_FILE = BASE_DIR / 'token.json'

def get_service():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def main():
    parser = argparse.ArgumentParser(description='Supprimer un événement Google Calendar')
    parser.add_argument('--event-id', help='ID de l\'événement à supprimer')
    parser.add_argument('--search', help='Titre ou partie du titre à chercher')
    parser.add_argument('--date', help='Date de l\'événement (YYYY-MM-DD) pour la recherche', default=datetime.date.today().isoformat())
    parser.add_argument('--calendar-id', default='primary', help='ID du calendrier')
    
    args = parser.parse_args()
    service = get_service()

    if args.event_id:
        try:
            service.events().delete(calendarId=args.calendar_id, eventId=args.event_id).execute()
            print(f"[OK] Événement {args.event_id} supprimé.")
        except Exception as e:
            print(f"[ERREUR] Impossible de supprimer l'événement {args.event_id}: {e}")
            return 1
    elif args.search:
        # Recherche par date et titre
        try:
            # Définir la plage de recherche (la journée donnée)
            start_date = datetime.datetime.strptime(args.date, "%Y-%m-%d")
            end_date = start_date + datetime.timedelta(days=1)
            time_min = start_date.astimezone().isoformat()
            time_max = end_date.astimezone().isoformat()
            
            print(f"Recherche de '{args.search}' le {args.date}...")
            events_result = service.events().list(
                calendarId=args.calendar_id, 
                timeMin=time_min, 
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            
            found = False
            for event in events:
                if args.search.lower() in event.get('summary', '').lower():
                    print(f"Trouvé: {event['summary']} ({event['start'].get('dateTime', event['start'].get('date'))}) - ID: {event['id']}")
                    service.events().delete(calendarId=args.calendar_id, eventId=event['id']).execute()
                    print(f"[OK] Événement supprimé.")
                    found = True
            
            if not found:
                print(f"[INFO] Aucun événement trouvé correspondant à '{args.search}' le {args.date}.")
                
        except Exception as e:
            print(f"[ERREUR] Erreur lors de la recherche/suppression: {e}")
            return 1
    else:
        print("Erreur: Vous devez spécifier --event-id ou --search")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
