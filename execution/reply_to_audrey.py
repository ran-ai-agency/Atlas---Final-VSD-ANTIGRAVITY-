#!/usr/bin/env python3
"""
Repond specifiquement a l'email d'Audrey Gagnon avec verification
"""

import os
import sys
import json
import requests
import time
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
            return data.get("data", [])
        return []

    def search_email_from_sender(self, sender_email: str):
        """Recherche le dernier email d'un expediteur specifique"""
        accounts = self.get_all_accounts()

        for account in accounts:
            account_id = account.get("accountId")
            account_name = account.get("accountDisplayName", "Unknown")

            print(f"Recherche dans compte: {account_name}")

            try:
                # Lister les emails recents
                result = self._call("tools/call", {
                    "name": "ZohoMail_listEmails",
                    "arguments": {
                        "path_variables": {"accountId": account_id},
                        "query_params": {"limit": 100, "start": 1}
                    }
                })

                content = result.get("content", [])
                if content and isinstance(content, list):
                    text = content[0].get("text", "{}")
                    data = json.loads(text)
                    emails = data.get("data", [])

                    # Chercher l'email de l'expediteur
                    for email in emails:
                        from_addr = email.get("fromAddress", "").lower()
                        if sender_email.lower() in from_addr:
                            email["_account_id"] = account_id
                            email["_account_name"] = account_name
                            return email

            except Exception as e:
                print(f"  Erreur: {e}")

        return None

    def send_reply(self, account_id: str, message_id: str, content: str):
        """Repond a un email"""
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

        content = result.get("content", [])
        if content and isinstance(content, list):
            text = content[0].get("text", "{}")
            return json.loads(text)
        return {}

    def verify_sent_email(self, account_id: str, to_email: str, minutes_ago: int = 5):
        """Verifie si un email a ete envoye recemment"""
        print(f"\nVerification dans les emails envoyes...")

        try:
            # Lister les emails envoyes
            result = self._call("tools/call", {
                "name": "ZohoMail_listEmails",
                "arguments": {
                    "path_variables": {"accountId": account_id},
                    "query_params": {
                        "limit": 20,
                        "start": 1,
                        "includesent": True
                    }
                }
            })

            content = result.get("content", [])
            if content and isinstance(content, list):
                text = content[0].get("text", "{}")
                data = json.loads(text)
                emails = data.get("data", [])

                # Chercher un email recent au destinataire
                now_ts = time.time() * 1000
                cutoff_ts = now_ts - (minutes_ago * 60 * 1000)

                for email in emails:
                    to_addr = email.get("toAddress", "").lower()
                    sent_time = email.get("sentTime", 0)

                    if to_email.lower() in to_addr and sent_time > cutoff_ts:
                        return email

        except Exception as e:
            print(f"  Erreur verification: {e}")

        return None


def main():
    """Fonction principale"""
    AUDREY_EMAIL = "allo@dagstudio.co"
    REPLY_CONTENT = "Merci"

    try:
        client = ZohoMailMCP()

        print("=" * 70)
        print("REPONSE A AUDREY GAGNON")
        print("=" * 70)
        print()

        # 1. Rechercher l'email d'Audrey
        print(f"Etape 1: Recherche de l'email de {AUDREY_EMAIL}...")
        email = client.search_email_from_sender(AUDREY_EMAIL)

        if not email:
            print(f"\n[ERREUR] Aucun email trouve de {AUDREY_EMAIL}")
            return 1

        # 2. Afficher les details
        print(f"\n[OK] Email trouve!")
        print(f"  De: {email.get('fromAddress')}")
        print(f"  Sujet: {email.get('subject', 'Sans sujet')}")

        received_time = email.get('receivedTime', 0)
        if isinstance(received_time, str):
            try:
                received_time = int(received_time)
            except:
                received_time = 0

        if received_time > 0:
            date_str = datetime.fromtimestamp(received_time / 1000).strftime('%Y-%m-%d %H:%M')
        else:
            date_str = "Inconnue"

        print(f"  Date: {date_str}")
        print(f"  Compte: {email['_account_name']}")
        print()

        # 3. Confirmation
        account_id = email["_account_id"]
        message_id = email["messageId"]

        print(f"Etape 2: Envoi de la reponse...")
        print(f"  Contenu: \"{REPLY_CONTENT}\"")
        print()

        # 4. Envoyer
        result = client.send_reply(account_id, message_id, REPLY_CONTENT)

        # 5. Verifier le resultat
        status = result.get("status", {})
        status_code = status.get("code")
        data = result.get("data", {})

        print(f"[REPONSE API] Code: {status_code}")
        print(f"  Description: {status.get('description', 'N/A')}")

        if status_code != 200:
            print(f"\n[ERREUR] Echec de l'envoi")
            print(f"  Details: {data.get('moreInfo', 'N/A')}")
            return 1

        print(f"\n[OK] API confirme l'envoi")
        print(f"  Message ID: {data.get('messageId', 'N/A')}")
        print()

        # 6. Verification dans les emails envoyes
        print("Etape 3: Verification dans le dossier Envoyes...")
        time.sleep(3)  # Attendre 3 secondes

        sent_email = client.verify_sent_email(account_id, AUDREY_EMAIL, minutes_ago=5)

        if sent_email:
            print(f"[OK] Email confirme dans le dossier Envoyes!")
            print(f"  A: {sent_email.get('toAddress')}")
            print(f"  Sujet: {sent_email.get('subject', 'N/A')}")
            print(f"  Date envoi: {datetime.fromtimestamp(sent_email.get('sentTime', 0) / 1000).strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"[ATTENTION] Email non trouve dans le dossier Envoyes")
            print(f"  L'API a retourne code 200 mais l'email n'apparait pas encore")
            print(f"  Verifiez manuellement dans quelques minutes")

        print()
        print("=" * 70)
        print("RESUME")
        print("=" * 70)
        print(f"De: {email.get('fromAddress')}")
        print(f"Sujet original: {email.get('subject', 'N/A')}")
        print(f"Reponse envoyee: \"{REPLY_CONTENT}\"")
        print(f"Statut API: {status_code}")
        print(f"Verification dossier: {'OK' if sent_email else 'EN ATTENTE'}")
        print("=" * 70)

        return 0

    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
