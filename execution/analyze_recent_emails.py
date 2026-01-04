#!/usr/bin/env python3
"""
Analyse des courriels récents - Script d'exécution
Utilise l'API Zoho Mail pour analyser les emails récents
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import Counter, defaultdict
import re

# Ajouter le répertoire courant au path pour importer zoho_client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from zoho_client import ZohoClient


class EmailAnalyzer:
    """Analyseur d'emails pour Zoho Mail"""

    def __init__(self):
        self.client = ZohoClient()
        self.account_id = self._get_account_id()

    def _get_account_id(self) -> str:
        """Obtient l'ID du compte mail principal"""
        try:
            # Essayer de récupérer les comptes mail
            url = f"{self.client.config.mail_url}/api/accounts"
            response = self.client.session.get(url, headers=self.client._headers())
            response.raise_for_status()
            accounts = response.json().get("data", [])

            if accounts:
                # Retourner le premier compte (généralement le principal)
                return accounts[0]["accountId"]

        except Exception as e:
            print(f"Erreur lors de la récupération du compte: {e}")

        # Fallback: demander à l'utilisateur ou utiliser une valeur par défaut
        return os.getenv("ZOHO_MAIL_ACCOUNT_ID", "")

    def get_recent_emails(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """Récupère les emails récents"""
        if not self.account_id:
            raise ValueError("Impossible de déterminer l'ID du compte mail")

        # Calculer la date de début
        date_from = datetime.now() - timedelta(days=days)

        # Lister les dossiers
        folders = self.client.mail_list_folders(self.account_id)

        # Identifier les dossiers principaux
        inbox_folder = None
        sent_folder = None

        for folder in folders:
            if folder.get("name", "").lower() in ["inbox", "boîte de réception"]:
                inbox_folder = folder
            elif folder.get("name", "").lower() in ["sent", "envoyés", "sent items"]:
                sent_folder = folder

        all_emails = []

        # Récupérer les emails de la boîte de réception
        if inbox_folder:
            try:
                emails = self.client.mail_list_messages(
                    self.account_id,
                    inbox_folder["folderId"],
                    limit=limit
                )
                for email in emails:
                    email["_folder"] = "inbox"
                    all_emails.append(email)
            except Exception as e:
                print(f"Erreur lors de la récupération des emails inbox: {e}")

        # Récupérer les emails envoyés
        if sent_folder:
            try:
                emails = self.client.mail_list_messages(
                    self.account_id,
                    sent_folder["folderId"],
                    limit=limit//2  # Moins d'emails envoyés
                )
                for email in emails:
                    email["_folder"] = "sent"
                    all_emails.append(email)
            except Exception as e:
                print(f"Erreur lors de la récupération des emails envoyés: {e}")

        # Filtrer par date et trier par date décroissante
        recent_emails = []
        for email in all_emails:
            email_date = email.get("receivedTime", 0) / 1000  # Convertir ms en secondes
            if datetime.fromtimestamp(email_date) >= date_from:
                recent_emails.append(email)

        # Trier par date décroissante
        recent_emails.sort(key=lambda x: x.get("receivedTime", 0), reverse=True)

        return recent_emails[:limit]

    def analyze_emails(self, emails: List[Dict]) -> Dict[str, Any]:
        """Analyse une liste d'emails"""
        if not emails:
            return {
                "total_emails": 0,
                "message": "Aucun email récent trouvé"
            }

        analysis = {
            "total_emails": len(emails),
            "period_days": 7,
            "stats": {},
            "top_senders": [],
            "priority_emails": [],
            "categories": {},
            "recommendations": []
        }

        # Statistiques de base
        senders = Counter()
        subjects = []
        dates = []

        # Mots-clés pour la classification
        urgent_keywords = [
            "urgent", "urgence", "immédiat", "deadline", "échéance",
            "important", "critique", "asap", "dès que possible"
        ]

        business_keywords = [
            "proposition", "offre", "contrat", "projet", "client",
            "partenaire", "réunion", "meeting", "appel", "call"
        ]

        personal_keywords = [
            "famille", "ami", "personnel", "privé", "vacances"
        ]

        for email in emails:
            sender = email.get("sender", {}).get("address", "Unknown")
            subject = email.get("subject", "")
            received_time = email.get("receivedTime", 0)

            senders[sender] += 1
            subjects.append(subject)
            dates.append(datetime.fromtimestamp(received_time / 1000))

            # Classification par priorité
            subject_lower = subject.lower()
            is_urgent = any(keyword in subject_lower for keyword in urgent_keywords)

            if is_urgent:
                analysis["priority_emails"].append({
                    "subject": subject,
                    "sender": sender,
                    "date": datetime.fromtimestamp(received_time / 1000).strftime("%Y-%m-%d %H:%M"),
                    "folder": email.get("_folder", "unknown")
                })

        # Statistiques générales
        analysis["stats"] = {
            "total_senders": len(senders),
            "emails_per_day": len(emails) / 7,  # Sur 7 jours par défaut
            "date_range": {
                "from": min(dates).strftime("%Y-%m-%d") if dates else None,
                "to": max(dates).strftime("%Y-%m-%d") if dates else None
            }
        }

        # Top expéditeurs
        analysis["top_senders"] = [
            {"email": email, "count": count}
            for email, count in senders.most_common(10)
        ]

        # Catégorisation basique
        analysis["categories"] = {
            "urgent": len(analysis["priority_emails"]),
            "business": len([e for e in emails if any(k in e.get("subject", "").lower() for k in business_keywords)]),
            "personal": len([e for e in emails if any(k in e.get("subject", "").lower() for k in personal_keywords)])
        }

        # Recommandations
        if analysis["priority_emails"]:
            analysis["recommendations"].append(
                f"📋 {len(analysis['priority_emails'])} emails prioritaires à traiter"
            )

        if len(senders) > 20:
            analysis["recommendations"].append(
                "📊 Forte activité email - considérer une revue des abonnements"
            )

        if analysis["stats"]["emails_per_day"] > 50:
            analysis["recommendations"].append(
                "⚡ Volume élevé d'emails - optimisation de la gestion nécessaire"
            )

        return analysis

    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Génère un rapport formaté"""
        if analysis["total_emails"] == 0:
            return "📭 Aucun email récent trouvé dans la période analysée."

        report = f"""📊 Analyse des courriels récents ({analysis['period_days']} jours)

📈 Statistiques générales:
• Total d'emails: {analysis['total_emails']}
• Expéditeurs uniques: {analysis['stats']['total_senders']}
• Emails par jour: {analysis['stats']['emails_per_day']:.1f}
• Période: {analysis['stats']['date_range']['from']} → {analysis['stats']['date_range']['to']}

👤 Top expéditeurs:
"""

        for i, sender in enumerate(analysis["top_senders"][:5], 1):
            report += f"{i}. {sender['email']} ({sender['count']} emails)\n"

        report += f"\n🏷️ Catégorisation:\n"
        report += f"• Urgents: {analysis['categories']['urgent']}\n"
        report += f"• Business: {analysis['categories']['business']}\n"
        report += f"• Personnel: {analysis['categories']['personal']}\n"

        if analysis["priority_emails"]:
            report += f"\n🚨 Emails prioritaires:\n"
            for email in analysis["priority_emails"][:5]:
                report += f"• {email['subject']} (de {email['sender']})\n"

        if analysis["recommendations"]:
            report += f"\n💡 Recommandations:\n"
            for rec in analysis["recommendations"]:
                report += f"• {rec}\n"

        return report


def main():
    """Fonction principale"""
    try:
        # Configuration
        days = int(os.getenv("EMAIL_ANALYSIS_DAYS", "7"))
        limit = int(os.getenv("EMAIL_ANALYSIS_LIMIT", "200"))

        print(f"🔍 Analyse des emails récents ({days} jours, max {limit} emails)...")

        # Initialiser l'analyseur
        analyzer = EmailAnalyzer()

        # Récupérer les emails récents
        emails = analyzer.get_recent_emails(days=days, limit=limit)
        print(f"📬 {len(emails)} emails récupérés")

        # Analyser les emails
        analysis = analyzer.analyze_emails(emails)

        # Générer et afficher le rapport
        report = analyzer.generate_report(analysis)
        print("\n" + "="*60)
        print(report)
        print("="*60)

        # Sauvegarder l'analyse complète en JSON
        output_file = "email_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)

        print(f"\n💾 Analyse complète sauvegardée dans {output_file}")

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())