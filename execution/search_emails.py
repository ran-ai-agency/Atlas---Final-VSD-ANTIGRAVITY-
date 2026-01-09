#!/usr/bin/env python3
"""
Recherche d'emails sur tous les comptes Zoho Mail
Usage: python search_emails.py "mot-cle" [--limit 20]
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')


class ZohoMailSearch:
    """Client Zoho Mail pour recherche d'emails"""

    # Mapping des comptes pour affichage
    ACCOUNT_NAMES = {
        '219196000000002002': 'Ran.AI Agency',
        '219196000000029010': 'Sympatico',
        '219196000000034010': 'Bell Net',
        '219196000000072002': 'Gmail'
    }

    def __init__(self):
        self.mail_url = os.getenv("MCP_ZOHO_MAIL_URL", "")
        self.mail_key = os.getenv("MCP_ZOHO_MAIL_KEY", "")

        if not self.mail_url or not self.mail_key:
            raise ValueError("MCP_ZOHO_MAIL_URL et MCP_ZOHO_MAIL_KEY requis dans .env")

        self.url = f"{self.mail_url}?key={self.mail_key}"
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
            self.url,
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
        if content:
            text = content[0].get("text", "{}")
            data = json.loads(text)
            self.accounts = data.get("data", [])
        return self.accounts

    def search_in_account(self, account_id: str, search_key: str, limit: int = 20):
        """Recherche dans un compte specifique"""
        result = self._call("tools/call", {
            "name": "ZohoMail_searchEmails",
            "arguments": {
                "path_variables": {"accountId": account_id},
                "query_params": {
                    "searchKey": search_key,
                    "limit": limit
                }
            }
        })

        content = result.get("content", [])
        if content:
            text = content[0].get("text", "{}")
            # Verifier si c'est une erreur
            if "error" in text.lower() or "mandatory" in text.lower():
                return []
            try:
                data = json.loads(text)
                return data.get("data", [])
            except:
                return []
        return []

    def list_emails_in_account(self, account_id: str, limit: int = 30):
        """Liste les emails d'un compte (fallback si search ne marche pas)"""
        result = self._call("tools/call", {
            "name": "ZohoMail_listEmails",
            "arguments": {
                "path_variables": {"accountId": account_id},
                "query_params": {"limit": limit, "start": 1}
            }
        })

        content = result.get("content", [])
        if content:
            text = content[0].get("text", "{}")
            try:
                data = json.loads(text)
                return data.get("data", [])
            except:
                return []
        return []

    def search_all_accounts(self, keywords: list, limit_per_account: int = 30):
        """
        Recherche par mots-cles sur tous les comptes.
        Utilise listEmails puis filtre localement car searchEmails peut etre limite.
        """
        if not self.accounts:
            self.get_accounts()

        all_results = []

        for acc in self.accounts:
            acc_id = acc.get("accountId")
            acc_name = self.ACCOUNT_NAMES.get(acc_id, acc.get("accountDisplayName", "Unknown"))

            try:
                # Recuperer les emails
                emails = self.list_emails_in_account(acc_id, limit=limit_per_account)

                # Filtrer par mots-cles
                for email in emails:
                    subject = (email.get("subject") or "").lower()
                    sender = (email.get("sender") or "").lower()
                    from_addr = (email.get("fromAddress") or "").lower()

                    # Verifier si un mot-cle correspond
                    for kw in keywords:
                        kw_lower = kw.lower()
                        if kw_lower in subject or kw_lower in sender or kw_lower in from_addr:
                            email["_account_name"] = acc_name
                            email["_account_id"] = acc_id
                            email["_matched_keyword"] = kw
                            all_results.append(email)
                            break

            except Exception as e:
                print(f"[WARN] Erreur compte {acc_name}: {e}")

        # Trier par date
        all_results.sort(key=lambda e: e.get("receivedTime", 0), reverse=True)
        return all_results


def format_date(timestamp_ms):
    """Formate un timestamp en date lisible"""
    if timestamp_ms:
        try:
            ts = int(timestamp_ms) if isinstance(timestamp_ms, str) else timestamp_ms
            dt = datetime.fromtimestamp(ts / 1000)
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return str(timestamp_ms)
    return "N/A"


def main():
    parser = argparse.ArgumentParser(description="Recherche d'emails sur tous les comptes Zoho Mail")
    parser.add_argument("keywords", nargs="+", help="Mots-cles a rechercher")
    parser.add_argument("--limit", type=int, default=30, help="Limite d'emails par compte (defaut: 30)")
    parser.add_argument("--json", action="store_true", help="Sortie en JSON")
    args = parser.parse_args()

    try:
        client = ZohoMailSearch()

        print("=" * 60)
        print(f"RECHERCHE: {', '.join(args.keywords)}")
        print("=" * 60)

        results = client.search_all_accounts(args.keywords, limit_per_account=args.limit)

        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
            return 0

        if not results:
            print("\nAucun email trouve avec ces mots-cles.")
            return 0

        print(f"\n{len(results)} email(s) trouve(s):\n")
        print("-" * 60)

        for i, email in enumerate(results, 1):
            subject = email.get("subject", "Sans sujet")
            sender = email.get("sender", email.get("fromAddress", "Inconnu"))
            date_str = format_date(email.get("receivedTime"))
            account = email.get("_account_name", "")
            keyword = email.get("_matched_keyword", "")
            is_read = "" if email.get("isRead", True) else " [NON LU]"
            msg_id = email.get("messageId", "")

            # Nettoyer pour console Windows
            subject = subject.encode('ascii', 'replace').decode('ascii')[:70]
            sender = sender.encode('ascii', 'replace').decode('ascii')

            print(f"{i}. {subject}{is_read}")
            print(f"   De: {sender}")
            print(f"   Date: {date_str} | Compte: {account}")
            print(f"   Mot-cle: '{keyword}' | ID: {msg_id}")
            print()

        return 0

    except Exception as e:
        print(f"[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
