#!/usr/bin/env python3
"""
Scanner d'événements dans les emails via Zoho Mail MCP
Extrait webinars, conférences, formations, etc.
"""

import os
import sys
import json
import re
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from html import unescape
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Event:
    """Structure d'un événement détecté"""
    title: str
    event_type: str  # webinar, conference, workshop, meetup, demo, etc.
    date: Optional[str]
    time: Optional[str]
    organizer: str
    sender_email: str
    email_subject: str
    email_date: str
    registration_url: Optional[str]
    description: str
    relevance_score: int  # 1-10
    message_id: str


class ZohoMailMCPClient:
    """Client pour Zoho Mail via MCP"""

    def __init__(self):
        self.mail_url = os.getenv("MCP_ZOHO_MAIL_URL", "")
        self.mail_key = os.getenv("MCP_ZOHO_MAIL_KEY", "")

        if not self.mail_url or not self.mail_key:
            raise ValueError("Zoho Mail MCP non configuré. Vérifiez MCP_ZOHO_MAIL_URL et MCP_ZOHO_MAIL_KEY dans .env")

    def _call_mcp(self, method: str, params: Optional[Dict] = None) -> Any:
        """Appelle le MCP server Zoho Mail"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.mail_key}"
        }

        try:
            response = requests.post(self.mail_url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()

            result = response.json()

            if "error" in result:
                raise Exception(f"Erreur MCP: {result['error']}")

            return result.get("result", {})

        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de l'appel MCP mail: {e}")

    def list_folders(self) -> List[Dict]:
        """Liste les dossiers mail"""
        return self._call_mcp("tools/call", {
            "name": "list_folders",
            "arguments": {}
        })

    def list_emails(self, folder_id: str = None, limit: int = 50) -> List[Dict]:
        """Liste les emails d'un dossier"""
        args = {"limit": limit}
        if folder_id:
            args["folder_id"] = folder_id

        return self._call_mcp("tools/call", {
            "name": "list_emails",
            "arguments": args
        })

    def get_email(self, message_id: str) -> Dict:
        """Obtient le contenu d'un email"""
        return self._call_mcp("tools/call", {
            "name": "get_email",
            "arguments": {"message_id": message_id}
        })

    def search_emails(self, query: str, limit: int = 50) -> List[Dict]:
        """Recherche dans les emails"""
        return self._call_mcp("tools/call", {
            "name": "search_emails",
            "arguments": {"query": query, "limit": limit}
        })

    def discover_tools(self) -> Dict:
        """Découvre les outils disponibles"""
        return self._call_mcp("tools/list", {})


class EmailEventsScanner:
    """Scanne les emails pour extraire les événements"""

    EVENT_KEYWORDS = {
        'webinar': ['webinar', 'webinaire', 'online event', 'virtual event', 'live session', 'web conference', 'live webinar'],
        'conference': ['conference', 'conférence', 'summit', 'sommet', 'forum', 'congress', 'symposium'],
        'workshop': ['workshop', 'atelier', 'formation', 'training', 'masterclass', 'bootcamp', 'hands-on'],
        'meetup': ['meetup', 'networking', 'réseautage', 'afterwork', 'apéro', 'rencontre'],
        'demo': ['demo', 'démonstration', 'product launch', 'lancement', 'showcase', 'preview'],
        'talk': ['talk', 'présentation', 'keynote', 'speech', 'conférencier', 'speaker'],
        'course': ['course', 'cours', 'class', 'lesson', 'e-learning', 'certification', 'learning'],
    }

    DATE_PATTERNS = [
        r'(\d{1,2})\s*(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|jan\.?|fév\.?|mar\.?|avr\.?|mai\.?|juin\.?|juil\.?|août\.?|sept\.?|oct\.?|nov\.?|déc\.?)\s*(\d{4})?',
        r'(January|February|March|April|May|June|July|August|September|October|November|December|Jan\.?|Feb\.?|Mar\.?|Apr\.?|May\.?|Jun\.?|Jul\.?|Aug\.?|Sep\.?|Oct\.?|Nov\.?|Dec\.?)\s*(\d{1,2}),?\s*(\d{4})?',
        r'(\d{1,2})\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s*(\d{4})?',
        r'(\d{4})-(\d{2})-(\d{2})',
        r'(\d{1,2})[/\.](\d{1,2})[/\.](\d{4})',
    ]

    TIME_PATTERNS = [
        r'(\d{1,2})[h:](\d{2})?\s*(AM|PM|am|pm)?',
        r'(\d{1,2})\s*(AM|PM|am|pm)',
        r'à\s*(\d{1,2})[h:](\d{2})?',
        r'at\s*(\d{1,2}):?(\d{2})?\s*(AM|PM|am|pm)?',
    ]

    REGISTRATION_PATTERNS = [
        r'(https?://[^\s<>"]+(?:register|inscription|signup|rsvp|event|webinar|zoom\.us|teams\.microsoft|meet\.google|eventbrite|hopin|livestorm|gotowebinar|crowdcast|demio)[^\s<>"]*)',
        r'(https?://[^\s<>"]+)',
    ]

    def __init__(self):
        self.client = ZohoMailMCPClient()

    def _clean_html(self, html_content: str) -> str:
        """Nettoie le HTML pour extraire le texte"""
        if not html_content:
            return ""
        text = re.sub(r'<[^>]+>', ' ', html_content)
        text = unescape(text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _detect_event_type(self, text: str) -> Optional[str]:
        """Détecte le type d'événement dans le texte"""
        text_lower = text.lower()
        for event_type, keywords in self.EVENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return event_type
        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """Extrait la date de l'événement"""
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _extract_time(self, text: str) -> Optional[str]:
        """Extrait l'heure de l'événement"""
        for pattern in self.TIME_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None

    def _extract_registration_url(self, text: str) -> Optional[str]:
        """Extrait l'URL d'inscription"""
        for pattern in self.REGISTRATION_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for url in matches:
                    if any(kw in url.lower() for kw in ['register', 'inscription', 'signup', 'rsvp', 'event', 'webinar', 'zoom']):
                        return url
                return matches[0]
        return None

    def _calculate_relevance(self, text: str, subject: str, sender: str) -> int:
        """Calcule un score de pertinence (1-10)"""
        score = 5

        subject_lower = subject.lower()
        for keywords in self.EVENT_KEYWORDS.values():
            if any(kw in subject_lower for kw in keywords):
                score += 2
                break

        if self._extract_date(text):
            score += 1

        if self._extract_registration_url(text):
            score += 1

        trusted_domains = ['zoom.us', 'eventbrite', 'linkedin', 'microsoft', 'google',
                          'salesforce', 'hubspot', 'gartner', 'forrester', 'meetup']
        if any(domain in sender.lower() for domain in trusted_domains):
            score += 1

        return min(10, score)

    def scan_email(self, email: Dict) -> Optional[Event]:
        """Scanne un email pour détecter un événement"""
        subject = email.get("subject", "")
        sender_email = email.get("fromAddress", email.get("sender", ""))
        sender_name = email.get("fromName", sender_email)
        received_time = email.get("receivedTime", email.get("date", ""))
        message_id = email.get("messageId", email.get("id", ""))

        preview = email.get("summary", email.get("snippet", ""))
        content = email.get("content", email.get("body", ""))

        combined_text = f"{subject} {preview}"

        event_type = self._detect_event_type(combined_text)
        if not event_type:
            return None

        full_text = f"{subject} {preview} {self._clean_html(content)}"

        event_date = self._extract_date(full_text)
        event_time = self._extract_time(full_text)
        registration_url = self._extract_registration_url(full_text)
        relevance = self._calculate_relevance(full_text, subject, sender_email)

        description = preview[:200] if preview else self._clean_html(content)[:200]
        if len(description) == 200:
            description += "..."

        if isinstance(received_time, (int, float)):
            email_date = datetime.fromtimestamp(received_time / 1000).strftime("%Y-%m-%d %H:%M")
        else:
            email_date = str(received_time)

        return Event(
            title=subject,
            event_type=event_type,
            date=event_date,
            time=event_time,
            organizer=sender_name,
            sender_email=sender_email,
            email_subject=subject,
            email_date=email_date,
            registration_url=registration_url,
            description=description,
            relevance_score=relevance,
            message_id=message_id
        )

    def scan_with_search(self, search_queries: List[str] = None, limit: int = 50) -> List[Event]:
        """Scanne les emails en utilisant la recherche MCP"""
        if search_queries is None:
            search_queries = ["webinar", "conference", "workshop", "formation", "event invitation", "inscrivez-vous"]

        events = []
        seen_ids = set()

        for query in search_queries:
            print(f"  Recherche: '{query}'...")
            try:
                result = self.client.search_emails(query, limit=limit)
                emails = result.get("content", []) if isinstance(result, dict) else result

                if isinstance(emails, list):
                    for email in emails:
                        msg_id = email.get("messageId", email.get("id", ""))
                        if msg_id in seen_ids:
                            continue
                        seen_ids.add(msg_id)

                        event = self.scan_email(email)
                        if event:
                            events.append(event)
                            print(f"    -> Événement: {event.event_type} - {event.title[:40]}...")
            except Exception as e:
                print(f"    Erreur recherche '{query}': {e}")

        events.sort(key=lambda e: e.relevance_score, reverse=True)
        return events

    def scan_inbox(self, limit: int = 100) -> List[Event]:
        """Scanne la boîte de réception"""
        print("  Récupération des emails récents...")
        events = []

        try:
            result = self.client.list_emails(limit=limit)
            emails = result.get("content", []) if isinstance(result, dict) else result

            if isinstance(emails, list):
                print(f"  {len(emails)} emails trouvés")
                for i, email in enumerate(emails):
                    subject = email.get("subject", "")[:40]
                    print(f"  [{i+1}/{len(emails)}] {subject}...")

                    event = self.scan_email(email)
                    if event:
                        events.append(event)
                        print(f"    -> Événement trouvé: {event.event_type}")
        except Exception as e:
            print(f"  Erreur liste emails: {e}")

        events.sort(key=lambda e: e.relevance_score, reverse=True)
        return events


def format_events_for_display(events: List[Event]) -> str:
    """Formate les événements pour affichage"""
    if not events:
        return "Aucun événement trouvé dans vos emails récents."

    output = []
    output.append(f"\n{'='*70}")
    output.append(f"  ÉVÉNEMENTS DÉTECTÉS ({len(events)} trouvés)")
    output.append(f"{'='*70}\n")

    for i, event in enumerate(events, 1):
        stars = "" * min(event.relevance_score, 5) + "" * (5 - min(event.relevance_score, 5))

        output.append(f"[{i}] {event.title}")
        output.append(f"    Type: {event.event_type.upper()} | Pertinence: {stars}")
        output.append(f"    Organisateur: {event.organizer}")
        if event.date:
            date_str = f"{event.date}"
            if event.time:
                date_str += f" à {event.time}"
            output.append(f"    Date: {date_str}")
        if event.registration_url:
            url_display = event.registration_url[:80] + "..." if len(event.registration_url) > 80 else event.registration_url
            output.append(f"    Inscription: {url_display}")
        output.append(f"    Email reçu le: {event.email_date}")
        if event.description:
            desc = event.description[:150] + "..." if len(event.description) > 150 else event.description
            output.append(f"    {desc}")
        output.append("")

    return "\n".join(output)


def main():
    """Fonction principale"""
    try:
        print("=" * 70)
        print("  SCANNER D'ÉVÉNEMENTS - ZOHO MAIL MCP")
        print("=" * 70)
        print()

        print("1. Initialisation du client MCP...")
        scanner = EmailEventsScanner()
        print("   Client MCP initialisé")
        print()

        print("2. Découverte des outils disponibles...")
        try:
            tools = scanner.client.discover_tools()
            print(f"   Outils: {json.dumps(tools, indent=2)[:500]}...")
        except Exception as e:
            print(f"   Note: {e}")
        print()

        print("3. Scan des emails par recherche de mots-clés événements...")
        events = scanner.scan_with_search(limit=30)

        if not events:
            print("\n4. Essai avec scan de la boîte de réception...")
            events = scanner.scan_inbox(limit=50)

        print(format_events_for_display(events))

        # Sauvegarder en JSON
        output_file = ".tmp/email_events.json"
        os.makedirs(".tmp", exist_ok=True)

        events_data = [asdict(e) for e in events]
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "scan_date": datetime.now().isoformat(),
                "total_events": len(events),
                "events": events_data
            }, f, indent=2, ensure_ascii=False)

        print(f"\nRésultats sauvegardés dans {output_file}")
        return 0

    except Exception as e:
        print(f"\nErreur: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
