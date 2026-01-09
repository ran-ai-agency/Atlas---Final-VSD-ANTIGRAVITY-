#!/usr/bin/env python3
"""
Liste les emails envoyés récents
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')


class ZohoMailMCP:
    """Client Zoho Mail via MCP"""

    def __init__(self):
        self.mail_url = os.getenv("MCP_ZOHO_MAIL_URL", "")
        self.mail_key = os.getenv("MCP_ZOHO_MAIL_KEY", "")

        if not self.mail_url or not self.mail_key:
            raise ValueError("MCP_ZOHO_MAIL_URL et MCP_ZOHO_MAIL_KEY requis")

        self.mail_url = f"{self.mail_url}?key={self.mail_key}"

    def _call(self, method: str, params: dict):
        """Appelle le MCP"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }

        response = requests.post(
            self.mail_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        response.raise_for_status()

        result = response.json()
        if "error" in result:
            raise Exception(f"MCP Error: {result['error']}")

        return result.get("result", {})

    def get_all_accounts(self):
        """Recupere tous les comptes mail"""
        result = self._call("tools/call", {
            "name": "ZohoMail_getMailAccounts",
            "arguments": {}
        })

        content = result.get("content", [])
        if content and isinstance(content, list):
            text = content[0].get("text", "{}")
            data = json.loads(text)
            accounts = data.get("data", [])
            return [
                {
                    "id": acc.get("accountId"),
                    "name": acc.get("accountDisplayName", "Unknown"),
                    "email": acc.get("primaryEmailAddress", "")
                }
                for acc in accounts
                if acc.get("enabled", True)
            ]
        return []

    def get_folders(self, account_id: str):
        """Liste les dossiers d'un compte"""
        result = self._call("tools/call", {
            "name": "ZohoMail_getFolders",
            "arguments": {
                "path_variables": {
                    "accountId": account_id
                }
            }
        })

        content = result.get("content", [])
        if content and isinstance(content, list):
            text = content[0].get("text", "{}")
            data = json.loads(text)
            return data.get("data", [])
        return []

    def list_emails_from_folder(self, account_id: str, folder_id: str, limit: int = 20):
        """Liste les emails d'un dossier specifique"""
        result = self._call("tools/call", {
            "name": "ZohoMail_listEmails",
            "arguments": {
                "path_variables": {
                    "accountId": account_id,
                    "folderId": folder_id
                },
                "query_params": {
                    "limit": limit,
                    "start": 1
                }
            }
        })

        content = result.get("content", [])
        if content and isinstance(content, list):
            text = content[0].get("text", "{}")
            data = json.loads(text)
            return data.get("data", [])
        return []


def format_timestamp(ts):
    """Formate un timestamp"""
    if isinstance(ts, (int, float)) and ts > 0:
        dt = datetime.fromtimestamp(int(ts) / 1000)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "?"


def clean_text(text):
    """Nettoie le texte"""
    if not text:
        return ""
    text = text[:100].replace('\n', ' ').replace('\r', ' ')
    try:
        text = text.encode('ascii', 'replace').decode('ascii')
    except:
        pass
    return text


def main():
    """Fonction principale"""
    import argparse

    parser = argparse.ArgumentParser(description="Liste des emails envoyes")
    parser.add_argument("--limit", type=int, default=20, help="Nombre d'emails (defaut: 20)")
    args = parser.parse_args()

    try:
        client = ZohoMailMCP()

        print("Recuperation des comptes...\n")
        accounts = client.get_all_accounts()

        if not accounts:
            print("Aucun compte trouve")
            return 1

        all_sent = []

        for account in accounts:
            account_id = account["id"]
            account_name = account["name"]
            account_email = account["email"]

            print(f"Compte: {account_name} ({account_email})")

            # Recuperer les dossiers
            folders = client.get_folders(account_id)

            # Trouver le dossier "Sent" / "Envoyes"
            sent_folder = None
            for folder in folders:
                folder_name = folder.get("folderName", "").lower()
                if folder_name in ["sent", "envoyes", "envoyés", "sent items"]:
                    sent_folder = folder
                    break

            if not sent_folder:
                print(f"  Dossier 'Envoyes' non trouve")
                print(f"  Dossiers disponibles: {[f.get('folderName') for f in folders]}")
                continue

            folder_id = sent_folder.get("folderId")
            print(f"  Dossier trouve: {sent_folder.get('folderName')} (ID: {folder_id})")

            # Lister les emails envoyes
            sent_emails = client.list_emails_from_folder(account_id, folder_id, limit=args.limit)
            print(f"  {len(sent_emails)} emails envoyes recuperes\n")

            for email in sent_emails:
                email["_account"] = account_name
                all_sent.append(email)

        if not all_sent:
            print("Aucun email envoye trouve")
            return 0

        # Trier par date decroissante
        all_sent.sort(key=lambda e: e.get("sentTime", 0), reverse=True)

        print("=" * 80)
        print("EMAILS ENVOYES RECENTS")
        print("=" * 80)
        print()

        for i, email in enumerate(all_sent[:20], 1):
            subject = clean_text(email.get("subject", "Sans sujet"))
            to_addr = clean_text(email.get("toAddress", ""))
            sent_time = format_timestamp(email.get("sentTime", 0))
            account = email.get("_account", "")

            print(f"{i:2}. [{sent_time}]")
            print(f"    A: {to_addr}")
            print(f"    Sujet: {subject}")
            print(f"    Compte: {account}")
            print()

        return 0

    except Exception as e:
        print(f"[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
