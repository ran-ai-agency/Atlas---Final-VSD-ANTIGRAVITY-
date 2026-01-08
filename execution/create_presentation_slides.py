#!/usr/bin/env python3
"""
Création automatique de la présentation Google Slides
Boîte à Outils GR - L'IA Agentique
"""

import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Scopes nécessaires
SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive.file'
]

# Couleurs du site Ran.AI Agency
COLORS = {
    'primary_green': {'red': 97/255, 'green': 126/255, 'blue': 77/255},      # #617E4D
    'dark_green': {'red': 99/255, 'green': 116/255, 'blue': 87/255},         # #637457
    'light_green': {'red': 139/255, 'green': 187/255, 'blue': 103/255},      # #8BBB67
    'pale_green_bg': {'red': 238/255, 'green': 243/255, 'blue': 229/255},    # #EEF3E5
    'white': {'red': 1, 'green': 1, 'blue': 1},
    'dark_text': {'red': 33/255, 'green': 33/255, 'blue': 33/255},           # #212121
    'gray_text': {'red': 106/255, 'green': 106/255, 'blue': 106/255},        # #6A6A6A
}

def get_credentials():
    """Obtient les credentials Google avec OAuth2"""
    creds = None
    token_path = Path(__file__).parent.parent / 'token_slides.json'
    credentials_path = Path(__file__).parent.parent / 'credentials.json'

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds

def apply_theme(slides_service, presentation_id):
    """Applique le thème Ran.AI Agency aux slides"""

    # Récupérer la présentation
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()

    requests = []

    # Appliquer le fond pale green à toutes les slides
    for slide in presentation.get('slides', []):
        slide_id = slide['objectId']

        # Fond de la slide
        requests.append({
            'updatePageProperties': {
                'objectId': slide_id,
                'pageProperties': {
                    'pageBackgroundFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': COLORS['pale_green_bg']
                            }
                        }
                    }
                },
                'fields': 'pageBackgroundFill'
            }
        })

        # Mettre à jour les couleurs du texte
        for element in slide.get('pageElements', []):
            if 'shape' in element:
                shape = element['shape']
                element_id = element['objectId']

                if shape.get('placeholder'):
                    placeholder_type = shape['placeholder'].get('type')

                    # Titres en vert foncé
                    if placeholder_type in ['TITLE', 'CENTERED_TITLE']:
                        requests.append({
                            'updateTextStyle': {
                                'objectId': element_id,
                                'style': {
                                    'foregroundColor': {
                                        'opaqueColor': {
                                            'rgbColor': COLORS['primary_green']
                                        }
                                    },
                                    'bold': True,
                                    'fontFamily': 'Roboto',
                                    'fontSize': {
                                        'magnitude': 36,
                                        'unit': 'PT'
                                    }
                                },
                                'fields': 'foregroundColor,bold,fontFamily,fontSize'
                            }
                        })

                    # Corps en texte foncé
                    elif placeholder_type in ['BODY', 'SUBTITLE']:
                        requests.append({
                            'updateTextStyle': {
                                'objectId': element_id,
                                'style': {
                                    'foregroundColor': {
                                        'opaqueColor': {
                                            'rgbColor': COLORS['dark_text']
                                        }
                                    },
                                    'fontFamily': 'Open Sans',
                                    'fontSize': {
                                        'magnitude': 18,
                                        'unit': 'PT'
                                    }
                                },
                                'fields': 'foregroundColor,fontFamily,fontSize'
                            }
                        })

    if requests:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        print("[OK] Thème Ran.AI Agency appliqué")

def create_presentation():
    """Crée la présentation Google Slides"""
    creds = get_credentials()
    slides_service = build('slides', 'v1', credentials=creds)

    # Créer une nouvelle présentation
    presentation = slides_service.presentations().create(
        body={
            'title': "L'IA Agentique - Boîte à Outils GR - Roland Ranaivoarison"
        }
    ).execute()

    presentation_id = presentation.get('presentationId')
    print(f"[OK] Présentation créée: https://docs.google.com/presentation/d/{presentation_id}")

    # Définir les slides
    slides_content = [
        {
            "title": "L'IA AGENTIQUE",
            "subtitle": "Quand l'IA devient votre partenaire de croissance\n\nRoland Ranaivoarison\nRan.AI Agency",
            "layout": "TITLE"
        },
        {
            "title": "73%",
            "body": "des entrepreneurs travaillent\nplus de 50h/semaine\n\n(dont 40% en tâches administratives)",
            "layout": "TITLE_AND_BODY"
        },
        {
            "title": "IA Classique vs IA Agentique",
            "body": "IA CLASSIQUE (ChatGPT)\n• Vous posez une question\n• L'IA répond\n• VOUS faites l'action\n= ASSISTANT\n\nIA AGENTIQUE\n• Vous définissez un OBJECTIF\n• L'IA PLANIFIE\n• L'IA EXÉCUTE\n• L'IA VÉRIFIE\n= PARTENAIRE",
            "layout": "TITLE_AND_BODY"
        },
        {
            "title": "Vous l'utilisez DÉJÀ!",
            "body": "ZOHO\n• Zia prédit vos ventes\n• Workflows automatiques\n• Alertes quand un deal stagne\n\nSALESFORCE\n• Einstein AI prédit les opportunités\n• Recommande la prochaine action\n• Détecte les clients à risque\n\nGO HIGH LEVEL\n• Conversations SMS automatisées\n• Booking automatique\n• Nurturing sur pilote automatique",
            "layout": "TITLE_AND_BODY"
        },
        {
            "title": "Cas #1: Analyse Stratégique",
            "body": "LE DÉFI\nAnalyser la stratégie de GR International\n(site web, réseaux sociaux, YouTube, concurrence)\n\nAVANT (manuel): 40+ heures\n\nAVEC IA AGENTIQUE: 2 heures\n→ Rapport de 790 lignes\n→ SWOT complet\n→ Plan d'action 90 jours\n\nGAIN: 95% du temps économisé",
            "layout": "TITLE_AND_BODY"
        },
        {
            "title": "Cas #2: Comptabilité Automatisée",
            "body": "LE PROBLÈME\n• Saisie manuelle = erreurs\n• Oublis TPS/TVQ = problèmes fiscaux\n• Doublons = temps perdu\n\nLA SOLUTION AGENTIQUE\n[Facture] → [IA analyse] → [Zoho Books]\n✓ Détecte le type de dépense\n✓ Calcule TPS + TVQ (14.975%)\n✓ Vérifie les doublons\n✓ Crée l'entrée automatiquement\n\nRÉSULTAT: 2-3h/mois → 5 min | 0 erreur",
            "layout": "TITLE_AND_BODY"
        },
        {
            "title": "Cas #3: Équipe de Direction IA",
            "body": "VOUS\n    ↓\nCEO | CFO | CMO | CTO | COO | EA\nVision | Finance | Marketing | Tech | Ops | Admin\n\nCOMMENT ÇA FONCTIONNE\n\n\"Je dois préparer ma déclaration\"\n→ [CFO] analyse, prépare le dossier\n\n\"J'ai besoin d'une stratégie marketing\"\n→ [CMO] analyse le marché, propose un plan\n\n6 directeurs seniors... sans les 6 salaires",
            "layout": "TITLE_AND_BODY"
        },
        {
            "title": "3 Questions pour Commencer",
            "body": "1️⃣ QUELLE TÂCHE RÉPÉTEZ-VOUS CHAQUE SEMAINE?\n→ C'est votre première cible d'automatisation\n\n2️⃣ QUELS OUTILS UTILISEZ-VOUS DÉJÀ?\n→ Zoho, Salesforce, Go High Level?\n→ Explorez leurs fonctions d'automatisation\n\n3️⃣ QU'EST-CE QUI VOUS EMPÊCHE DE DORMIR?\n→ Trésorerie? Prospects? Organisation?\n→ L'IA agentique peut probablement aider",
            "layout": "TITLE_AND_BODY"
        },
        {
            "title": "Pour Aller Plus Loin",
            "body": "RESSOURCES GRATUITES\n\n• ChatGPT → Créez vos propres GPTs\n• YouTube: \"AI Automation Agency\"\n• Explorez les workflows dans VOS outils\n\n\nQUESTIONS?\n\nRoland Ranaivoarison\nroland@ran-ai-agency.ca\n\nMerci de votre attention!",
            "layout": "TITLE_AND_BODY"
        }
    ]

    # Créer les slides
    requests = []

    for i, slide_data in enumerate(slides_content):
        # Créer une nouvelle slide (sauf la première qui existe déjà)
        if i > 0:
            requests.append({
                'createSlide': {
                    'insertionIndex': i,
                    'slideLayoutReference': {
                        'predefinedLayout': 'TITLE_AND_BODY' if slide_data.get('layout') == 'TITLE_AND_BODY' else 'TITLE'
                    }
                }
            })

    # Exécuter la création des slides
    if requests:
        response = slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        print(f"[OK] {len(slides_content)} slides créées")

    # Récupérer les IDs des slides
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()

    slide_ids = [slide['objectId'] for slide in presentation.get('slides', [])]

    # Ajouter le contenu à chaque slide
    content_requests = []

    for i, (slide_id, slide_data) in enumerate(zip(slide_ids, slides_content)):
        # Trouver les placeholders
        slide = presentation['slides'][i]
        title_id = None
        body_id = None
        subtitle_id = None

        for element in slide.get('pageElements', []):
            if 'shape' in element:
                shape = element['shape']
                if shape.get('placeholder'):
                    placeholder_type = shape['placeholder'].get('type')
                    if placeholder_type == 'TITLE' or placeholder_type == 'CENTERED_TITLE':
                        title_id = element['objectId']
                    elif placeholder_type == 'BODY':
                        body_id = element['objectId']
                    elif placeholder_type == 'SUBTITLE':
                        subtitle_id = element['objectId']

        # Ajouter le titre
        if title_id and slide_data.get('title'):
            content_requests.append({
                'insertText': {
                    'objectId': title_id,
                    'text': slide_data['title'],
                    'insertionIndex': 0
                }
            })

        # Ajouter le corps ou sous-titre
        if slide_data.get('body') and body_id:
            content_requests.append({
                'insertText': {
                    'objectId': body_id,
                    'text': slide_data['body'],
                    'insertionIndex': 0
                }
            })
        elif slide_data.get('subtitle') and subtitle_id:
            content_requests.append({
                'insertText': {
                    'objectId': subtitle_id,
                    'text': slide_data['subtitle'],
                    'insertionIndex': 0
                }
            })

    # Exécuter l'ajout de contenu
    if content_requests:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': content_requests}
        ).execute()
        print("[OK] Contenu ajouté aux slides")

    # Appliquer le thème Ran.AI Agency
    apply_theme(slides_service, presentation_id)

    print(f"\n{'='*60}")
    print(f"PRÉSENTATION CRÉÉE AVEC SUCCÈS!")
    print(f"{'='*60}")
    print(f"URL: https://docs.google.com/presentation/d/{presentation_id}/edit")
    print(f"\nThème appliqué: Ran.AI Agency")
    print(f"  - Fond: Vert pâle (#EEF3E5)")
    print(f"  - Titres: Vert foncé (#617E4D) - Roboto Bold")
    print(f"  - Corps: Gris foncé (#212121) - Open Sans")
    print(f"\nProchaines étapes:")
    print("1. Ouvrir le lien ci-dessus")
    print("2. Ajouter le logo Ran.AI Agency sur la slide titre")
    print("3. Ajouter des icônes si nécessaire")
    print("4. Tester en mode présentation")

    return presentation_id

def update_existing_presentation(presentation_id):
    """Met à jour une présentation existante avec le thème"""
    creds = get_credentials()
    slides_service = build('slides', 'v1', credentials=creds)
    apply_theme(slides_service, presentation_id)
    print(f"[OK] Thème appliqué à la présentation existante")
    print(f"URL: https://docs.google.com/presentation/d/{presentation_id}/edit")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--update':
        # Mettre à jour la présentation existante
        presentation_id = "1VumGoCPj3yecmhd5BUwiCmyugFyOQ927L4jQRmMdZAY"
        update_existing_presentation(presentation_id)
    else:
        create_presentation()
