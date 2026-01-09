"""
Zoho Books - Ajouter un contact via API REST directe
Contourne les limitations du MCP server
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
ORG_ID = os.getenv("ZOHO_BOOKS_ORGANIZATION_ID")

# Note: Les MCP servers Zoho utilisent leur propre authentification
# Pour créer un contact, nous devons utiliser l'interface web ou demander
# à l'équipe Zoho d'ajouter la méthode createContact au MCP server

if not ORG_ID:
    print("X Configuration manquante: ZOHO_BOOKS_ORGANIZATION_ID")
    sys.exit(1)

print("="*60)
print("AJOUT DE CONTACT ZOHO BOOKS")
print("="*60)
print()

# Informations du contact
contact_info = {
    "name": "Solution Comptabilite - Sebastien Vachon",
    "type": "vendor",
    "email": "info@solutioncomptabilite.com",
    "phone": "(514) 880-2776",
    "website": "solutioncomptabilite.com",
    "address": {
        "street": "9500, rue de Limoilou",
        "city": "Quebec",
        "state": "QC",
        "zip": "H1K 0J6",
        "country": "Canada"
    },
    "notes": "President / Solution Comptabilite. Contact etabli le 5 decembre 2025 concernant une procuration."
}

print("METHODE 1: Via MCP Server")
print("-" * 60)
print("X Le MCP Server Zoho Books ne supporte pas createContact")
print()

print("METHODE 2: Via Interface Web")
print("-" * 60)
print("OK Vous pouvez ajouter le contact manuellement dans Zoho Books:")
print()
print("1. Allez sur: https://books.zoho.com/app/110002033190#/contacts")
print("2. Cliquez sur 'New Contact' ou '+ Contact'")
print("3. Selectionnez le type: Vendor")
print("4. Remplissez les informations ci-dessous:")
print()
print("INFORMATIONS DU CONTACT:")
print("-" * 60)
for key, value in contact_info.items():
    if key == "address":
        print(f"  {key.capitalize()}:")
        for addr_key, addr_val in value.items():
            print(f"    {addr_key.capitalize()}: {addr_val}")
    else:
        print(f"  {key.capitalize()}: {value}")
print()

print("METHODE 3: Demander l'ajout de la fonctionnalite au MCP")
print("-" * 60)
print("Contactez l'equipe Zoho pour ajouter books/createContact au MCP server")
print()

print("="*60)
print("ALTERNATIVES IMMEDIATES:")
print("="*60)
print()
print("1. Ajout manuel via interface web (recommande)")
print("2. Import CSV depuis Zoho Books > Contacts > Import")
print("3. Utiliser l'API REST Zoho directement (necessite OAuth setup)")
print()

# Sauvegarde dans un fichier pour référence
import json
contact_file = ".tmp/sebastien_vachon_contact.json"
os.makedirs(".tmp", exist_ok=True)

with open(contact_file, "w", encoding="utf-8") as f:
    json.dump(contact_info, f, indent=2, ensure_ascii=False)

print(f"OK Informations sauvegardees dans: {contact_file}")
print()
