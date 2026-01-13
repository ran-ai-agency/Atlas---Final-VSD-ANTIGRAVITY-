#!/usr/bin/env python3
"""
Recherche Gmail pour Patrick RBC
"""
import sys
from pathlib import Path

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
            print("Rafraichissement du token...")
            creds.refresh(Request())
        else:
            print("Autorisation Gmail requise...")
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=8080)

        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def search_emails(service, query, max_results=50):
    """Rechercher des emails"""
    print(f"\nRecherche: {query}")
    print("-" * 60)

    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        print("Aucun email trouve.")
        return []

    print(f"Trouve: {len(messages)} email(s)\n")

    for i, msg in enumerate(messages, 1):
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['Date', 'From', 'To', 'Subject']
        ).execute()

        headers = {h['name']: h['value'] for h in msg_data['payload']['headers']}

        subject = headers.get('Subject', '?')
        sender = headers.get('From', '?')
        date = headers.get('Date', '?')

        # Clean for console
        try:
            subject = subject.encode('cp1252', 'replace').decode('cp1252')[:60]
            sender = sender.encode('cp1252', 'replace').decode('cp1252')
        except:
            pass

        print(f"{i}. {subject}")
        print(f"   De: {sender}")
        print(f"   Date: {date}")
        print(f"   ID: {msg['id']}")
        print()

    return messages

def main():
    print("=" * 60)
    print("  RECHERCHE GMAIL: RBC / PATRICK")
    print("=" * 60)

    service = get_gmail_service()

    # Recherches RBC
    queries = [
        'from:rbc',           # Tous les emails DE RBC
        'to:rbc',             # Tous les emails VERS RBC
        'Patrick RBC',        # Patrick + RBC
        'from:patrick rbc',   # Patrick expéditeur + RBC
        'banque royale',      # Banque Royale
    ]

    for query in queries:
        search_emails(service, query, max_results=30)
        print("=" * 60)

if __name__ == "__main__":
    main()
