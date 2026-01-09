#!/usr/bin/env python3
"""
Crée une page Notion pour une réunion GR International.

Usage:
    python create_gr_meeting_page.py --date 2026-01-08 --chat-file meeting_chat.txt
    python create_gr_meeting_page.py --date 2026-01-15 --chat-file chat.txt --presenter "Jessica Legault" --topic "Propreté professionnelle"

Examples:
    python create_gr_meeting_page.py --date 2026-01-08 --chat-file .tmp/gr_chat_20260108.txt
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Configuration
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
if not NOTION_TOKEN:
    raise ValueError("NOTION_TOKEN environment variable is required")
NOTION_VERSION = '2022-06-28'
NOTION_DATABASE_ID = os.getenv('NOTION_GR_DATABASE_ID', '1c441b52-d187-80f9-b3f9-ff470d73a72d')

def notion_request(method: str, endpoint: str, data: dict = None) -> dict:
    """Fait une requête à l'API Notion"""
    url = f"https://api.notion.com/v1{endpoint}"
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': NOTION_VERSION,
        'Content-Type': 'application/json'
    }

    if method == 'POST':
        response = requests.post(url, headers=headers, json=data)
    elif method == 'GET':
        response = requests.get(url, headers=headers)
    else:
        raise ValueError(f"Unsupported method: {method}")

    response.raise_for_status()
    return response.json()

def parse_chat_file(chat_file: Path) -> Tuple[List[Dict], List[Dict]]:
    """
    Parse le fichier chat et extrait:
    - Les messages du chat
    - Les contacts partagés
    """
    with open(chat_file, 'r', encoding='utf-8') as f:
        content = f.read()

    chat_messages = []
    contacts = []

    lines = content.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Détecter les messages (format: "Nom: message")
        if ':' in line:
            parts = line.split(':', 1)
            author = parts[0].strip()
            message = parts[1].strip()

            # Détecter si c'est un contact (contient téléphone, email, URL)
            is_contact = any([
                '@' in message,
                'http://' in message,
                'https://' in message,
                any(c.isdigit() for c in message) and ('-' in message or '.' in message)
            ])

            if is_contact:
                contacts.append({
                    'author': author,
                    'content': message
                })
            else:
                chat_messages.append({
                    'author': author,
                    'message': message
                })

    return chat_messages, contacts

def create_chat_blocks(chat_messages: List[Dict], presenter: str = None, topic: str = None) -> List[Dict]:
    """Crée les blocs Notion pour le chat"""
    blocks = [
        {
            'object': 'block',
            'type': 'heading_2',
            'heading_2': {
                'rich_text': [{'type': 'text', 'text': {'content': 'Chat de la réunion'}}]
            }
        }
    ]

    # Ajouter heading pour boîte à outils si présent
    if presenter and topic:
        blocks.append({
            'object': 'block',
            'type': 'heading_3',
            'heading_3': {
                'rich_text': [{'type': 'text', 'text': {'content': f'Boîte à outils: {presenter} - {topic}'}}]
            }
        })

    # Ajouter les messages
    for msg in chat_messages:
        is_special = any(word in msg['message'].lower() for word in ['énergie', 'électricité', 'intéressant', 'bien'])

        blocks.append({
            'object': 'block',
            'type': 'paragraph',
            'paragraph': {
                'rich_text': [
                    {
                        'type': 'text',
                        'text': {'content': f"{msg['author']}: {msg['message']}"},
                        'annotations': {'italic': is_special}
                    }
                ]
            }
        })

    return blocks

def create_contacts_blocks(contacts: List[Dict]) -> List[Dict]:
    """Crée les blocs Notion pour les contacts partagés"""
    if not contacts:
        return []

    blocks = [
        {
            'object': 'block',
            'type': 'divider',
            'divider': {}
        },
        {
            'object': 'block',
            'type': 'heading_3',
            'heading_3': {
                'rich_text': [{'type': 'text', 'text': {'content': 'Contacts partagés'}}]
            }
        }
    ]

    # Grouper par auteur
    contacts_by_author = {}
    for contact in contacts:
        author = contact['author']
        if author not in contacts_by_author:
            contacts_by_author[author] = []
        contacts_by_author[author].append(contact['content'])

    # Créer les blocs
    for author, info_list in contacts_by_author.items():
        full_info = ' '.join(info_list)

        # Extraire le nom d'entreprise si présent (pattern: "Nom - Entreprise:")
        if ' - ' in author:
            display_name = author
        else:
            display_name = author

        # Détecter les URLs
        has_url = 'http' in full_info
        url = None
        if has_url:
            import re
            url_match = re.search(r'https?://[^\s,]+', full_info)
            if url_match:
                url = url_match.group(0)

        rich_text = [
            {
                'type': 'text',
                'text': {'content': f'{display_name}: ', 'link': None},
                'annotations': {'bold': True}
            },
            {
                'type': 'text',
                'text': {'content': full_info, 'link': {'url': url} if url else None}
            }
        ]

        blocks.append({
            'object': 'block',
            'type': 'bulleted_list_item',
            'bulleted_list_item': {
                'rich_text': rich_text
            }
        })

    return blocks

def create_meeting_page(date: str, chat_file: Path, presenter: str = None, topic: str = None) -> str:
    """
    Crée une page Notion pour la réunion GR.
    Retourne l'ID de la page créée.
    """
    # Parser le fichier chat
    print(f"Parsing chat file: {chat_file}")
    chat_messages, contacts = parse_chat_file(chat_file)

    print(f"Found {len(chat_messages)} chat messages")
    print(f"Found {len(contacts)} contacts")

    # Créer le titre
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    title = f"Réunion GR International Vaudreuil-Dorion 1 - {date_obj.strftime('%-d %B %Y')}"

    # Créer les blocs
    blocks = []
    blocks.extend(create_chat_blocks(chat_messages, presenter, topic))
    blocks.extend(create_contacts_blocks(contacts))

    # Créer la page
    page_payload = {
        'parent': {
            'database_id': NOTION_DATABASE_ID
        },
        'properties': {
            'Session Title': {
                'title': [
                    {
                        'text': {
                            'content': title
                        }
                    }
                ]
            },
            'Date': {
                'date': {
                    'start': date
                }
            }
        },
        'children': blocks
    }

    print(f"\nCreating Notion page...")
    print(f"Title: {title}")
    print(f"Date: {date}")

    response = notion_request('POST', '/pages', page_payload)
    page_id = response['id']

    print(f"\n✅ Page created successfully!")
    print(f"Page ID: {page_id}")
    print(f"URL: https://www.notion.so/{page_id.replace('-', '')}")

    return page_id

def main():
    parser = argparse.ArgumentParser(
        description='Crée une page Notion pour une réunion GR International',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_gr_meeting_page.py --date 2026-01-08 --chat-file .tmp/gr_chat.txt
  python create_gr_meeting_page.py --date 2026-01-15 --chat-file chat.txt --presenter "Jessica Legault" --topic "Propreté professionnelle"
        """
    )

    parser.add_argument(
        '--date',
        required=True,
        help='Date de la réunion (format: YYYY-MM-DD)'
    )

    parser.add_argument(
        '--chat-file',
        required=True,
        type=Path,
        help='Fichier contenant le chat de la réunion'
    )

    parser.add_argument(
        '--presenter',
        help='Nom du présentateur de la boîte à outils'
    )

    parser.add_argument(
        '--topic',
        help='Sujet de la boîte à outils'
    )

    args = parser.parse_args()

    # Vérifier que le fichier existe
    if not args.chat_file.exists():
        print(f"❌ Error: File not found: {args.chat_file}")
        sys.exit(1)

    # Vérifier le format de la date
    try:
        datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        print(f"❌ Error: Invalid date format. Use YYYY-MM-DD")
        sys.exit(1)

    # Créer la page
    try:
        page_id = create_meeting_page(
            date=args.date,
            chat_file=args.chat_file,
            presenter=args.presenter,
            topic=args.topic
        )

        print(f"\n📝 Next steps:")
        print(f"1. Add detailed meeting notes to the page")
        print(f"2. Generate analysis with: python generate_meeting_analysis.py --page-id {page_id}")
        print(f"3. Sync participant names with: python sync_participant_names.py --page-ids {page_id}")

    except Exception as e:
        print(f"\n❌ Error creating page: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
