#!/usr/bin/env python3
"""
⚠️ DEPRECATED: Ce script est déprécié depuis le 8 janvier 2026.
Utiliser Google Calendar pour supprimer des événements.
Voir: execution/DEPRECATED_ZOHO_CALENDAR_SCRIPTS.md

Supprime les doublons Zoho-natifs en gardant les événements Google-synced
"""

import os
import sys
import json
import requests
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')


class ZohoCalendarCleaner:
    def __init__(self):
        self.url = os.getenv('MCP_ZOHO_CALENDAR_URL')
        self.key = os.getenv('MCP_ZOHO_CALENDAR_KEY')

    def _call(self, method, params):
        payload = {
            'jsonrpc': '2.0',
            'id': '1',
            'method': method,
            'params': params
        }
        response = requests.post(f'{self.url}?key={self.key}', json=payload, timeout=60)
        return response.json().get('result', {})

    def get_events(self, start_date, end_date):
        """Get events in date range"""
        result = self._call('tools/call', {
            'name': 'ZohoCalendar_getEventsInRange',
            'arguments': {
                'query_params': {
                    'start': start_date,
                    'end': end_date
                }
            }
        })

        content = result.get('content', [])
        if content:
            data = json.loads(content[0].get('text', '{}'))
            return data.get('events', [])
        return []

    def delete_event(self, caluid, uid, etag):
        """Delete an event"""
        result = self._call('tools/call', {
            'name': 'ZohoCalendar_deleteEvent',
            'arguments': {
                'body': {
                    'caluid': caluid,
                    'uid': uid,
                    'etag': int(etag)
                }
            }
        })

        content = result.get('content', [])
        if content:
            text = content[0].get('text', '{}')
            return 'error' not in text.lower() and '<html' not in text.lower()
        return False


def main():
    print('=' * 60)
    print('  SUPPRESSION DES DOUBLONS ZOHO-NATIFS')
    print('  (Garde les evenements Google-synced)')
    print('=' * 60)
    print()

    cleaner = ZohoCalendarCleaner()

    # Get all events for January and February 2026
    print('1. Recuperation des evenements...')
    all_events = []

    # January
    events_jan = cleaner.get_events('20260101', '20260131')
    print(f'   Janvier: {len(events_jan)} evenements')
    all_events.extend(events_jan)

    # February
    events_feb = cleaner.get_events('20260201', '20260228')
    print(f'   Fevrier: {len(events_feb)} evenements')
    all_events.extend(events_feb)

    print(f'   Total: {len(all_events)} evenements')
    print()

    # Group by title + start time
    groups = defaultdict(list)
    for e in all_events:
        title = e.get('title', 'Sans titre')
        start = e.get('dateandtime', {}).get('start', '')
        key = f'{title}|{start}'
        groups[key].append(e)

    # Identify duplicates and categorize
    print('2. Analyse des doublons...')
    duplicates_to_delete = []

    for key, group in groups.items():
        if len(group) > 1:
            # Separate Google-synced vs Zoho-native
            google_events = [e for e in group if '@google.com' in e.get('uid', '')]
            zoho_events = [e for e in group if '@zohocloud.ca' in e.get('uid', '')]

            title = group[0].get('title', '')[:40].encode('ascii', 'replace').decode()
            print(f'   Doublon: {title}')
            print(f'      Google: {len(google_events)}, Zoho: {len(zoho_events)}')

            # If there's at least one Google event, delete all Zoho-native events
            if google_events and zoho_events:
                for e in zoho_events:
                    duplicates_to_delete.append(e)
                print(f'      -> Supprimer {len(zoho_events)} evenement(s) Zoho-natif(s)')
            # If only Zoho events, keep one and delete the rest
            elif len(zoho_events) > 1:
                sorted_zoho = sorted(zoho_events, key=lambda x: int(x.get('etag', 0)))
                for e in sorted_zoho[1:]:
                    duplicates_to_delete.append(e)
                print(f'      -> Supprimer {len(sorted_zoho) - 1} doublon(s) Zoho')

    print()
    print(f'   Total a supprimer: {len(duplicates_to_delete)} evenements')
    print()

    if not duplicates_to_delete:
        print('Aucun doublon Zoho-natif a supprimer.')
        return 0

    # Delete duplicates
    print('3. Suppression des doublons Zoho-natifs...')
    deleted = 0
    errors = 0

    for e in duplicates_to_delete:
        title = e.get('title', '')[:35].encode('ascii', 'replace').decode()
        caluid = e.get('caluid', '')
        uid = e.get('uid', '')
        etag = e.get('etag', '')

        if caluid and uid and etag:
            success = cleaner.delete_event(caluid, uid, etag)
            if success:
                deleted += 1
                print(f'   [DEL] {title}')
            else:
                errors += 1
                print(f'   [ERR] {title}')
        else:
            errors += 1
            print(f'   [SKIP] {title} - donnees manquantes')

    print()
    print('=' * 60)
    print(f'  RESULTAT: {deleted} supprimes, {errors} erreurs')
    print('=' * 60)

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
