from list_zoho_calendar_today import ZohoCalendarClient
import json

c = ZohoCalendarClient()
r = c._call('tools/call', {'name': 'ZohoCalendar_getEventsInRange', 'arguments': {'query_params': {'start': '20260116', 'end': '20260116'}}})
data = json.loads(r.get('content', [{}])[0].get('text', '{}'))
events = data.get('events', [])
print(f'Nombre: {len(events)}')
for e in events:
    print(f"- {e.get('title')}: {e.get('dateandtime', {}).get('start')} -> {e.get('dateandtime', {}).get('end')}")
