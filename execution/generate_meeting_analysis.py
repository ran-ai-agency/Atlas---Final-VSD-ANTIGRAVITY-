#!/usr/bin/env python3
"""
Génère une analyse stratégique d'une réunion GR International.

Ce script crée un template d'analyse que Claude peut remplir avec:
- Insights clés
- Prochaines étapes
- Actions immédiates
- Réflexion stratégique
- Documents connexes

Usage:
    python generate_meeting_analysis.py --page-id <notion_page_id>
    python generate_meeting_analysis.py --page-id <notion_page_id> --output-file analysis.json

Examples:
    python generate_meeting_analysis.py --page-id 2e241b52-d187-8102-bd74-e3fc5f84d4d7
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Dict, List

# Configuration
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
if not NOTION_TOKEN:
    raise ValueError("NOTION_TOKEN environment variable is required")
NOTION_VERSION = '2022-06-28'

def notion_request(method: str, endpoint: str, data: dict = None) -> dict:
    """Fait une requête à l'API Notion"""
    url = f"https://api.notion.com/v1{endpoint}"
    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': NOTION_VERSION,
        'Content-Type': 'application/json'
    }

    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'PATCH':
        response = requests.patch(url, headers=headers, json=data)
    else:
        raise ValueError(f"Unsupported method: {method}")

    response.raise_for_status()
    return response.json()

def get_page_info(page_id: str) -> Dict:
    """Récupère les informations d'une page"""
    return notion_request('GET', f'/pages/{page_id}')

def create_analysis_template(participants_count: int = 11) -> Dict:
    """
    Crée un template d'analyse stratégique.

    Le template suit la structure standard:
    - Insights Clés (5-7 points)
    - Prochaines Étapes (4-5 actions)
    - Actions Immédiates (5-7 todos)
    - Réflexion Stratégique
    - Documents connexes
    """
    return {
        'children': [
            {
                'object': 'block',
                'type': 'divider',
                'divider': {}
            },
            {
                'object': 'block',
                'type': 'heading_2',
                'heading_2': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': '📊 Insights Clés'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'bulleted_list_item',
                'bulleted_list_item': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'Participation active: ', 'link': None},
                            'annotations': {'bold': True}
                        },
                        {
                            'type': 'text',
                            'text': {'content': f'{participants_count} membres ont partagé leurs contacts, démontrant un engagement élevé'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'bulleted_list_item',
                'bulleted_list_item': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'Boîte à outils bien reçue: ', 'link': None},
                            'annotations': {'bold': True}
                        },
                        {
                            'type': 'text',
                            'text': {'content': '[À compléter: Nom présentateur + réactions positives]'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'bulleted_list_item',
                'bulleted_list_item': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'Diversité des services: ', 'link': None},
                            'annotations': {'bold': True}
                        },
                        {
                            'type': 'text',
                            'text': {'content': '[À compléter: Liste des domaines représentés]'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'bulleted_list_item',
                'bulleted_list_item': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'Votre positionnement unique: ', 'link': None},
                            'annotations': {'bold': True}
                        },
                        {
                            'type': 'text',
                            'text': {'content': 'Seul consultant IA du groupe - différenciation claire vs services traditionnels'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'bulleted_list_item',
                'bulleted_list_item': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'Opportunité de collaboration: ', 'link': None},
                            'annotations': {'bold': True}
                        },
                        {
                            'type': 'text',
                            'text': {'content': '[À compléter: Membres avec CRM/outils à automatiser]'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'divider',
                'divider': {}
            },
            {
                'object': 'block',
                'type': 'heading_2',
                'heading_2': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': '🎯 Prochaines Étapes'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'numbered_list_item',
                'numbered_list_item': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'Réseautage ciblé: ', 'link': None},
                            'annotations': {'bold': True}
                        },
                        {
                            'type': 'text',
                            'text': {'content': 'Contacter 3-5 membres pour RDA (Rendez-vous d\'affaires) individuels d\'ici fin du mois'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'numbered_list_item',
                'numbered_list_item': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'Préparer boîte à outils: ', 'link': None},
                            'annotations': {'bold': True}
                        },
                        {
                            'type': 'text',
                            'text': {'content': 'Finaliser slides, pratiquer présentation 13 min + 5 min Q&R (date: 29 janvier 2026)'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'numbered_list_item',
                'numbered_list_item': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'Stratégie de suivi: ', 'link': None},
                            'annotations': {'bold': True}
                        },
                        {
                            'type': 'text',
                            'text': {'content': 'Envoyer message LinkedIn personnalisé aux membres actifs'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'numbered_list_item',
                'numbered_list_item': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'Identifier prospects chauds: ', 'link': None},
                            'annotations': {'bold': True}
                        },
                        {
                            'type': 'text',
                            'text': {'content': 'Qualifier lesquels utilisent déjà Zoho/Salesforce/Go High Level → opportunités d\'automatisation'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'numbered_list_item',
                'numbered_list_item': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'Documenter learnings: ', 'link': None},
                            'annotations': {'bold': True}
                        },
                        {
                            'type': 'text',
                            'text': {'content': 'Ajouter à CRM Zoho les membres actifs comme leads'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'divider',
                'divider': {}
            },
            {
                'object': 'block',
                'type': 'heading_2',
                'heading_2': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': '✅ Actions Immédiates'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'to_do',
                'to_do': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': '[À compléter: Membre prioritaire 1] - opportunité [spécifique]'}
                        }
                    ],
                    'checked': False
                }
            },
            {
                'object': 'block',
                'type': 'to_do',
                'to_do': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': '[À compléter: Membre prioritaire 2] - explorer besoins CRM'}
                        }
                    ],
                    'checked': False
                }
            },
            {
                'object': 'block',
                'type': 'to_do',
                'to_do': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': '[À compléter: Membre prioritaire 3] - synergies [domaine]'}
                        }
                    ],
                    'checked': False
                }
            },
            {
                'object': 'block',
                'type': 'to_do',
                'to_do': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'Préparer 3 questions pour mieux qualifier prospects GR lors des prochaines réunions'}
                        }
                    ],
                    'checked': False
                }
            },
            {
                'object': 'block',
                'type': 'to_do',
                'to_do': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'Créer lead magnet spécifique GR: "Mini-audit IA pour votre entreprise de services"'}
                        }
                    ],
                    'checked': False
                }
            },
            {
                'object': 'block',
                'type': 'divider',
                'divider': {}
            },
            {
                'object': 'block',
                'type': 'heading_2',
                'heading_2': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': '💡 Réflexion Stratégique'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'paragraph',
                'paragraph': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'GR International = pipeline stable: ', 'link': None},
                            'annotations': {'bold': True}
                        },
                        {
                            'type': 'text',
                            'text': {'content': f'~{participants_count} membres actifs × 10 groupes Québec = {participants_count * 10}+ entrepreneurs PME exposés à votre message chaque mois'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'paragraph',
                'paragraph': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'Stratégie 2026: ', 'link': None},
                            'annotations': {'bold': True}
                        },
                        {
                            'type': 'text',
                            'text': {'content': 'Positionner GR comme canal d\'acquisition principal Q1-Q2. Objectif: 2-3 clients signés directement du réseau GR d\'ici fin mars.'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'paragraph',
                'paragraph': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'Avantage concurrentiel: ', 'link': None},
                            'annotations': {'bold': True}
                        },
                        {
                            'type': 'text',
                            'text': {'content': 'Vous êtes membre actif (Secrétaire-Trésorier) = crédibilité > consultant externe. Votre boîte à outils 29 janvier = démonstration de votre expertise devant audience qualifiée.'}
                        }
                    ]
                }
            },
            {
                'object': 'block',
                'type': 'callout',
                'callout': {
                    'rich_text': [
                        {
                            'type': 'text',
                            'text': {'content': 'Note pour prochaine réunion: ', 'link': None},
                            'annotations': {'bold': True}
                        },
                        {
                            'type': 'text',
                            'text': {'content': 'Poser la question "Qui ici utilise Zoho, Salesforce ou un autre CRM?" après votre pitch. Cela identifie immédiatement vos prospects chauds.'}
                        }
                    ],
                    'icon': {
                        'type': 'emoji',
                        'emoji': '💡'
                    }
                }
            }
        ]
    }

def add_analysis_to_page(page_id: str, analysis_blocks: Dict) -> bool:
    """Ajoute l'analyse à une page Notion"""
    try:
        print(f"Adding analysis to page {page_id}...")
        notion_request('PATCH', f'/blocks/{page_id}/children', analysis_blocks)
        print("✅ Analysis added successfully!")
        return True
    except Exception as e:
        print(f"❌ Error adding analysis: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Génère une analyse stratégique pour une réunion GR International',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_meeting_analysis.py --page-id 2e241b52-d187-8102-bd74-e3fc5f84d4d7
  python generate_meeting_analysis.py --page-id 2e241b52-d187-8102-bd74-e3fc5f84d4d7 --output-file .tmp/analysis.json
        """
    )

    parser.add_argument(
        '--page-id',
        required=True,
        help='ID de la page Notion de la réunion'
    )

    parser.add_argument(
        '--output-file',
        type=Path,
        help='Fichier de sortie pour sauvegarder le JSON (optionnel)'
    )

    parser.add_argument(
        '--participants',
        type=int,
        default=11,
        help='Nombre de participants (défaut: 11)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Générer le template sans l\'ajouter à Notion'
    )

    args = parser.parse_args()

    # Vérifier que la page existe
    try:
        print(f"Fetching page info...")
        page_info = get_page_info(args.page_id)
        title = page_info['properties']['Session Title']['title'][0]['text']['content']
        print(f"Page title: {title}")
    except Exception as e:
        print(f"❌ Error fetching page: {e}")
        sys.exit(1)

    # Créer le template
    print(f"\nGenerating analysis template...")
    analysis = create_analysis_template(participants_count=args.participants)

    # Sauvegarder si demandé
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"✅ Template saved to: {args.output_file}")

    # Ajouter à Notion si pas dry-run
    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - Analysis not added to Notion")
        print("Template structure:")
        print("  - 📊 Insights Clés (5 bullet points)")
        print("  - 🎯 Prochaines Étapes (5 numbered items)")
        print("  - ✅ Actions Immédiates (5 todos)")
        print("  - 💡 Réflexion Stratégique (3 paragraphs + callout)")
    else:
        success = add_analysis_to_page(args.page_id, analysis)

        if success:
            print(f"\n📝 Next steps:")
            print(f"1. Open the page and customize the [À compléter] sections")
            print(f"2. Add cross-references to related documents")
            print(f"3. Run sync_participant_names.py to ensure consistency")
            print(f"\nPage URL: https://www.notion.so/{args.page_id.replace('-', '')}")

if __name__ == '__main__':
    main()
