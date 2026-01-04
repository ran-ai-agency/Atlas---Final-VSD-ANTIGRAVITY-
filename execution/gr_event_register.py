#!/usr/bin/env python3
"""
GR International Event Registration - Automatisation des inscriptions
Remplit et soumet le formulaire "Je veux participer a cet evenement"
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://www.grinternational.ca"


@dataclass
class RegistrationProfile:
    """Profil d'inscription aux evenements"""
    prenom: str
    nom: str
    compagnie: str
    courriel: str
    telephone: str
    ville: str = ""
    site_web: str = ""
    refere_par: str = ""
    refere_nom: str = ""

    @classmethod
    def from_env(cls) -> 'RegistrationProfile':
        """Charge le profil depuis les variables d'environnement"""
        return cls(
            prenom=os.getenv('GR_PRENOM', ''),
            nom=os.getenv('GR_NOM', ''),
            compagnie=os.getenv('GR_COMPAGNIE', ''),
            courriel=os.getenv('GR_EMAIL', ''),
            telephone=os.getenv('GR_TELEPHONE', ''),
            ville=os.getenv('GR_VILLE', ''),
            site_web=os.getenv('GR_SITEWEB', ''),
            refere_par="",
            refere_nom=""
        )

    def is_valid(self) -> bool:
        """Verifie que les champs obligatoires sont remplis"""
        return all([self.prenom, self.nom, self.compagnie, self.courriel, self.telephone])


class GREventRegistration:
    """Gere l'inscription aux evenements GR International"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.page = None
        self.profile = RegistrationProfile.from_env()
        self.tmp_dir = Path(__file__).parent.parent / ".tmp"
        self.tmp_dir.mkdir(exist_ok=True)

    def start_browser(self):
        """Demarre le navigateur Playwright"""
        from playwright.sync_api import sync_playwright

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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
        member_url = os.getenv('GR_MEMBER_URL', '')

        if not member_url:
            print("[WARN] GR_MEMBER_URL non configure")
            return False

        try:
            print("[AUTH] Connexion via lien membre...")
            self.page.goto(member_url, wait_until='networkidle', timeout=30000)
            self.page.wait_for_timeout(2000)

            content = self.page.content().lower()
            if 'member' in content or 'membre' in content:
                print("[OK] Authentification reussie")
                return True
            else:
                print("[WARN] Authentification incertaine")
                return True  # Continuer quand meme

        except Exception as e:
            print(f"[ERROR] Erreur d'authentification: {e}")
            return False

    def register_for_event(self, event_url: str, dry_run: bool = True) -> dict:
        """
        Inscrit l'utilisateur a un evenement

        Args:
            event_url: URL de la page de l'evenement
            dry_run: Si True, remplit le formulaire mais ne soumet pas

        Returns:
            dict avec le resultat de l'inscription
        """
        result = {
            'success': False,
            'event_url': event_url,
            'event_name': '',
            'message': '',
            'dry_run': dry_run
        }

        if not self.profile.is_valid():
            result['message'] = "Profil incomplet. Verifiez GR_PRENOM, GR_NOM, GR_COMPAGNIE, GR_EMAIL, GR_TELEPHONE dans .env"
            print(f"[ERROR] {result['message']}")
            return result

        try:
            # Naviguer vers la page de l'evenement
            print(f"[EVENT] Navigation vers l'evenement...")
            self.page.goto(event_url, wait_until='networkidle', timeout=30000)
            self.page.wait_for_timeout(2000)

            # Extraire le nom de l'evenement
            try:
                title_elem = self.page.locator('h1, h2, .event-title, .titre').first
                if title_elem.is_visible():
                    result['event_name'] = title_elem.inner_text().strip()[:100]
            except:
                pass

            print(f"   -> Evenement: {result['event_name'][:50] or 'Non trouve'}")

            # Trouver et cliquer sur le bouton "Je veux participer"
            print("[FORM] Recherche du bouton de participation...")

            participate_btn = self.page.locator(
                'button:has-text("Je veux participer"), '
                'a:has-text("Je veux participer"), '
                'input[value*="participer"]'
            ).first

            if participate_btn.count() == 0:
                result['message'] = "Bouton 'Je veux participer' non trouve"
                print(f"[ERROR] {result['message']}")
                return result

            # Cliquer sur le bouton
            participate_btn.click()
            self.page.wait_for_timeout(2000)
            print("   -> Formulaire ouvert")

            # Screenshot du formulaire
            self.page.screenshot(path=str(self.tmp_dir / "registration_form.png"))

            # Remplir les champs du formulaire
            print("[FORM] Remplissage du formulaire...")

            fields_to_fill = [
                ('input[name="Prenom"]', self.profile.prenom, "Prenom"),
                ('input[name="Nom"]', self.profile.nom, "Nom"),
                ('input[name="Compagnie"]', self.profile.compagnie, "Compagnie"),
                ('input[name="Courriel"]', self.profile.courriel, "Courriel"),
                ('input[name="Telephone"]', self.profile.telephone, "Telephone"),
                ('input[name="Ville"]', self.profile.ville, "Ville"),
                ('input[name="SiteWeb"]', self.profile.site_web, "Site Web"),
            ]

            for selector, value, label in fields_to_fill:
                if value:
                    try:
                        field = self.page.locator(selector).first
                        if field.count() > 0:
                            field.fill(value)
                            print(f"   -> {label}: {value[:30]}")
                    except Exception as e:
                        print(f"   -> {label}: Erreur - {e}")

            # Screenshot apres remplissage
            self.page.screenshot(path=str(self.tmp_dir / "registration_filled.png"))

            if dry_run:
                result['success'] = True
                result['message'] = "Formulaire rempli (mode test - non soumis)"
                print(f"\n[DRY RUN] {result['message']}")
                print("   -> Pour soumettre reellement, utilisez dry_run=False")
            else:
                # Chercher et cliquer sur le bouton de soumission
                print("[SUBMIT] Soumission du formulaire...")

                submit_btn = self.page.locator(
                    'button[type="submit"], '
                    'input[type="submit"], '
                    'button:has-text("Envoyer"), '
                    'button:has-text("Soumettre"), '
                    'button:has-text("Confirmer")'
                ).first

                if submit_btn.count() > 0:
                    submit_btn.click()
                    self.page.wait_for_timeout(3000)

                    # Verifier le resultat
                    page_content = self.page.content().lower()
                    if any(x in page_content for x in ['merci', 'confirmation', 'inscrit', 'succes', 'thank']):
                        result['success'] = True
                        result['message'] = "Inscription reussie!"
                        print(f"[OK] {result['message']}")
                    else:
                        result['message'] = "Formulaire soumis, verifiez votre courriel"
                        result['success'] = True
                        print(f"[INFO] {result['message']}")

                    # Screenshot de confirmation
                    self.page.screenshot(path=str(self.tmp_dir / "registration_result.png"))
                else:
                    result['message'] = "Bouton de soumission non trouve"
                    print(f"[ERROR] {result['message']}")

        except Exception as e:
            result['message'] = f"Erreur: {str(e)}"
            print(f"[ERROR] {result['message']}")

        return result

    def register_multiple(self, event_urls: List[str], dry_run: bool = True) -> List[dict]:
        """Inscrit l'utilisateur a plusieurs evenements"""
        results = []

        try:
            self.start_browser()

            if not self.authenticate():
                return [{'success': False, 'message': 'Authentification echouee'}]

            for i, url in enumerate(event_urls):
                print(f"\n{'='*60}")
                print(f"[{i+1}/{len(event_urls)}] Inscription en cours...")
                print(f"{'='*60}")

                result = self.register_for_event(url, dry_run=dry_run)
                results.append(result)

                # Attendre entre les inscriptions
                if i < len(event_urls) - 1:
                    self.page.wait_for_timeout(2000)

        finally:
            self.close_browser()

        return results


def show_events_menu():
    """Affiche le menu des evenements disponibles"""
    tmp_dir = Path(__file__).parent.parent / ".tmp"
    json_files = list(tmp_dir.glob("gr_events_*.json"))

    if not json_files:
        print("[ERROR] Aucun fichier d'evenements trouve. Executez d'abord gr_international_scraper.py")
        return []

    # Prendre le fichier le plus recent
    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
    print(f"[INFO] Lecture de {latest_file.name}")

    with open(latest_file, 'r', encoding='utf-8') as f:
        events = json.load(f)

    # Filtrer les evenements recommandes (score >= 3)
    recommended = [e for e in events if e.get('score', 0) >= 3 and e.get('registration_url')]

    print(f"\n{'='*60}")
    print("EVENEMENTS RECOMMANDES")
    print(f"{'='*60}\n")

    for i, event in enumerate(recommended, 1):
        print(f"[{i}] {event['name'][:60]}")
        print(f"    Date: {event['date']} | Format: {event['format']}")
        print(f"    Groupe: {event['group']}")
        print()

    return recommended


def main():
    """Point d'entree principal"""
    print("="*60)
    print("GR International - Inscription aux Evenements")
    print("="*60)

    # Charger le profil
    profile = RegistrationProfile.from_env()

    if not profile.is_valid():
        print("\n[ERROR] Profil incomplet!")
        print("Configurez les variables suivantes dans .env:")
        print("  - GR_PRENOM")
        print("  - GR_NOM")
        print("  - GR_COMPAGNIE")
        print("  - GR_EMAIL")
        print("  - GR_TELEPHONE")
        return

    print(f"\nProfil d'inscription:")
    print(f"  Nom: {profile.prenom} {profile.nom}")
    print(f"  Entreprise: {profile.compagnie}")
    print(f"  Courriel: {profile.courriel}")
    print(f"  Telephone: {profile.telephone}")

    # Mode ligne de commande
    if len(sys.argv) > 1:
        event_url = sys.argv[1]
        dry_run = '--submit' not in sys.argv

        registration = GREventRegistration(headless='--visible' not in sys.argv)

        try:
            registration.start_browser()
            if registration.authenticate():
                result = registration.register_for_event(event_url, dry_run=dry_run)
                print(f"\nResultat: {result}")
        finally:
            registration.close_browser()
    else:
        # Mode interactif
        events = show_events_menu()

        if not events:
            return

        print("\nEntrez le numero de l'evenement (ou 'q' pour quitter):")
        choice = input("> ").strip()

        if choice.lower() == 'q':
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(events):
                event = events[idx]
                print(f"\n[SELECTED] {event['name']}")
                print(f"URL: {event['registration_url']}")

                print("\nVoulez-vous proceder a l'inscription? (o/n)")
                confirm = input("> ").strip().lower()

                if confirm == 'o':
                    registration = GREventRegistration(headless=False)
                    try:
                        registration.start_browser()
                        if registration.authenticate():
                            # Mode test par defaut
                            result = registration.register_for_event(
                                event['registration_url'],
                                dry_run=True
                            )

                            if result['success']:
                                print("\n[OK] Formulaire rempli avec succes!")
                                print("Pour soumettre reellement, ajoutez --submit")
                    finally:
                        registration.close_browser()
            else:
                print("[ERROR] Numero invalide")
        except ValueError:
            print("[ERROR] Entrez un numero valide")


if __name__ == "__main__":
    main()
