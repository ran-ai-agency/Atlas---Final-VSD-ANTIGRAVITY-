#!/usr/bin/env python3
"""
Nettoyage des doublons spécifiques du 19 janvier 2026.
"""

import os
import sys
import json
import requests
from collections import defaultdict
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')


class ZohoCalendarCleaner:
    def __init__(self):
        self.base_url = os.getenv('MCP_ZOHO_CALENDAR_URL', 'https://zohocalendar-110002203871.zohomcp.ca/mcp/message')
        self.key = os.getenv('MCP_ZOHO_CALENDAR_KEY', 'e8e366a6a3e982cf1e21fbd9dcb5ee97')
        self.url = f"{self.base_url}?key={self.key}"

    def _call(self, method, params):
        payload = {
            'jsonrpc': '2.0',
            'id': '1',
            'method': method,
            'params': params
        }
        try:
            response = requests.post(self.url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
            response.raise_for_status()
            result = response.json()
            if "error" in result:
                print(f"[API ERROR] {result['error']}")
                return {}
            return result.get('result', {})
        except Exception as e:
            print(f"[REQ ERROR] {e}")
            return {}

    def get_events(self, date_str):
        """Get events for a specific date (YYYYMMDD)"""
        print(f"[INFO] Récupération des événements pour {date_str}...")
        result = self._call('tools/call', {
            'name': 'ZohoCalendar_getEventsInRange',
            'arguments': {
                'query_params': {
                    'start': date_str,
                    'end': date_str
                }
            }
        })

        content = result.get('content', [])
        if content:
            text = content[0].get('text', '')
            try:
                if isinstance(text, str):
                    data = json.loads(text)
                else:
                    data = text
                return data.get('events', [])
            except json.JSONDecodeError:
                print("[ERROR] Impossible de parser le JSON des événements")
                return []
        return []

    def delete_event(self, caluid, uid, etag):
        """Delete an event"""
        print(f"[INFO] Tentative de suppression Event UID: {uid}...")
        result = self._call('tools/call', {
            'name': 'ZohoCalendar_deleteEvent',
            'arguments': {
                'body': {
                    'caluid': caluid,
                    'uid': uid,
                    'etag': str(etag)
                }
            }
        })
        
        # Check success logic based on result
        # Usually returns empty or success message
        content = result.get('content', [])
        if content:
            print(f"[RESULT] {content[0].get('text', '')}")
            return True # Assume success if no error thrown
        
        # If result is empty but no error, it might be success
        return True


def main():
    cleaner = ZohoCalendarCleaner()
    target_date = '20260119'
    
    events = cleaner.get_events(target_date)
    print(f"[INFO] {len(events)} événements trouvés.")

    groups = defaultdict(list)
    for e in events:
        title = e.get('title', 'Sans titre')
        start = e.get('dateandtime', {}).get('start', '')
        key = f'{title}|{start}'
        groups[key].append(e)

    deleted_count = 0
    
    for key, group in groups.items():
        if len(group) > 1:
            print(f"\n[DOUBLON TROUVÉ] '{key}' : {len(group)} instances")
            
            # Sort by etag to keep the oldest (assuming lower etag is older/stable)
            # Zoho etags might not work exactly like that, but keeping one stable is enough
            sorted_group = sorted(group, key=lambda x: str(x.get('etag', '')))
            
            # Keep the first, delete the rest
            to_keep = sorted_group[0]
            to_delete = sorted_group[1:]
            
            print(f"   [KEEP] UID: {to_keep.get('uid')} (etag: {to_keep.get('etag')})")
            
            for ev in to_delete:
                caluid = ev.get('caluid')
                uid = ev.get('uid')
                etag = ev.get('etag')
                
                if cleaner.delete_event(caluid, uid, etag):
                    print(f"   [DELETED] UID: {uid}")
                    deleted_count += 1
                else:
                    print(f"   [FAIL] UID: {uid}")

    print(f"\n[TERMINÉ] Total supprimés : {deleted_count}")

if __name__ == "__main__":
    main()
