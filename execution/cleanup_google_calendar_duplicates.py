#!/usr/bin/env python3
"""
Nettoyage des doublons dans Google Calendar
"""

import os
import sys
from pathlib import Path
from collections import defaultdict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

SCOPES = ['https://www.googleapis.com/auth/calendar']
BASE_DIR = Path(__file__).parent.parent
TOKEN_FILE = BASE_DIR / 'token.json'


def main():
    # Authenticate
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build('calendar', 'v3', credentials=creds)

    print('=' * 60)
    print('  NETTOYAGE DES DOUBLONS GOOGLE CALENDAR')
    print('=' * 60)
    print()

    # Get all events
    print('1. Recuperation des evenements...')
    events_result = service.events().list(
        calendarId='primary',
        timeMin='2026-01-01T00:00:00Z',
        timeMax='2026-03-01T00:00:00Z',
        maxResults=500,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    print(f'   {len(events)} evenements trouves')
    print()

    # Group by title + start time
    groups = defaultdict(list)
    for e in events:
        title = e.get('summary', 'Sans titre')
        start = e.get('start', {}).get('dateTime', e.get('start', {}).get('date', ''))
        key = f'{title}|{start}'
        groups[key].append(e)

    # Delete duplicates
    print('2. Suppression des doublons...')
    deleted = 0
    errors = 0

    for key, group in groups.items():
        if len(group) > 1:
            # Keep the one with zoho_uid if exists, else the first one
            has_zoho = [e for e in group if e.get('extendedProperties', {}).get('private', {}).get('zoho_uid')]
            if has_zoho:
                keep = has_zoho[0]
            else:
                keep = group[0]

            keep_id = keep['id']

            # Delete the rest
            for e in group:
                if e['id'] != keep_id:
                    try:
                        service.events().delete(calendarId='primary', eventId=e['id']).execute()
                        deleted += 1
                        title = e.get('summary', '')[:35].encode('ascii', 'replace').decode()
                        print(f'   [DEL] {title}')
                    except Exception as ex:
                        errors += 1
                        print(f'   [ERR] {str(ex)[:50]}')

    print()
    print('=' * 60)
    print(f'  RESULTAT: {deleted} supprimes, {errors} erreurs')
    print('=' * 60)

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
