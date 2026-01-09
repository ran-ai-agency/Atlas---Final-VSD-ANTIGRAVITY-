"""
Lister les contacts depuis Zoho Books pour verifier l'ajout
"""

from zoho_mcp_client import ZohoMCPClient

print("="*60)
print("LISTE DES CONTACTS - ZOHO BOOKS")
print("="*60)
print()

try:
    client = ZohoMCPClient()
    print("Client MCP initialise")
    print()

    print("Recuperation de la liste des contacts...")
    contacts = client.books_list_customers()

    print(f"Nombre de contacts: {len(contacts)}")
    print()

    # Chercher Sebastien Vachon
    found = False
    for contact in contacts:
        name = contact.get("contact_name", "")
        if "Vachon" in name or "Sebastien" in name.lower():
            found = True
            print(f"TROUVE: {name}")
            print(f"  ID: {contact.get('contact_id')}")
            print(f"  Type: {contact.get('contact_type')}")
            print(f"  Email: {contact.get('email')}")
            print(f"  Phone: {contact.get('phone')}")
            print()

    if not found:
        print("Sebastien Vachon n'a pas ete trouve dans les contacts.")
        print()
        print("Premiers 5 contacts:")
        for contact in contacts[:5]:
            print(f"  - {contact.get('contact_name')} ({contact.get('contact_type')})")

except Exception as e:
    print(f"Erreur: {e}")

print("="*60)
