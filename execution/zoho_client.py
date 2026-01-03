"""
Zoho One Client - Interface Python pour les APIs Zoho One
Supporte: CRM, Books, Projects, Cliq, Calendar, Mail, WorkDrive
"""

import os
import requests
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ZohoConfig:
    client_id: str
    client_secret: str
    refresh_token: str
    org_id: str
    region: str = "eu"

    @property
    def base_url(self) -> str:
        regions = {
            "com": "https://www.zohoapis.com",
            "eu": "https://www.zohoapis.eu",
            "in": "https://www.zohoapis.in",
            "com.au": "https://www.zohoapis.com.au",
            "jp": "https://www.zohoapis.jp"
        }
        return regions.get(self.region, regions["eu"])

    @property
    def accounts_url(self) -> str:
        regions = {
            "com": "https://accounts.zoho.com",
            "eu": "https://accounts.zoho.eu",
            "in": "https://accounts.zoho.in",
            "com.au": "https://accounts.zoho.com.au",
            "jp": "https://accounts.zoho.jp"
        }
        return regions.get(self.region, regions["eu"])

    @property
    def mail_url(self) -> str:
        regions = {
            "com": "https://mail.zoho.com",
            "eu": "https://mail.zoho.eu",
            "in": "https://mail.zoho.in",
            "com.au": "https://mail.zoho.com.au",
            "jp": "https://mail.zoho.jp"
        }
        return regions.get(self.region, regions["eu"])

    @property
    def cliq_url(self) -> str:
        regions = {
            "com": "https://cliq.zoho.com",
            "eu": "https://cliq.zoho.eu",
            "in": "https://cliq.zoho.in",
            "com.au": "https://cliq.zoho.com.au",
            "jp": "https://cliq.zoho.jp"
        }
        return regions.get(self.region, regions["eu"])

    @property
    def workdrive_url(self) -> str:
        regions = {
            "com": "https://workdrive.zoho.com",
            "eu": "https://workdrive.zoho.eu",
            "in": "https://workdrive.zoho.in",
            "com.au": "https://workdrive.zoho.com.au",
            "jp": "https://workdrive.zoho.jp"
        }
        return regions.get(self.region, regions["eu"])


class ZohoClient:
    """Client unifie pour interagir avec toutes les APIs Zoho One."""

    def __init__(self, config: Optional[ZohoConfig] = None):
        if config is None:
            config = ZohoConfig(
                client_id=os.getenv("ZOHO_CLIENT_ID", ""),
                client_secret=os.getenv("ZOHO_CLIENT_SECRET", ""),
                refresh_token=os.getenv("ZOHO_REFRESH_TOKEN", ""),
                org_id=os.getenv("ZOHO_ORG_ID", ""),
                region=os.getenv("ZOHO_REGION", "eu")
            )
        self.config = config
        self._access_token: Optional[str] = None

    def _refresh_access_token(self) -> str:
        """Obtient un nouveau access token via le refresh token."""
        url = f"{self.config.accounts_url}/oauth/v2/token"
        params = {
            "refresh_token": self.config.refresh_token,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "refresh_token"
        }
        response = requests.post(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "access_token" not in data:
            print(f"DEBUG: Token refresh response error: {data}")
        self._access_token = data["access_token"]
        return self._access_token

    @property
    def access_token(self) -> str:
        if self._access_token is None:
            self._refresh_access_token()
        return self._access_token

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/json"
        }

    # ==========================================
    # ZOHO CRM
    # ==========================================

    def crm_search(self, module: str, criteria: str, page: int = 1, per_page: int = 200) -> List[Dict]:
        """Recherche dans un module CRM."""
        url = f"{self.config.base_url}/crm/v2/{module}/search"
        params = {"criteria": criteria, "page": page, "per_page": per_page}
        response = requests.get(url, headers=self._headers(), params=params)
        if response.status_code == 204:
            return []
        response.raise_for_status()
        return response.json().get("data", [])

    def crm_get_record(self, module: str, record_id: str) -> Dict:
        """Obtient un enregistrement CRM par ID."""
        url = f"{self.config.base_url}/crm/v2/{module}/{record_id}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        data = response.json().get("data", [])
        return data[0] if data else {}

    def crm_create_record(self, module: str, data: Dict) -> Dict:
        """Cree un enregistrement dans un module CRM."""
        url = f"{self.config.base_url}/crm/v2/{module}"
        payload = {"data": [data]}
        response = requests.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    def crm_update_record(self, module: str, record_id: str, data: Dict) -> Dict:
        """Met a jour un enregistrement CRM."""
        url = f"{self.config.base_url}/crm/v2/{module}/{record_id}"
        payload = {"data": [data]}
        response = requests.put(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    def crm_list_records(self, module: str, page: int = 1, per_page: int = 200) -> List[Dict]:
        """Liste les enregistrements d'un module."""
        url = f"{self.config.base_url}/crm/v2/{module}"
        params = {"page": page, "per_page": per_page}
        response = requests.get(url, headers=self._headers(), params=params)
        if response.status_code == 204:
            return []
        response.raise_for_status()
        return response.json().get("data", [])

    # ==========================================
    # ZOHO BOOKS
    # ==========================================

    def books_list_invoices(self, status: Optional[str] = None) -> List[Dict]:
        """Liste les factures. Status: draft, sent, overdue, paid, void, all."""
        url = f"{self.config.base_url}/books/v3/invoices"
        params = {"organization_id": self.config.org_id}
        if status:
            params["status"] = status
        response = requests.get(url, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json().get("invoices", [])

    def books_get_invoice(self, invoice_id: str) -> Dict:
        """Obtient les details d'une facture."""
        url = f"{self.config.base_url}/books/v3/invoices/{invoice_id}"
        params = {"organization_id": self.config.org_id}
        response = requests.get(url, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json().get("invoice", {})

    def books_create_invoice(self, customer_id: str, line_items: List[Dict], **kwargs) -> Dict:
        """Cree une nouvelle facture."""
        url = f"{self.config.base_url}/books/v3/invoices"
        params = {"organization_id": self.config.org_id}
        payload = {
            "customer_id": customer_id,
            "line_items": line_items,
            **kwargs
        }
        response = requests.post(url, headers=self._headers(), params=params, json=payload)
        response.raise_for_status()
        return response.json()

    def books_list_customers(self) -> List[Dict]:
        """Liste les clients dans Books."""
        url = f"{self.config.base_url}/books/v3/contacts"
        params = {"organization_id": self.config.org_id, "contact_type": "customer"}
        response = requests.get(url, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json().get("contacts", [])

    def books_list_expenses(self, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[Dict]:
        """Liste les depenses."""
        url = f"{self.config.base_url}/books/v3/expenses"
        params = {"organization_id": self.config.org_id}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        response = requests.get(url, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json().get("expenses", [])

    # ==========================================
    # ZOHO PROJECTS
    # ==========================================

    def projects_list(self, status: str = "active") -> List[Dict]:
        """Liste les projets. Status: active, archived, all."""
        url = f"{self.config.base_url}/projects/v1/portals/{self.config.org_id}/projects/"
        params = {"status": status}
        response = requests.get(url, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json().get("projects", [])

    def projects_get(self, project_id: str) -> Dict:
        """Obtient les details d'un projet."""
        url = f"{self.config.base_url}/projects/v1/portals/{self.config.org_id}/projects/{project_id}/"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json().get("projects", [{}])[0]

    def projects_list_tasks(self, project_id: str) -> List[Dict]:
        """Liste les taches d'un projet."""
        url = f"{self.config.base_url}/projects/v1/portals/{self.config.org_id}/projects/{project_id}/tasks/"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json().get("tasks", [])

    def projects_create_task(self, project_id: str, name: str, **kwargs) -> Dict:
        """Cree une tache dans un projet."""
        url = f"{self.config.base_url}/projects/v1/portals/{self.config.org_id}/projects/{project_id}/tasks/"
        payload = {"name": name, **kwargs}
        response = requests.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    def projects_update_task(self, project_id: str, task_id: str, data: Dict) -> Dict:
        """Met a jour une tache."""
        url = f"{self.config.base_url}/projects/v1/portals/{self.config.org_id}/projects/{project_id}/tasks/{task_id}/"
        response = requests.put(url, headers=self._headers(), json=data)
        response.raise_for_status()
        return response.json()

    def projects_log_time(self, project_id: str, task_id: str, hours: float, date: str, notes: str = "") -> Dict:
        """Enregistre du temps sur une tache."""
        url = f"{self.config.base_url}/projects/v1/portals/{self.config.org_id}/projects/{project_id}/tasks/{task_id}/logs/"
        payload = {"hours": hours, "date": date, "notes": notes}
        response = requests.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    # ==========================================
    # ZOHO CLIQ
    # ==========================================

    def cliq_list_channels(self) -> List[Dict]:
        """Liste les canaux Cliq."""
        url = f"{self.config.cliq_url}/api/v2/channels"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json().get("channels", [])

    def cliq_post_to_channel(self, channel_id: str, text: str, bot_name: str = "Atlas") -> Dict:
        """Poste un message dans un canal."""
        url = f"{self.config.cliq_url}/api/v2/channelsbyid/{channel_id}/message"
        payload = {"text": text, "bot": {"name": bot_name}}
        response = requests.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    def cliq_send_direct_message(self, user_email: str, text: str) -> Dict:
        """Envoie un message direct a un utilisateur."""
        url = f"{self.config.cliq_url}/api/v2/buddies/{user_email}/message"
        payload = {"text": text}
        response = requests.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    # ==========================================
    # ZOHO CALENDAR
    # ==========================================

    def calendar_list_calendars(self) -> List[Dict]:
        """Liste les calendriers."""
        url = f"{self.config.base_url}/calendar/v1/calendars"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json().get("calendars", [])

    def calendar_list_events(self, calendar_uid: str, start_date: str, end_date: str) -> List[Dict]:
        """Liste les evenements d'un calendrier."""
        url = f"{self.config.base_url}/calendar/v1/calendars/{calendar_uid}/events"
        params = {"range": f"{start_date},{end_date}"}
        response = requests.get(url, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json().get("events", [])

    def calendar_create_event(self, calendar_uid: str, title: str, start: str, end: str, **kwargs) -> Dict:
        """Cree un evenement."""
        url = f"{self.config.base_url}/calendar/v1/calendars/{calendar_uid}/events"
        payload = {
            "eventdata": {
                "title": title,
                "dateandtime": {"start": start, "end": end},
                **kwargs
            }
        }
        response = requests.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    def calendar_delete_event(self, calendar_uid: str, event_uid: str) -> Dict:
        """Supprime un evenement."""
        url = f"{self.config.base_url}/calendar/v1/calendars/{calendar_uid}/events/{event_uid}"
        response = requests.delete(url, headers=self._headers())
        response.raise_for_status()
        return {"status": "deleted"}

    # ==========================================
    # ZOHO MAIL
    # ==========================================

    def mail_list_folders(self, account_id: str) -> List[Dict]:
        """Liste les dossiers mail."""
        url = f"{self.config.mail_url}/api/accounts/{account_id}/folders"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json().get("data", [])

    def mail_list_messages(self, account_id: str, folder_id: str, limit: int = 50) -> List[Dict]:
        """Liste les emails d'un dossier."""
        url = f"{self.config.mail_url}/api/accounts/{account_id}/messages/view"
        params = {"folderId": folder_id, "limit": limit}
        response = requests.get(url, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json().get("data", [])

    def mail_get_message(self, account_id: str, message_id: str) -> Dict:
        """Obtient le contenu d'un email."""
        url = f"{self.config.mail_url}/api/accounts/{account_id}/messages/{message_id}/content"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json().get("data", {})

    def mail_send(self, account_id: str, to: str, subject: str, content: str, **kwargs) -> Dict:
        """Envoie un email."""
        url = f"{self.config.mail_url}/api/accounts/{account_id}/messages"
        payload = {
            "toAddress": to,
            "subject": subject,
            "content": content,
            **kwargs
        }
        response = requests.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    # ==========================================
    # ZOHO WORKDRIVE
    # ==========================================

    def workdrive_list_teams(self) -> List[Dict]:
        """Liste les teams WorkDrive."""
        url = f"{self.config.workdrive_url}/api/v1/teams"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json().get("data", [])

    def workdrive_list_files(self, folder_id: str) -> List[Dict]:
        """Liste les fichiers d'un dossier."""
        url = f"{self.config.workdrive_url}/api/v1/files/{folder_id}/files"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json().get("data", [])

    def workdrive_create_folder(self, parent_id: str, name: str) -> Dict:
        """Cree un dossier."""
        url = f"{self.config.workdrive_url}/api/v1/files"
        payload = {
            "data": {
                "attributes": {"name": name, "parent_id": parent_id},
                "type": "files"
            }
        }
        response = requests.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    def workdrive_download_file(self, file_id: str) -> bytes:
        """Telecharge un fichier."""
        url = f"{self.config.workdrive_url}/api/v1/download/{file_id}"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.content


# ==========================================
# FONCTIONS UTILITAIRES
# ==========================================

def get_pipeline_summary() -> Dict:
    """Obtient un resume du pipeline commercial."""
    client = ZohoClient()
    deals = client.crm_list_records("Deals")

    summary = {
        "total_deals": len(deals),
        "by_stage": {},
        "total_value": 0
    }

    for deal in deals:
        stage = deal.get("Stage", "Unknown")
        amount = deal.get("Amount", 0) or 0

        if stage not in summary["by_stage"]:
            summary["by_stage"][stage] = {"count": 0, "value": 0}

        summary["by_stage"][stage]["count"] += 1
        summary["by_stage"][stage]["value"] += amount
        summary["total_value"] += amount

    return summary


def get_recent_leads(days: int = 7) -> List[Dict]:
    """Obtient les leads recents."""
    client = ZohoClient()
    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    criteria = f"(Created_Time:greater_equal:{date_from})"
    return client.crm_search("Leads", criteria)


def get_unpaid_invoices() -> List[Dict]:
    """Obtient les factures non payees."""
    client = ZohoClient()
    return client.books_list_invoices(status="overdue")


def get_active_projects_summary() -> Dict:
    """Resume des projets actifs."""
    client = ZohoClient()
    projects = client.projects_list(status="active")

    summary = {
        "total_projects": len(projects),
        "projects": []
    }

    for project in projects:
        tasks = client.projects_list_tasks(project["id"])
        open_tasks = [t for t in tasks if t.get("status", {}).get("name") != "Completed"]
        summary["projects"].append({
            "name": project.get("name"),
            "id": project.get("id"),
            "open_tasks": len(open_tasks),
            "total_tasks": len(tasks)
        })

    return summary


def get_today_events() -> List[Dict]:
    """Obtient les evenements du jour."""
    client = ZohoClient()
    calendars = client.calendar_list_calendars()
    today = datetime.now().strftime("%Y-%m-%d")

    all_events = []
    for cal in calendars:
        events = client.calendar_list_events(cal["uid"], today, today)
        all_events.extend(events)

    return all_events


if __name__ == "__main__":
    # Test de connexion
    try:
        client = ZohoClient()
        token = client.access_token
        print(f"Connexion Zoho reussie. Token: {token[:20]}...")

        # Test CRM
        print("\n--- Test CRM ---")
        contacts = client.crm_list_records("Contacts", per_page=5)
        print(f"Contacts trouves: {len(contacts)}")

    except Exception as e:
        print(f"Erreur de connexion Zoho: {e}")
