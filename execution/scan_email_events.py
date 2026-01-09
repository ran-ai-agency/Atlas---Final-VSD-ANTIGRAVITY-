#!/usr/bin/env python3
"""
Scanner d'événements emails via Zoho Mail MCP
Détecte webinars, conférences, workshops, meetups, etc.
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
    event_type: str
    date: Optional[str]
    time: Optional[str]
    organizer: str
    sender_email: str
    email_date: str
    description: str
    relevance_score: int
    message_id: str


class ZohoMailMCP:
    """Client Zoho Mail via MCP - Scanne TOUS les comptes"""

    def __init__(self):
        self.mail_url = os.getenv("MCP_ZOHO_MAIL_URL", "")
        self.mail_key = os.getenv("MCP_ZOHO_MAIL_KEY", "")

        if not self.mail_url or not self.mail_key:
            raise ValueError("MCP_ZOHO_MAIL_URL et MCP_ZOHO_MAIL_KEY requis dans .env")

        # Ajouter la clé en query param
        self.mail_url = f"{self.mail_url}?key={self.mail_key}"
        self.accounts = []

    def _call(self, method: str, params: dict) -> Any:
        """Appelle le MCP"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }

        response = requests.post(
            self.mail_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        response.raise_for_status()

        result = response.json()
        if "error" in result:
            raise Exception(f"MCP Error: {result['error']}")

        return result.get("result", {})

    def get_all_accounts(self) -> List[Dict]:
        """Recupere tous les comptes mail configures"""
        result = self._call("tools/call", {
            "name": "ZohoMail_getMailAccounts",
            "arguments": {}
        })

        content = result.get("content", [])
        if content and isinstance(content, list):
            text = content[0].get("text", "{}")
            data = json.loads(text)
            accounts = data.get("data", [])
            # Filtrer les comptes actifs
            self.accounts = [
                {
                    "id": acc.get("accountId"),
                    "name": acc.get("accountDisplayName", acc.get("accountName", "Unknown")),
                    "email": acc.get("incomingUserName", acc.get("primaryEmailAddress", "")),
                    "type": acc.get("type", "UNKNOWN")
                }
                for acc in accounts
                if acc.get("enabled", True)
            ]
            return self.accounts
        return []

    def list_emails_for_account(self, account_id: str, limit: int = 100) -> List[Dict]:
        """Liste les emails d'un compte specifique"""
        result = self._call("tools/call", {
            "name": "ZohoMail_listEmails",
            "arguments": {
                "path_variables": {"accountId": account_id},
                "query_params": {"limit": limit, "start": 1}
            }
        })

        content = result.get("content", [])
        if content and isinstance(content, list):
            text = content[0].get("text", "{}")
            data = json.loads(text)
            return data.get("data", [])
        return []

    def list_emails_all_accounts(self, limit_per_account: int = 100) -> List[Dict]:
        """Liste les emails de TOUS les comptes"""
        if not self.accounts:
            self.get_all_accounts()

        all_emails = []
        for acc in self.accounts:
            acc_id = acc["id"]
            acc_name = acc["name"]
            print(f"    Compte: {acc_name} ({acc['email']})...")

            try:
                emails = self.list_emails_for_account(acc_id, limit=limit_per_account)
                # Ajouter info du compte source
                for email in emails:
                    email["_source_account"] = acc_name
                    email["_source_email"] = acc["email"]
                all_emails.extend(emails)
                print(f"      -> {len(emails)} emails")
            except Exception as e:
                print(f"      -> Erreur: {e}")

        return all_emails


class EventScanner:
    """Detecteur d'evenements dans les emails"""

    EVENT_KEYWORDS = {
        'webinar': ['webinar', 'webinaire', 'online event', 'virtual event', 'live session', 'info session', 'live workshop'],
        'conference': ['conference', 'conférence', 'summit', 'sommet', 'forum', 'symposium'],
        'workshop': ['workshop', 'atelier', 'formation', 'training', 'masterclass', 'bootcamp', 'hands-on', 'live workshop'],
        'meetup': ['meetup', 'networking', 'réseautage', 'afterwork', 'rencontre', 'event invitation'],
        'demo': ['demo', 'démonstration', 'product launch', 'lancement', 'showcase'],
        'course': ['course', 'cours', 'class', 'certification', 'learning session'],
        'rsvp': ['rsvp', 'register now', 'inscrivez-vous', 'join us', 'save your spot', 'reserve your seat'],
    }

    DATE_PATTERNS = [
        r'(\d{1,2})\s*(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)',
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s*(\d{1,2})',
        r'(\d{1,2})\s*(January|February|March|April|May|June|July|August|September|October|November|December)',
        r'(\d{4})-(\d{2})-(\d{2})',
        r'(\d{1,2})[/\.](\d{1,2})[/\.](\d{4})',
    ]

    TIME_PATTERNS = [
        r'(\d{1,2})[h:](\d{2})?\s*(AM|PM|EST|PST)?',
        r'at\s*(\d{1,2}):?(\d{2})?\s*(AM|PM)',
        r'à\s*(\d{1,2})[h:](\d{2})?',
    ]

    def __init__(self):
        self.mcp = ZohoMailMCP()

    def _clean_html(self, text: str) -> str:
        """Nettoie le HTML"""
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', ' ', text)
        text = unescape(text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _detect_event_type(self, text: str) -> Optional[str]:
        """Détecte le type d'événement"""
        text_lower = text.lower()
        for event_type, keywords in self.EVENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return event_type
        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """Extrait la date"""
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _extract_time(self, text: str) -> Optional[str]:
        """Extrait l'heure"""
        for pattern in self.TIME_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _calculate_score(self, text: str, subject: str, sender: str) -> int:
        """Calcule le score de pertinence"""
        score = 5

        # Bonus si mot-clé dans le sujet
        subject_lower = subject.lower()
        for keywords in self.EVENT_KEYWORDS.values():
            if any(kw in subject_lower for kw in keywords):
                score += 2
                break

        # Bonus si date détectée
        if self._extract_date(text):
            score += 1

        # Bonus pour sources connues
        trusted = ['eventbrite', 'zoom', 'microsoft', 'google', 'meetup', 'uottawa']
        if any(t in sender.lower() for t in trusted):
            score += 1

        return min(10, score)

    def scan_email(self, email: Dict) -> Optional[Event]:
        """Analyse un email pour détecter un événement"""
        subject = email.get("subject", "")
        sender = email.get("sender", "")
        sender_email = email.get("fromAddress", "")
        summary = email.get("summary", "")
        message_id = email.get("messageId", "")
        received_time = email.get("receivedTime", 0)

        combined_text = f"{subject} {summary}"

        # Détecter le type d'événement
        event_type = self._detect_event_type(combined_text)
        if not event_type:
            return None

        # Extraire les détails
        event_date = self._extract_date(combined_text)
        event_time = self._extract_time(combined_text)
        score = self._calculate_score(combined_text, subject, sender_email)

        # Formater la date de l'email
        if isinstance(received_time, (int, float)) and received_time > 0:
            email_date = datetime.fromtimestamp(int(received_time) / 1000).strftime("%Y-%m-%d %H:%M")
        else:
            email_date = "Unknown"

        # Description nettoyée
        description = self._clean_html(summary)[:200]

        return Event(
            title=self._clean_html(subject),
            event_type=event_type,
            date=event_date,
            time=event_time,
            organizer=sender,
            sender_email=sender_email,
            email_date=email_date,
            description=description,
            relevance_score=score,
            message_id=message_id
        )

    def scan_recent_emails(self, limit: int = 200) -> List[Event]:
        """Scanne les emails recents de TOUS les comptes"""
        print(f"Recuperation des emails (limite {limit} par compte)...")
        print("  Scan de tous les comptes configures:")

        # Utiliser la nouvelle methode qui scanne tous les comptes
        emails = self.mcp.list_emails_all_accounts(limit_per_account=limit)
        print(f"  Total: {len(emails)} emails recuperes")

        events = []
        for email in emails:
            event = self.scan_email(email)
            if event:
                events.append(event)

        # Trier par score decroissant
        events.sort(key=lambda e: e.relevance_score, reverse=True)
        return events


def format_events(events: List[Event]) -> str:
    """Formate les événements pour affichage"""
    if not events:
        return "Aucun evenement trouve."

    lines = []
    lines.append("")
    lines.append("=" * 70)
    lines.append(f"  EVENEMENTS DETECTES ({len(events)})")
    lines.append("=" * 70)
    lines.append("")

    for i, e in enumerate(events, 1):
        stars = "*" * min(e.relevance_score // 2, 5)
        # Nettoyer le titre pour l'affichage console
        title = e.title[:60].encode('ascii', 'replace').decode('ascii')
        organizer = e.organizer.encode('ascii', 'replace').decode('ascii')
        description = e.description[:100].encode('ascii', 'replace').decode('ascii')

        lines.append(f"[{i}] {title}")
        lines.append(f"    Type: {e.event_type.upper()} | Score: {stars}")
        lines.append(f"    Organisateur: {organizer}")
        if e.date:
            date_str = e.date
            if e.time:
                date_str += f" a {e.time}"
            lines.append(f"    Date evenement: {date_str}")
        lines.append(f"    Email recu: {e.email_date}")
        lines.append(f"    {description}...")
        lines.append("")

    return "\n".join(lines)


def send_to_cliq(events: List[Event], channel: str = "veilleia") -> bool:
    """Envoie une notification Cliq avec les événements"""
    cliq_url = os.getenv("MCP_ZOHO_CLIQ_URL", "")
    cliq_key = os.getenv("MCP_ZOHO_CLIQ_KEY", "")

    if not cliq_url or not cliq_key:
        print("  Cliq non configure")
        return False

    # Formater le message pour Cliq (Markdown)
    message_lines = [f"**EVENEMENTS DETECTES ({len(events)})**\n"]

    for i, e in enumerate(events[:5], 1):  # Top 5
        title = e.title[:50].encode('ascii', 'replace').decode('ascii')
        organizer = e.organizer.encode('ascii', 'replace').decode('ascii')
        message_lines.append(f"{i}. **{title}** - {e.event_type.upper()}")
        message_lines.append(f"   Date: {e.date or 'A confirmer'}")
        message_lines.append(f"   De: {organizer}")
        message_lines.append("")

    if len(events) > 5:
        message_lines.append(f"_...et {len(events) - 5} autres evenements_")

    message_lines.append("\n_Scan automatique ATLAS_")
    message = "\n".join(message_lines)

    # Envoyer via MCP Cliq
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "Post message in a channel",
                "arguments": {
                    "path_variables": {"CHANNEL_UNIQUE_NAME": channel},
                    "body": {"text": message}
                }
            }
        }

        response = requests.post(
            f"{cliq_url}?key={cliq_key}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code == 200:
            print(f"  Notification Cliq envoyee dans #{channel}")
            return True
    except Exception as e:
        print(f"  Erreur Cliq: {e}")

    return False


def main():
    """Fonction principale"""
    import argparse

    parser = argparse.ArgumentParser(description="Scanner d'evenements email")
    parser.add_argument("--alert", action="store_true", help="Envoyer alerte Cliq")
    parser.add_argument("--channel", default="veilleia", help="Canal Cliq (defaut: veilleia)")
    parser.add_argument("--limit", type=int, default=200, help="Nombre d'emails a scanner")
    args = parser.parse_args()

    try:
        print("=" * 70)
        print("  SCANNER D'EVENEMENTS EMAIL")
        print("=" * 70)
        print()

        scanner = EventScanner()
        events = scanner.scan_recent_emails(limit=args.limit)

        print(format_events(events))

        # Sauvegarder en JSON
        os.makedirs(".tmp", exist_ok=True)
        output = {
            "scan_date": datetime.now().isoformat(),
            "total_events": len(events),
            "events": [asdict(e) for e in events]
        }

        with open(".tmp/email_events.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\nResultats: .tmp/email_events.json")

        # Envoyer alerte Cliq si demande
        if args.alert and events:
            send_to_cliq(events, channel=args.channel)

        return 0

    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
