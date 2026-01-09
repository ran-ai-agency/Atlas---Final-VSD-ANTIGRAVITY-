#!/usr/bin/env python3
"""
GR International - Extracteur de Membres
Utilise la liste des groupes du Québec et extrait les membres de chaque groupe
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


class GRMembersExtractor:
    """Extracteur de membres GR International"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.page = None
        self.authenticated = False
        self.all_members = []

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

            # Remplir le formulaire
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

            # Soumettre
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

    def extract_members_from_group(self, group_num: str, group_name: str) -> List[Dict]:
        """Extrait les membres d'un groupe en naviguant vers sa page"""
        members = []

        # URLs possibles pour accéder à un groupe
        possible_urls = [
            f"{BASE_URL}/groupes/view.php?num={group_num}",
            f"{BASE_URL}/groupe?id={group_num}",
            f"{BASE_URL}/groups/{group_num}",
            f"{BASE_URL}/groupe/{group_num}",
        ]

        for url in possible_urls:
            try:
                self.page.goto(url, wait_until='load', timeout=30000)
                self.page.wait_for_timeout(3000)

                # Vérifier si la page a chargé correctement (pas 404)
                page_text = self.page.inner_text('body').lower()
                if '404' in page_text or 'not found' in page_text:
                    continue

                # Sauvegarder pour debug
                tmp_dir = Path(__file__).parent.parent / ".tmp"
                tmp_dir.mkdir(exist_ok=True)

                safe_name = re.sub(r'[^a-z0-9]+', '_', group_name.lower())[:30]
                self.page.screenshot(path=str(tmp_dir / f"group_{group_num}_{safe_name}.png"))

                # Chercher section membres/directory
                # Patterns courants: "Members", "Membres", "Directory", "Annuaire"
                member_section_selectors = [
                    'a:has-text("Members")', 'a:has-text("Membres")',
                    'a:has-text("Directory")', 'a:has-text("Annuaire")',
                    'a:has-text("Member List")', 'a:has-text("Liste des membres")'
                ]

                for selector in member_section_selectors:
                    try:
                        if self.page.locator(selector).count() > 0:
                            self.page.locator(selector).first.click()
                            self.page.wait_for_timeout(3000)
                            print(f"      -> Section membres trouvée")
                            break
                    except:
                        continue

                # Extraire les membres de la page
                members = self._extract_members_from_page(group_num, group_name)

                if members:
                    print(f"      -> {len(members)} membres trouvés")
                    return members

            except Exception as e:
                continue

        # Si aucune URL ne fonctionne, chercher les membres sur la page publique du groupe
        try:
            public_url = f"{BASE_URL}/groupes/public.php?num={group_num}"
            self.page.goto(public_url, wait_until='load', timeout=30000)
            self.page.wait_for_timeout(3000)

            members = self._extract_members_from_page(group_num, group_name)
            if members:
                print(f"      -> {len(members)} membres trouvés (page publique)")
                return members

        except:
            pass

        print(f"      -> Aucun membre trouvé")
        return []

    def _extract_members_from_page(self, group_num: str, group_name: str) -> List[Dict]:
        """Extrait les membres de la page courante"""
        members = []

        try:
            page_html = self.page.content()
            page_text = self.page.inner_text('body')

            # Chercher des éléments qui pourraient contenir des membres
            # Patterns: div.member, div.member-card, table rows, list items
            member_selectors = [
                'div.member', 'div.member-card', 'div[class*="member"]',
                'tr.member', 'tr[class*="member"]',
                'li.member', 'li[class*="member"]',
                'div.contact', 'div[class*="contact"]',
                'div.person', 'div[class*="person"]'
            ]

            all_member_elements = []
            for selector in member_selectors:
                try:
                    elements = self.page.locator(selector).all()
                    if elements:
                        all_member_elements.extend(elements)
                except:
                    continue

            print(f"         -> {len(all_member_elements)} éléments potentiels de membres")

            # Si pas d'éléments structurés, chercher dans le texte
            if len(all_member_elements) == 0:
                # Chercher des patterns de noms + entreprises dans le texte
                # Format typique: "Prénom Nom\nEntreprise\nTitre"
                members = self._extract_members_from_text(page_text, group_num, group_name)
                return members

            # Extraire les données de chaque élément
            for elem in all_member_elements:
                try:
                    text = elem.inner_text().strip()
                    if len(text) < 5:
                        continue

                    member_data = {
                        'group_num': group_num,
                        'group_name': group_name,
                        'extracted_at': datetime.now().isoformat()
                    }

                    # Nom complet
                    name_selectors = ['h1', 'h2', 'h3', 'h4', '.name', '.member-name', 'strong', 'b']
                    for sel in name_selectors:
                        try:
                            name_elem = elem.locator(sel).first
                            if name_elem.count() > 0:
                                full_name = name_elem.inner_text().strip()
                                if len(full_name) > 2 and len(full_name) < 100:
                                    member_data['full_name'] = full_name

                                    # Séparer prénom/nom
                                    parts = full_name.split()
                                    if len(parts) >= 2:
                                        member_data['first_name'] = parts[0]
                                        member_data['last_name'] = ' '.join(parts[1:])
                                    break
                        except:
                            continue

                    # Si pas de nom structuré, prendre la première ligne du texte
                    if 'full_name' not in member_data:
                        lines = [l.strip() for l in text.split('\n') if l.strip()]
                        if lines:
                            potential_name = lines[0]
                            if len(potential_name) > 2 and len(potential_name) < 100:
                                member_data['full_name'] = potential_name
                                parts = potential_name.split()
                                if len(parts) >= 2:
                                    member_data['first_name'] = parts[0]
                                    member_data['last_name'] = ' '.join(parts[1:])

                    # Entreprise
                    company_patterns = [
                        r'(?:company|entreprise|compagnie)[:\s]+([^\n]+)',
                        r'([A-Z][A-Za-z\s&]+(?:Inc|Ltd|LLC|SARL|Corp|Ltée)\.?)'
                    ]
                    for pattern in company_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            member_data['company'] = match.group(1).strip()[:100]
                            break

                    # Titre/Poste
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
                    category_patterns = [
                        r'(?:category|catégorie|industrie|industry)[:\s]+([^\n]+)'
                    ]
                    for pattern in category_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            member_data['category'] = match.group(1).strip()[:100]
                            break

                    # Téléphone
                    phone_pattern = r'(\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})'
                    phone_match = re.search(phone_pattern, text)
                    if phone_match:
                        member_data['phone'] = phone_match.group(1).strip()

                    # Email
                    email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                    email_match = re.search(email_pattern, text)
                    if email_match:
                        member_data['email'] = email_match.group(1).strip()

                    # LinkedIn
                    try:
                        linkedin_link = elem.locator('a[href*="linkedin"]').first
                        if linkedin_link.count() > 0:
                            member_data['linkedin'] = linkedin_link.get_attribute('href')
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
                    role_patterns = [
                        r'(President|Vice[\s-]President|Secrétaire|Trésorier|Secretary|Treasurer)',
                        r'(Président|Vice-Président|Secrétaire-Trésorier)'
                    ]
                    for pattern in role_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            member_data['group_role'] = match.group(1).strip()
                            break

                    # Ajouter seulement si on a au moins un nom
                    if 'full_name' in member_data:
                        member_data['member_id'] = self._generate_member_id(member_data)
                        members.append(member_data)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"         -> Erreur extraction: {str(e)[:50]}")

        return members

    def _extract_members_from_text(self, text: str, group_num: str, group_name: str) -> List[Dict]:
        """Extrait les membres depuis le texte brut quand pas de structure HTML"""
        members = []

        # Chercher des patterns comme:
        # Prénom Nom
        # Entreprise
        # Titre

        lines = text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Chercher une ligne qui ressemble à un nom (2-4 mots, capitalisés)
            if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+', line) and len(line) < 50:
                member_data = {
                    'full_name': line,
                    'group_num': group_num,
                    'group_name': group_name,
                    'extracted_at': datetime.now().isoformat()
                }

                # Séparer prénom/nom
                parts = line.split()
                if len(parts) >= 2:
                    member_data['first_name'] = parts[0]
                    member_data['last_name'] = ' '.join(parts[1:])

                # Les 2-3 lignes suivantes pourraient être entreprise et titre
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if len(next_line) > 2 and len(next_line) < 100:
                        member_data['company'] = next_line

                if i + 2 < len(lines):
                    next_line = lines[i + 2].strip()
                    if len(next_line) > 2 and len(next_line) < 100:
                        member_data['title'] = next_line

                member_data['member_id'] = self._generate_member_id(member_data)
                members.append(member_data)

                i += 3
            else:
                i += 1

        return members

    def _generate_member_id(self, member: Dict) -> str:
        """Génère un ID unique pour un membre"""
        name = member.get('full_name', 'unknown')
        group = member.get('group_num', 'unknown')
        clean_name = re.sub(r'[^a-z0-9]+', '-', name.lower())
        return f"gr{group}_{clean_name}"[:80]

    def run(self, groups_json_path: str, max_groups: int = None):
        """Exécute l'extraction des membres"""
        print("=" * 60)
        print("[EXTRACTION] Membres des groupes GR International")
        print("=" * 60)

        # Charger les groupes
        groups_file = Path(groups_json_path)
        if not groups_file.exists():
            print(f"[ERROR] Fichier {groups_file} non trouvé")
            return

        with open(groups_file, 'r', encoding='utf-8') as f:
            groups = json.load(f)

        print(f"[INFO] {len(groups)} groupes à traiter")

        if max_groups:
            groups = groups[:max_groups]
            print(f"[INFO] Limité à {max_groups} groupes")

        try:
            self.start_browser()

            # Authentification
            if not self.authenticate():
                print("[WARN] Continuant sans authentification...")

            # Pour chaque groupe, extraire les membres
            for i, group in enumerate(groups, 1):
                group_num = group.get('group_num')
                group_name = group.get('group_name', 'Unknown')

                print(f"\n[{i}/{len(groups)}] {group_name[:60]}")
                print(f"   ID: {group_num}")

                members = self.extract_members_from_group(group_num, group_name)
                self.all_members.extend(members)

                # Pause entre groupes pour ne pas surcharger le serveur
                self.page.wait_for_timeout(2000)

            # Sauvegarder
            tmp_dir = Path(__file__).parent.parent / ".tmp"
            tmp_dir.mkdir(exist_ok=True)

            members_file = tmp_dir / "gr_members_complete.json"
            with open(members_file, 'w', encoding='utf-8') as f:
                json.dump(self.all_members, f, indent=2, ensure_ascii=False)

            print(f"\n[SAVED] Membres: {members_file}")

            # Résumé
            print("\n" + "=" * 60)
            print("RÉSUMÉ")
            print("=" * 60)
            print(f"Groupes traités: {len(groups)}")
            print(f"Membres extraits: {len(self.all_members)}")

            # Groupes avec le plus de membres
            members_by_group = {}
            for member in self.all_members:
                gname = member.get('group_name', 'Unknown')
                members_by_group[gname] = members_by_group.get(gname, 0) + 1

            if members_by_group:
                print("\nTop 5 groupes avec le plus de membres:")
                for gname, count in sorted(members_by_group.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"  {gname[:50]:50} {count:3} membres")

            return self.all_members

        finally:
            self.close_browser()


def main():
    """Point d'entrée principal"""
    import sys

    headless = '--visible' not in sys.argv
    max_groups = None

    # Chercher --limit dans les arguments
    for arg in sys.argv:
        if arg.startswith('--limit='):
            max_groups = int(arg.split('=')[1])

    # Utiliser le fichier des groupes du Québec
    tmp_dir = Path(__file__).parent.parent / ".tmp"
    groups_file = tmp_dir / "gr_groups_quebec.json"

    if not groups_file.exists():
        print(f"[ERROR] Fichier {groups_file} non trouvé")
        print("Exécutez d'abord:")
        print("  1. python execution/gr_api_groups_extractor.py")
        print("  2. python execution/gr_filter_quebec_groups.py")
        return

    extractor = GRMembersExtractor(headless=headless)
    extractor.run(str(groups_file), max_groups=max_groups)


if __name__ == "__main__":
    main()
