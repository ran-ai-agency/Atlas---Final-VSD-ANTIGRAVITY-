"""
Crée la structure de pages Notion pour le Projet Secteur Informel
avec la liste des fichiers à uploader manuellement
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from execution.notion_client import (
    NotionClient,
    create_heading_block,
    create_text_block,
    create_bullet_list,
    title_property
)

load_dotenv()

# Forcer UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Dossier source
SOURCE_DIR = Path(__file__).parent.parent / ".tmp" / "Projet Secteur Informel"


def get_file_icon(filename: str) -> str:
    """Retourne une icône selon le type de fichier."""
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    icons = {
        'pdf': '📄',
        'xlsx': '📊',
        'xls': '📊',
        'doc': '📝',
        'docx': '📝',
        'txt': '📃',
        'md': '📃',
        'jpg': '🖼️',
        'jpeg': '🖼️',
        'png': '🖼️',
        'gif': '🖼️',
        'js': '💻',
        'py': '🐍',
        'zip': '📦',
    }
    return icons.get(ext, '📄')


def format_size(size_bytes: int) -> str:
    """Formate une taille en format lisible."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def scan_directory(directory: Path) -> dict:
    """Scanne un répertoire et retourne sa structure."""
    structure = {
        'name': directory.name,
        'files': [],
        'subdirs': []
    }

    for item in sorted(directory.iterdir()):
        # Ignorer les dossiers cachés
        if item.name.startswith('.'):
            continue

        if item.is_file():
            structure['files'].append({
                'name': item.name,
                'size': item.stat().st_size,
                'path': str(item.relative_to(SOURCE_DIR.parent))
            })
        elif item.is_dir():
            structure['subdirs'].append(scan_directory(item))

    return structure


def find_parent_page(client: NotionClient, page_name: str) -> str:
    """Trouve une page parent par son nom."""
    results = client.search(query=page_name, filter_type="page")

    for result in results:
        props = result.get("properties", {})
        title_prop = props.get("title", {})
        if isinstance(title_prop, dict):
            title_list = title_prop.get("title", [])
            if title_list:
                title_text = title_list[0].get("plain_text", "")
                if page_name.lower() in title_text.lower():
                    return result["id"]

    return None


def create_file_list_blocks(files: list) -> list:
    """Crée des blocs pour lister les fichiers."""
    blocks = []

    for f in files:
        icon = get_file_icon(f['name'])
        size = format_size(f['size'])
        text = f"{icon} {f['name']} ({size})"
        blocks.append({
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }
        })

    return blocks


def create_structure_in_notion(client: NotionClient, parent_page_id: str, structure: dict, level: int = 0):
    """Crée récursivement la structure dans Notion."""

    # Créer une page pour ce dossier (sauf si c'est le niveau racine qui existe déjà)
    if level == 0:
        page_id = parent_page_id
    else:
        # Créer une sous-page
        page = client.create_page(
            parent={"page_id": parent_page_id},
            properties={"title": title_property(structure['name'])}
        )
        page_id = page["id"]
        print(f"{'  ' * level}📁 Créé: {structure['name']}")

    # Ajouter les fichiers comme liste
    if structure['files']:
        blocks = []

        # Header pour les fichiers
        blocks.append(create_heading_block("📎 Fichiers à uploader", level=2))
        blocks.append(create_text_block(
            f"⚠️ Glissez-déposez les {len(structure['files'])} fichiers ci-dessous depuis votre ordinateur:"
        ))

        # Liste des fichiers
        blocks.extend(create_file_list_blocks(structure['files']))

        # Ajouter une note
        blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content":
                    "Les fichiers sont dans: .tmp/Projet Secteur Informel/"
                }}],
                "icon": {"emoji": "📂"}
            }
        })

        try:
            client.append_block_children(page_id, blocks)
        except Exception as e:
            print(f"{'  ' * level}⚠️ Erreur ajout blocs: {e}")

    # Créer les sous-dossiers récursivement
    for subdir in structure['subdirs']:
        create_structure_in_notion(client, page_id, subdir, level + 1)


def main():
    print("=" * 60)
    print("CRÉATION STRUCTURE NOTION - PROJET SECTEUR INFORMEL")
    print("=" * 60)
    print()

    # Vérifier que le dossier source existe
    if not SOURCE_DIR.exists():
        print(f"❌ Dossier source non trouvé: {SOURCE_DIR}")
        return

    print(f"📂 Dossier source: {SOURCE_DIR}")
    print()

    # Scanner la structure
    print("🔍 Scan de la structure...")
    structure = scan_directory(SOURCE_DIR)

    total_files = sum(len(s.get('files', [])) for s in [structure] + structure.get('subdirs', []))
    print(f"   {len(structure['files'])} fichiers à la racine")
    print(f"   {len(structure['subdirs'])} sous-dossiers")
    print()

    # Connexion Notion
    print("🔗 Connexion à Notion...")
    try:
        client = NotionClient()

        # Chercher si la page existe déjà
        print("🔍 Recherche de la page 'Projet Secteur Informel'...")
        parent_id = find_parent_page(client, "Projet Secteur Informel")

        if parent_id:
            print(f"✅ Page trouvée: {parent_id}")
        else:
            # Créer la page à la racine
            print("📝 Création de la page principale...")
            # On ne peut pas créer à la racine sans parent
            # Chercher un workspace ou page parent
            results = client.search(page_size=1)
            if results:
                # Utiliser le premier résultat comme parent potentiel
                # Ou créer dans une database
                print("⚠️ Impossible de créer à la racine. Veuillez créer la page 'Projet Secteur Informel' dans Notion d'abord.")
                print("   Puis relancez ce script.")
                return
            else:
                print("❌ Aucune page trouvée dans Notion. Vérifiez vos permissions API.")
                return

        # Créer la structure
        print()
        print("📝 Création de la structure...")
        create_structure_in_notion(client, parent_id, structure)

        print()
        print("=" * 60)
        print("✅ TERMINÉ!")
        print()
        print("Prochaine étape:")
        print("  1. Ouvrez Notion et allez sur la page 'Projet Secteur Informel'")
        print("  2. Pour chaque sous-page, glissez-déposez les fichiers correspondants")
        print(f"  3. Les fichiers sont dans: {SOURCE_DIR}")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
