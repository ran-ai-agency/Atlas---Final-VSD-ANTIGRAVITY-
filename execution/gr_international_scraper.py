#!/usr/bin/env python3
"""
GR International Event Scraper - Version Playwright
Automatisation complete avec navigation JavaScript et authentification.
"""

import os
import re
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = "https://www.grinternational.ca"
SCHEDULE_URL = f"{BASE_URL}/schedule/"
EVENTS_URL = f"{BASE_URL}/events/"
MEMBERS_URL = f"{BASE_URL}/membres/"
# Lien d'acces membre avec token (peut expirer)
MEMBER_TOKEN_URL = os.getenv('GR_MEMBER_URL', '')

# Zones geographiques acceptees pour presentiel (rayon ~60km de Montreal)
ZONES_ACCEPTEES = [
    "montreal", "montréal", "laval", "longueuil", "brossard", "terrebonne",
    "repentigny", "saint-laurent", "dorval", "pointe-claire", "kirkland",
    "beaconsfield", "vaudreuil", "hudson", "pincourt", "ile-perrot", "île-perrot",
    "châteauguay", "chateauguay", "lasalle", "verdun", "lachine", "anjou",
    "saint-léonard", "saint-leonard", "rivière-des-prairies", "pierrefonds",
    "roxboro", "sainte-geneviève", "dollard-des-ormeaux", "côte-saint-luc",
    "westmount", "outremont", "mont-royal", "hampstead", "boucherville",
    "saint-bruno", "saint-hubert", "candiac", "la prairie", "saint-constant",
    "delson", "sainte-catherine", "saint-eustache", "deux-montagnes",
    "boisbriand", "rosemère", "blainville", "mirabel", "mascouche"
]


@dataclass
class Event:
    """Represente un evenement GR International"""
    name: str
    group: str
    date: str
    time: str
    format: str  # "Presentiel" ou "Zoom"
    location: Optional[str]
    event_type: str  # "Porte-ouverte", "Reunion", "Formation", "Conference"
    registration_url: Optional[str]
    score: int = 0  # 1-5
    notes: str = ""
    reasons: List[str] = None  # Raisons detaillees de la recommandation

    def __post_init__(self):
        if self.reasons is None:
            self.reasons = []

    def to_dict(self):
        d = asdict(self)
        return d


class GRInternationalScraper:
    """Scraper Playwright pour le site GR International"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.page = None
        self.authenticated = False
        self.events: List[Event] = []

    def start_browser(self):
        """Demarre le navigateur Playwright"""
        from playwright.sync_api import sync_playwright

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = self.context.new_page()
        print("[OK] Navigateur demarre")

    def close_browser(self):
        """Ferme le navigateur"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        print("[OK] Navigateur ferme")

    def authenticate(self) -> bool:
        """Authentification au portail membres"""
        email = os.getenv('GR_EMAIL')
        password = os.getenv('GR_PASSWORD')
        member_url = os.getenv('GR_MEMBER_URL', '')

        # Methode 1: Utiliser le lien membre avec token
        if member_url:
            try:
                print("[AUTH] Connexion via lien membre...")
                self.page.goto(member_url, wait_until='networkidle', timeout=30000)
                self.page.wait_for_timeout(3000)

                # Verifier si on est connecte
                content = self.page.content().lower()
                if 'member' in content or 'membre' in content or 'welcome' in content or 'bienvenue' in content:
                    self.authenticated = True
                    print("[OK] Authentification via token reussie")

                    # Sauvegarder capture
                    tmp_dir = Path(__file__).parent.parent / ".tmp"
                    tmp_dir.mkdir(exist_ok=True)
                    self.page.screenshot(path=str(tmp_dir / "member_page.png"))
                    return True
            except Exception as e:
                print(f"[WARN] Erreur token: {e}")

        # Methode 2: Login classique
        if not email or not password:
            print("[WARN] Identifiants GR non configures dans .env")
            return False

        try:
            print(f"[AUTH] Connexion avec {email}...")

            # Aller sur la page membres
            self.page.goto(MEMBERS_URL, wait_until='networkidle', timeout=30000)
            self.page.wait_for_timeout(2000)

            # Chercher le formulaire de connexion
            login_selectors = [
                'input[name="email"]',
                'input[type="email"]',
                'input[name="username"]',
                'input[name="user"]',
                '#email',
                '#username'
            ]

            email_field = None
            for selector in login_selectors:
                try:
                    if self.page.locator(selector).count() > 0:
                        email_field = self.page.locator(selector).first
                        break
                except:
                    continue

            if email_field:
                email_field.fill(email)

                password_selectors = [
                    'input[name="password"]',
                    'input[type="password"]',
                    '#password'
                ]

                for selector in password_selectors:
                    try:
                        if self.page.locator(selector).count() > 0:
                            self.page.locator(selector).first.fill(password)
                            break
                    except:
                        continue

                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Login")',
                    'button:has-text("Connexion")',
                    'button:has-text("Se connecter")',
                    '.login-btn',
                    '#login-btn'
                ]

                for selector in submit_selectors:
                    try:
                        if self.page.locator(selector).count() > 0:
                            self.page.locator(selector).first.click()
                            break
                    except:
                        continue

                self.page.wait_for_timeout(3000)

                if 'logout' in self.page.content().lower() or 'deconnexion' in self.page.content().lower():
                    self.authenticated = True
                    print("[OK] Authentification reussie")
                    return True

            print("[INFO] Navigation en mode public")
            return True

        except Exception as e:
            print(f"[ERROR] Erreur d'authentification: {e}")
            return False

    def fetch_schedule_events(self) -> List[Event]:
        """Recupere les evenements de la page Schedule avec Playwright"""
        events = []
        tmp_dir = Path(__file__).parent.parent / ".tmp"
        tmp_dir.mkdir(exist_ok=True)

        try:
            print("[SCHEDULE] Navigation vers la page des horaires...")
            self.page.goto(SCHEDULE_URL, wait_until='networkidle', timeout=30000)
            self.page.wait_for_timeout(3000)
            self.page.screenshot(path=str(tmp_dir / "schedule_page_initial.png"))

            # Le formulaire a plusieurs sections par pays (Canada, USA, France, etc.)
            # Dans la section Canada/Quebec, on doit:
            # 1. Selectionner la province "Quebec"
            # 2. Puis selectionner une region (Montreal, etc.)

            # Trouver et cliquer sur la section Canada/Quebec
            try:
                # Chercher tous les selects et trouver celui avec Quebec
                all_selects = self.page.locator('select').all()
                print(f"   -> {len(all_selects)} selects trouves")

                for i, select in enumerate(all_selects):
                    try:
                        options_text = select.inner_text()
                        if 'Quebec' in options_text or 'Québec' in options_text:
                            select.select_option(label='Quebec')
                            print(f"   -> Select #{i}: Province Quebec selectionnee")
                            self.page.wait_for_timeout(2000)

                            # Apres selection de Quebec, chercher le select de Region
                            # qui devrait se charger dynamiquement
                            self.page.screenshot(path=str(tmp_dir / "after_quebec_select.png"))
                            break
                    except Exception as e:
                        continue

                # Attendre que les regions se chargent et selectionner Montreal si disponible
                self.page.wait_for_timeout(2000)

                # Chercher un select avec des regions du Quebec
                for select in self.page.locator('select').all():
                    try:
                        options_text = select.inner_text().lower()
                        if any(r in options_text for r in ['montreal', 'montréal', 'laval', 'rive-sud', 'vaudreuil']):
                            # Selectionner Montreal ou laisser "tous"
                            try:
                                select.select_option(index=1)  # Premier element apres "---"
                                print("   -> Region selectionnee")
                            except:
                                pass
                            break
                    except:
                        continue

            except Exception as e:
                print(f"   -> Erreur selection: {e}")

            # Cliquer sur Send
            try:
                send_btn = self.page.locator('button:has-text("Send"), input[value="Send"], a:has-text("Send")').first
                if send_btn.is_visible():
                    send_btn.click()
                    print("   -> Bouton Send clique")
                    self.page.wait_for_timeout(5000)
                else:
                    # Essayer de soumettre le formulaire autrement
                    self.page.keyboard.press('Enter')
                    self.page.wait_for_timeout(5000)
            except Exception as e:
                print(f"   -> Erreur bouton Send: {e}")

            self.page.screenshot(path=str(tmp_dir / "schedule_page_results.png"))

            # Le site charge les donnees via AJAX dans #reunion_content
            # Attendre que le contenu soit charge
            try:
                self.page.wait_for_selector('#reunion_content', timeout=10000)
                self.page.wait_for_timeout(3000)  # Attendre le chargement AJAX
            except:
                pass

            # Sauvegarder le HTML pour analyse
            html_content = self.page.content()
            (tmp_dir / "schedule_page.html").write_text(html_content, encoding='utf-8')

            # Extraire le contenu de la zone de resultats (prendre le premier element)
            try:
                reunion_content = self.page.locator('#reunion_content').first.inner_text()
                print(f"   -> Contenu reunion: {len(reunion_content)} caracteres")

                # Parser chaque ligne/bloc qui ressemble a un evenement
                lines = reunion_content.split('\n')
                current_event_text = ""

                for line in lines:
                    line = line.strip()
                    if len(line) > 5:
                        current_event_text += " " + line

                        # Si on a accumule assez de texte, essayer de parser
                        if len(current_event_text) > 50:
                            if self._is_valid_event_text(current_event_text):
                                event = self._parse_text_to_event(current_event_text)
                                if event:
                                    events.append(event)
                            current_event_text = ""
            except Exception as e:
                print(f"   -> Erreur extraction reunion_content: {e}")

            # Chercher aussi les liens vers des groupes specifiques
            try:
                group_links = self.page.locator('a[href*="groupe"], a[href*="group"], a[href*="chapter"]').all()
                for link in group_links[:30]:
                    text = link.inner_text().strip()
                    href = link.get_attribute('href')
                    if text and len(text) > 3 and href:
                        # Verifier si c'est un lien vers un groupe/reunion
                        if any(x in text.lower() for x in ['groupe', 'group', 'chapter', 'vaudreuil', 'montreal', 'laval']):
                            event = Event(
                                name=text[:50],
                                group=text[:30],
                                date="Voir site",
                                time="Voir site",
                                format="Presentiel",
                                location=None,
                                event_type="Reunion",
                                registration_url=href if href.startswith('http') else BASE_URL + href
                            )
                            events.append(event)
            except:
                pass

            print(f"   -> {len(events)} evenements trouves sur Schedule")

        except Exception as e:
            print(f"[ERROR] Erreur Schedule: {e}")

        return events

    def fetch_events_page(self) -> List[Event]:
        """Recupere les evenements speciaux de la page Events (ancienne methode)"""
        # Cette methode est remplacee par fetch_evenements_page()
        return []

    def fetch_evenements_page(self) -> List[Event]:
        """
        Recupere les evenements depuis /evenements/ en extrayant les informations
        directement depuis la liste d'evenements (structure: div.event > div.titre, div.description)
        puis en cliquant sur "En savoir plus" pour les details complets
        """
        events = []
        tmp_dir = Path(__file__).parent.parent / ".tmp"
        tmp_dir.mkdir(exist_ok=True)

        evenements_url = f"{BASE_URL}/evenements/"

        try:
            print("[EVENEMENTS] Navigation vers la page des evenements...")
            self.page.goto(evenements_url, wait_until='networkidle', timeout=30000)
            self.page.wait_for_timeout(3000)
            self.page.screenshot(path=str(tmp_dir / "evenements_page_initial.png"))

            # Sauvegarder le HTML pour debug
            html_content = self.page.content()
            (tmp_dir / "evenements_page.html").write_text(html_content, encoding='utf-8')

            # Chercher le lien vers "Tous les evenements"
            try:
                all_events_link = self.page.locator('#event_side_menu a:has-text("Tous")').first
                if all_events_link.is_visible():
                    all_events_link.click()
                    self.page.wait_for_timeout(3000)
                    print("   -> Page 'Tous les evenements' chargee")
                    self.page.screenshot(path=str(tmp_dir / "all_events_page.png"))
            except Exception as e:
                print(f"   -> Pas de lien 'Tous les evenements': {e}")

            # Collecter les evenements de toutes les pages
            all_event_data = []
            pages_visited = 0
            max_pages = 5  # Limiter a 5 pages

            while pages_visited < max_pages:
                pages_visited += 1
                print(f"   -> Analyse page {pages_visited}...")

                # Extraire les evenements de la page courante
                # Structure: div.event contient div.titre et div.description
                event_divs = self.page.locator('div.event').all()
                print(f"      -> {len(event_divs)} evenements sur cette page")

                for event_div in event_divs:
                    try:
                        # Extraire le titre
                        titre_elem = event_div.locator('div.titre').first
                        titre = ""
                        group_location = ""

                        if titre_elem.count() > 0:
                            titre_text = titre_elem.inner_text().strip()
                            # Le titre contient souvent: "Titre evenement\nGroupe / Region / Province / Pays"
                            titre_parts = titre_text.split('\n')
                            if titre_parts:
                                titre = titre_parts[0].strip()
                            if len(titre_parts) > 1:
                                group_location = titre_parts[1].strip()

                        # Si pas de div.titre, chercher dans le texte complet
                        if not titre:
                            full_text = event_div.inner_text().strip()
                            lines = [l.strip() for l in full_text.split('\n') if l.strip()]
                            titre = lines[0] if lines else "Evenement"

                        # Extraire la description
                        description = ""
                        desc_elem = event_div.locator('div.description').first
                        if desc_elem.count() > 0:
                            description = desc_elem.inner_text().strip()

                        # Extraire le jour (div.day)
                        day = ""
                        day_elem = event_div.locator('div.day').first
                        if day_elem.count() > 0:
                            day = day_elem.inner_text().strip()

                        # Extraire le lien "En savoir plus"
                        detail_url = None
                        plus_link = event_div.locator('a:has-text("En savoir plus")').first
                        if plus_link.count() > 0:
                            href = plus_link.get_attribute('href')
                            if href:
                                detail_url = href if href.startswith('http') else BASE_URL + href

                        # Stocker les donnees
                        if titre and len(titre) > 5:
                            all_event_data.append({
                                'titre': titre,
                                'group_location': group_location,
                                'description': description,
                                'day': day,
                                'detail_url': detail_url
                            })

                    except Exception as e:
                        continue

                # Chercher le lien vers la page suivante
                try:
                    next_link = self.page.locator('li.paginate_button.next a, a:has-text(">")').first
                    if next_link.is_visible():
                        next_link.click()
                        self.page.wait_for_timeout(2000)
                    else:
                        break  # Plus de page suivante
                except:
                    break  # Plus de pagination

            print(f"   -> {len(all_event_data)} evenements collectes au total")

            # Maintenant, visiter les pages de detail pour extraire plus d'infos
            for i, event_data in enumerate(all_event_data[:30]):  # Limiter a 30
                try:
                    titre = event_data['titre']
                    detail_url = event_data['detail_url']

                    print(f"   -> [{i+1}/{min(len(all_event_data), 30)}] {titre[:50]}...")

                    if detail_url:
                        self.page.goto(detail_url, wait_until='networkidle', timeout=20000)
                        self.page.wait_for_timeout(1500)

                        # Extraire les details complets
                        event = self._extract_event_details_v2(
                            url=detail_url,
                            titre_preview=titre,
                            group_preview=event_data['group_location'],
                            day_preview=event_data['day'],
                            desc_preview=event_data['description']
                        )
                    else:
                        # Creer un evenement basique avec les infos collectees
                        event = self._create_event_from_preview(event_data)

                    if event:
                        events.append(event)
                        print(f"      [OK] {event.name[:50]}")

                except Exception as e:
                    print(f"      [ERREUR] {str(e)[:50]}")
                    continue

            # Sauvegarder capture finale
            self.page.screenshot(path=str(tmp_dir / "evenements_final.png"))
            print(f"   -> {len(events)} evenements extraits avec details")

        except Exception as e:
            print(f"[ERROR] Erreur page evenements: {e}")

        return events

    def _create_event_from_preview(self, event_data: dict) -> Optional[Event]:
        """Cree un evenement a partir des donnees de preview"""
        try:
            titre = event_data.get('titre', 'Evenement')
            group_loc = event_data.get('group_location', '')
            desc = event_data.get('description', '')
            day = event_data.get('day', '')

            # Determiner le format
            combined_text = (titre + ' ' + desc).lower()
            is_zoom = any(x in combined_text for x in ['zoom', 'virtual', 'virtuel', 'en ligne'])
            format_type = "Zoom" if is_zoom else "Presentiel"

            # Determiner le type
            event_type = "Reunion"
            if any(x in combined_text for x in ['porte', 'open house', 'guest day']):
                event_type = "Porte-ouverte"
            elif any(x in combined_text for x in ['formation', 'training']):
                event_type = "Formation"
            elif any(x in combined_text for x in ['conference', 'conférence']):
                event_type = "Conference"

            # Extraire le groupe depuis group_location
            group = "Non specifie"
            if group_loc:
                parts = group_loc.split('/')
                if parts:
                    group = parts[0].strip()[:40]

            return Event(
                name=titre[:100],
                group=group,
                date=f"Jour {day}" if day else "Date a confirmer",
                time="Heure a confirmer",
                format=format_type,
                location=group_loc if not is_zoom else None,
                event_type=event_type,
                registration_url=event_data.get('detail_url')
            )
        except:
            return None

    def _extract_event_details_v2(self, url: str, titre_preview: str, group_preview: str,
                                   day_preview: str, desc_preview: str) -> Optional[Event]:
        """
        Extrait les details complets d'un evenement depuis sa page individuelle
        en utilisant les infos de preview comme fallback
        """
        try:
            page_text = self.page.inner_text('body')
            page_text_lower = page_text.lower()

            # Titre: utiliser le preview ou chercher h1/h2
            title = titre_preview
            try:
                h1_elem = self.page.locator('h1, h2, .event-title, .titre').first
                if h1_elem.is_visible():
                    h1_text = h1_elem.inner_text().strip()
                    # Ne pas remplacer si c'est juste le titre de la page
                    if h1_text and len(h1_text) > 5 and 'GR International' not in h1_text:
                        title = h1_text
            except:
                pass

            # Nettoyer le titre
            title = re.sub(r'\s+', ' ', title).strip()

            # Date: chercher dans la page
            date_str = f"Janvier {day_preview}" if day_preview else "Date a confirmer"
            date_patterns = [
                r'(\d{1,2}\s+(?:janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)\s+\d{4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'((?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+\d{1,2}\s+\w+\s+\d{4})',
            ]

            for pattern in date_patterns:
                match = re.search(pattern, page_text_lower, re.IGNORECASE)
                if match:
                    date_str = match.group(1).strip()
                    break

            # Heure
            time_str = "Heure a confirmer"
            time_patterns = [
                r'(\d{1,2}\s*[h:]\s*\d{2})',
                r'(\d{1,2}\s*h\s*\d{0,2})',
                r'de\s+(\d{1,2}[h:]\d{2})\s+[aà]\s+(\d{1,2}[h:]\d{2})'
            ]

            for pattern in time_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    time_str = match.group(0) if match.lastindex and match.lastindex > 1 else match.group(1)
                    break

            # Format
            is_zoom = any(x in page_text_lower for x in ['zoom', 'virtual', 'virtuel', 'en ligne', 'webinaire'])
            format_type = "Zoom" if is_zoom else "Presentiel"

            # Type d'evenement
            event_type = "Reunion"
            if any(x in page_text_lower for x in ['porte ouverte', 'portes ouvertes', 'open house']):
                event_type = "Porte-ouverte"
            elif any(x in page_text_lower for x in ['formation', 'training', 'atelier']):
                event_type = "Formation"
            elif any(x in page_text_lower for x in ['conference', 'conférence']):
                event_type = "Conference"
            elif any(x in page_text_lower for x in ['5 a 7', '5 à 7', '5@7', 'cocktail']):
                event_type = "5 a 7"
            elif any(x in page_text_lower for x in ['lancement']):
                event_type = "Lancement"

            # Lieu
            location = None
            if not is_zoom and group_preview:
                location = group_preview

            # Groupe
            group = "Non specifie"
            if group_preview:
                parts = group_preview.split('/')
                if parts:
                    group = parts[0].strip()[:40]

            # Verifier zones Montreal
            if any(zone in page_text_lower for zone in ZONES_ACCEPTEES):
                for zone in ZONES_ACCEPTEES:
                    if zone in page_text_lower:
                        if group == "Non specifie":
                            group = zone.capitalize()
                        break

            return Event(
                name=title[:100],
                group=group,
                date=date_str,
                time=time_str,
                format=format_type,
                location=location,
                event_type=event_type,
                registration_url=url
            )

        except Exception as e:
            print(f"      [ERREUR extraction v2] {str(e)[:50]}")
            # Fallback: utiliser les donnees de preview
            return self._create_event_from_preview({
                'titre': titre_preview,
                'group_location': group_preview,
                'day': day_preview,
                'description': desc_preview,
                'detail_url': url
            })

    def _extract_event_details(self, url: str) -> Optional[Event]:
        """
        Extrait les details complets d'un evenement depuis sa page individuelle
        """
        try:
            # Recuperer le contenu de la page
            page_text = self.page.inner_text('body')
            page_html = self.page.content()

            # Extraire le titre (plusieurs methodes)
            title = None
            title_selectors = [
                'h1',
                '.event-title',
                '.titre-evenement',
                'article h1',
                '.entry-title',
                '[class*="title"]'
            ]

            for selector in title_selectors:
                try:
                    elem = self.page.locator(selector).first
                    if elem.is_visible():
                        title = elem.inner_text().strip()
                        if title and len(title) > 3:
                            break
                except:
                    continue

            if not title:
                # Utiliser le titre de la page
                title = self.page.title() or "Evenement GR"

            # Nettoyer le titre
            title = re.sub(r'\s+', ' ', title).strip()
            title = title.replace('\n', ' ').replace('\t', ' ')

            # Extraire la date
            date_str = "Date a confirmer"
            date_patterns = [
                r'(\d{1,2}\s+(?:janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)\s+\d{4})',
                r'(\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'((?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+\d{1,2}\s+\w+)',
                r'((?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)[,\s]+\w+\s+\d{1,2})',
            ]

            page_text_lower = page_text.lower()
            for pattern in date_patterns:
                match = re.search(pattern, page_text_lower, re.IGNORECASE)
                if match:
                    date_str = match.group(1).strip()
                    break

            # Chercher aussi dans des elements specifiques
            date_selectors = [
                '.event-date',
                '.date',
                '[class*="date"]',
                'time',
                '.meta-date'
            ]

            for selector in date_selectors:
                try:
                    elem = self.page.locator(selector).first
                    if elem.is_visible():
                        date_text = elem.inner_text().strip()
                        if date_text and len(date_text) > 3 and len(date_text) < 100:
                            date_str = date_text
                            break
                except:
                    continue

            # Extraire l'heure
            time_str = "Heure a confirmer"
            time_patterns = [
                r'(\d{1,2}[h:]\d{2})',
                r'(\d{1,2}\s*(?:am|pm|h))',
                r'(\d{1,2}:\d{2}\s*(?:am|pm)?)'
            ]

            for pattern in time_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    time_str = match.group(1)
                    break

            # Determiner le format (Zoom ou Presentiel)
            is_zoom = any(x in page_text_lower for x in ['zoom', 'virtual', 'virtuel', 'online', 'en ligne', 'webinar', 'webinaire'])
            format_type = "Zoom" if is_zoom else "Presentiel"

            # Determiner le type d'evenement
            event_type = "Reunion"
            if any(x in page_text_lower for x in ['porte-ouverte', 'portes ouvertes', 'open house', 'guest day', 'journee porte']):
                event_type = "Porte-ouverte"
            elif any(x in page_text_lower for x in ['formation', 'training', 'workshop', 'atelier']):
                event_type = "Formation"
            elif any(x in page_text_lower for x in ['conference', 'conférence', 'summit', 'sommet', 'congres']):
                event_type = "Conference"
            elif any(x in page_text_lower for x in ['5 a 7', '5 à 7', '5@7', 'cocktail', 'networking']):
                event_type = "5 a 7"

            # Extraire le lieu
            location = None
            if not is_zoom:
                location_selectors = [
                    '.event-location',
                    '.location',
                    '.lieu',
                    '[class*="location"]',
                    '[class*="lieu"]',
                    '.address',
                    '.adresse'
                ]

                for selector in location_selectors:
                    try:
                        elem = self.page.locator(selector).first
                        if elem.is_visible():
                            loc_text = elem.inner_text().strip()
                            if loc_text and len(loc_text) > 5 and len(loc_text) < 200:
                                location = loc_text
                                break
                    except:
                        continue

                # Chercher dans le texte
                if not location:
                    loc_patterns = [
                        r'(?:lieu|location|adresse|address|ou|where)\s*[:\-]?\s*([^\n]{10,100})',
                    ]
                    for pattern in loc_patterns:
                        match = re.search(pattern, page_text, re.IGNORECASE)
                        if match:
                            location = match.group(1).strip()[:100]
                            break

            # Extraire le groupe organisateur
            group = "Non specifie"
            group_patterns = [
                r'(?:groupe?|chapter|club|organise par|organized by)\s*[:\-]?\s*([A-Za-zÀ-ÿ\s\-0-9]+)',
            ]

            for pattern in group_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    group = match.group(1).strip()[:40]
                    break

            # Verifier si c'est un groupe de la region de Montreal/Vaudreuil
            if any(zone in page_text_lower for zone in ['vaudreuil', 'montreal', 'montréal', 'laval', 'longueuil']):
                for zone in ['vaudreuil', 'montreal', 'montréal', 'laval', 'longueuil', 'brossard', 'rive-sud', 'rive-nord']:
                    if zone in page_text_lower:
                        if group == "Non specifie":
                            group = zone.capitalize()
                        break

            # Creer l'evenement
            event = Event(
                name=title[:100],
                group=group,
                date=date_str,
                time=time_str,
                format=format_type,
                location=location,
                event_type=event_type,
                registration_url=url
            )

            return event

        except Exception as e:
            print(f"      [ERREUR extraction] {str(e)[:50]}")
            return None

    def _is_valid_event_text(self, text: str) -> bool:
        """Verifie si le texte ressemble a un evenement valide"""
        if not text or len(text) < 20 or len(text) > 1000:
            return False

        text_lower = text.lower()

        # Mots a ignorer (navigation, footer, faux positifs)
        skip_words = [
            'recherche', 'search', 'filter', 'menu', 'navigation', 'copyright',
            'footer', 'solution d\'affaires', 'plans et prix', 'medias',
            'memberships', 'adhésion', 'demarrer gr', 'demarrer votre groupe',
            'find your local', 'trouvez votre groupe', 'all rights reserved',
            'politique de confidentialite', 'conditions d\'utilisation',
            'start a gr group', 'start your own group', 'demarrer un nouveau',
            'gr group', 'gr groups', 'commencer un groupe', 'joindre gr',
            'join now', 'en savoir plus', 'learn more', 'click here',
            'cliquez ici', 'inscription gratuite', 'free registration'
        ]
        if any(word in text_lower for word in skip_words):
            return False

        # Mots requis (doit contenir au moins un)
        required_words = [
            'groupe', 'group', 'chapter', 'meeting', 'reunion', 'rencontre',
            'zoom', 'presentiel', 'virtuel', 'virtual',
            'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
            'janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin',
            'juillet', 'aout', 'septembre', 'octobre', 'novembre', 'decembre',
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december',
            'am', 'pm', 'h00', ':00', ':30'
        ]
        if not any(word in text_lower for word in required_words):
            return False

        return True

    def _parse_text_to_event(self, text: str) -> Optional[Event]:
        """Parse du texte brut en evenement"""
        if not text or len(text) < 10:
            return None

        text_lower = text.lower()

        # Double verification
        if not self._is_valid_event_text(text):
            return None

        # Determiner le format
        is_zoom = any(x in text_lower for x in ['zoom', 'virtual', 'virtuel', 'online', 'en ligne'])
        format_type = "Zoom" if is_zoom else "Presentiel"

        # Determiner le type
        event_type = "Reunion"
        if any(x in text_lower for x in ['porte-ouverte', 'portes ouvertes', 'open house', 'guest day']):
            event_type = "Porte-ouverte"
        elif any(x in text_lower for x in ['formation', 'training', 'workshop', 'atelier']):
            event_type = "Formation"
        elif any(x in text_lower for x in ['conference', 'conférence', 'summit', 'sommet']):
            event_type = "Conference"

        # Extraire la date
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}\s+(?:jan|fév|feb|mar|avr|apr|mai|may|jun|jul|aoû|aug|sep|oct|nov|déc|dec)\w*\.?\s+\d{4})',
            r'((?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+\d{1,2})',
        ]

        date_str = "Date a confirmer"
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                break

        # Extraire l'heure
        time_pattern = r'(\d{1,2}[h:]\d{2}(?:\s*(?:am|pm))?)'
        time_match = re.search(time_pattern, text, re.IGNORECASE)
        time_str = time_match.group(1) if time_match else "Heure a confirmer"

        # Extraire le nom du groupe
        group_pattern = r'(?:groupe?|chapter|club)\s*:?\s*([A-Za-zÀ-ÿ\s\-]+\d*)'
        group_match = re.search(group_pattern, text, re.IGNORECASE)
        group = group_match.group(1).strip()[:30] if group_match else "Non specifie"

        # Nom de l'evenement (premiere ligne significative)
        lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 5]
        name = lines[0][:50] if lines else "Evenement GR"

        # Localisation
        location = None
        if not is_zoom:
            loc_pattern = r'(?:lieu|location|adresse|address)\s*:?\s*([^\n]+)'
            loc_match = re.search(loc_pattern, text, re.IGNORECASE)
            if loc_match:
                location = loc_match.group(1).strip()[:50]

        return Event(
            name=name,
            group=group,
            date=date_str,
            time=time_str,
            format=format_type,
            location=location,
            event_type=event_type,
            registration_url=None
        )

    def score_event(self, event: Event) -> int:
        """Calcule le score de pertinence d'un evenement (1-5)"""
        score = 1
        notes = []
        reasons = []  # Raisons detaillees pour le rapport

        # Priorite haute: Porte-ouverte
        if event.event_type == "Porte-ouverte":
            score += 2
            notes.append("Activite porte-ouverte")
            reasons.append("Les portes ouvertes sont ideales pour elargir votre reseau et inviter des prospects")

        # Votre groupe
        event_name_lower = event.name.lower()
        if 'vaudreuil' in event.group.lower() or 'vaudreuil' in event_name_lower:
            score += 2
            notes.append("Votre groupe (Vaudreuil 1)")
            reasons.append("Evenement de votre propre groupe - presence recommandee en tant que secretaire-tresorier")

        # Zoom = toujours accessible
        if event.format == "Zoom":
            score += 1
            notes.append("Accessible en Zoom")
            reasons.append("Format virtuel - participez depuis n'importe ou sans deplacement")

        # Presentiel dans zone acceptable
        elif event.location:
            loc_lower = event.location.lower()
            if any(zone in loc_lower for zone in ZONES_ACCEPTEES):
                score += 1
                notes.append("Proche de Montreal")
                reasons.append("Lieu accessible dans la region de Montreal")
            else:
                score -= 1
                notes.append("Eloigne geographiquement")
        else:
            # Verifier le nom pour la localisation
            if any(zone in event_name_lower for zone in ['brossard', 'longueuil', 'laval', 'montreal', 'montréal']):
                score += 1
                notes.append("Region Montreal")
                reasons.append("Evenement dans la grande region de Montreal - facilement accessible")

        # Formations et conferences
        if event.event_type in ["Formation", "Conference"]:
            score += 1
            notes.append("Opportunite d'apprentissage")
            reasons.append("Formation ou conference - excellent pour developper vos competences en reseautage")

        # Bonus pour certains mots-cles
        if 'elite' in event_name_lower or 'élite' in event_name_lower:
            reasons.append("Groupe Elite - reseautage de haut niveau avec entrepreneurs etablis")
        if 'b2b' in event_name_lower:
            reasons.append("Evenement B2B - ideal pour les contacts professionnels inter-entreprises")
        if '5 a 7' in event_name_lower or '5 à 7' in event_name_lower or '5@7' in event_name_lower:
            reasons.append("Format 5 a 7 - ambiance decontractee propice aux echanges")
        if 'lancement' in event_name_lower:
            reasons.append("Lancement de groupe - opportunite de rejoindre des le debut")

        # Limiter a 5
        score = max(1, min(5, score))
        event.score = score
        event.notes = " | ".join(notes) if notes else ""
        event.reasons = reasons  # Stocker les raisons pour le rapport

        return score

    def generate_report(self, events: List[Event]) -> str:
        """Genere le rapport Markdown"""
        now = datetime.now()

        # Scorer tous les evenements
        for event in events:
            self.score_event(event)

        # Trier par score puis date
        events.sort(key=lambda e: (-e.score, e.date))

        # Separer recommandes (score >= 3) et autres
        recommended = [e for e in events if e.score >= 3]
        others = [e for e in events if e.score < 3]

        # Utiliser des caracteres ASCII pour compatibilite Windows
        def stars(n):
            return "[" + "*" * n + "-" * (5-n) + "]"

        report = f"""# Rapport Hebdomadaire GR International
**Date du rapport**: {now.strftime('%Y-%m-%d %H:%M')}
**Periode analysee**: Prochaines 2 semaines
**Authentifie**: {"Oui" if self.authenticated else "Non (mode public)"}

---

## Resume Executif

- **Evenements trouves**: {len(events)}
- **Evenements recommandes**: {len(recommended)}
- **Prochaine action**: {"Voir les evenements recommandes ci-dessous" if recommended else "Aucun evenement prioritaire cette semaine"}

---

## Evenements Recommandes

"""

        if recommended:
            for i, event in enumerate(recommended, 1):
                # Construire la section "Pourquoi y participer"
                reasons_text = ""
                if hasattr(event, 'reasons') and event.reasons:
                    reasons_text = "\n".join([f"  - {r}" for r in event.reasons])
                else:
                    reasons_text = "  - Evenement pertinent pour votre reseautage"

                # Determiner l'urgence basee sur la date
                urgency = ""
                date_lower = event.date.lower()
                if 'janvier' in date_lower or 'january' in date_lower:
                    if any(str(d) in date_lower for d in range(1, 15)):
                        urgency = ">> TRES PROCHE - Inscription rapide recommandee <<"
                    else:
                        urgency = "> Ce mois-ci <"
                elif 'fevrier' in date_lower or 'february' in date_lower:
                    urgency = "Prochain mois"

                report += f"""### {i}. {event.name}

**Priorite**: {stars(event.score)} {"HAUTE PRIORITE" if event.score >= 4 else "RECOMMANDE"}
{urgency}

| Detail | Information |
|--------|-------------|
| **Date** | {event.date} |
| **Heure** | {event.time} |
| **Format** | {event.format} {"(aucun deplacement requis)" if event.format == "Zoom" else ""} |
| **Lieu** | {event.location or "Voir details sur le site"} |
| **Type d'evenement** | {event.event_type} |
| **Groupe organisateur** | {event.group} |
| **Inscription** | {event.registration_url or "https://www.grinternational.ca/events/"} |

**Pourquoi y participer:**
{reasons_text}

**Action suggeree**: {"S'inscrire rapidement - places limitees pour les portes ouvertes" if event.event_type == "Porte-ouverte" else "Ajouter a votre calendrier et confirmer votre presence"}

---

"""
        else:
            report += "*Aucun evenement hautement recommande cette semaine.*\n\n---\n\n"

        # Section resume des actions
        if recommended:
            report += """## Actions Recommandees Cette Semaine

"""
            zoom_events = [e for e in recommended if e.format == "Zoom"]
            presentiel_events = [e for e in recommended if e.format == "Presentiel"]

            if zoom_events:
                report += f"### Evenements Zoom ({len(zoom_events)})\n"
                report += "Faciles a integrer - aucun deplacement requis:\n"
                for e in zoom_events[:5]:
                    report += f"- **{e.date}**: {e.name[:40]}\n"
                report += "\n"

            if presentiel_events:
                report += f"### Evenements Presentiels ({len(presentiel_events)})\n"
                report += "Opportunites de reseautage en personne:\n"
                for e in presentiel_events[:5]:
                    report += f"- **{e.date}**: {e.name[:40]}\n"
                report += "\n"

            report += "---\n\n"

        report += "## Autres Evenements\n\n"

        if others:
            report += "| Evenement | Groupe | Date | Format | Score |\n"
            report += "|-----------|--------|------|--------|-------|\n"
            for event in others[:10]:  # Limiter a 10
                report += f"| {event.name[:30]} | {event.group[:20]} | {event.date} | {event.format} | {stars(event.score)} |\n"
            if len(others) > 10:
                report += f"\n*... et {len(others) - 10} autres evenements*\n"
        else:
            report += "*Aucun autre evenement.*\n"

        report += f"""

---

## Rappel - Criteres de Selection

Les evenements sont evalues selon vos preferences:
- **Portes ouvertes**: Priorite maximale (ideal pour inviter des prospects)
- **Votre groupe (Vaudreuil 1)**: Presence attendue en tant que secretaire-tresorier
- **Evenements Zoom**: Toujours accessibles, flexibilite maximale
- **Region Montreal**: Presentiels dans un rayon de ~60km

## Liens Utiles

- Site GR International: https://www.grinternational.ca
- Page des evenements: https://www.grinternational.ca/events/
- Horaires des reunions: https://www.grinternational.ca/schedule/

---

*Rapport genere automatiquement le {now.strftime('%Y-%m-%d a %H:%M')}*
*Prochain scan prevu: Vendredi prochain a 7h00*
"""

        return report

    def run(self, headless: bool = True) -> str:
        """Execute le scraping complet et retourne le rapport"""
        self.headless = headless

        print("=" * 60)
        print("[SCAN] Demarrage de l'exploration GR International...")
        print("=" * 60)

        try:
            # Demarrer le navigateur
            self.start_browser()

            # Authentification
            if not self.authenticate():
                print("[WARN] Continuant sans authentification...")

            # Recuperer les evenements
            # Utiliser la nouvelle methode qui explore /evenements/ en detail
            evenements_events = self.fetch_evenements_page()

            # Aussi recuperer les evenements du schedule (optionnel)
            schedule_events = self.fetch_schedule_events()

            # Combiner les resultats
            special_events = evenements_events

            # Combiner et dedupliquer
            all_events = schedule_events + special_events
            seen = set()
            unique_events = []
            for event in all_events:
                key = (event.name.lower()[:30], event.date)
                if key not in seen:
                    seen.add(key)
                    unique_events.append(event)

            print(f"\n[TOTAL] {len(unique_events)} evenements uniques")

            # Generer le rapport
            report = self.generate_report(unique_events)

            # Sauvegarder
            tmp_dir = Path(__file__).parent.parent / ".tmp"
            tmp_dir.mkdir(exist_ok=True)

            report_path = tmp_dir / f"gr_events_report_{datetime.now().strftime('%Y-%m-%d')}.md"
            report_path.write_text(report, encoding='utf-8')
            print(f"\n[SAVED] Rapport sauvegarde: {report_path}")

            # Sauvegarder JSON
            json_path = tmp_dir / f"gr_events_{datetime.now().strftime('%Y-%m-%d')}.json"
            json_path.write_text(
                json.dumps([e.to_dict() for e in unique_events], indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            print(f"[SAVED] Donnees JSON: {json_path}")

            return report

        finally:
            self.close_browser()


def main():
    """Point d'entree principal"""
    # Mode headless par defaut, sauf si --visible est passe
    headless = '--visible' not in sys.argv

    scraper = GRInternationalScraper()
    report = scraper.run(headless=headless)

    print("\n" + "=" * 60)
    print("RAPPORT:")
    print("=" * 60)
    print(report)


if __name__ == "__main__":
    main()
