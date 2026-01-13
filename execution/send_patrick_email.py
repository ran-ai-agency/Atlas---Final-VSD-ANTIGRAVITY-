#!/usr/bin/env python3
"""Envoyer le courriel a Patrick Kochanowski - RBC"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

mail_url = os.getenv('MCP_ZOHO_MAIL_URL', '')
mail_key = os.getenv('MCP_ZOHO_MAIL_KEY', '')
url = f'{mail_url}?key={mail_key}'

# Le compte Gmail dans Zoho Mail
GMAIL_ACCOUNT_ID = '219196000000072002'
FROM_ADDRESS = 'ranai.vision.agency@gmail.com'
TO_ADDRESS = 'patrick.kochanowski@rbc.com'
SUBJECT = 'Demande de transfert - Compte Investisseur vers Compte Affaires'

CONTENT = """Bonjour Patrick,

J'espère que vous allez bien.

Je vous écris afin de vous demander d'effectuer un transfert de fonds entre mes comptes RBC :

- Compte de départ : 07121-00000495107633 (Investisseur)
- Compte de destination : 07121-1000421 (Affaires)
- Montant : 5 000,00 $ CAD

Pourriez-vous s'il vous plaît procéder à ce transfert dans les meilleurs délais ?

N'hésitez pas à me contacter si vous avez besoin d'informations supplémentaires ou d'une confirmation de ma part.

Merci d'avance pour votre aide.

Cordialement,

Roland Ranaivoarison
514-918-1241
"""

def call_mcp(method, params):
    response = requests.post(url, json={'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}, timeout=60)
    return response.json()

print("=" * 60)
print("ENVOI DU COURRIEL A PATRICK KOCHANOWSKI - RBC")
print("=" * 60)
print(f"\nDe: {FROM_ADDRESS}")
print(f"A: {TO_ADDRESS}")
print(f"Sujet: {SUBJECT}")
print("-" * 60)

result = call_mcp('tools/call', {
    'name': 'ZohoMail_sendEmail',
    'arguments': {
        'path_variables': {
            'accountId': GMAIL_ACCOUNT_ID
        },
        'body': {
            'toAddress': TO_ADDRESS,
            'fromAddress': FROM_ADDRESS,
            'subject': SUBJECT,
            'content': CONTENT,
            'mailFormat': 'plaintext'
        }
    }
})

print("\nReponse API:")
print(json.dumps(result, indent=2, ensure_ascii=False))

if 'error' not in str(result).lower():
    print("\n" + "=" * 60)
    print("[OK] COURRIEL ENVOYE AVEC SUCCES!")
    print("=" * 60)
else:
    print("\n[ERREUR] Probleme lors de l'envoi")
