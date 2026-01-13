#!/usr/bin/env python3
"""
Script pour autoriser l'accès Gmail et chercher des emails
"""
import sys
import json
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_PATH = Path(__file__).parent.parent / 'gmail_token.json'
CREDS_PATH = Path(__file__).parent.parent / 'credentials.json'

def get_gmail_service():
    """Obtenir le service Gmail avec autorisation"""
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Rafraîchissement du token...")
            creds.refresh(Request())
        else:
            print("Autorisation Gmail requise...")
            print("Une fenêtre de navigateur va s'ouvrir.")
            print()
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=8080)

        # Sauvegarder le token
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
        print(f"Token sauvegardé: {TOKEN_PATH}")

    return build('gmail', 'v1', credentials=creds)

def search_emails(service, query, max_results=20):
    """Rechercher des emails"""
    print(f"\nRecherche: {query}")
    print("-" * 50)

    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        print("Aucun email trouvé.")
        return []

    print(f"Trouvé: {len(messages)} email(s)\n")

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['Date', 'From', 'To', 'Subject']
        ).execute()

        headers = {h['name']: h['value'] for h in msg_data['payload']['headers']}

        print(f"Date: {headers.get('Date', '?')}")
        print(f"De: {headers.get('From', '?')}")
        print(f"À: {headers.get('To', '?')}")
        print(f"Sujet: {headers.get('Subject', '?')}")
        print()

    return messages

def main():
    print("=" * 50)
    print("  RECHERCHE EMAIL GMAIL")
    print("=" * 50)
    print()

    service = get_gmail_service()

    # Rechercher emails avec Sébastien Vachon
    queries = [
        'to:sebastien@solutioncomptabilite.com',
        'from:sebastien@solutioncomptabilite.com',
        'vachon comptable',
        'solution comptabilite'
    ]

    for query in queries:
        search_emails(service, query)
        print("=" * 50)

if __name__ == "__main__":
    main()
