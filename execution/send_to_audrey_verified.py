#!/usr/bin/env python3
"""
Envoie un email a Audrey Gagnon avec verification complete
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

    def get_accounts(self):
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

    def send_email_direct(self, account_id: str, to_address: str, subject: str, content: str, from_address: str):
        """Envoie un email directement (pas une reponse)"""
        result = self._call("tools/call", {
            "name": "ZohoMail_sendEmail",
            "arguments": {
                "path_variables": {
                    "accountId": account_id
                },
                "body": {
                    "toAddress": to_address,
                    "fromAddress": from_address,
                    "subject": subject,
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

    def list_sent_emails(self, account_id: str, limit: int = 20):
        """Liste les emails envoyes recemment"""
        # Essayer avec includesent
        try:
            result = self._call("tools/call", {
                "name": "ZohoMail_listEmails",
                "arguments": {
                    "path_variables": {"accountId": account_id},
                    "query_params": {
                        "limit": limit,
                        "start": 1,
                        "includesent": True
                    }
                }
            })

            content = result.get("content", [])
            if content and isinstance(content, list):
                text = content[0].get("text", "{}")
                data = json.loads(text)
                return data.get("data", [])
        except:
            pass

        return []

    def verify_sent_to(self, account_id: str, to_email: str, subject_contains: str, minutes_ago: int = 5):
        """Verifie qu'un email a ete envoye a un destinataire"""
        print(f"\nVerification envoi a {to_email}...")

        emails = self.list_sent_emails(account_id, limit=50)

        now_ts = time.time() * 1000
        cutoff_ts = now_ts - (minutes_ago * 60 * 1000)

        for email in emails:
            to_addr = email.get("toAddress", "").lower()
            subject = email.get("subject", "").lower()
            sent_time = email.get("sentTime", 0)

            # Convertir sent_time si string
            if isinstance(sent_time, str):
                try:
                    sent_time = int(sent_time)
                except:
                    sent_time = 0

            if (to_email.lower() in to_addr and
                subject_contains.lower() in subject and
                sent_time > cutoff_ts):
                return email

        return None


def main():
    """Fonction principale"""
    TO_EMAIL = "allo@dagstudio.co"
    SUBJECT = "Re: Chat sauvegarde"
    CONTENT = "Merci"

    try:
        client = ZohoMailMCP()

        print("=" * 80)
        print("ENVOI EMAIL A AUDREY GAGNON")
        print("=" * 80)
        print()

        # 1. Recuperer les comptes
        print("Etape 1: Recuperation des comptes...")
        accounts = client.get_accounts()

        if not accounts:
            print("[ERREUR] Aucun compte trouve")
            return 1

        # Utiliser le compte principal (ranai-ai-agency)
        account = None
        for acc in accounts:
            email = acc.get("primaryEmailAddress", "")
            if "ran-ai-agency" in email:
                account = acc
                break

        if not account:
            account = accounts[0]  # Fallback au premier compte

        account_id = account.get("accountId")
        from_email = account.get("primaryEmailAddress", "")

        print(f"[OK] Compte: {account.get('accountDisplayName')}")
        print(f"     Email: {from_email}")
        print()

        # 2. Envoyer l'email
        print("Etape 2: Envoi de l'email...")
        print(f"  De: {from_email}")
        print(f"  A: {TO_EMAIL}")
        print(f"  Sujet: {SUBJECT}")
        print(f"  Contenu: \"{CONTENT}\"")
        print()

        result = client.send_email_direct(
            account_id=account_id,
            to_address=TO_EMAIL,
            subject=SUBJECT,
            content=CONTENT,
            from_address=from_email
        )

        # 3. Verifier la reponse
        status = result.get("status", {})
        status_code = status.get("code")
        data = result.get("data", {})

        print(f"[REPONSE API]")
        print(f"  Code: {status_code}")
        print(f"  Description: {status.get('description', 'N/A')}")

        if status_code != 200:
            print(f"\n[ERREUR] Echec de l'envoi")
            print(f"  Details: {data.get('moreInfo', 'N/A')}")
            print(f"  Full response: {json.dumps(result, indent=2)}")
            return 1

        message_id = data.get("messageId", "N/A")
        print(f"  Message ID: {message_id}")
        print()

        # 4. Attendre un peu
        print("Etape 3: Attente de la synchronisation (5 secondes)...")
        time.sleep(5)
        print()

        # 5. Verification dans les emails envoyes
        print("Etape 4: Verification dans le dossier Envoyes...")

        sent_email = client.verify_sent_to(
            account_id=account_id,
            to_email=TO_EMAIL,
            subject_contains="chat",
            minutes_ago=10
        )

        print()
        print("=" * 80)
        print("RESULTAT FINAL")
        print("=" * 80)

        if sent_email:
            sent_time = sent_email.get("sentTime", 0)
            if isinstance(sent_time, str):
                try:
                    sent_time = int(sent_time)
                except:
                    sent_time = 0

            if sent_time > 0:
                date_str = datetime.fromtimestamp(sent_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
            else:
                date_str = "Inconnue"

            print(f"[SUCCESS] Email CONFIRME envoye et present dans le dossier Envoyes!")
            print()
            print(f"  A: {sent_email.get('toAddress')}")
            print(f"  Sujet: {sent_email.get('subject')}")
            print(f"  Date envoi: {date_str}")
            print(f"  Message ID: {sent_email.get('messageId', 'N/A')}")
            print()
            print("L'email a ete envoye avec succes et est verifiable.")
        else:
            print(f"[ATTENTION] Email non trouve dans le dossier Envoyes")
            print()
            print(f"L'API a retourne code 200 mais:")
            print(f"- Soit le dossier Envoyes n'est pas accessible via listEmails")
            print(f"- Soit il y a un delai de synchronisation plus long")
            print()
            print(f"Veuillez verifier manuellement dans Zoho Mail:")
            print(f"  mail.zoho.com > Envoyes > Chercher: {TO_EMAIL}")

        print("=" * 80)

        return 0 if sent_email else 1

    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
