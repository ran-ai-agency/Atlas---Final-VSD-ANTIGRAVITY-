#!/usr/bin/env python3
"""
Liste les emails recents de tous les comptes Zoho Mail
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

    def list_emails_for_account(self, account_id: str, limit: int = 20):
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

    def list_all_recent_emails(self, limit_per_account: int = 20):
        """Liste les emails recents de TOUS les comptes"""
        if not self.accounts:
            self.get_all_accounts()

        all_emails = []
        for acc in self.accounts:
            acc_id = acc["id"]
            acc_name = acc["name"]

            try:
                emails = self.list_emails_for_account(acc_id, limit=limit_per_account)
                for email in emails:
                    email["_source_account"] = acc_name
                    email["_source_email"] = acc["email"]
                all_emails.extend(emails)
            except Exception as e:
                print(f"Erreur compte {acc_name}: {e}")

        # Trier par date decroissante
        all_emails.sort(key=lambda e: e.get("receivedTime", 0), reverse=True)
        return all_emails


def format_timestamp(ts):
    """Formate un timestamp en date lisible"""
    if isinstance(ts, (int, float)) and ts > 0:
        dt = datetime.fromtimestamp(int(ts) / 1000)
        # Calculer le temps ecoule
        now = datetime.now()
        delta = now - dt

        if delta.days == 0:
            if delta.seconds < 3600:
                mins = delta.seconds // 60
                return f"il y a {mins} min"
            else:
                hours = delta.seconds // 3600
                return f"il y a {hours}h"
        elif delta.days == 1:
            return "hier " + dt.strftime("%H:%M")
        elif delta.days < 7:
            return dt.strftime("%A %H:%M")
        else:
            return dt.strftime("%d/%m/%Y %H:%M")
    return "?"


def clean_text(text):
    """Nettoie le texte pour l'affichage console"""
    if not text:
        return ""
    # Limiter la longueur et enlever les caracteres problematiques
    text = text[:80].replace('\n', ' ').replace('\r', ' ')
    # Encoder en ASCII en remplacant les caracteres non-ASCII
    try:
        text = text.encode('ascii', 'replace').decode('ascii')
    except:
        pass
    return text


def main():
    """Fonction principale"""
    import argparse

    parser = argparse.ArgumentParser(description="Liste des emails recents")
    parser.add_argument("--limit", type=int, default=10, help="Nombre d'emails par compte (defaut: 10)")
    args = parser.parse_args()

    try:
        client = ZohoMailMCP()

        print(f"=== Derniers emails (limite: {args.limit} par compte) ===\n")

        emails = client.list_all_recent_emails(limit_per_account=args.limit)

        if not emails:
            print("Aucun email trouve.\n")
            return 0

        for i, email in enumerate(emails[:30], 1):  # Top 30
            subject = clean_text(email.get("subject", "Sans sujet"))
            sender = clean_text(email.get("sender", "Inconnu"))
            account = clean_text(email.get("_source_account", ""))
            time_str = format_timestamp(email.get("receivedTime", 0))

            # Indicateurs
            is_unread = "*" if not email.get("isRead", False) else " "
            has_attachment = "[+]" if email.get("hasAttachment", False) else ""

            print(f"{i:2}. {is_unread} [{time_str:15}] {subject}")
            print(f"    De: {sender}")
            print(f"    Compte: {account} {has_attachment}")
            print()

        print(f"Total: {len(emails)} emails recuperes\n")
        return 0

    except Exception as e:
        print(f"[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
