#!/usr/bin/env python3
"""
Scanner d'événements dans les emails - Extrait webinars, conférences, etc.
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from html import unescape

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from zoho_client import ZohoClient


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


class EmailEventsScanner:
    """Scanne les emails pour extraire les événements"""

    # Mots-clés pour détecter les types d'événements
    EVENT_KEYWORDS = {
        'webinar': ['webinar', 'webinaire', 'online event', 'virtual event', 'live session', 'web conference'],
        'conference': ['conference', 'conférence', 'summit', 'sommet', 'forum', 'congress'],
        'workshop': ['workshop', 'atelier', 'formation', 'training', 'masterclass', 'bootcamp'],
        'meetup': ['meetup', 'networking', 'réseautage', 'afterwork', 'apéro'],
        'demo': ['demo', 'démonstration', 'product launch', 'lancement', 'showcase'],
        'talk': ['talk', 'présentation', 'keynote', 'speech', 'conférencier'],
        'course': ['course', 'cours', 'class', 'lesson', 'e-learning', 'certification'],
    }

    # Patterns pour extraire les dates
    DATE_PATTERNS = [
        # Français: 15 janvier 2026, 15 jan. 2026
        r'(\d{1,2})\s*(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|jan\.?|fév\.?|mar\.?|avr\.?|mai\.?|juin\.?|juil\.?|août\.?|sept\.?|oct\.?|nov\.?|déc\.?)\s*(\d{4})?',
        # Anglais: January 15, 2026 ou 15 January 2026
        r'(January|February|March|April|May|June|July|August|September|October|November|December|Jan\.?|Feb\.?|Mar\.?|Apr\.?|May\.?|Jun\.?|Jul\.?|Aug\.?|Sep\.?|Oct\.?|Nov\.?|Dec\.?)\s*(\d{1,2}),?\s*(\d{4})?',
        r'(\d{1,2})\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s*(\d{4})?',
        # ISO: 2026-01-15
        r'(\d{4})-(\d{2})-(\d{2})',
        # EU: 15/01/2026 ou 15.01.2026
        r'(\d{1,2})[/\.](\d{1,2})[/\.](\d{4})',
    ]

    # Patterns pour extraire les heures
    TIME_PATTERNS = [
        r'(\d{1,2})[h:](\d{2})?\s*(AM|PM|am|pm)?',
        r'(\d{1,2})\s*(AM|PM|am|pm)',
        r'à\s*(\d{1,2})[h:](\d{2})?',
        r'at\s*(\d{1,2}):?(\d{2})?\s*(AM|PM|am|pm)?',
    ]

    # Patterns pour les URLs d'inscription
    REGISTRATION_PATTERNS = [
        r'(https?://[^\s<>"]+(?:register|inscription|signup|rsvp|event|webinar|zoom\.us|teams\.microsoft|meet\.google|eventbrite|hopin|livestorm|gotowebinar|crowdcast|demio)[^\s<>"]*)',
        r'(https?://[^\s<>"]+)',  # Fallback: any URL
    ]

    def __init__(self):
        self.client = ZohoClient()
        self.account_id = self._get_account_id()

    def _get_account_id(self) -> str:
        """Obtient l'ID du compte mail principal"""
        import requests
        try:
            url = f"{self.client.config.mail_url}/api/accounts"
            response = requests.get(url, headers=self.client._headers())
            response.raise_for_status()
            accounts = response.json().get("data", [])
            if accounts:
                return accounts[0]["accountId"]
        except Exception as e:
            print(f"Erreur lors de la récupération du compte: {e}")
        return os.getenv("ZOHO_MAIL_ACCOUNT_ID", "")

    def _clean_html(self, html_content: str) -> str:
        """Nettoie le HTML pour extraire le texte"""
        if not html_content:
            return ""
        # Supprimer les tags HTML
        text = re.sub(r'<[^>]+>', ' ', html_content)
        # Décoder les entités HTML
        text = unescape(text)
        # Nettoyer les espaces multiples
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
                # Préférer les URLs avec des mots-clés d'inscription
                for url in matches:
                    if any(kw in url.lower() for kw in ['register', 'inscription', 'signup', 'rsvp', 'event']):
                        return url
                return matches[0]
        return None

    def _calculate_relevance(self, text: str, subject: str, sender: str) -> int:
        """Calcule un score de pertinence (1-10)"""
        score = 5  # Score de base

        # Bonus si mot-clé dans le sujet
        subject_lower = subject.lower()
        for keywords in self.EVENT_KEYWORDS.values():
            if any(kw in subject_lower for kw in keywords):
                score += 2
                break

        # Bonus si date mentionnée
        if self._extract_date(text):
            score += 1

        # Bonus si URL d'inscription
        if self._extract_registration_url(text):
            score += 1

        # Bonus pour certains expéditeurs connus (business/tech)
        trusted_domains = ['zoom.us', 'eventbrite', 'linkedin', 'microsoft', 'google',
                          'salesforce', 'hubspot', 'gartner', 'forrester']
        if any(domain in sender.lower() for domain in trusted_domains):
            score += 1

        return min(10, score)

    def get_email_content(self, message_id: str) -> str:
        """Récupère le contenu complet d'un email"""
        try:
            content = self.client.mail_get_message(self.account_id, message_id)
            return self._clean_html(content.get("content", ""))
        except Exception as e:
            print(f"  Erreur lecture email {message_id}: {e}")
            return ""

    def scan_email(self, email: Dict) -> Optional[Event]:
        """Scanne un email pour détecter un événement"""
        subject = email.get("subject", "")
        sender = email.get("sender", {})
        sender_email = sender.get("address", "")
        sender_name = sender.get("name", sender_email)
        received_time = email.get("receivedTime", 0)
        message_id = email.get("messageId", "")

        # Combiner sujet et aperçu pour la détection initiale
        preview = email.get("summary", "")
        combined_text = f"{subject} {preview}"

        # Détecter le type d'événement
        event_type = self._detect_event_type(combined_text)
        if not event_type:
            return None

        # Récupérer le contenu complet pour plus de détails
        full_content = self.get_email_content(message_id)
        full_text = f"{subject} {preview} {full_content}"

        # Extraire les détails
        event_date = self._extract_date(full_text)
        event_time = self._extract_time(full_text)
        registration_url = self._extract_registration_url(full_text)

        # Calculer la pertinence
        relevance = self._calculate_relevance(full_text, subject, sender_email)

        # Créer une description courte
        description = preview[:200] if preview else full_content[:200]
        if len(description) == 200:
            description += "..."

        email_date = datetime.fromtimestamp(received_time / 1000).strftime("%Y-%m-%d %H:%M")

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

    def scan_recent_emails(self, days: int = 30, limit: int = 200) -> List[Event]:
        """Scanne les emails récents pour trouver des événements"""
        print(f"Scanning emails des {days} derniers jours...")

        if not self.account_id:
            raise ValueError("Impossible de déterminer l'ID du compte mail")

        # Récupérer les dossiers
        folders = self.client.mail_list_folders(self.account_id)
        inbox_folder = None
        for folder in folders:
            if folder.get("name", "").lower() in ["inbox", "boîte de réception"]:
                inbox_folder = folder
                break

        if not inbox_folder:
            raise ValueError("Dossier Inbox non trouvé")

        # Récupérer les emails
        emails = self.client.mail_list_messages(
            self.account_id,
            inbox_folder["folderId"],
            limit=limit
        )

        # Filtrer par date
        date_from = datetime.now() - timedelta(days=days)
        recent_emails = []
        for email in emails:
            email_date = datetime.fromtimestamp(email.get("receivedTime", 0) / 1000)
            if email_date >= date_from:
                recent_emails.append(email)

        print(f"  {len(recent_emails)} emails récents trouvés")

        # Scanner chaque email
        events = []
        for i, email in enumerate(recent_emails):
            subject = email.get("subject", "")[:50]
            print(f"  [{i+1}/{len(recent_emails)}] {subject}...")

            event = self.scan_email(email)
            if event:
                print(f"    -> Event trouvé: {event.event_type}")
                events.append(event)

        # Trier par score de pertinence décroissant
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
        stars = "★" * min(event.relevance_score, 5) + "☆" * (5 - min(event.relevance_score, 5))

        output.append(f"[{i}] {event.title}")
        output.append(f"    Type: {event.event_type.upper()} | Pertinence: {stars}")
        output.append(f"    Organisateur: {event.organizer}")
        if event.date:
            date_str = f"{event.date}"
            if event.time:
                date_str += f" à {event.time}"
            output.append(f"    Date: {date_str}")
        if event.registration_url:
            output.append(f"    Inscription: {event.registration_url[:80]}...")
        output.append(f"    Email reçu le: {event.email_date}")
        output.append(f"    {event.description[:150]}...")
        output.append("")

    return "\n".join(output)


def main():
    """Fonction principale"""
    try:
        days = int(os.getenv("EVENT_SCAN_DAYS", "30"))
        limit = int(os.getenv("EVENT_SCAN_LIMIT", "200"))

        print(f"Démarrage du scan des événements...")

        scanner = EmailEventsScanner()
        events = scanner.scan_recent_emails(days=days, limit=limit)

        # Afficher les résultats
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
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
