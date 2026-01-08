#!/usr/bin/env python3
"""
Lit le contenu d'un Google Doc
"""

import os
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Scopes nécessaires
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/documents.readonly'
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

def extract_doc_id(url_or_id):
    """Extrait l'ID du document d'une URL Google Docs"""
    if 'docs.google.com' in url_or_id:
        # Format: https://docs.google.com/document/d/DOC_ID/edit
        if '/d/' in url_or_id:
            return url_or_id.split('/d/')[-1].split('/')[0]
    return url_or_id

def read_google_doc(doc_id):
    """Lit le contenu d'un Google Doc et retourne le texte"""
    creds = get_credentials()

    # Utiliser l'API Drive pour exporter le document en texte
    drive_service = build('drive', 'v3', credentials=creds)

    # Exporter en texte brut
    content = drive_service.files().export(
        fileId=doc_id,
        mimeType='text/plain'
    ).execute()

    # Décoder le contenu
    if isinstance(content, bytes):
        content = content.decode('utf-8')

    return content

def main(doc_url, output_file=None):
    """Fonction principale"""
    doc_id = extract_doc_id(doc_url)
    print(f"Reading document: {doc_id}")

    content = read_google_doc(doc_id)

    # Sauvegarder dans un fichier
    if output_file:
        output_path = Path(output_file)
    else:
        output_path = Path(__file__).parent.parent / '.tmp' / f'doc_{doc_id}.txt'

    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Document saved to: {output_path}")
    return content, output_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        doc_url = sys.argv[1]
    else:
        print("Usage: python read_google_doc.py <document_url_or_id>")
        sys.exit(1)

    main(doc_url)
