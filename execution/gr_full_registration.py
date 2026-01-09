#!/usr/bin/env python3
"""
GR International - Workflow complet d'inscription aux evenements
1. Inscription au formulaire
2. Verification des emails de confirmation
3. Ajout au calendrier Google
"""

import os
import sys
import json
import time
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Google Calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Playwright pour l'inscription
from playwright.sync_api import sync_playwright

load_dotenv(Path(__file__).parent.parent / '.env')

# Configuration
BASE_DIR = Path(__file__).parent.parent
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Infos utilisateur
USER_INFO = {
    'prenom': os.getenv('GR_PRENOM', ''),
    'nom': os.getenv('GR_NOM', ''),
    'email': os.getenv('GR_EMAIL', ''),
    'telephone': os.getenv('GR_TELEPHONE', ''),
    'compagnie': os.getenv('GR_COMPAGNIE', ''),
    'siteweb': os.getenv('GR_SITEWEB', ''),
    'ville': os.getenv('GR_VILLE', ''),
}

# Compte email pour verification (Sympatico)
SYMPATICO_ACCOUNT_ID = '219196000000029010'


class GRRegistrationWorkflow:
    """Workflow complet d'inscription GR International"""

    def __init__(self):
        self.mail_url = os.getenv('MCP_ZOHO_MAIL_URL', '')
        self.mail_key = os.getenv('MCP_ZOHO_MAIL_KEY', '')
        self.results = []

    # ========================================
    # ETAPE 1: INSCRIPTION
    # ========================================

    def register_to_event(self, event_url: str, event_name: str = "Evenement"):
        """Inscrit l'utilisateur a un evenement"""
        print(f"\n{'='*60}")
        print(f"ETAPE 1: INSCRIPTION - {event_name}")
        print('='*60)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()

            # Auth via token
            member_url = os.getenv('GR_MEMBER_URL', '')
            if member_url:
                print('[AUTH] Connexion via token...')
                page.goto(member_url, wait_until='networkidle', timeout=30000)
                page.wait_for_timeout(2000)

            try:
                page.goto(event_url, wait_until='networkidle', timeout=30000)
                page.wait_for_timeout(2000)

                # Cliquer sur 'Je veux participer'
                btn = None
                buttons = page.query_selector_all('button, a.btn, input[type=button]')
                for b in buttons:
                    text = b.inner_text() or b.get_attribute('value') or ''
                    if 'participer' in text.lower():
                        btn = b
                        break

                if btn:
                    btn.click()
                    page.wait_for_timeout(3000)
                    print('[OK] Formulaire ouvert')

                # Remplir via JavaScript
                page.evaluate(f'''() => {{
                    const inputs = document.querySelectorAll('input[type=text], input[type=email], input[type=tel]');
                    const mapping = {{
                        'prenom': '{USER_INFO["prenom"]}',
                        'nom': '{USER_INFO["nom"]}',
                        'email': '{USER_INFO["email"]}',
                        'courriel': '{USER_INFO["email"]}',
                        'tel': '{USER_INFO["telephone"]}',
                        'phone': '{USER_INFO["telephone"]}',
                        'compagnie': '{USER_INFO["compagnie"]}',
                        'company': '{USER_INFO["compagnie"]}',
                        'site': '{USER_INFO["siteweb"]}',
                        'web': '{USER_INFO["siteweb"]}',
                        'ville': '{USER_INFO["ville"]}',
                        'city': '{USER_INFO["ville"]}'
                    }};

                    inputs.forEach(inp => {{
                        const name = (inp.name || '').toLowerCase();
                        const placeholder = (inp.placeholder || '').toLowerCase();
                        for (const [key, value] of Object.entries(mapping)) {{
                            if ((name.includes(key) || placeholder.includes(key)) && value && !inp.value) {{
                                inp.value = value;
                                inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                break;
                            }}
                        }}
                    }});

                    // Cocher Oui pour membre GR
                    const radios = document.querySelectorAll('input[type=radio]');
                    radios.forEach(r => {{
                        const label = r.nextSibling?.textContent || r.parentElement?.textContent || '';
                        if (label.toLowerCase().includes('oui')) {{
                            r.checked = true;
                            r.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }}
                    }});
                }}''')

                print('[OK] Formulaire rempli')

                # Screenshot
                safe_name = event_name.replace(' ', '_').replace("'", '')[:20]
                page.screenshot(path=str(BASE_DIR / f'.tmp/form_{safe_name}.png'))

                # Soumettre
                submit_btn = None
                buttons = page.query_selector_all('button, input[type=submit]')
                for b in buttons:
                    text = (b.inner_text() or b.get_attribute('value') or '').lower()
                    if 'envoyer' in text or 'submit' in text:
                        submit_btn = b
                        break

                if submit_btn:
                    submit_btn.click()
                    page.wait_for_timeout(4000)
                    print('[OK] Formulaire soumis')
                    result = 'submitted'
                else:
                    print('[WARN] Bouton Envoyer non trouve')
                    result = 'no_submit'

            except Exception as e:
                print(f'[ERROR] {e}')
                result = 'error'

            browser.close()
            return result

    # ========================================
    # ETAPE 2: VERIFICATION EMAIL
    # ========================================

    def _call_mail_mcp(self, method: str, params: dict):
        """Appelle le MCP Zoho Mail"""
        url = f"{self.mail_url}?key={self.mail_key}"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
        return response.json().get("result", {})

    def check_confirmation_email(self, wait_seconds: int = 60):
        """Verifie si les emails de confirmation sont arrives"""
        print(f"\n{'='*60}")
        print("ETAPE 2: VERIFICATION DES EMAILS")
        print('='*60)

        print(f"[WAIT] Attente de {wait_seconds} secondes pour les emails...")
        time.sleep(wait_seconds)

        print("[SEARCH] Recherche des emails GR International...")

        result = self._call_mail_mcp("tools/call", {
            "name": "ZohoMail_listEmails",
            "arguments": {
                "path_variables": {"accountId": SYMPATICO_ACCOUNT_ID},
                "query_params": {"limit": 20, "start": 1}
            }
        })

        content = result.get("content", [])
        if not content:
            print("[WARN] Impossible de recuperer les emails")
            return []

        text = content[0].get("text", "{}")
        try:
            data = json.loads(text)
            emails = data.get("data", [])
        except:
            print("[WARN] Erreur parsing emails")
            return []

        # Filtrer les emails GR recents (moins de 10 minutes)
        now = datetime.now()
        gr_emails = []

        for email in emails:
            sender = (email.get("sender") or email.get("fromAddress") or "").lower()
            subject = (email.get("subject") or "").lower()
            received = email.get("receivedTime", 0)

            if received:
                try:
                    ts = int(received) if isinstance(received, str) else received
                    email_time = datetime.fromtimestamp(ts / 1000)
                    age_minutes = (now - email_time).total_seconds() / 60

                    if age_minutes < 10 and ("gr" in sender or "grinternational" in sender):
                        gr_emails.append({
                            "subject": email.get("subject"),
                            "sender": sender,
                            "time": email_time.strftime("%H:%M"),
                            "age_minutes": round(age_minutes, 1)
                        })
                except:
                    pass

        if gr_emails:
            print(f"[OK] {len(gr_emails)} email(s) de confirmation trouve(s):")
            for e in gr_emails:
                subj = e['subject'][:50] if e['subject'] else 'N/A'
                # Nettoyer pour console Windows
                subj = subj.encode('ascii', 'replace').decode('ascii')
                print(f"     - {subj} (il y a {e['age_minutes']} min)")
        else:
            print("[WARN] Aucun email de confirmation trouve")
            print("       Verifiez le dossier spam ou reessayez dans quelques minutes")

        return gr_emails

    # ========================================
    # ETAPE 3: AJOUT CALENDRIER GOOGLE
    # ========================================

    def get_google_calendar_service(self):
        """Obtient le service Google Calendar"""
        creds = None
        token_file = BASE_DIR / 'token.json'
        creds_file = BASE_DIR / 'credentials.json'

        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_file, 'w') as token:
                token.write(creds.to_json())

        return build('calendar', 'v3', credentials=creds)

    def add_to_google_calendar(self, event_name: str, event_date: str, event_time: str,
                                duration_hours: float = 1.5, location: str = None,
                                description: str = None, is_zoom: bool = False):
        """Ajoute un evenement au calendrier Google"""
        print(f"\n{'='*60}")
        print("ETAPE 3: AJOUT AU CALENDRIER GOOGLE")
        print('='*60)

        try:
            service = self.get_google_calendar_service()
            print("[OK] Connecte a Google Calendar")

            # Parser la date et l'heure
            start_dt = datetime.strptime(f"{event_date} {event_time}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(hours=duration_hours)

            # Construire l'evenement
            event_body = {
                'summary': f"GR - {event_name}",
                'description': description or f"Evenement GR International\n\nInscription confirmee le {datetime.now().strftime('%Y-%m-%d')}",
                'start': {
                    'dateTime': start_dt.strftime('%Y-%m-%dT%H:%M:%S'),
                    'timeZone': 'America/Toronto',
                },
                'end': {
                    'dateTime': end_dt.strftime('%Y-%m-%dT%H:%M:%S'),
                    'timeZone': 'America/Toronto',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 1440},  # 1 jour avant
                        {'method': 'popup', 'minutes': 30 if is_zoom else 60},
                    ],
                },
            }

            if location:
                event_body['location'] = location

            event = service.events().insert(calendarId='primary', body=event_body).execute()
            print(f"[OK] Evenement cree: {event.get('summary')}")
            print(f"     Lien: {event.get('htmlLink')}")

            return event

        except Exception as e:
            print(f"[ERROR] Erreur calendrier: {e}")
            return None

    # ========================================
    # WORKFLOW COMPLET
    # ========================================

    def run_full_workflow(self, events: list):
        """
        Execute le workflow complet pour une liste d'evenements.

        events: liste de dicts avec keys: name, url, date, time, location (opt), is_zoom (opt)
        """
        print("\n" + "=" * 70)
        print("GR INTERNATIONAL - WORKFLOW COMPLET D'INSCRIPTION")
        print("=" * 70)
        print(f"Evenements a inscrire: {len(events)}")

        results = []

        # Etape 1: Inscriptions
        for event in events:
            reg_result = self.register_to_event(event['url'], event['name'])
            results.append({
                'event': event,
                'registration': reg_result
            })

        # Etape 2: Verification emails (une seule fois pour tous)
        confirmed_emails = self.check_confirmation_email(wait_seconds=60)

        # Etape 3: Ajout calendrier pour les inscriptions reussies
        for result in results:
            event = result['event']
            if result['registration'] in ['submitted', 'success']:
                cal_event = self.add_to_google_calendar(
                    event_name=event['name'],
                    event_date=event['date'],
                    event_time=event['time'],
                    location=event.get('location'),
                    is_zoom=event.get('is_zoom', False),
                    description=event.get('description')
                )
                result['calendar'] = 'added' if cal_event else 'failed'
            else:
                result['calendar'] = 'skipped'

        # Resume final
        print("\n" + "=" * 70)
        print("RESUME FINAL")
        print("=" * 70)

        for r in results:
            event_name = r['event']['name'][:40]
            reg_status = '[OK]' if r['registration'] in ['submitted', 'success'] else '[X]'
            cal_status = '[OK]' if r['calendar'] == 'added' else '[X]'
            print(f"{reg_status} Inscription | {cal_status} Calendrier | {event_name}")

        email_status = '[OK]' if confirmed_emails else '[?]'
        print(f"\n{email_status} Emails de confirmation: {len(confirmed_emails)} recu(s)")

        return results


def main():
    parser = argparse.ArgumentParser(description="GR International - Workflow complet d'inscription")
    parser.add_argument("--url", action="append", help="URL de l'evenement (peut etre repete)")
    parser.add_argument("--name", action="append", help="Nom de l'evenement (dans le meme ordre que --url)")
    parser.add_argument("--date", action="append", help="Date de l'evenement YYYY-MM-DD")
    parser.add_argument("--time", action="append", help="Heure de l'evenement HH:MM")
    parser.add_argument("--location", action="append", help="Lieu (optionnel)")
    parser.add_argument("--zoom", action="store_true", help="Evenement Zoom")

    args = parser.parse_args()

    if not args.url:
        print("Usage: python gr_full_registration.py --url URL --name NOM --date YYYY-MM-DD --time HH:MM")
        print("\nExemple:")
        print('  python gr_full_registration.py \\')
        print('    --url "https://www.grinternational.ca/evenements/..." \\')
        print('    --name "100% Web 1 Elite" \\')
        print('    --date "2026-01-21" \\')
        print('    --time "08:00" \\')
        print('    --zoom')
        return 1

    # Construire la liste des evenements
    events = []
    for i, url in enumerate(args.url):
        event = {
            'url': url,
            'name': args.name[i] if args.name and len(args.name) > i else f"Evenement {i+1}",
            'date': args.date[i] if args.date and len(args.date) > i else datetime.now().strftime('%Y-%m-%d'),
            'time': args.time[i] if args.time and len(args.time) > i else '09:00',
            'location': args.location[i] if args.location and len(args.location) > i else None,
            'is_zoom': args.zoom
        }
        events.append(event)

    workflow = GRRegistrationWorkflow()
    workflow.run_full_workflow(events)

    return 0


if __name__ == "__main__":
    sys.exit(main())
