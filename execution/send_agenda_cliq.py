#!/usr/bin/env python3
"""
Envoie l'agenda du 16 janvier 2026 sur Zoho Cliq
"""

import os
import json
import requests
from list_zoho_calendar_today import ZohoCalendarClient
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / '.env')

ZOHO_CLIQ_MCP_URL = os.getenv("MCP_ZOHO_CLIQ_URL", "")
ZOHO_CLIQ_MCP_KEY = os.getenv("MCP_ZOHO_CLIQ_KEY", "")

def post_to_cliq(message: str, channel: str = "atlas"):
    """Poste un message dans un canal Cliq."""
    url = f"{ZOHO_CLIQ_MCP_URL}?key={ZOHO_CLIQ_MCP_KEY}"
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "ZohoCliq_Post_message_in_a_channel",
            "arguments": {
                "body": {"text": message},
                "path_variables": {"CHANNEL_UNIQUE_NAME": channel}
            }
        },
        "id": 1
    }
    response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
    return response.json()

def parse_time(dt_str):
    """Parse 20260116T140000-0500 -> 14:00"""
    if 'T' in dt_str:
        time_part = dt_str.split('T')[1][:6]
        return f"{time_part[:2]}:{time_part[2:4]}"
    return "?"

def main():
    # Récupérer les événements du 16 janvier
    c = ZohoCalendarClient()
    r = c._call('tools/call', {
        'name': 'ZohoCalendar_getEventsInRange',
        'arguments': {'query_params': {'start': '20260116', 'end': '20260116'}}
    })
    data = json.loads(r.get('content', [{}])[0].get('text', '{}'))
    events = data.get('events', [])
    
    # Dédupliquer et trier par heure
    seen = set()
    unique_events = []
    for e in events:
        key = (e.get('title'), e.get('dateandtime', {}).get('start'))
        if key not in seen:
            seen.add(key)
            unique_events.append(e)
    
    unique_events.sort(key=lambda e: e.get('dateandtime', {}).get('start', ''))
    
    # Construire le message
    lines = ["📅 **Agenda - Vendredi 16 janvier 2026**", ""]
    
    for e in unique_events:
        title = e.get('title', 'Sans titre')
        start = parse_time(e.get('dateandtime', {}).get('start', ''))
        end = parse_time(e.get('dateandtime', {}).get('end', ''))
        
        # Mettre en évidence la réunion avec Sébastien
        if 'Sebastien' in title or 'Vachon' in title:
            lines.append(f"⭐ **{start} - {end}** : {title}")
        else:
            lines.append(f"• {start} - {end} : {title}")
    
    lines.append("")
    lines.append("_Envoyé par Atlas_")
    
    message = "\n".join(lines)
    print("Message à envoyer:")
    print("-" * 40)
    print(message)
    print("-" * 40)
    
    # Envoyer sur Cliq
    result = post_to_cliq(message, "veilleia")
    print(f"\nRésultat: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    main()
