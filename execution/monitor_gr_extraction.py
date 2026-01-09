#!/usr/bin/env python3
"""
Script de monitoring pour l'extraction GR en cours
"""

import json
import time
from pathlib import Path
from datetime import datetime

def monitor_extraction():
    """Affiche la progression de l'extraction en temps réel"""

    progress_file = Path(__file__).parent.parent / ".tmp" / "gr_extraction_progress.json"
    last_update_time = None

    print("=" * 70)
    print("MONITORING - Extraction GR International")
    print("=" * 70)
    print()

    while True:
        try:
            if not progress_file.exists():
                print("En attente du démarrage de l'extraction...")
                time.sleep(5)
                continue

            # Lire le fichier de progression
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)

            # Vérifier si nouvelle mise à jour
            current_update = progress.get('last_update')
            if current_update != last_update_time:
                last_update_time = current_update

                groups_processed = progress.get('groups_processed', [])
                total_members = progress.get('total_members', 0)

                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Progression:")
                print(f"  - Groupes traités: {len(groups_processed)}/28")
                print(f"  - Membres extraits: {total_members}")

                # Afficher les 3 derniers groupes traités
                if groups_processed:
                    print(f"\n  Derniers groupes:")
                    for group in groups_processed[-3:]:
                        group_name = group['group_name'][:50]
                        member_count = len(group.get('members', []))
                        print(f"    - {group_name}: {member_count} membres")

                # Vérifier si terminé
                if len(groups_processed) >= 28:
                    print("\n" + "=" * 70)
                    print("EXTRACTION TERMINÉE!")
                    print("=" * 70)
                    print(f"Total: {total_members} membres extraits de 28 groupes")
                    break

            time.sleep(5)  # Vérifier toutes les 5 secondes

        except KeyboardInterrupt:
            print("\n\nMonitoring arrêté par l'utilisateur.")
            break
        except Exception as e:
            print(f"\nErreur: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_extraction()
