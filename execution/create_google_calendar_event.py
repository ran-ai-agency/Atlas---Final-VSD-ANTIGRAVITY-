#!/usr/bin/env python3
"""
Créer un événement dans Google Calendar
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv(Path(__file__).parent.parent / '.env')

SCOPES = ['https://www.googleapis.com/auth/calendar']
BASE_DIR = Path(__file__).parent.parent
CREDENTIALS_FILE = BASE_DIR / 'credentials.json'
TOKEN_FILE = BASE_DIR / 'token.json'


def get_google_calendar_service():
    """Authentification et création du service Google Calendar"""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(f"credentials.json non trouvé: {CREDENTIALS_FILE}")
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def create_event(title: str, start_datetime: str, end_datetime: str,
                 description: str = None, location: str = None,
                 timezone: str = 'America/Toronto', calendar_id: str = 'primary'):
    """
    Crée un événement dans Google Calendar

    Args:
        title: Titre de l'événement
        start_datetime: Date/heure de début (format ISO: 2026-01-11T08:00:00)
        end_datetime: Date/heure de fin (format ISO: 2026-01-11T12:00:00)
        description: Description optionnelle
        location: Lieu optionnel
        timezone: Fuseau horaire (défaut: America/Toronto)
        calendar_id: ID du calendrier (défaut: primary)

    Returns:
        dict: Événement créé
    """
    service = get_google_calendar_service()

    event_body = {
        'summary': title,
        'start': {
            'dateTime': start_datetime,
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': timezone,
        },
    }

    if description:
        event_body['description'] = description

    if location:
        event_body['location'] = location

    event = service.events().insert(calendarId=calendar_id, body=event_body).execute()

    print(f"[OK] Evenement cree: {event.get('summary')}")
    print(f"  ID: {event.get('id')}")
    print(f"  Lien: {event.get('htmlLink')}")

    return event


def main():
    parser = argparse.ArgumentParser(description='Créer un événement Google Calendar')
    parser.add_argument('--title', required=True, help='Titre de l\'événement')
    parser.add_argument('--start', required=True, help='Date/heure début (YYYY-MM-DDTHH:MM:SS)')
    parser.add_argument('--end', required=True, help='Date/heure fin (YYYY-MM-DDTHH:MM:SS)')
    parser.add_argument('--description', help='Description')
    parser.add_argument('--location', help='Lieu')
    parser.add_argument('--timezone', default='America/Toronto', help='Fuseau horaire')
    parser.add_argument('--calendar-id', default='primary', help='ID du calendrier')

    args = parser.parse_args()

    try:
        create_event(
            title=args.title,
            start_datetime=args.start,
            end_datetime=args.end,
            description=args.description,
            location=args.location,
            timezone=args.timezone,
            calendar_id=args.calendar_id
        )
        return 0
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
