#!/usr/bin/env python3
"""
Liste le contenu d'un dossier Google Drive
"""

import os
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

# Scopes nécessaires pour lire Google Drive
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly'
]

def get_credentials():
    """Obtient les credentials Google avec OAuth2"""
    creds = None
    token_path = Path(__file__).parent.parent / 'token_drive.json'
    credentials_path = Path(__file__).parent.parent / 'credentials.json'

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds

def extract_folder_id(url_or_id):
    """Extrait l'ID du dossier d'une URL Google Drive ou retourne l'ID directement"""
    if 'drive.google.com' in url_or_id:
        # Format: https://drive.google.com/drive/u/0/folders/FOLDER_ID
        if '/folders/' in url_or_id:
            return url_or_id.split('/folders/')[-1].split('?')[0]
    return url_or_id

def list_folder_contents(folder_id, indent=0):
    """Liste récursivement le contenu d'un dossier Google Drive"""
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    results = []
    page_token = None

    while True:
        response = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType, size, modifiedTime, webViewLink)',
            pageToken=page_token,
            orderBy='folder,name'
        ).execute()

        files = response.get('files', [])

        for file in files:
            file_info = {
                'id': file['id'],
                'name': file['name'],
                'type': 'folder' if file['mimeType'] == 'application/vnd.google-apps.folder' else 'file',
                'mimeType': file['mimeType'],
                'size': file.get('size', 'N/A'),
                'modifiedTime': file.get('modifiedTime', 'N/A'),
                'link': file.get('webViewLink', ''),
                'indent': indent
            }

            results.append(file_info)

            # Si c'est un dossier, lister son contenu récursivement
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                sub_contents = list_folder_contents(file['id'], indent + 1)
                results.extend(sub_contents)

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    return results

def format_size(size):
    """Formate la taille en format lisible"""
    if size == 'N/A':
        return size
    size = int(size)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def main(folder_url):
    """Fonction principale"""
    folder_id = extract_folder_id(folder_url)
    print(f"Listing contents of folder: {folder_id}\n")
    print("=" * 80)

    contents = list_folder_contents(folder_id)

    # Affichage structuré
    for item in contents:
        indent = "  " * item['indent']
        icon = "[DIR]" if item['type'] == 'folder' else "[FILE]"
        size_str = f" ({format_size(item['size'])})" if item['type'] == 'file' and item['size'] != 'N/A' else ""

        print(f"{indent}{icon} {item['name']}{size_str}")

    print("\n" + "=" * 80)
    print(f"Total items: {len(contents)}")

    # Exporter en JSON pour analyse
    output_path = Path(__file__).parent.parent / '.tmp' / 'drive_contents.json'
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(contents, f, indent=2, ensure_ascii=False)

    print(f"\nDetailed JSON exported to: {output_path}")

    return contents

if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder_url = sys.argv[1]
    else:
        # Dossier par défaut: Projet Secteur Informel
        folder_url = "https://drive.google.com/drive/u/0/folders/1wu75efUX-McV_cgKG4Qfs86OmU354Z1J"

    main(folder_url)
