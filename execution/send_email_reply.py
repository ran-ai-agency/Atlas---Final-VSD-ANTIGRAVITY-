#!/usr/bin/env python3
"""
Envoie un email via Zoho Mail MCP
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
            raise ValueError("MCP_ZOHO_MAIL_URL et MCP_ZOHO_MAIL_KEY requis dans .env")

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

    def get_default_account(self):
        """Recupere le compte par defaut"""
        result = self._call("tools/call", {
            "name": "ZohoMail_getMailAccounts",
            "arguments": {}
        })

        content = result.get("content", [])
        if content and isinstance(content, list):
            text = content[0].get("text", "{}")
            data = json.loads(text)
            accounts = data.get("data", [])
            if accounts:
                return accounts[0].get("accountId")
        return None

    def send_email(self, to_address: str, subject: str, content: str, account_id: str = None, from_address: str = None):
        """Envoie un email"""

        if not account_id:
            account_id = self.get_default_account()
            if not account_id:
                raise Exception("Impossible de trouver un compte mail")

        body = {
            "toAddress": to_address,
            "subject": subject,
            "content": content,
            "mailFormat": "plaintext"
        }

        if from_address:
            body["fromAddress"] = from_address

        result = self._call("tools/call", {
            "name": "ZohoMail_sendEmail",
            "arguments": {
                "path_variables": {
                    "accountId": account_id
                },
                "body": body
            }
        })

        return result


def main():
    """Fonction principale"""
    import argparse

    parser = argparse.ArgumentParser(description="Envoyer un email")
    parser.add_argument("--to", required=True, help="Destinataire")
    parser.add_argument("--subject", required=True, help="Sujet")
    parser.add_argument("--content", required=True, help="Contenu")
    parser.add_argument("--from", dest="from_address", help="Adresse expediteur (optionnel)")
    args = parser.parse_args()

    try:
        client = ZohoMailMCP()

        print(f"Envoi de l'email a {args.to}...")
        print(f"Sujet: {args.subject}")
        print()

        result = client.send_email(
            to_address=args.to,
            subject=args.subject,
            content=args.content,
            from_address=args.from_address
        )

        print("[OK] Email envoye avec succes!")
        print(json.dumps(result, indent=2))

        return 0

    except Exception as e:
        print(f"[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
