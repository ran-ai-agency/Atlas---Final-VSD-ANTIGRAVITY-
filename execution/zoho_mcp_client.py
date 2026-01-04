"""
Zoho MCP Client - Interface Python pour les MCP Servers Zoho
Utilise les MCP servers heberges via HTTP
"""

import os
import requests
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

load_dotenv()


class ZohoMCPClient:
    """Client pour interagir avec les MCP servers Zoho via HTTP."""
    
    def __init__(self):
        """Initialise le client avec les configurations du .env"""
        # Zoho Books MCP
        self.books_enabled = os.getenv("MCP_ZOHO_BOOKS_ENABLED", "false").lower() == "true"
        self.books_url = os.getenv("MCP_ZOHO_BOOKS_URL", "")
        self.books_key = os.getenv("MCP_ZOHO_BOOKS_KEY", "")
        
        # Zoho CRM MCP
        self.crm_enabled = os.getenv("MCP_ZOHO_CRM_ENABLED", "false").lower() == "true"
        self.crm_url = os.getenv("MCP_ZOHO_CRM_URL", "")
        self.crm_key = os.getenv("MCP_ZOHO_CRM_KEY", "")
        
        # Zoho Mail MCP
        self.mail_enabled = os.getenv("MCP_ZOHO_MAIL_ENABLED", "false").lower() == "true"
        self.mail_url = os.getenv("MCP_ZOHO_MAIL_URL", "")
        self.mail_key = os.getenv("MCP_ZOHO_MAIL_KEY", "")
        
        if not self.books_enabled or not self.books_url or not self.books_key:
            raise ValueError(
                "Zoho Books MCP non configure. Verifiez MCP_ZOHO_BOOKS_ENABLED, "
                "MCP_ZOHO_BOOKS_URL et MCP_ZOHO_BOOKS_KEY dans .env"
            )
    
    def _call_mcp(self, service: str, method: str, params: Optional[Dict] = None) -> Any:
        """
        Appelle un MCP server via HTTP.
        
        Args:
            service: 'books', 'crm', ou 'mail'
            method: Nom de la methode MCP a appeler
            params: Parametres de la methode
        
        Returns:
            Reponse du MCP server
        """
        # Selectionner l'URL et la cle selon le service
        if service == "books":
            url = self.books_url
            key = self.books_key
        elif service == "crm":
            url = self.crm_url
            key = self.crm_key
        elif service == "mail":
            url = self.mail_url
            key = self.mail_key
        else:
            raise ValueError(f"Service inconnu: {service}")
        
        # Construire la requete MCP
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Verifier les erreurs MCP
            if "error" in result:
                raise Exception(f"Erreur MCP: {result['error']}")
            
            return result.get("result", {})
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de l'appel MCP {service}/{method}: {e}")
    
    # ========================================
    # ZOHO BOOKS - Factures
    # ========================================
    
    def books_list_invoices(self, status: Optional[str] = None) -> List[Dict]:
        """
        Liste les factures depuis Zoho Books.
        
        Args:
            status: Filtre par statut (paid, sent, overdue, void, all)
        
        Returns:
            Liste des factures
        """
        params = {}
        if status:
            params["status"] = status
        
        result = self._call_mcp("books", "books/listInvoices", params)
        return result.get("invoices", [])
    
    def books_get_invoice(self, invoice_id: str) -> Dict:
        """
        Obtient les details d'une facture.
        
        Args:
            invoice_id: ID de la facture
        
        Returns:
            Details de la facture
        """
        result = self._call_mcp("books", "books/getInvoice", {"invoice_id": invoice_id})
        return result.get("invoice", {})
    
    # ========================================
    # ZOHO BOOKS - Depenses
    # ========================================
    
    def books_list_expenses(
        self, 
        from_date: Optional[str] = None, 
        to_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Liste les depenses depuis Zoho Books.
        
        Args:
            from_date: Date de debut (format: YYYY-MM-DD)
            to_date: Date de fin (format: YYYY-MM-DD)
        
        Returns:
            Liste des depenses
        """
        params = {}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        
        result = self._call_mcp("books", "books/listExpenses", params)
        return result.get("expenses", [])
    
    # ========================================
    # ZOHO BOOKS - Clients
    # ========================================
    
    def books_list_customers(self) -> List[Dict]:
        """
        Liste les clients depuis Zoho Books.
        
        Returns:
            Liste des clients
        """
        result = self._call_mcp("books", "books/listCustomers", {})
        return result.get("contacts", [])
    
    def books_get_customer(self, customer_id: str) -> Dict:
        """
        Obtient les details d'un client.
        
        Args:
            customer_id: ID du client
        
        Returns:
            Details du client
        """
        result = self._call_mcp("books", "books/getCustomer", {"customer_id": customer_id})
        return result.get("contact", {})
    
    # ========================================
    # ZOHO BOOKS - Autres
    # ========================================
    
    def books_get_organization(self) -> Dict:
        """
        Obtient les informations de l'organisation.
        
        Returns:
            Details de l'organisation
        """
        result = self._call_mcp("books", "books/getOrganization", {})
        return result.get("organization", {})
    
    # ========================================
    # ZOHO CRM - Contacts et Deals
    # ========================================
    
    def crm_list_contacts(self, page: int = 1, per_page: int = 200) -> List[Dict]:
        """
        Liste les contacts depuis Zoho CRM.
        
        Args:
            page: Numero de page
            per_page: Nombre de resultats par page
        
        Returns:
            Liste des contacts
        """
        params = {"page": page, "per_page": per_page}
        result = self._call_mcp("crm", "crm/listContacts", params)
        return result.get("data", [])
    
    def crm_list_deals(self, page: int = 1, per_page: int = 200) -> List[Dict]:
        """
        Liste les deals depuis Zoho CRM.
        
        Args:
            page: Numero de page
            per_page: Nombre de resultats par page
        
        Returns:
            Liste des deals
        """
        params = {"page": page, "per_page": per_page}
        result = self._call_mcp("crm", "crm/listDeals", params)
        return result.get("data", [])
    
    # ========================================
    # Methodes utilitaires
    # ========================================
    
    def test_connection(self) -> Dict[str, bool]:
        """
        Teste la connexion aux differents MCP servers.
        
        Returns:
            Dict avec le statut de chaque service
        """
        status = {}
        
        # Test Zoho Books
        if self.books_enabled:
            try:
                self.books_get_organization()
                status["books"] = True
            except Exception as e:
                status["books"] = False
                status["books_error"] = str(e)
        else:
            status["books"] = False
            status["books_error"] = "Non active"
        
        # Test Zoho CRM
        if self.crm_enabled:
            try:
                self.crm_list_contacts(per_page=1)
                status["crm"] = True
            except Exception as e:
                status["crm"] = False
                status["crm_error"] = str(e)
        else:
            status["crm"] = False
            status["crm_error"] = "Non active"
        
        return status


# Test du client
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU CLIENT MCP ZOHO")
    print("=" * 60)
    print()
    
    try:
        client = ZohoMCPClient()
        print("✅ Client MCP initialise")
        print()
        
        print("📡 Test de connexion...")
        status = client.test_connection()
        
        for service, is_ok in status.items():
            if service.endswith("_error"):
                continue
            
            if is_ok:
                print(f"  ✅ {service.upper()}: Connecte")
            else:
                error = status.get(f"{service}_error", "Erreur inconnue")
                print(f"  ❌ {service.upper()}: {error}")
        
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
