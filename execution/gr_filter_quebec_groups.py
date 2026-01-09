#!/usr/bin/env python3
"""
Filtre et organise les groupes GR du Québec
"""

import json
from pathlib import Path
from datetime import datetime

def filter_quebec_groups():
    """Filtre les groupes du Québec depuis les données de l'API"""

    tmp_dir = Path(__file__).parent.parent / ".tmp"
    api_file = tmp_dir / "gr_groups_from_api.json"

    if not api_file.exists():
        print(f"[ERROR] Fichier {api_file} non trouvé. Exécutez d'abord gr_api_groups_extractor.py")
        return

    # Charger les données
    with open(api_file, 'r', encoding='utf-8') as f:
        all_groups = json.load(f)

    print(f"[INFO] {len(all_groups)} groupes totaux dans la base de données")

    # Régions du Québec à rechercher
    quebec_keywords = [
        'Montréal', 'Montreal',
        'Québec', 'Quebec',
        'Montérégie', 'Monteregie',
        'Laval',
        'Longueuil',
        'Brossard',
        'Gatineau', 'Outaouais',
        'Vaudreuil',
        'Laurentides',
        'Lanaudière', 'Lanaudiere',
        'Mauricie',
        'Estrie',
        'Abitibi',
        'Saguenay', 'Lac-Saint-Jean',
        'Bas-Saint-Laurent',
        'Gaspésie', 'Gaspesie',
        'Côte-Nord', 'Cote-Nord',
        'Nord-du-Québec', 'Nord-du-Quebec',
        'Chaudière-Appalaches', 'Chaudiere-Appalaches',
        'Centre-du-Québec', 'Centre-du-Quebec',
        'Drummondville',
        'Sherbrooke',
        'Trois-Rivières', 'Trois-Rivieres',
        'La Prairie',
    ]

    # Filtrer les groupes du Québec
    quebec_groups = []
    for group in all_groups:
        group_name = group.get('group_name', '')
        if any(keyword in group_name for keyword in quebec_keywords):
            quebec_groups.append(group)

    print(f"[INFO] {len(quebec_groups)} groupes du Québec trouvés")

    # Organiser par région
    regions = {}
    for group in quebec_groups:
        group_name = group.get('group_name', '')

        # Déterminer la région principale
        region = 'Autre'
        if 'Montreal' in group_name or 'Montréal' in group_name:
            region = 'Montreal'
        elif 'Brossard' in group_name or 'Longueuil' in group_name or 'Montérégie' in group_name or 'Monteregie' in group_name or 'La Prairie' in group_name:
            region = 'Montérégie (Rive-Sud)'
        elif 'Québec' in group_name or 'Quebec' in group_name:
            region = 'Québec (Capitale-Nationale)'
        elif 'Laval' in group_name:
            region = 'Laval'
        elif 'Gatineau' in group_name or 'Outaouais' in group_name:
            region = 'Outaouais'
        elif 'Vaudreuil' in group_name:
            region = 'Vaudreuil-Soulanges'
        elif 'Laurentides' in group_name:
            region = 'Laurentides'
        elif 'Drummondville' in group_name or 'Centre-du-Québec' in group_name or 'Centre-du-Quebec' in group_name:
            region = 'Centre-du-Québec'

        if region not in regions:
            regions[region] = []
        regions[region].append(group)

    # Sauvegarder les groupes du Québec
    quebec_file = tmp_dir / "gr_groups_quebec.json"
    with open(quebec_file, 'w', encoding='utf-8') as f:
        json.dump(quebec_groups, f, indent=2, ensure_ascii=False)

    print(f"[SAVED] Groupes du Québec: {quebec_file}")

    # Sauvegarder par région
    regions_file = tmp_dir / "gr_groups_by_region.json"
    with open(regions_file, 'w', encoding='utf-8') as f:
        json.dump(regions, f, indent=2, ensure_ascii=False)

    print(f"[SAVED] Groupes par région: {regions_file}")

    # Générer un rapport texte
    report = f"""# Groupes GR International - Québec
**Date du rapport**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Source**: API GR International

---

## Résumé

- **Groupes totaux dans la base de données**: {len(all_groups)}
- **Groupes du Québec**: {len(quebec_groups)}

---

## Groupes par Région

"""

    for region, groups in sorted(regions.items()):
        report += f"### {region} ({len(groups)} groupes)\n\n"
        for group in groups:
            report += f"- **{group['group_name']}** (ID: {group['group_num']})\n"
        report += "\n"

    report += """---

## Utilisation

Ces données peuvent être utilisées pour:
- Identifier les groupes actifs dans votre région
- Planifier votre stratégie de networking
- Trouver des groupes spécialisés (Virtuel, Élite, B2B, etc.)

**Note**: Pour obtenir les détails complets d'un groupe (horaires, membres, etc.), utilisez le numéro de groupe (group_num) pour naviguer vers sa page sur le site GR International.

---

*Rapport généré le {datetime.now().strftime('%Y-%m-%d à %H:%M')}*
"""

    report_file = tmp_dir / "gr_groups_quebec_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"[SAVED] Rapport: {report_file}")

    # Afficher résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ PAR RÉGION")
    print("=" * 60)
    for region, groups in sorted(regions.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"{region:30} {len(groups):3} groupes")

    print("\n" + "=" * 60)
    print(f"Tous les fichiers sauvegardés dans: {tmp_dir}")
    print("=" * 60)


if __name__ == "__main__":
    filter_quebec_groups()
