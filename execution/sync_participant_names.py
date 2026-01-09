#!/usr/bin/env python3
"""
Synchronise les noms des participants entre plusieurs pages Notion.

Usage:
    python sync_participant_names.py --page-ids <id1> <id2> [...]
    python sync_participant_names.py --page-ids <id1> <id2> --dry-run

Examples:
    python sync_participant_names.py --page-ids 2e241b52-d187-814a-88a7-fa99519cdbb9 2e241b52-d187-8102-bd74-e3fc5f84d4d7
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from typing import List, Dict, Tuple

# Configuration
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
if not NOTION_TOKEN:
    raise ValueError("NOTION_TOKEN environment variable is required")
NOTION_VERSION = '2022-06-28'
RATE_LIMIT_DELAY = 0.3  # secondes entre chaque requête

# Charger la référence des participants
SCRIPT_DIR = Path(__file__).parent
PARTICIPANTS_FILE = SCRIPT_DIR / 'participants_reference.json'

def load_participants_reference() -> Dict:
    """Charge la référence des participants"""
    with open(PARTICIPANTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def notion_request(method: str, endpoint: str, data: dict = None) -> dict:
    """Fait une requête à l'API Notion"""
    url = f"https://api.notion.com/v1{endpoint}"
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': NOTION_VERSION,
        'Content-Type': 'application/json'
    }

    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'PATCH':
        response = requests.patch(url, headers=headers, json=data)
    else:
        raise ValueError(f"Unsupported method: {method}")

    response.raise_for_status()
    return response.json()

def get_page_blocks(page_id: str) -> List[Dict]:
    """Récupère tous les blocs d'une page Notion"""
    blocks = []
    has_more = True
    start_cursor = None

    while has_more:
        endpoint = f"/blocks/{page_id}/children?page_size=100"
        if start_cursor:
            endpoint += f"&start_cursor={start_cursor}"

        response = notion_request('GET', endpoint)
        blocks.extend(response['results'])

        has_more = response.get('has_more', False)
        start_cursor = response.get('next_cursor')

        if has_more:
            time.sleep(RATE_LIMIT_DELAY)

    return blocks

def extract_text_from_block(block: Dict) -> str:
    """Extrait le texte d'un bloc Notion"""
    block_type = block['type']
    if block_type not in block:
        return ''

    rich_texts = block[block_type].get('rich_text', [])
    return ' '.join([rt['text']['content'] for rt in rich_texts if rt['type'] == 'text'])

def apply_name_corrections(text: str, corrections: Dict[str, str]) -> Tuple[str, List[str]]:
    """
    Applique les corrections de noms à un texte.
    Retourne le texte corrigé et la liste des corrections appliquées.
    """
    corrected_text = text
    applied_corrections = []

    for wrong_name, correct_name in corrections.items():
        if wrong_name in corrected_text:
            corrected_text = corrected_text.replace(wrong_name, correct_name)
            applied_corrections.append(f"{wrong_name} → {correct_name}")

    return corrected_text, applied_corrections

def update_block_text(block_id: str, block_type: str, rich_texts: List[Dict]) -> bool:
    """Met à jour le texte d'un bloc Notion"""
    try:
        payload = {
            block_type: {
                'rich_text': rich_texts
            }
        }

        notion_request('PATCH', f'/blocks/{block_id}', payload)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to update block {block_id}: {e}")
        return False

def sync_page_names(page_id: str, corrections: Dict[str, str], dry_run: bool = False) -> Dict:
    """
    Synchronise les noms dans une page Notion.
    Retourne un dict avec les stats de correction.
    """
    print(f"\n{'='*60}")
    print(f"Processing page: {page_id}")
    print(f"{'='*60}")

    # Télécharger les blocs
    print("Downloading blocks...")
    blocks = get_page_blocks(page_id)
    print(f"Found {len(blocks)} blocks")

    # Analyser et corriger
    stats = {
        'blocks_checked': 0,
        'blocks_corrected': 0,
        'corrections_applied': []
    }

    for block in blocks:
        block_id = block['id']
        block_type = block['type']

        # Skip types sans texte
        if block_type not in block:
            continue

        rich_texts = block[block_type].get('rich_text', [])
        if not rich_texts:
            continue

        stats['blocks_checked'] += 1

        # Vérifier si corrections nécessaires
        modified = False
        for rt in rich_texts:
            if rt['type'] != 'text':
                continue

            original_text = rt['text']['content']
            corrected_text, applied = apply_name_corrections(original_text, corrections)

            if corrected_text != original_text:
                rt['text']['content'] = corrected_text
                modified = True
                stats['corrections_applied'].extend(applied)

        if modified:
            stats['blocks_corrected'] += 1

            if dry_run:
                print(f"[DRY RUN] Would update block {block_id}")
            else:
                print(f"[{stats['blocks_corrected']}] Updating block {block_id}")
                success = update_block_text(block_id, block_type, rich_texts)

                if success:
                    time.sleep(RATE_LIMIT_DELAY)
                else:
                    stats['blocks_corrected'] -= 1

    return stats

def main():
    parser = argparse.ArgumentParser(
        description='Synchronise les noms des participants GR entre pages Notion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sync_participant_names.py --page-ids 2e241b52-d187-814a-88a7-fa99519cdbb9 2e241b52-d187-8102-bd74-e3fc5f84d4d7
  python sync_participant_names.py --page-ids <id1> <id2> --dry-run
        """
    )

    parser.add_argument(
        '--page-ids',
        nargs='+',
        required=True,
        help='IDs des pages Notion à synchroniser'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Mode simulation (ne modifie pas les pages)'
    )

    args = parser.parse_args()

    # Charger les corrections de référence
    print("Loading participant reference...")
    reference = load_participants_reference()
    corrections = reference.get('erreurs_courantes', {})

    print(f"\nCorrections à appliquer:")
    for wrong, correct in corrections.items():
        print(f"  • {wrong} → {correct}")

    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made")

    # Traiter chaque page
    total_stats = {
        'pages_processed': 0,
        'total_blocks_checked': 0,
        'total_blocks_corrected': 0,
        'all_corrections': []
    }

    for page_id in args.page_ids:
        stats = sync_page_names(page_id, corrections, args.dry_run)

        total_stats['pages_processed'] += 1
        total_stats['total_blocks_checked'] += stats['blocks_checked']
        total_stats['total_blocks_corrected'] += stats['blocks_corrected']
        total_stats['all_corrections'].extend(stats['corrections_applied'])

        print(f"\nPage stats:")
        print(f"  Blocks checked: {stats['blocks_checked']}")
        print(f"  Blocks corrected: {stats['blocks_corrected']}")
        print(f"  Corrections applied: {len(stats['corrections_applied'])}")

    # Résumé final
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Pages processed: {total_stats['pages_processed']}")
    print(f"Total blocks checked: {total_stats['total_blocks_checked']}")
    print(f"Total blocks corrected: {total_stats['total_blocks_corrected']}")
    print(f"Total corrections: {len(total_stats['all_corrections'])}")

    if total_stats['all_corrections']:
        print(f"\nCorrections breakdown:")
        from collections import Counter
        correction_counts = Counter(total_stats['all_corrections'])
        for correction, count in correction_counts.most_common():
            print(f"  • {correction}: {count}×")

    if args.dry_run:
        print("\n⚠️  This was a DRY RUN. No changes were made.")
        print("Run without --dry-run to apply changes.")
    else:
        print("\n✅ All corrections applied successfully!")

if __name__ == '__main__':
    main()
