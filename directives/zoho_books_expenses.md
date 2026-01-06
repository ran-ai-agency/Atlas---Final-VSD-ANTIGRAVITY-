# Directive: Gestion des dépenses Zoho Books

## Objectif
Enregistrer les dépenses dans Zoho Books via l'API MCP de manière fiable et sans doublons.

## Règles critiques

### 1. TOUJOURS vérifier les doublons AVANT de créer une dépense
- Lister les dépenses récentes avec `list_expenses()`
- Vérifier si une dépense avec le même `reference_number` ou les mêmes caractéristiques (date, montant, fournisseur) existe déjà
- Ne jamais créer de dépense si un doublon potentiel est détecté

### 2. Structure des dépenses avec taxes (Québec)
- Utiliser le groupe de taxes `TPS+TVQ Québec` (ID: `89554000000113107`) pour les dépenses taxables
- Les taxes TPS et TVQ seront séparées automatiquement dans les rapports fiscaux
- Le pourboire doit être créé comme dépense séparée SANS taxe

### 3. Informations requises pour chaque dépense
- `date`: Format YYYY-MM-DD
- `amount`: Montant HT (avant taxes)
- `vendor_name`: Nom du fournisseur
- `reference_number`: Numéro de reçu/facture (utilisé pour détecter les doublons)
- `description`: Description de la dépense
- `account_id`: Compte de dépense (ex: Repas et divertissements)
- `paid_through_account_id`: Compte de paiement (ex: RBC MasterCard)

## Comptes disponibles

### Comptes de dépenses
| ID | Nom |
|----|-----|
| 89554000000000406 | Repas et divertissements |
| 89554000000057001 | Formation |
| 89554000000000385 | Dépenses informatiques et d'Internet |
| 89554000000000376 | Frais de déplacement |
| 89554000000000361 | Publicité et marketing |

### Comptes de paiement
| ID | Nom |
|----|-----|
| 89554000000057009 | RBC MasterCard |
| 89554000000117281 | Desjardins Visa |
| 89554000000000319 | Petite caisse |

### Taxes
| ID | Nom | Taux |
|----|-----|------|
| 89554000000113107 | TPS+TVQ Québec | 14.975% |
| 89554000000019067 | TPS | 5% |
| 89554000000111047 | TVQ | 9.975% |

## Script d'exécution
`execution/zoho_books_create_expense.py`

## Configuration requise
- `ZOHO_BOOKS_ORGANIZATION_ID` dans `.env` (valeur: 110002033190)
- MCP Server Zoho Books configuré avec clé valide

## Limitations actuelles
- L'API MCP ne supporte pas l'ajout de pièces jointes (reçus)
- Les pièces jointes doivent être ajoutées manuellement dans Zoho Books

## Flux de travail recommandé

1. **Analyser le reçu**
   - Extraire: date, fournisseur, sous-total, taxes, pourboire, total

2. **Vérifier les doublons**
   ```python
   expenses = list_expenses(ORG_ID)
   # Chercher par reference_number ou date+montant+fournisseur
   ```

3. **Créer la dépense principale** (avec taxes)
   ```python
   create_expense_with_tax(
       org_id=ORG_ID,
       account_id="...",
       paid_through_account_id="...",
       date="YYYY-MM-DD",
       amount=sous_total,  # Montant HT
       tax_id="89554000000113107",  # TPS+TVQ
       vendor_name="...",
       reference_number="..."
   )
   ```

4. **Créer le pourboire** (si applicable, sans taxe)
   ```python
   create_expense_with_tax(
       org_id=ORG_ID,
       account_id="...",
       paid_through_account_id="...",
       date="YYYY-MM-DD",
       amount=pourboire,
       tax_id=None,
       vendor_name="...",
       reference_number="...-TIP"
   )
   ```

5. **Vérifier la création**
   ```python
   list_expenses(ORG_ID, limit=5)
   ```
