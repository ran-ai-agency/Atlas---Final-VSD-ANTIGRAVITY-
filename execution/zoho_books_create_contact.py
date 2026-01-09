"""
Zoho Books - Créer un contact
Ajoute un nouveau contact (client/fournisseur) dans Zoho Books
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
ORG_ID = os.getenv("ZOHO_BOOKS_ORGANIZATION_ID")
MCP_URL = os.getenv("MCP_ZOHO_BOOKS_URL")
MCP_KEY = os.getenv("MCP_ZOHO_BOOKS_KEY")

if not all([ORG_ID, MCP_URL, MCP_KEY]):
    print("X Configuration manquante dans .env:")
    print("   - ZOHO_BOOKS_ORGANIZATION_ID")
    print("   - MCP_ZOHO_BOOKS_URL")
    print("   - MCP_ZOHO_BOOKS_KEY")
    sys.exit(1)


def call_mcp(method: str, params: dict):
    """Appelle le MCP server Zoho Books."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }

    headers = {"Content-Type": "application/json"}
    url_with_key = f"{MCP_URL}?key={MCP_KEY}"

    try:
        response = requests.post(url_with_key, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            raise Exception(f"Erreur MCP: {result['error']}")

        return result.get("result", {})

    except requests.exceptions.RequestException as e:
        raise Exception(f"Erreur lors de l'appel MCP: {e}")


def create_contact(
    contact_name: str,
    contact_type: str = "vendor",  # "customer" ou "vendor"
    email: str = None,
    phone: str = None,
    mobile: str = None,
    website: str = None,
    billing_address: dict = None,
    notes: str = None
):
    """
    Crée un contact dans Zoho Books.

    Args:
        contact_name: Nom du contact (entreprise ou personne)
        contact_type: "customer" ou "vendor"
        email: Email du contact
        phone: Numéro de téléphone
        mobile: Numéro de mobile
        website: Site web
        billing_address: Dict avec street, city, state, zip, country
        notes: Notes additionnelles

    Returns:
        Contact créé
    """
    print(f"\n{'='*60}")
    print(f"CREATION DE CONTACT ZOHO BOOKS")
    print(f"{'='*60}\n")

    # Construction du body (sans organization_id)
    body = {
        "contact_name": contact_name,
        "contact_type": contact_type
    }

    # Champs optionnels
    if email:
        body["email"] = email
    if phone:
        body["phone"] = phone
    if mobile:
        body["mobile"] = mobile
    if website:
        body["website"] = website
    if notes:
        body["notes"] = notes

    # Adresse de facturation
    if billing_address:
        body["billing_address"] = billing_address

    print(f"Nom: {contact_name}")
    print(f"Type: {contact_type}")
    if email:
        print(f"Email: {email}")
    if phone:
        print(f"Telephone: {phone}")
    if billing_address:
        print(f"Adresse: {billing_address.get('street', '')}, {billing_address.get('city', '')}")

    print(f"\nCreation du contact...")

    try:
        # IMPORTANT: Les outils Zoho Books MCP utilisent des noms avec espaces et minuscules
        # PAS de préfixe "ZohoBooks_"
        result = call_mcp("tools/call", {
            "name": "create contact",
            "arguments": {
                "query_params": {
                    "organization_id": ORG_ID
                },
                "body": body
            }
        })

        # Parser la reponse JSON
        content = result.get("content", [])
        if content and content[0].get("type") == "text":
            import json
            response_data = json.loads(content[0].get("text", "{}"))
            contact = response_data.get("contact", {})

            print(f"\nContact cree avec succes!")
            print(f"   ID: {contact.get('contact_id')}")
            print(f"   Nom: {contact.get('contact_name')}")
            print(f"   Type: {contact.get('contact_type')}")

            return contact

    except Exception as e:
        print(f"\nErreur lors de la creation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Exemple: Sébastien Vachon
    contact = create_contact(
        contact_name="Solution Comptabilité - Sébastien Vachon",
        contact_type="vendor",
        email="info@solutioncomptabilite.com",
        phone="(514) 880-2776",
        website="solutioncomptabilite.com",
        billing_address={
            "street": "9500, rue de Limoilou",
            "city": "Québec",
            "state": "QC",
            "zip": "H1K 0J6",
            "country": "Canada"
        },
        notes="Président / Solution Comptabilité. Contact établi le 5 décembre 2025 concernant une procuration."
    )

    print(f"\n{'='*60}")
    print("Contact créé et prêt à utiliser dans Zoho Books!")
    print(f"{'='*60}\n")
