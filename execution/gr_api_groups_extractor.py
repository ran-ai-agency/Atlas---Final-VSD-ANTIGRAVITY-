#!/usr/bin/env python3
"""
GR International - Extracteur via API
Utilise l'API d'autocomplétion pour obtenir tous les groupes,
puis extrait les informations de chaque groupe
"""

import os
import json
import re
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = "https://www.grinternational.ca"
API_SUGGEST_URL = f"{BASE_URL}/__includes/suggest_groupe_actif-eng.php"


def get_all_groups_from_api() -> List[Dict]:
    """
    Interroge l'API d'autocomplétion avec toutes les lettres de l'alphabet
    pour obtenir la liste complète des groupes actifs
    """
    all_groups = []
    seen_nums = set()

    print("[API] Interrogation de l'API d'autocomplétion...")

    # Essayer avec toutes les lettres + chiffres + "GR"
    search_terms = list('abcdefghijklmnopqrstuvwxyz') + list('0123456789') + ['GR', 'Groupe', 'Group']

    for term in search_terms:
        try:
            # L'API jQuery autocomplete attend un paramètre 'term'
            response = requests.get(API_SUGGEST_URL, params={'term': term}, timeout=10)

            if response.status_code == 200:
                try:
                    data = response.json()

                    # L'API retourne un tableau d'objets avec 'label', 'value', 'num', etc.
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                num = item.get('num') or item.get('id')
                                label = item.get('label') or item.get('value', '')

                                if num and num not in seen_nums:
                                    seen_nums.add(num)
                                    group_data = {
                                        'group_num': num,
                                        'group_name': label,
                                        'extracted_at': datetime.now().isoformat()
                                    }
                                    all_groups.append(group_data)
                                    print(f"   -> {label}")

                except json.JSONDecodeError:
                    # Parfois l'API retourne du texte brut
                    pass

        except Exception as e:
            print(f"   -> Erreur {term}: {str(e)[:30]}")
            continue

    print(f"[API] {len(all_groups)} groupes uniques trouvés")
    return all_groups


def extract_group_details_simple(group_num: str, group_name: str) -> Dict:
    """
    Extrait les détails simples d'un groupe sans Playwright
    En utilisant uniquement requests
    """
    try:
        # Construire l'URL du groupe
        # Format typique: /groupes/view.php?num=XXX ou similaire
        # On va essayer plusieurs patterns
        possible_urls = [
            f"{BASE_URL}/groupes/view.php?num={group_num}",
            f"{BASE_URL}/group?id={group_num}",
            f"{BASE_URL}/groups/{group_num}",
        ]

        for url in possible_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    html = response.text

                    # Extraire des informations basiques via regex
                    group_data = {
                        'group_num': group_num,
                        'group_name': group_name,
                        'group_url': url,
                        'extracted_at': datetime.now().isoformat()
                    }

                    # Chercher jour de réunion
                    day_match = re.search(
                        r'(?:meeting day|jour de réunion|day)[:\s]+(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
                        html,
                        re.IGNORECASE
                    )
                    if day_match:
                        group_data['meeting_day'] = day_match.group(1)

                    # Chercher heure
                    time_match = re.search(r'(\d{1,2}[h:]\d{2}(?:\s*(?:am|pm))?)', html)
                    if time_match:
                        group_data['meeting_time'] = time_match.group(1)

                    # Format
                    if any(x in html.lower() for x in ['zoom', 'virtual', 'virtuel']):
                        group_data['format'] = 'Zoom'
                    else:
                        group_data['format'] = 'Présentiel'

                    return group_data

            except Exception as e:
                continue

        # Si aucune URL ne fonctionne, retourner les données minimales
        return {
            'group_num': group_num,
            'group_name': group_name,
            'group_url': f"{BASE_URL}/groups/{group_num}",
            'extracted_at': datetime.now().isoformat()
        }

    except Exception as e:
        return {
            'group_num': group_num,
            'group_name': group_name,
            'error': str(e),
            'extracted_at': datetime.now().isoformat()
        }


def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("[EXTRACTION] Groupes GR via API")
    print("=" * 60)

    # Obtenir les groupes via l'API
    groups = get_all_groups_from_api()

    if not groups:
        print("[ERROR] Aucun groupe trouvé via l'API")
        return

    print(f"\n[ENRICHISSEMENT] Extraction des détails de {len(groups)} groupes...")

    # Enrichir les données de chaque groupe
    enriched_groups = []
    for i, group in enumerate(groups[:50], 1):  # Limiter à 50 pour le test
        print(f"[{i}/{min(len(groups), 50)}] {group['group_name'][:50]}...")
        detailed_group = extract_group_details_simple(
            group['group_num'],
            group['group_name']
        )
        enriched_groups.append(detailed_group)

    # Sauvegarder
    tmp_dir = Path(__file__).parent.parent / ".tmp"
    tmp_dir.mkdir(exist_ok=True)

    # Groupes bruts de l'API
    api_groups_path = tmp_dir / "gr_groups_from_api.json"
    api_groups_path.write_text(
        json.dumps(groups, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print(f"\n[SAVED] Groupes API: {api_groups_path}")

    # Groupes enrichis
    enriched_path = tmp_dir / "gr_groups_enriched.json"
    enriched_path.write_text(
        json.dumps(enriched_groups, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print(f"[SAVED] Groupes enrichis: {enriched_path}")

    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"Groupes trouvés via API: {len(groups)}")
    print(f"Groupes enrichis: {len(enriched_groups)}")
    print(f"\nFichiers sauvegardés dans: {tmp_dir}")


if __name__ == "__main__":
    main()
