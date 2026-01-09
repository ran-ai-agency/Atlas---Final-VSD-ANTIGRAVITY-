#!/usr/bin/env python3
"""
Script de monitoring de l'extraction GR en cours
"""

import json
import time
from pathlib import Path
from datetime import datetime

def monitor_extraction():
    """Surveille et affiche la progression de l'extraction"""

    tmp_dir = Path(__file__).parent.parent / ".tmp"
    progress_file = tmp_dir / "gr_extraction_progress.json"

    print("=" * 70)
    print("MONITORING EXTRACTION GR INTERNATIONAL")
    print("=" * 70)
    print("\nAppuyez sur Ctrl+C pour arrêter le monitoring\n")

    last_groups_count = 0
    last_members_count = 0

    try:
        while True:
            if progress_file.exists():
                try:
                    with open(progress_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    groups_count = len(data.get('groups_processed', []))
                    members_count = data.get('total_members', 0)
                    last_update = data.get('last_update', 'N/A')

                    # Afficher seulement si changement
                    if groups_count != last_groups_count or members_count != last_members_count:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                              f"Groupes: {groups_count}/28 | "
                              f"Membres: {members_count} | "
                              f"MAJ: {last_update.split('T')[1][:8] if 'T' in last_update else last_update}")

                        # Afficher les derniers groupes traités
                        if data.get('groups_processed'):
                            recent_groups = data['groups_processed'][-3:]
                            for g in recent_groups:
                                success = "✓" if g.get('extraction_success') else "✗"
                                member_count = len(g.get('members', []))
                                print(f"  {success} {g.get('group_name', 'Unknown')[:50]} ({member_count} membres)")

                        print()

                        last_groups_count = groups_count
                        last_members_count = members_count

                        # Si terminé
                        if groups_count >= 28:
                            print("\n" + "=" * 70)
                            print("EXTRACTION TERMINÉE!")
                            print("=" * 70)
                            print(f"Total groupes traités: {groups_count}")
                            print(f"Total membres extraits: {members_count}")

                            # Statistiques
                            successful = len([g for g in data['groups_processed'] if g.get('extraction_success')])
                            print(f"Taux de succès: {successful}/{groups_count} ({successful*100//groups_count}%)")
                            break

                except Exception as e:
                    print(f"Erreur lecture: {e}")

            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] En attente du démarrage de l'extraction...")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\nMonitoring arrêté par l'utilisateur")

        # Afficher état final
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"\nDernier état: {len(data['groups_processed'])} groupes, {data['total_members']} membres")

if __name__ == "__main__":
    monitor_extraction()
