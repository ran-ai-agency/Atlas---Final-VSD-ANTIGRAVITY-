#!/usr/bin/env python3
"""
Presentation: Solutions IA pour Chantal Dery
Projet Maxime - Relance Janvier 2026
"""

import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive.file'
]

COLORS = {
    'primary_green': {'red': 97/255, 'green': 126/255, 'blue': 77/255},
    'dark_green': {'red': 99/255, 'green': 116/255, 'blue': 87/255},
    'light_green': {'red': 139/255, 'green': 187/255, 'blue': 103/255},
    'pale_green_bg': {'red': 238/255, 'green': 243/255, 'blue': 229/255},
    'white': {'red': 1, 'green': 1, 'blue': 1},
    'dark_text': {'red': 33/255, 'green': 33/255, 'blue': 33/255},
    'accent_orange': {'red': 230/255, 'green': 126/255, 'blue': 34/255},
    'accent_red': {'red': 192/255, 'green': 57/255, 'blue': 43/255},
}

def get_credentials():
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
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()

    requests = []

    for slide in presentation.get('slides', []):
        slide_id = slide['objectId']
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

        for element in slide.get('pageElements', []):
            if 'shape' in element:
                shape = element['shape']
                element_id = element['objectId']

                if shape.get('placeholder'):
                    placeholder_type = shape['placeholder'].get('type')

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
                                    'fontSize': {'magnitude': 32, 'unit': 'PT'}
                                },
                                'fields': 'foregroundColor,bold,fontFamily,fontSize'
                            }
                        })

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
                                    'fontSize': {'magnitude': 16, 'unit': 'PT'}
                                },
                                'fields': 'foregroundColor,fontFamily,fontSize'
                            }
                        })

    if requests:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()

def create_presentation():
    creds = get_credentials()
    slides_service = build('slides', 'v1', credentials=creds)

    presentation = slides_service.presentations().create(
        body={'title': "Chantal Dery - Nouvelles Solutions IA - Ran.AI Agency"}
    ).execute()

    presentation_id = presentation.get('presentationId')
    print(f"[OK] Presentation creee: https://docs.google.com/presentation/d/{presentation_id}")

    slides_content = [
        {
            "title": "Bonne Annee Chantal!",
            "subtitle": "Session de decouverte\n\nAdjointe Virtuelle x Ran.AI\nJanvier 2026",
            "layout": "TITLE"
        },
        {
            "title": "Objectif d'aujourd'hui",
            "body": "COMPRENDRE avant de proposer\n\n\n1. Qu'est-ce que tu cherchais a accomplir avec Maxime?\n\n2. Qu'est-ce qui t'a bloquee concretement?\n\n3. A quoi ressemblerait l'outil IDEAL pour toi?\n\n\nPas de pitch - juste une conversation.",
            "layout": "TITLE_AND_BODY"
        },
        {
            "title": "Ce que tu nous as dit",
            "body": "\"C'est comme s'il ne voyait pas la meme chose que moi.\nComme si c'etait une autre pas la meme version.\nDonc, je ne l'ai pas reutilise.\"\n\n\nQUESTIONS POUR MIEUX COMPRENDRE\n\n- C'etait quoi la \"chose\" qu'il ne voyait pas?\n  (un client? une conversation? un document?)\n\n- Qu'est-ce que tu essayais de faire a ce moment-la?\n\n- Combien de fois as-tu essaye avant d'abandonner?",
            "layout": "TITLE_AND_BODY"
        },
        {
            "title": "Ton business aujourd'hui",
            "body": "CE QU'ON SAIT\n- Entreprise: Adjointe Virtuelle\n- Besoin cle: Centralisation clients, suivi\n- Heures/semaine: 8h de travail repetitif\n- Objectif Phase 2: Automatisation taches recurrentes\n\n\nQUESTIONS\n\n- C'est quoi une journee typique pour toi?\n\n- Quelles taches te prennent le plus de temps?\n\n- Ou sont tes donnees clients actuellement?\n  (GHL? Sheets? Cahier? Tete?)",
            "layout": "TITLE_AND_BODY"
        },
        {
            "title": "L'assistant ideal",
            "body": "SI TU AVAIS UN ASSISTANT PARFAIT...\n\n\n- Quelles 3 taches lui donnerais-tu en premier?\n\n\n- Qu'est-ce qu'il devrait TOUJOURS savoir?\n\n\n- Qu'est-ce qu'il ne devrait JAMAIS faire seul?\n\n\n(Prends le temps d'y penser - c'est important)",
            "layout": "TITLE_AND_BODY"
        },
        {
            "title": "Pistes de solutions (apercu)",
            "body": "SELON CE QUE TU ME DIS...\n\nJe vais pouvoir te proposer quelque chose d'adapte:\n\n\nOption 1: Reparer Maxime dans GHL\n-> Si le probleme etait juste technique/configuration\n\nOption 2: Un vrai agent IA personnalise\n-> Si tu as besoin de plus que du chat/booking\n\nOption 3: Approche hybride\n-> Garder ce qui marche, ajouter ce qui manque\n\n\nMais d'abord, je veux bien comprendre TON besoin.",
            "layout": "TITLE_AND_BODY"
        },
        {
            "title": "Prochaines etapes",
            "body": "APRES CETTE RENCONTRE\n\n1. Je digere ce que tu m'as dit\n\n2. Je te reviens avec UNE proposition concrete\n   (pas 10 options - UNE qui fait du sens pour toi)\n\n3. On en discute, tu decides\n\n4. Si oui: on deploie avec suivi serre\n   Si non: pas de probleme, on reste en contact\n\n\nMON ENGAGEMENT\n\nJe veux que tu sois satisfaite AVANT de payer.\nComme en decembre - pas de facture si ca marche pas.",
            "layout": "TITLE_AND_BODY"
        },
        {
            "title": "Questions?",
            "body": "\n\n\nMerci de me donner une deuxieme chance.\n\n\nRoland Ranaivoarison\nRan.AI Agency\n\nroland@ran-ai-agency.ca",
            "layout": "TITLE_AND_BODY"
        }
    ]

    # Create slides
    requests = []
    for i, slide_data in enumerate(slides_content):
        if i > 0:
            layout = 'TITLE_AND_BODY' if slide_data.get('layout') == 'TITLE_AND_BODY' else 'TITLE'
            requests.append({
                'createSlide': {
                    'insertionIndex': i,
                    'slideLayoutReference': {'predefinedLayout': layout}
                }
            })

    if requests:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        print(f"[OK] {len(slides_content)} slides creees")

    # Get slide IDs
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()

    slide_ids = [slide['objectId'] for slide in presentation.get('slides', [])]

    # Add content
    content_requests = []

    for i, (slide_id, slide_data) in enumerate(zip(slide_ids, slides_content)):
        slide = presentation['slides'][i]
        title_id = None
        body_id = None
        subtitle_id = None

        for element in slide.get('pageElements', []):
            if 'shape' in element:
                shape = element['shape']
                if shape.get('placeholder'):
                    placeholder_type = shape['placeholder'].get('type')
                    if placeholder_type in ['TITLE', 'CENTERED_TITLE']:
                        title_id = element['objectId']
                    elif placeholder_type == 'BODY':
                        body_id = element['objectId']
                    elif placeholder_type == 'SUBTITLE':
                        subtitle_id = element['objectId']

        if title_id and slide_data.get('title'):
            content_requests.append({
                'insertText': {
                    'objectId': title_id,
                    'text': slide_data['title'],
                    'insertionIndex': 0
                }
            })

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

    if content_requests:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': content_requests}
        ).execute()
        print("[OK] Contenu ajoute aux slides")

    apply_theme(slides_service, presentation_id)

    print(f"\n{'='*60}")
    print(f"PRESENTATION CREEE AVEC SUCCES!")
    print(f"{'='*60}")
    print(f"URL: https://docs.google.com/presentation/d/{presentation_id}/edit")

    return presentation_id

if __name__ == "__main__":
    create_presentation()
