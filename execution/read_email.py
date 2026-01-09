#!/usr/bin/env python3
"""
Lit le contenu complet d'un email via Zoho Mail MCP
"""

import os
import sys
import json
import re
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from html import unescape

load_dotenv(Path(__file__).parent.parent / '.env')


class ZohoMailMCP:
    """Client Zoho Mail via MCP"""

    def __init__(self):
        self.mail_url = os.getenv("MCP_ZOHO_MAIL_URL", "")
        self.mail_key = os.getenv("MCP_ZOHO_MAIL_KEY", "")

        if not self.mail_url or not self.mail_key:
            raise ValueError("MCP_ZOHO_MAIL_URL et MCP_ZOHO_MAIL_KEY requis dans .env")

        self.mail_url = f"{self.mail_url}?key={self.mail_key}"
        self.accounts = []

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
        """Recupere tous les comptes mail configures"""
        result = self._call("tools/call", {
            "name": "ZohoMail_getMailAccounts",
            "arguments": {}
        })

        content = result.get("content", [])
        if content and isinstance(content, list):
            text = content[0].get("text", "{}")
            data = json.loads(text)
            accounts = data.get("data", [])
            self.accounts = [
                {
                    "id": acc.get("accountId"),
                    "name": acc.get("accountDisplayName", acc.get("accountName", "Unknown")),
                    "email": acc.get("incomingUserName", acc.get("primaryEmailAddress", "")),
                    "type": acc.get("type", "UNKNOWN")
                }
                for acc in accounts
                if acc.get("enabled", True)
            ]
            return self.accounts
        return []

    def list_emails_for_account(self, account_id: str, limit: int = 50):
        """Liste les emails d'un compte specifique"""
        result = self._call("tools/call", {
            "name": "ZohoMail_listEmails",
            "arguments": {
                "path_variables": {"accountId": account_id},
                "query_params": {"limit": limit, "start": 1}
            }
        })

        content = result.get("content", [])
        if content and isinstance(content, list):
            text = content[0].get("text", "{}")
            data = json.loads(text)
            return data.get("data", [])
        return []

    def get_email_by_index(self, index: int):
        """Recupere un email par son index dans la liste consolidee"""
        if not self.accounts:
            self.get_all_accounts()

        all_emails = []
        for acc in self.accounts:
            try:
                emails = self.list_emails_for_account(acc["id"], limit=50)
                for email in emails:
                    email["_source_account"] = acc["name"]
                    email["_account_id"] = acc["id"]
                all_emails.extend(emails)
            except Exception as e:
                print(f"Erreur compte {acc['name']}: {e}")

        all_emails.sort(key=lambda e: e.get("receivedTime", 0), reverse=True)

        if index < 1 or index > len(all_emails):
            raise ValueError(f"Index {index} invalide (1-{len(all_emails)})")

        return all_emails[index - 1]

    def get_email_content(self, account_id: str, folder_id: str, message_id: str):
        """Recupere le contenu complet d'un email"""
        result = self._call("tools/call", {
            "name": "ZohoMail_getMessageContent",
            "arguments": {
                "path_variables": {
                    "accountId": account_id,
                    "folderId": folder_id,
                    "messageId": message_id
                },
                "query_params": {
                    "includeBlockContent": True
                }
            }
        })

        content = result.get("content", [])
        if content and isinstance(content, list):
            text = content[0].get("text", "")

            # Debug
            if not text or text.strip() == "":
                print(f"[DEBUG] Empty response from ZohoMail_ViewMail")
                print(f"[DEBUG] Full result: {json.dumps(result, indent=2)}")
                return {}

            try:
                data = json.loads(text)
                return data.get("data", {})
            except json.JSONDecodeError as e:
                print(f"[DEBUG] JSON decode error: {e}")
                print(f"[DEBUG] Text content: {text[:200]}")
                return {}
        return {}


def clean_html(html_text):
    """Nettoie le HTML et convertit en texte brut"""
    if not html_text:
        return ""

    # Enlever les balises HTML
    text = re.sub(r'<style[^>]*>.*?</style>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '\n', text)

    # Decoder les entites HTML
    text = unescape(text)

    # Nettoyer les espaces
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)

    # Encoder en ASCII pour eviter les erreurs d'affichage
    text = text.encode('ascii', 'replace').decode('ascii')

    return text


def format_timestamp(ts):
    """Formate un timestamp"""
    if isinstance(ts, (int, float)) and ts > 0:
        dt = datetime.fromtimestamp(int(ts) / 1000)
        return dt.strftime("%Y-%m-%d %H:%M")
    return "?"


def main():
    """Fonction principale"""
    import argparse

    parser = argparse.ArgumentParser(description="Lire un email")
    parser.add_argument("index", type=int, help="Index de l'email (1-N)")
    parser.add_argument("--raw", action="store_true", help="Afficher le HTML brut")
    args = parser.parse_args()

    try:
        client = ZohoMailMCP()

        print(f"Recuperation de l'email #{args.index}...\n")

        # Recuperer l'email par index
        email_meta = client.get_email_by_index(args.index)

        account_id = email_meta["_account_id"]
        folder_id = email_meta.get("folderId", "")
        message_id = email_meta["messageId"]

        if not folder_id:
            print(f"[ERREUR] Pas de folderId trouve pour cet email")
            return 1

        # Recuperer le contenu complet
        email_full = client.get_email_content(account_id, folder_id, message_id)

        # Afficher les metadonnees
        print("=" * 70)
        print(f"SUJET: {email_full.get('subject', 'Sans sujet')}")
        print("=" * 70)
        print(f"De: {email_full.get('fromAddress', 'Inconnu')}")
        print(f"A: {email_full.get('toAddress', '')}")
        print(f"Date: {format_timestamp(email_full.get('receivedTime', 0))}")
        print(f"Compte: {email_meta['_source_account']}")
        print("=" * 70)
        print()

        # Afficher le contenu
        if args.raw:
            content = email_full.get("content", "")
            print(content)
        else:
            content_html = email_full.get("content", "")
            content_text = clean_html(content_html)

            # Limiter la longueur pour l'affichage
            if len(content_text) > 3000:
                content_text = content_text[:3000] + "\n\n[...contenu tronque...]"

            print(content_text)

        print()
        print("=" * 70)

        return 0

    except Exception as e:
        print(f"[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
