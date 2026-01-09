#!/usr/bin/env python3
"""
Repond a un email via sendReplyEmail de Zoho Mail MCP
"""

import os
import sys
import json
import requests
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
            self.accounts = [
                {
                    "id": acc.get("accountId"),
                    "name": acc.get("accountDisplayName", "Unknown"),
                    "email": acc.get("primaryEmailAddress", "")
                }
                for acc in accounts
                if acc.get("enabled", True)
            ]
            return self.accounts
        return []

    def list_emails_for_account(self, account_id: str, limit: int = 50):
        """Liste les emails d'un compte"""
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
        """Recupere un email par son index"""
        if not self.accounts:
            self.get_all_accounts()

        all_emails = []
        for acc in self.accounts:
            try:
                emails = self.list_emails_for_account(acc["id"], limit=50)
                for email in emails:
                    email["_account_id"] = acc["id"]
                    email["_account_name"] = acc["name"]
                all_emails.extend(emails)
            except Exception as e:
                print(f"Erreur compte {acc['name']}: {e}")

        all_emails.sort(key=lambda e: e.get("receivedTime", 0), reverse=True)

        if index < 1 or index > len(all_emails):
            raise ValueError(f"Index {index} invalide (1-{len(all_emails)})")

        return all_emails[index - 1]

    def send_reply(self, account_id: str, message_id: str, content: str):
        """Repond a un email avec sendReplyEmail"""
        result = self._call("tools/call", {
            "name": "ZohoMail_sendReplyEmail",
            "arguments": {
                "path_variables": {
                    "accountId": account_id,
                    "messageId": message_id
                },
                "body": {
                    "action": "reply",
                    "content": content,
                    "mailFormat": "plaintext"
                }
            }
        })

        return result


def main():
    """Fonction principale"""
    import argparse

    parser = argparse.ArgumentParser(description="Repondre a un email")
    parser.add_argument("index", type=int, help="Index de l'email auquel repondre (1-N)")
    parser.add_argument("--content", required=True, help="Contenu de la reponse")
    args = parser.parse_args()

    try:
        client = ZohoMailMCP()

        print(f"Recuperation de l'email #{args.index}...\n")

        # Recuperer l'email par index
        email = client.get_email_by_index(args.index)

        account_id = email["_account_id"]
        folder_id = email.get("folderId", "")
        message_id = email["messageId"]
        subject = email.get("subject", "")
        sender = email.get("fromAddress", "")

        if not folder_id:
            print(f"[ERREUR] Pas de folderId pour cet email")
            return 1

        print(f"Email original:")
        print(f"  De: {sender}")
        print(f"  Sujet: {subject}")
        print(f"  Compte: {email['_account_name']}")
        print()
        print(f"Envoi de la reponse...")
        print(f"  Contenu: {args.content}")
        print()

        # Envoyer la reponse
        result = client.send_reply(account_id, message_id, args.content)

        print("[OK] Reponse envoyee avec succes!")
        print(json.dumps(result, indent=2))

        return 0

    except Exception as e:
        print(f"[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
