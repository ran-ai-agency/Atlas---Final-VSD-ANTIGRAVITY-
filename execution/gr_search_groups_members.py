#!/usr/bin/env python3
"""
GR International - Extracteur de Membres via Recherche
Utilise le champ de recherche avec autocomplétion pour accéder à chaque groupe
et extraire tous les membres avec leurs détails complets
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://www.grinternational.ca"


class GRSearchMembersExtractor:
    """Extracteur via le champ de recherche du site"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.page = None
        self.authenticated = False
        self.all_members = []
        self.groups_processed = []

    def start_browser(self):
        """Démarre le navigateur Playwright"""
        from playwright.sync_api import sync_playwright

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = self.context.new_page()
        print("[OK] Navigateur démarré")

    def close_browser(self):
        """Ferme le navigateur"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
        print("[OK] Navigateur fermé")

    def authenticate(self) -> bool:
        """Authentification au portail membres"""
        member_url = os.getenv('GR_MEMBER_URL', '')
        email = os.getenv('GR_EMAIL')
        password = os.getenv('GR_PASSWORD')

        if member_url:
            try:
                print("[AUTH] Connexion via lien membre...")
                self.page.goto(member_url, wait_until='load', timeout=60000)
                self.page.wait_for_timeout(5000)

                content = self.page.content().lower()
                if 'member' in content or 'membre' in content:
                    self.authenticated = True
                    print("[OK] Authentification réussie")
                    return True
            except Exception as e:
                print(f"[WARN] Erreur token: {e}")

        if not email or not password:
            print("[WARN] Identifiants non configurés")
            return False

        try:
            print(f"[AUTH] Connexion avec {email}...")
            self.page.goto(f"{BASE_URL}/membres/", wait_until='load', timeout=60000)
            self.page.wait_for_timeout(3000)

            # Remplir le formulaire de connexion
            email_selectors = ['input[name="email"]', 'input[type="email"]', '#email']
            for selector in email_selectors:
                try:
                    if self.page.locator(selector).count() > 0:
                        self.page.locator(selector).first.fill(email)
                        break
                except:
                    continue

            password_selectors = ['input[name="password"]', 'input[type="password"]', '#password']
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
                'button:has-text("Connexion")'
            ]
            for selector in submit_selectors:
                try:
                    if self.page.locator(selector).count() > 0:
                        self.page.locator(selector).first.click()
                        break
                except:
                    continue

            self.page.wait_for_timeout(3000)

            if 'logout' in self.page.content().lower():
                self.authenticated = True
                print("[OK] Authentification réussie")
                return True

            print("[INFO] Mode public")
            return True

        except Exception as e:
            print(f"[ERROR] Erreur authentification: {e}")
            return False

    def search_and_extract_group_members(self, group_name: str, group_num: str) -> Dict:
        """
        Utilise le champ de recherche pour accéder au groupe et extraire les membres
        """
        tmp_dir = Path(__file__).parent.parent / ".tmp"
        tmp_dir.mkdir(exist_ok=True)

        # Nom sécurisé pour les fichiers
        safe_name = re.sub(r'[^a-z0-9_]', '_', group_name[:50].lower())

        group_data = {
            'group_num': group_num,
            'group_name': group_name,
            'members': [],
            'extraction_date': datetime.now().isoformat(),
            'extraction_success': False
        }

        try:
            # Rester sur la page membre (déjà authentifié)
            # Chercher la section "Recherche" ou "Search" sur le portail membre
            print(f"\n   -> Recherche de la section recherche sur le portail membre...")
            current_url = self.page.url
            print(f"   -> URL actuelle: {current_url}")

            # Prendre un screenshot pour voir où nous sommes
            self.page.screenshot(path=str(tmp_dir / f"portal_member_{safe_name}.png"))

            # Chercher un lien ou menu "Recherche" / "Search"
            search_links = [
                'a:has-text("Recherche")',
                'a:has-text("Search")',
                'a:has-text("Groupes")',
                'a:has-text("Groups")',
                'a[href*="search"]',
                'a[href*="recherche"]'
            ]

            search_found = False
            for selector in search_links:
                try:
                    if self.page.locator(selector).count() > 0:
                        print(f"   -> Lien recherche trouvé: {selector}")
                        self.page.locator(selector).first.click()
                        self.page.wait_for_load_state('networkidle', timeout=10000)
                        search_found = True
                        break
                except:
                    continue

            if not search_found:
                print("   -> Pas de lien recherche trouvé, reste sur la page actuelle")

            self.page.wait_for_timeout(3000)

            # Trouver le champ de recherche avec autocomplétion
            # Les IDs possibles: gsearch, gsearchAccueil, gsearch_num, etc.
            search_field_selectors = [
                '#gsearchAccueil',
                '#gsearch',
                'input[id*="gsearch"]',
                'input[name*="search"]',
                'input[placeholder*="Search"]',
                'input[placeholder*="Recherch"]'
            ]

            search_field = None
            search_field_selector = None
            for selector in search_field_selectors:
                try:
                    if self.page.locator(selector).count() > 0:
                        search_field = self.page.locator(selector).first
                        search_field_selector = selector
                        print(f"   -> Champ de recherche trouvé: {selector}")
                        break
                except:
                    continue

            if not search_field:
                print("   -> [ERREUR] Champ de recherche non trouvé")
                return group_data

            # Sauvegarder screenshot avant recherche
            tmp_dir = Path(__file__).parent.parent / ".tmp"
            tmp_dir.mkdir(exist_ok=True)
            safe_name = re.sub(r'[^a-z0-9]+', '_', group_name.lower())[:30]
            self.page.screenshot(path=str(tmp_dir / f"search_before_{safe_name}.png"))

            # Nettoyer et préparer le terme de recherche
            # Prendre les premiers mots du nom du groupe
            search_terms = group_name.split('•')[0].strip()  # Avant le •
            search_terms = search_terms.split(' - ')[0].strip()  # Avant le -

            print(f"   -> Recherche: '{search_terms}'")

            # Attendre que le champ soit vraiment visible et cliquable
            try:
                self.page.wait_for_selector(search_field_selector, state='visible', timeout=10000)
                self.page.wait_for_timeout(1000)
            except:
                print("   -> Timeout waiting for field, continuing anyway...")

            # Taper progressivement dans le champ de recherche
            # L'autocomplétion se déclenche après 2 caractères
            try:
                search_field.click(timeout=10000)
            except:
                # Si le click échoue, essayer de focus directement
                print("   -> Click timeout, trying focus...")
                search_field.focus()
            self.page.wait_for_timeout(500)

            # Taper lettre par lettre pour déclencher l'autocomplétion
            for char in search_terms:
                search_field.type(char, delay=100)
                self.page.wait_for_timeout(150)

            # Attendre que l'autocomplétion apparaisse (le dropdown se remplit)
            self.page.wait_for_timeout(2000)

            # Screenshot avec dropdown d'autocomplétion
            self.page.screenshot(path=str(tmp_dir / f"search_autocomplete_{safe_name}.png"))

            # Approche clavier: descendre dans le menu et appuyer sur Enter
            # C'est plus fiable que de cliquer sur les éléments du dropdown jQuery UI
            print("   -> Navigation clavier dans le dropdown...")

            # Appuyer sur ArrowDown pour sélectionner le premier élément
            search_field.press('ArrowDown')
            self.page.wait_for_timeout(300)

            # Appuyer sur Enter pour sélectionner et soumettre
            print("   -> Sélection et soumission...")
            search_field.press('Enter')

            # Attendre que la page charge les résultats
            print("   -> Attente du chargement des résultats...")
            self.page.wait_for_load_state('networkidle', timeout=15000)
            self.page.wait_for_timeout(3000)

            # Scroller vers le bas pour voir la section des membres
            print("   -> Scroll vers la section des membres...")
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(2000)

            # Screenshot après scroll
            self.page.screenshot(path=str(tmp_dir / f"search_result_scrolled_{safe_name}.png"))

            # La liste des membres devrait être en bas de la page
            print("   -> Recherche des widgets de membres...")

            # Sauvegarder le HTML pour analyse
            (tmp_dir / f"group_page_{safe_name}.html").write_text(
                self.page.content(),
                encoding='utf-8'
            )

            # Extraire les membres depuis le dropdown <select>
            members = self._extract_members_from_select_dropdown(group_name, group_num)

            if members:
                print(f"   -> {len(members)} membres trouvés")
                group_data['members'] = members
                group_data['extraction_success'] = True
                self.all_members.extend(members)
            else:
                print("   -> Aucun membre trouvé")

        except Exception as e:
            print(f"   -> [ERREUR] {str(e)[:100]}")
            group_data['error'] = str(e)

        return group_data

    def _extract_members_from_page(self, group_name: str, group_num: str) -> List[Dict]:
        """Extrait les membres de la page courante"""
        members = []

        try:
            page_text = self.page.inner_text('body')

            # Chercher des sections/éléments de membres
            # Patterns communs: liste de membres, tableau, cartes
            member_selectors = [
                'div.member',
                'div.member-card',
                'div[class*="member"]',
                'tr.member',
                'li.member',
                'div.contact',
                'div[class*="contact"]',
                'a[href*="member"]',
                'a[href*="membre"]'
            ]

            all_member_elements = []
            for selector in member_selectors:
                try:
                    elements = self.page.locator(selector).all()
                    if elements:
                        all_member_elements.extend(elements)
                        print(f"      -> {len(elements)} éléments trouvés ({selector})")
                except:
                    continue

            # Si on trouve des éléments structurés
            if all_member_elements:
                for elem in all_member_elements:
                    try:
                        member_data = self._extract_member_details_from_element(
                            elem, group_name, group_num
                        )
                        if member_data and 'full_name' in member_data:
                            members.append(member_data)
                    except:
                        continue

            # Fallback: chercher des liens vers des profils de membres
            if not members:
                print("      -> Recherche de liens vers profils membres...")
                member_links = self.page.locator('a[href*="membre"], a[href*="member"]').all()

                for link in member_links[:50]:  # Limiter à 50 pour ne pas surcharger
                    try:
                        link_text = link.inner_text().strip()
                        href = link.get_attribute('href')

                        # Si le texte ressemble à un nom (2-4 mots)
                        if len(link_text.split()) >= 2 and len(link_text) < 100:
                            print(f"         -> Exploration: {link_text[:40]}")

                            # Cliquer sur le lien pour voir les détails
                            full_url = href if href.startswith('http') else BASE_URL + href

                            member_data = self._visit_member_profile(
                                full_url, link_text, group_name, group_num
                            )

                            if member_data:
                                members.append(member_data)

                            # Retourner à la page du groupe
                            self.page.go_back(wait_until='load', timeout=10000)
                            self.page.wait_for_timeout(1000)

                    except Exception as e:
                        print(f"         -> Erreur lien: {str(e)[:30]}")
                        continue

        except Exception as e:
            print(f"      -> Erreur extraction: {str(e)[:50]}")

        return members

    def _extract_member_details_from_element(self, elem, group_name: str, group_num: str) -> Optional[Dict]:
        """Extrait les détails d'un membre depuis un élément HTML"""
        try:
            text = elem.inner_text().strip()
            if len(text) < 5:
                return None

            member_data = {
                'group_num': group_num,
                'group_name': group_name,
                'extracted_at': datetime.now().isoformat()
            }

            # Nom complet (chercher dans h1-h6, strong, b, ou première ligne)
            name_selectors = ['h1', 'h2', 'h3', 'h4', 'strong', 'b', '.name']
            for sel in name_selectors:
                try:
                    name_elem = elem.locator(sel).first
                    if name_elem.count() > 0:
                        full_name = name_elem.inner_text().strip()
                        if 2 < len(full_name) < 100 and not any(skip in full_name.lower() for skip in ['contact', 'email', 'phone']):
                            member_data['full_name'] = full_name
                            parts = full_name.split()
                            if len(parts) >= 2:
                                member_data['first_name'] = parts[0]
                                member_data['last_name'] = ' '.join(parts[1:])
                            break
                except:
                    continue

            # Si pas de nom trouvé, extraire de la première ligne
            if 'full_name' not in member_data:
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                if lines:
                    potential_name = lines[0]
                    if 2 < len(potential_name) < 100:
                        member_data['full_name'] = potential_name
                        parts = potential_name.split()
                        if len(parts) >= 2:
                            member_data['first_name'] = parts[0]
                            member_data['last_name'] = ' '.join(parts[1:])

            # Entreprise
            company_patterns = [
                r'(?:company|entreprise|compagnie)[:\s]+([^\n]+)',
                r'([A-Z][A-Za-z\s&\-]+(?:Inc|Ltd|LLC|SARL|Corp|Ltée)\.?)'
            ]
            for pattern in company_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    member_data['company'] = match.group(1).strip()[:100]
                    break

            # Titre
            title_patterns = [
                r'(?:title|titre|position|poste)[:\s]+([^\n]+)',
                r'(CEO|President|Président|Directeur|Manager|Consultant|Founder|Owner|Partner|Vice[\s-]President)'
            ]
            for pattern in title_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    member_data['title'] = match.group(1).strip()[:100]
                    break

            # Catégorie
            category_match = re.search(r'(?:category|catégorie|industrie|industry)[:\s]+([^\n]+)', text, re.IGNORECASE)
            if category_match:
                member_data['category'] = category_match.group(1).strip()[:100]

            # Téléphone
            phone_match = re.search(r'(\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})', text)
            if phone_match:
                member_data['phone'] = phone_match.group(1).strip()

            # Email
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            if email_match:
                member_data['email'] = email_match.group(1).strip()

            # LinkedIn
            try:
                linkedin = elem.locator('a[href*="linkedin"]').first
                if linkedin.count() > 0:
                    member_data['linkedin'] = linkedin.get_attribute('href')
            except:
                pass

            # Site web
            try:
                web_links = elem.locator('a[href^="http"]').all()
                for link in web_links:
                    href = link.get_attribute('href')
                    if href and 'linkedin' not in href.lower() and 'grinternational' not in href.lower():
                        member_data['website'] = href
                        break
            except:
                pass

            # Rôle dans le groupe
            role_match = re.search(
                r'(President|Vice[\s-]President|Secrétaire|Trésorier|Secretary|Treasurer|Président|Vice-Président|Secrétaire-Trésorier)',
                text,
                re.IGNORECASE
            )
            if role_match:
                member_data['group_role'] = role_match.group(1).strip()

            # Générer ID unique
            if 'full_name' in member_data:
                name = member_data['full_name']
                clean_name = re.sub(r'[^a-z0-9]+', '-', name.lower())
                member_data['member_id'] = f"gr{group_num}_{clean_name}"[:80]
                return member_data

        except:
            pass

        return None

    def _visit_member_profile(self, url: str, name_hint: str, group_name: str, group_num: str) -> Optional[Dict]:
        """Visite le profil d'un membre pour extraire tous les détails"""
        try:
            self.page.goto(url, wait_until='load', timeout=20000)
            self.page.wait_for_timeout(2000)

            page_text = self.page.inner_text('body')

            # Vérifier que ce n'est pas une page 404
            if '404' in page_text or 'not found' in page_text.lower():
                return None

            member_data = {
                'group_num': group_num,
                'group_name': group_name,
                'full_name': name_hint,
                'profile_url': url,
                'extracted_at': datetime.now().isoformat()
            }

            # Séparer prénom/nom
            parts = name_hint.split()
            if len(parts) >= 2:
                member_data['first_name'] = parts[0]
                member_data['last_name'] = ' '.join(parts[1:])

            # Extraire toutes les informations disponibles sur la page
            # Entreprise
            company_patterns = [
                r'(?:company|entreprise|compagnie)[:\s]+([^\n]+)',
                r'(?:works at|travaille chez)[:\s]+([^\n]+)',
                r'([A-Z][A-Za-z\s&\-]+(?:Inc|Ltd|LLC|SARL|Corp|Ltée)\.?)'
            ]
            for pattern in company_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    member_data['company'] = match.group(1).strip()[:100]
                    break

            # Titre
            title_patterns = [
                r'(?:title|titre|position|poste)[:\s]+([^\n]+)',
                r'(CEO|President|Président|Directeur|Director|Manager|Consultant|Founder|Owner|Partner|Vice[\s-]President)'
            ]
            for pattern in title_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    member_data['title'] = match.group(1).strip()[:100]
                    break

            # Catégorie/Industrie
            category_patterns = [
                r'(?:category|catégorie|industrie|industry|sector|secteur)[:\s]+([^\n]+)',
            ]
            for pattern in category_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    member_data['category'] = match.group(1).strip()[:100]
                    break

            # Téléphone
            phone_match = re.search(r'(\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})', page_text)
            if phone_match:
                member_data['phone'] = phone_match.group(1).strip()

            # Email
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', page_text)
            if email_match:
                member_data['email'] = email_match.group(1).strip()

            # LinkedIn
            try:
                linkedin = self.page.locator('a[href*="linkedin"]').first
                if linkedin.count() > 0:
                    member_data['linkedin'] = linkedin.get_attribute('href')
            except:
                pass

            # Site web
            try:
                web_links = self.page.locator('a[href^="http"]').all()
                for link in web_links:
                    href = link.get_attribute('href')
                    if href and 'linkedin' not in href.lower() and 'grinternational' not in href.lower():
                        member_data['website'] = href
                        break
            except:
                pass

            # Rôle
            role_match = re.search(
                r'(President|Vice[\s-]President|Secrétaire|Trésorier|Secretary|Treasurer|Président|Vice-Président)',
                page_text,
                re.IGNORECASE
            )
            if role_match:
                member_data['group_role'] = role_match.group(1).strip()

            # Bio/Description
            bio_patterns = [
                r'(?:about|bio|description|présentation)[:\s]+([^\n]{50,500})',
            ]
            for pattern in bio_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    member_data['bio'] = match.group(1).strip()[:500]
                    break

            # Générer ID
            clean_name = re.sub(r'[^a-z0-9]+', '-', name_hint.lower())
            member_data['member_id'] = f"gr{group_num}_{clean_name}"[:80]

            return member_data

        except Exception as e:
            print(f"            -> Erreur profil: {str(e)[:30]}")
            return None

    def _extract_members_from_select_dropdown(self, group_name: str, group_num: str) -> List[Dict]:
        """
        Extrait les membres depuis le dropdown <select id="vis_refere_par_[GROUP_NUM]">
        """
        members = []

        try:
            # Le select a un ID de la forme: vis_refere_par_91, vis_refere_par_13, etc.
            select_id = f"vis_refere_par_{group_num}"
            print(f"      -> Recherche du select #{select_id}...")

            # Vérifier si le select existe
            select_element = self.page.locator(f"#{select_id}")
            if select_element.count() == 0:
                # Essayer d'autres patterns
                select_element = self.page.locator(f"select[name='refere_par']")
                if select_element.count() == 0:
                    print(f"      -> Select non trouvé")
                    return members

            print(f"      -> Select trouvé!")

            # Extraire toutes les options dans l'optgroup "Membres"
            options = select_element.locator("optgroup[label='Membres'] option, optgroup[label='Members'] option").all()

            if not options:
                # Fallback: toutes les options sauf les premières
                all_options = select_element.locator("option").all()
                options = [opt for opt in all_options if opt.get_attribute('value') not in ['', '0', '99999999']]

            print(f"      -> {len(options)} membres trouvés dans le dropdown")

            for option in options:
                try:
                    member_id_value = option.get_attribute('value')
                    member_full_name = option.inner_text().strip()

                    if not member_full_name or member_full_name in ['---', 'Autre', 'GR', 'Other']:
                        continue

                    # Parser le nom (format: "Nom, Prénom" ou "Prénom Nom")
                    if ',' in member_full_name:
                        # Format: "Arpin, Jean-François"
                        parts = member_full_name.split(',')
                        last_name = parts[0].strip()
                        first_name = parts[1].strip() if len(parts) > 1 else ''
                        full_name = f"{first_name} {last_name}".strip()
                    else:
                        # Format: "Jean-François Arpin"
                        parts = member_full_name.split()
                        first_name = parts[0] if parts else ''
                        last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
                        full_name = member_full_name

                    member_data = {
                        'group_num': group_num,
                        'group_name': group_name,
                        'member_id_gr': member_id_value,
                        'full_name': full_name,
                        'first_name': first_name,
                        'last_name': last_name,
                        'extracted_at': datetime.now().isoformat()
                    }

                    # Générer un ID unique
                    safe_name = re.sub(r'[^a-z0-9]', '-', full_name.lower())[:50]
                    member_data['member_id'] = f"gr{group_num}_{safe_name}"

                    members.append(member_data)

                    print(f"         -> {full_name} (ID GR: {member_id_value})")

                except Exception as e:
                    print(f"         -> Erreur option: {str(e)[:50]}")
                    continue

        except Exception as e:
            print(f"      -> Erreur extraction select: {str(e)[:100]}")

        return members

    def _extract_members_by_clicking_widgets(self, group_name: str, group_num: str, tmp_dir: Path) -> List[Dict]:
        """
        Trouve les widgets de membres en bas de la page et clique sur chacun pour obtenir les détails
        """
        members = []

        try:
            # Chercher les widgets/cartes de membres
            # Sélecteurs possibles pour les cartes de membres
            widget_selectors = [
                'div.member-card',
                'div.member-widget',
                'div[class*="member"]',
                'div.card',
                'article.member',
                '.member-list > div',
                '.members-section > div',
                'div[onclick*="member"]',
                'div[data-member-id]'
            ]

            member_widgets = []
            for selector in widget_selectors:
                try:
                    widgets = self.page.locator(selector).all()
                    if widgets:
                        print(f"      -> {len(widgets)} widgets trouvés ({selector})")
                        member_widgets = widgets
                        break
                except:
                    continue

            # Si pas de widgets spécifiques, chercher tous les divs cliquables en bas de page
            if not member_widgets:
                print("      -> Recherche générique de divs cliquables...")
                # Chercher dans la dernière moitié de la page
                all_divs = self.page.locator('div[class]').all()
                # Filtrer ceux qui ont un contenu text (nom, titre, etc.)
                for div in all_divs[-50:]:  # Les 50 derniers divs
                    try:
                        text = div.inner_text().strip()
                        # Si le div contient du texte qui ressemble à un nom (2+ mots, pas trop long)
                        words = text.split('\n')[0].split()
                        if 2 <= len(words) <= 5 and len(text) < 200:
                            member_widgets.append(div)
                    except:
                        continue

            print(f"      -> {len(member_widgets)} widgets de membres potentiels")

            # Cliquer sur chaque widget pour obtenir les détails
            for i, widget in enumerate(member_widgets[:30]):  # Limiter à 30 premiers membres
                try:
                    # Extraire un aperçu du nom depuis le widget
                    preview_text = widget.inner_text().strip()[:50]
                    print(f"         [{i+1}/{min(len(member_widgets), 30)}] Clic sur widget: {preview_text}")

                    # Scroller vers le widget
                    widget.scroll_into_view_if_needed()
                    self.page.wait_for_timeout(300)

                    # Prendre screenshot avant click
                    if i == 0:
                        self.page.screenshot(path=str(tmp_dir / f"before_click_widget_{group_num}.png"))

                    # Cliquer sur le widget
                    widget.click()
                    self.page.wait_for_timeout(2000)

                    # Prendre screenshot après click (modal ou page de détails)
                    if i == 0:
                        self.page.screenshot(path=str(tmp_dir / f"after_click_widget_{group_num}.png"))

                    # Extraire les données depuis la modal/page de détails
                    member_data = self._extract_member_from_modal_or_page(group_name, group_num)

                    if member_data:
                        members.append(member_data)
                        print(f"            -> Extrait: {member_data.get('full_name', 'N/A')}")

                    # Fermer la modal si elle existe
                    close_selectors = [
                        'button.close',
                        'button[aria-label="Close"]',
                        '.modal-close',
                        '[data-dismiss="modal"]',
                        '.close-button'
                    ]
                    for close_sel in close_selectors:
                        try:
                            if self.page.locator(close_sel).count() > 0:
                                self.page.locator(close_sel).first.click()
                                self.page.wait_for_timeout(500)
                                break
                        except:
                            continue

                    # Ou revenir en arrière si nouvelle page
                    current_url = self.page.url
                    if 'member' in current_url or 'profile' in current_url:
                        self.page.go_back()
                        self.page.wait_for_timeout(1000)

                except Exception as e:
                    print(f"            -> Erreur widget: {str(e)[:50]}")
                    continue

        except Exception as e:
            print(f"      -> Erreur extraction widgets: {str(e)[:100]}")

        return members

    def _extract_member_from_modal_or_page(self, group_name: str, group_num: str) -> Optional[Dict]:
        """Extrait les données d'un membre depuis une modal ou une page de détails"""
        try:
            # Attendre que le contenu charge
            self.page.wait_for_load_state('networkidle', timeout=5000)

            page_text = self.page.inner_text('body')

            member_data = {
                'group_num': group_num,
                'group_name': group_name,
                'extracted_at': datetime.now().isoformat()
            }

            # Nom complet
            name_patterns = [
                r'^([A-Z][a-zà-ÿ]+(?:\s+[A-Z][a-zà-ÿ]+)+)',  # Nom avec capitales
                r'<h[1-4][^>]*>([^<]+)</h[1-4]>',  # Dans un header
            ]
            for pattern in name_patterns:
                match = re.search(pattern, page_text, re.MULTILINE | re.IGNORECASE)
                if match:
                    full_name = match.group(1).strip()
                    if len(full_name.split()) >= 2:
                        member_data['full_name'] = full_name
                        parts = full_name.split()
                        member_data['first_name'] = parts[0]
                        member_data['last_name'] = ' '.join(parts[1:])
                        break

            # Entreprise
            company_match = re.search(
                r'(?:Company|Entreprise|Compagnie|Organization)[:\s]*([^\n]+)',
                page_text,
                re.IGNORECASE
            )
            if company_match:
                member_data['company'] = company_match.group(1).strip()[:100]

            # Titre/Poste
            title_match = re.search(
                r'(?:Title|Titre|Position|Poste|Role|Rôle)[:\s]*([^\n]+)',
                page_text,
                re.IGNORECASE
            )
            if title_match:
                member_data['title'] = title_match.group(1).strip()[:100]

            # Email
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', page_text)
            if email_match:
                member_data['email'] = email_match.group(1)

            # Téléphone
            phone_match = re.search(
                r'(?:Tel|Phone|Tél|Téléphone)[:\s]*([\d\s\(\)\-\.ext]+)',
                page_text,
                re.IGNORECASE
            )
            if phone_match:
                member_data['phone'] = phone_match.group(1).strip()

            # LinkedIn
            try:
                linkedin_link = self.page.locator('a[href*="linkedin.com"]').first
                if linkedin_link.count() > 0:
                    member_data['linkedin'] = linkedin_link.get_attribute('href')
            except:
                pass

            # ID membre
            if 'full_name' in member_data:
                safe_name = re.sub(r'[^a-z0-9]', '-', member_data['full_name'].lower())[:50]
                member_data['member_id'] = f"gr{group_num}_{safe_name}"
                return member_data

        except Exception as e:
            print(f"         -> Erreur extraction modal: {str(e)[:50]}")

        return None

    def run(self, groups_json_path: str, max_groups: int = None, start_from: int = 0):
        """Exécute l'extraction complète"""
        print("=" * 70)
        print("[EXTRACTION] Membres GR via Recherche + Autocomplétion")
        print("=" * 70)

        # Charger les groupes
        groups_file = Path(groups_json_path)
        if not groups_file.exists():
            print(f"[ERROR] Fichier {groups_file} non trouvé")
            return

        with open(groups_file, 'r', encoding='utf-8') as f:
            groups = json.load(f)

        print(f"[INFO] {len(groups)} groupes chargés")

        # Appliquer start_from et max_groups
        if start_from > 0:
            groups = groups[start_from:]
            print(f"[INFO] Démarrage depuis le groupe #{start_from}")

        if max_groups:
            groups = groups[:max_groups]
            print(f"[INFO] Limité à {max_groups} groupes")

        try:
            self.start_browser()

            # Authentification
            if not self.authenticate():
                print("[WARN] Continuant sans authentification...")

            # Traiter chaque groupe
            for i, group in enumerate(groups, start_from + 1):
                group_num = group.get('group_num')
                group_name = group.get('group_name', 'Unknown')

                print(f"\n{'='*70}")
                print(f"[{i}/{start_from + len(groups)}] {group_name}")
                print(f"{'='*70}")
                print(f"   ID: {group_num}")

                # Rechercher et extraire les membres
                group_data = self.search_and_extract_group_members(group_name, group_num)
                self.groups_processed.append(group_data)

                # Pause entre groupes
                self.page.wait_for_timeout(3000)

                # Sauvegarder progressivement tous les 5 groupes
                if i % 5 == 0:
                    self._save_progress()

            # Sauvegarder final
            self._save_final()

        finally:
            self.close_browser()

    def _save_progress(self):
        """Sauvegarde progressive des données"""
        tmp_dir = Path(__file__).parent.parent / ".tmp"
        tmp_dir.mkdir(exist_ok=True)

        # Sauvegarder les groupes traités
        progress_file = tmp_dir / "gr_extraction_progress.json"
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump({
                'groups_processed': self.groups_processed,
                'total_members': len(self.all_members),
                'last_update': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)

        print(f"\n   [SAVE] Progression sauvegardée: {len(self.groups_processed)} groupes, {len(self.all_members)} membres")

    def _save_final(self):
        """Sauvegarde finale de toutes les données"""
        tmp_dir = Path(__file__).parent.parent / ".tmp"
        tmp_dir.mkdir(exist_ok=True)

        # Membres complets
        members_file = tmp_dir / "gr_members_complete.json"
        with open(members_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_members, f, indent=2, ensure_ascii=False)

        # Groupes avec leurs membres
        groups_with_members_file = tmp_dir / "gr_groups_with_members.json"
        with open(groups_with_members_file, 'w', encoding='utf-8') as f:
            json.dump(self.groups_processed, f, indent=2, ensure_ascii=False)

        # Statistiques
        stats = {
            'total_groups': len(self.groups_processed),
            'total_members': len(self.all_members),
            'successful_groups': len([g for g in self.groups_processed if g.get('extraction_success')]),
            'extraction_date': datetime.now().isoformat()
        }

        stats_file = tmp_dir / "gr_extraction_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 70)
        print("RÉSUMÉ FINAL")
        print("=" * 70)
        print(f"Groupes traités: {stats['total_groups']}")
        print(f"Groupes réussis: {stats['successful_groups']}")
        print(f"Membres extraits: {stats['total_members']}")
        print(f"\nFichiers sauvegardés:")
        print(f"  - {members_file}")
        print(f"  - {groups_with_members_file}")
        print(f"  - {stats_file}")


def main():
    """Point d'entrée principal"""
    import sys

    headless = '--visible' not in sys.argv
    max_groups = None
    start_from = 0

    # Arguments
    for arg in sys.argv:
        if arg.startswith('--limit='):
            max_groups = int(arg.split('=')[1])
        elif arg.startswith('--start='):
            start_from = int(arg.split('=')[1])

    # Utiliser le fichier des groupes du Québec par défaut
    tmp_dir = Path(__file__).parent.parent / ".tmp"
    groups_file = tmp_dir / "gr_groups_quebec.json"

    # Ou tous les groupes si spécifié
    if '--all' in sys.argv:
        groups_file = tmp_dir / "gr_groups_from_api.json"

    if not groups_file.exists():
        print(f"[ERROR] Fichier {groups_file} non trouvé")
        print("Exécutez d'abord:")
        print("  1. python execution/gr_api_groups_extractor.py")
        print("  2. python execution/gr_filter_quebec_groups.py")
        return

    extractor = GRSearchMembersExtractor(headless=headless)
    extractor.run(str(groups_file), max_groups=max_groups, start_from=start_from)


if __name__ == "__main__":
    main()
