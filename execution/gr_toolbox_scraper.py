#!/usr/bin/env python3
"""
GR International - Extracteur des Boîtes à Outils (Trucs)
Extrait la liste des boîtes à outils passées de la section membres.
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

# Configuration
# URL de la page des boîtes à outils (section membre)
TOOLBOX_URL = "https://www.grinternational.ca/membres/index.php?c=SGdsY2VHdHh1bVd3YjJta1pIdUZFVXplM1ZrWThkSVc6OjliZjAwZTdiZDY5N2MxMjk0MThiMDM5Y2QxMmZkYzdi"
MEMBER_TOKEN_URL = os.getenv('GR_MEMBER_URL', '')
GR_EMAIL = os.getenv('GR_EMAIL', '')
GR_PASSWORD = os.getenv('GR_PASSWORD', '')


@dataclass
class Toolbox:
    """Représente une boîte à outils GR"""
    title: str
    presenter: str = ""
    date: str = ""
    group: str = ""
    description: str = ""
    category: str = ""  # "passé" ou "à venir"
    link: str = ""

    def to_dict(self):
        return asdict(self)


class GRToolboxScraper:
    """Scraper pour extraire les boîtes à outils GR International"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.page = None
        self.authenticated = False
        self.toolboxes: List[Toolbox] = []

    def start_browser(self):
        """Démarre le navigateur Playwright"""
        from playwright.sync_api import sync_playwright

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
        """Authentification via formulaire de login puis navigation vers boîtes à outils"""
        tmp_dir = Path(__file__).parent.parent / ".tmp"
        tmp_dir.mkdir(exist_ok=True)

        try:
            # Étape 1: Aller sur la page de login
            login_url = "https://www.grinternational.ca/membres/membre_connection/membres_login.php"
            print(f"[AUTH] Navigation vers page de login...")
            self.page.goto(login_url, wait_until='networkidle', timeout=30000)
            self.page.wait_for_timeout(2000)

            self.page.screenshot(path=str(tmp_dir / "gr_toolbox_login_page.png"))
            print(f"[AUTH] Page de login chargée: {self.page.url}")

            # Étape 2: Remplir le formulaire de login
            if GR_EMAIL and GR_PASSWORD:
                print(f"[AUTH] Tentative de login avec {GR_EMAIL}...")

                # Chercher les champs de formulaire
                # Le formulaire GR utilise Username et Password
                email_selectors = [
                    '#username_id',
                    'input[name="Username"]',
                    'input[name="email"]',
                    'input[name="courriel"]',
                    'input[type="email"]',
                ]

                password_selectors = [
                    '#password_id',
                    'input[name="Password"]',
                    'input[name="password"]',
                    'input[name="motdepasse"]',
                    'input[type="password"]',
                ]

                email_input = None
                password_input = None

                for selector in email_selectors:
                    try:
                        el = self.page.locator(selector).first
                        if el.count() > 0 and el.is_visible():
                            email_input = el
                            print(f"[AUTH] Champ email trouvé: {selector}")
                            break
                    except:
                        continue

                for selector in password_selectors:
                    try:
                        el = self.page.locator(selector).first
                        if el.count() > 0 and el.is_visible():
                            password_input = el
                            print(f"[AUTH] Champ password trouvé: {selector}")
                            break
                    except:
                        continue

                if email_input and password_input:
                    email_input.fill(GR_EMAIL)
                    password_input.fill(GR_PASSWORD)

                    self.page.screenshot(path=str(tmp_dir / "gr_toolbox_login_filled.png"))

                    # Soumettre le formulaire
                    submit_selectors = [
                        'input[name="Submit"]',
                        'input[value="Connexion"]',
                        '#signin-form_id input[type="submit"]',
                        'input[type="submit"]',
                        'button[type="submit"]',
                    ]

                    for selector in submit_selectors:
                        try:
                            btn = self.page.locator(selector).first
                            if btn.count() > 0 and btn.is_visible():
                                print(f"[AUTH] Bouton submit trouvé: {selector}")
                                btn.click()
                                self.page.wait_for_timeout(5000)
                                break
                        except:
                            continue

                    self.page.screenshot(path=str(tmp_dir / "gr_toolbox_after_login.png"))
                    print(f"[AUTH] URL après login: {self.page.url}")

                else:
                    print("[AUTH] Champs de login non trouvés, affichage du HTML...")
                    # Sauvegarder le HTML pour debug
                    html = self.page.content()
                    (tmp_dir / "gr_login_page.html").write_text(html, encoding='utf-8')

            # Étape 3: Naviguer vers la page des boîtes à outils
            print("[AUTH] Navigation vers la page des boîtes à outils...")
            self.page.goto(TOOLBOX_URL, wait_until='networkidle', timeout=30000)
            self.page.wait_for_timeout(3000)

            self.page.screenshot(path=str(tmp_dir / "gr_toolbox_final.png"))
            print(f"[AUTH] URL finale: {self.page.url}")

            self.authenticated = True
            return True

        except Exception as e:
            print(f"[ERROR] Erreur d'authentification: {e}")
            import traceback
            traceback.print_exc()
            return False

    def fetch_toolbox_page(self) -> str:
        """Récupère le contenu de la page des boîtes à outils"""
        tmp_dir = Path(__file__).parent.parent / ".tmp"
        tmp_dir.mkdir(exist_ok=True)

        try:
            print("[TOOLBOX] Navigation vers la page des boîtes à outils...")
            self.page.goto(TOOLBOX_URL, wait_until='networkidle', timeout=30000)
            self.page.wait_for_timeout(3000)

            # Sauvegarder capture d'écran
            self.page.screenshot(path=str(tmp_dir / "gr_toolbox_page.png"))

            # Sauvegarder le HTML pour analyse
            html_content = self.page.content()
            html_path = tmp_dir / "gr_toolbox_page.html"
            html_path.write_text(html_content, encoding='utf-8')
            print(f"[OK] HTML sauvegardé: {html_path}")

            return html_content

        except Exception as e:
            print(f"[ERROR] Erreur navigation: {e}")
            return ""

    def add_toolbox(self, date: str, title: str, presenter: str, headless: bool = True):
        """Ajoute une nouvelle boîte à outils via le formulaire web"""
        self.headless = headless
        tmp_dir = Path(__file__).parent.parent / ".tmp"
        tmp_dir.mkdir(exist_ok=True)

        print("=" * 60)
        print("[ADD] Ajout d'une nouvelle Boîte à Outils GR")
        print(f"      Date: {date}")
        print(f"      Titre: {title}")
        print(f"      Présentateur: {presenter}")
        print("=" * 60)

        try:
            self.start_browser()

            if not self.authenticate():
                print("[ERROR] Échec de l'authentification")
                return False

            # On est maintenant sur la page des boîtes à outils
            # Cliquer sur "Ajouter un truc"
            print("[ADD] Recherche du bouton 'Ajouter un truc'...")

            add_btn = self.page.locator('a:has-text("Ajouter un truc"), button:has-text("Ajouter un truc")').first
            if add_btn.count() > 0:
                print("[ADD] Bouton trouvé, clic...")
                add_btn.click()
                self.page.wait_for_timeout(3000)

                self.page.screenshot(path=str(tmp_dir / "gr_toolbox_add_form.png"))
                print(f"[ADD] Formulaire d'ajout: {self.page.url}")

                # Sauvegarder le HTML pour debug
                html = self.page.content()
                (tmp_dir / "gr_toolbox_form.html").write_text(html, encoding='utf-8')

                # Remplir le formulaire - Formulaire unique "Boîte à outils GR pour groupe"
                # Structure du formulaire:
                # - Reunion_Dt: champ date
                # - coachID: dropdown présentateur (format: "Nom, Prénom")
                # - coachSujetID: dropdown sujet existant OU coachSujet: nouveau sujet

                # 1. Date - champ #Reunion_Dt
                date_input = self.page.locator('#Reunion_Dt, input[name="Reunion_Dt"]').first
                if date_input.count() > 0:
                    date_input.fill(date)
                    print(f"[ADD] Date remplie: {date}")
                else:
                    print("[WARN] Champ date non trouvé")

                # Fermer le datepicker si ouvert
                self.page.keyboard.press('Escape')
                self.page.wait_for_timeout(500)

                # 2. Présentateur - dropdown #coachID (format: "Nom, Prénom")
                presenter_select = self.page.locator('#coachID, select[name="coachID"]').first
                presenter_filled = False
                if presenter_select.count() > 0:
                    # Chercher l'option qui correspond au présentateur
                    # Le format dans le dropdown est "Nom, Prénom"
                    options = presenter_select.locator('option').all()
                    presenter_lower = presenter.lower()

                    # Extraire prénom et nom du paramètre (format: "Prénom Nom")
                    presenter_parts = presenter.split()
                    if len(presenter_parts) >= 2:
                        prenom = presenter_parts[0]
                        nom = ' '.join(presenter_parts[1:])
                    else:
                        prenom = presenter
                        nom = presenter

                    for opt in options:
                        opt_text = opt.inner_text().strip()
                        opt_lower = opt_text.lower()

                        # Vérifier différentes correspondances
                        if (prenom.lower() in opt_lower and nom.lower() in opt_lower) or \
                           (nom.lower() in opt_lower) or \
                           (presenter_lower in opt_lower):
                            opt_value = opt.get_attribute('value')
                            if opt_value and opt_value != '-1':
                                presenter_select.select_option(value=opt_value)
                                print(f"[ADD] Présentateur sélectionné: {opt_text} (value={opt_value})")
                                presenter_filled = True
                                break

                    if not presenter_filled:
                        print(f"[WARN] Présentateur '{presenter}' non trouvé dans la liste")
                        # Lister les options disponibles
                        print("[INFO] Options disponibles:")
                        for opt in options[:15]:
                            print(f"       - {opt.inner_text().strip()}")

                self.page.wait_for_timeout(500)

                # 3. Sujet - sélectionner "Autre" (value="0") pour afficher le champ texte
                # Le champ #coachSujet est dans un div caché par défaut (div#div_truc_coach_sujet)
                # Il faut sélectionner "Autre" dans #coachSujetID pour l'afficher

                sujet_select = self.page.locator('#coachSujetID, select[name="coachSujetID"]').first
                if sujet_select.count() > 0:
                    # Sélectionner "Autre" (value="0") pour afficher le champ texte
                    sujet_select.select_option(value="0")
                    print("[ADD] Option 'Autre' sélectionnée pour sujet personnalisé")
                    self.page.wait_for_timeout(1000)  # Attendre que le div s'affiche

                # Maintenant remplir le champ texte #coachSujet
                title_input = self.page.locator('#coachSujet, input[name="coachSujet"]').first
                if title_input.count() > 0:
                    if title_input.is_visible():
                        title_input.fill(title)
                        print(f"[ADD] Sujet rempli: {title}")
                    else:
                        print("[WARN] Champ sujet toujours non visible après sélection 'Autre'")
                        # Essayer de forcer l'affichage via JavaScript
                        self.page.evaluate('document.getElementById("div_truc_coach_sujet").style.display = "block"')
                        self.page.wait_for_timeout(500)
                        title_input.fill(title)
                        print(f"[ADD] Sujet rempli (après forçage affichage): {title}")
                else:
                    print("[WARN] Champ sujet non trouvé")

                self.page.screenshot(path=str(tmp_dir / "gr_toolbox_form_filled.png"))

                # Soumettre le formulaire - chercher le bouton dans la section groupe
                submit_selectors = [
                    '#groupeForm input[type="submit"]',
                    'form[name*="groupe"] input[type="submit"]',
                    'input[value="Enregistrer"]:visible',
                    'input[type="submit"]:visible',
                    'button[type="submit"]:visible',
                ]
                submit_btn = None
                for sel in submit_selectors:
                    try:
                        btn = self.page.locator(sel).first
                        if btn.count() > 0 and btn.is_visible():
                            submit_btn = btn
                            break
                    except:
                        continue

                if submit_btn:
                    print("[ADD] Soumission du formulaire...")
                    submit_btn.click()
                    self.page.wait_for_timeout(5000)

                    self.page.screenshot(path=str(tmp_dir / "gr_toolbox_after_submit.png"))
                    print(f"[ADD] Après soumission: {self.page.url}")

                    # Vérifier si l'ajout a réussi
                    page_content = self.page.content()
                    if title in page_content or 'succès' in page_content.lower() or 'success' in page_content.lower():
                        print("[OK] Boîte à outils ajoutée avec succès!")
                        return True
                    else:
                        print("[WARN] L'ajout semble terminé mais vérification incertaine")
                        return True
                else:
                    print("[ERROR] Bouton de soumission non trouvé")
                    # Sauvegarder le HTML pour debug
                    html = self.page.content()
                    (tmp_dir / "gr_toolbox_form.html").write_text(html, encoding='utf-8')
                    return False

            else:
                print("[ERROR] Bouton 'Ajouter un truc' non trouvé")
                return False

        except Exception as e:
            print(f"[ERROR] Erreur lors de l'ajout: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            self.close_browser()

    def extract_toolboxes(self, html_content: str) -> List[Toolbox]:
        """Extrait les boîtes à outils du HTML"""
        toolboxes = []

        print("[EXTRACT] Extraction des boîtes à outils...")

        try:
            # Scroller pour charger tout le contenu
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(1000)

            # Extraire les tableaux de trucs
            # Structure visible: Date | Titre | Présentateur | Modifier | Effacer

            # Section "Trucs à venir"
            print("[EXTRACT] Recherche de 'Trucs à venir'...")
            try:
                # Trouver le header "Trucs à venir" et le tableau suivant
                upcoming_header = self.page.locator('text=Trucs à venir').first
                if upcoming_header.count() > 0:
                    # Trouver le tableau après ce header
                    upcoming_table = self.page.locator('h4:has-text("Trucs à venir") + table, h3:has-text("Trucs à venir") + table').first
                    if upcoming_table.count() == 0:
                        # Essayer de trouver le tableau le plus proche
                        upcoming_table = upcoming_header.locator('xpath=following::table[1]').first

                    if upcoming_table.count() > 0:
                        rows = upcoming_table.locator('tr').all()
                        for row in rows:
                            cells = row.locator('td').all()
                            if len(cells) >= 3:
                                date = cells[0].inner_text().strip()
                                title = cells[1].inner_text().strip()
                                presenter = cells[2].inner_text().strip()

                                if date and title:
                                    toolbox = Toolbox(
                                        title=title,
                                        date=date,
                                        presenter=presenter,
                                        category="a_venir"
                                    )
                                    toolboxes.append(toolbox)
                                    print(f"   [A VENIR] {date}: {title[:50]}... - {presenter}")
            except Exception as e:
                print(f"[WARN] Erreur extraction trucs à venir: {e}")

            # Section "Trucs passés"
            print("[EXTRACT] Recherche de 'Trucs passés'...")
            try:
                # Chercher tous les tableaux de la page
                all_tables = self.page.locator('table').all()
                print(f"   {len(all_tables)} tableaux trouvés")

                for table_idx, table in enumerate(all_tables):
                    rows = table.locator('tr').all()
                    for row in rows:
                        cells = row.locator('td').all()
                        if len(cells) >= 3:
                            cell0_text = cells[0].inner_text().strip()
                            cell1_text = cells[1].inner_text().strip()
                            cell2_text = cells[2].inner_text().strip()

                            # Vérifier si c'est une ligne de données (date au format YYYY-MM-DD)
                            if re.match(r'\d{4}-\d{2}-\d{2}', cell0_text):
                                # Déterminer la catégorie basée sur la position dans la page
                                # ou sur la date
                                from datetime import datetime
                                try:
                                    item_date = datetime.strptime(cell0_text, '%Y-%m-%d')
                                    today = datetime.now()
                                    category = "a_venir" if item_date > today else "passe"
                                except:
                                    category = "passe"

                                # Vérifier si cet élément n'existe pas déjà
                                exists = any(t.date == cell0_text and t.title == cell1_text for t in toolboxes)
                                if not exists:
                                    toolbox = Toolbox(
                                        title=cell1_text,
                                        date=cell0_text,
                                        presenter=cell2_text,
                                        category=category
                                    )
                                    toolboxes.append(toolbox)
                                    print(f"   [{category.upper()}] {cell0_text}: {cell1_text[:50]}... - {cell2_text}")

            except Exception as e:
                print(f"[WARN] Erreur extraction tableaux: {e}")

        except Exception as e:
            print(f"[ERROR] Erreur extraction: {e}")

        return toolboxes

    def run(self, headless: bool = True) -> List[Toolbox]:
        """Exécute l'extraction complète"""
        self.headless = headless

        print("=" * 60)
        print("[SCAN] Extraction des Boîtes à Outils GR International")
        print("=" * 60)

        try:
            self.start_browser()

            if not self.authenticate():
                print("[WARN] Continuant sans authentification confirmée...")

            # Récupérer et analyser la page
            html_content = self.fetch_toolbox_page()

            if html_content:
                self.toolboxes = self.extract_toolboxes(html_content)

            # Sauvegarder les résultats
            self.save_results()

            return self.toolboxes

        finally:
            self.close_browser()

    def save_results(self):
        """Sauvegarde les résultats en JSON"""
        tmp_dir = Path(__file__).parent.parent / ".tmp"
        tmp_dir.mkdir(exist_ok=True)

        # Fichier JSON
        json_path = tmp_dir / "gr_toolboxes.json"

        output_data = {
            "derniere_mise_a_jour": datetime.now().isoformat(),
            "total": len(self.toolboxes),
            "toolboxes": [t.to_dict() for t in self.toolboxes]
        }

        json_path.write_text(
            json.dumps(output_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        print(f"\n[SAVED] Données JSON: {json_path}")

        # Résumé Markdown
        summary = f"""# Boîtes à Outils GR International

**Dernière mise à jour**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Total**: {len(self.toolboxes)} éléments

## Liste des Boîtes à Outils

"""
        for i, t in enumerate(self.toolboxes, 1):
            summary += f"{i}. **{t.title}**\n"
            if t.presenter:
                summary += f"   - Présentateur: {t.presenter}\n"
            if t.date:
                summary += f"   - Date: {t.date}\n"
            summary += "\n"

        summary_path = tmp_dir / "gr_toolboxes_summary.md"
        summary_path.write_text(summary, encoding='utf-8')
        print(f"[SAVED] Résumé: {summary_path}")


def main():
    """Point d'entrée principal"""
    import argparse

    parser = argparse.ArgumentParser(description='Extracteur des boîtes à outils GR International')
    parser.add_argument('--visible', action='store_true', help='Mode visible (non headless)')
    parser.add_argument('--add', action='store_true', help='Ajouter une nouvelle boîte à outils')
    parser.add_argument('--date', type=str, help='Date de la boîte à outils (YYYY-MM-DD)')
    parser.add_argument('--title', type=str, help='Titre de la boîte à outils')
    parser.add_argument('--presenter', type=str, help='Présentateur de la boîte à outils')

    args = parser.parse_args()

    scraper = GRToolboxScraper()

    if args.add:
        if not args.date or not args.title or not args.presenter:
            print("[ERROR] Pour ajouter une boîte à outils, spécifiez --date, --title et --presenter")
            return
        scraper.add_toolbox(
            date=args.date,
            title=args.title,
            presenter=args.presenter,
            headless=not args.visible
        )
        return

    toolboxes = scraper.run(headless=not args.visible)

    print("\n" + "=" * 60)
    print(f"EXTRACTION TERMINÉE: {len(toolboxes)} boîtes à outils")
    print("=" * 60)

    # Afficher un aperçu
    for t in toolboxes[:10]:
        print(f"  - {t.title[:80]}...")
    if len(toolboxes) > 10:
        print(f"  ... et {len(toolboxes) - 10} autres")


if __name__ == "__main__":
    main()
