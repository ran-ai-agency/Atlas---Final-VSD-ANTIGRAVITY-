# Directive: Gestion des contacts Zoho Books

## Objectif
Créer, modifier et gérer les contacts (clients et fournisseurs) dans Zoho Books via l'API MCP.

## Règles critiques

### 1. Format d'appel MCP pour Zoho Books
**IMPORTANT:** Tous les outils Zoho Books MCP utilisent:
- **Préfixe:** `ZohoBooks_` (avec underscore, pas d'espace)
- **Structure des arguments:**
  ```python
  {
      "query_params": {
          "organization_id": "110002033190"
      },
      "body": {
          # Données de l'objet ici
      }
  }
  ```

**ERREUR FRÉQUENTE À ÉVITER:**
- ❌ `"name": "create contact"` (avec espace)
- ❌ `"name": "create_contact"` (sans préfixe)
- ✅ `"name": "ZohoBooks_create_contact"` (CORRECT)

### 2. Organization ID obligatoire
- L'`organization_id` doit TOUJOURS être passé dans `query_params`
- Valeur: `110002033190` (stockée dans `.env` comme `ZOHO_BOOKS_ORGANIZATION_ID`)
- Ne JAMAIS inclure `organization_id` dans le `body`

### 3. Types de contacts
- `customer`: Client
- `vendor`: Fournisseur

## Script d'exécution
`execution/zoho_books_create_contact.py`

## Configuration requise
- `ZOHO_BOOKS_ORGANIZATION_ID` dans `.env` (valeur: 110002033190)
- `MCP_ZOHO_BOOKS_URL` dans `.env`
- `MCP_ZOHO_BOOKS_KEY` dans `.env`

## Création d'un contact

### Champs disponibles
| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| contact_name | string | ✅ | Nom du contact (entreprise ou personne) |
| contact_type | string | ✅ | "customer" ou "vendor" |
| email | string | ❌ | Email du contact |
| phone | string | ❌ | Numéro de téléphone |
| mobile | string | ❌ | Numéro de mobile |
| website | string | ❌ | Site web |
| billing_address | object | ❌ | Adresse de facturation |
| notes | string | ❌ | Notes additionnelles |

### Structure de l'adresse
```python
{
    "street": "9500, rue de Limoilou",
    "city": "Quebec",
    "state": "QC",
    "zip": "H1K 0J6",
    "country": "Canada"
}
```

## Exemple d'utilisation

### Via Python
```python
from zoho_books_create_contact import create_contact

contact = create_contact(
    contact_name="Solution Comptabilité - Sébastien Vachon",
    contact_type="vendor",
    email="info@solutioncomptabilite.com",
    phone="(514) 880-2776",
    website="solutioncomptabilite.com",
    billing_address={
        "street": "9500, rue de Limoilou",
        "city": "Quebec",
        "state": "QC",
        "zip": "H1K 0J6",
        "country": "Canada"
    },
    notes="Président / Solution Comptabilité"
)

print(f"Contact créé avec ID: {contact['contact_id']}")
```

### Via MCP direct
```python
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "ZohoBooks_create_contact",  # Avec préfixe ZohoBooks_
        "arguments": {
            "query_params": {
                "organization_id": "110002033190"
            },
            "body": {
                "contact_name": "Nom du contact",
                "contact_type": "vendor",
                "email": "email@example.com",
                "phone": "(514) 123-4567"
            }
        }
    }
}
```

## Format de réponse

La réponse MCP contient un JSON encodé dans `result.content[0].text`:

```json
{
    "code": 0,
    "message": "Le contact a été ajouté.",
    "contact": {
        "contact_id": "89554000000145003",
        "contact_name": "Solution Comptabilite - Sebastien Vachon",
        "contact_type": "vendor",
        "email": "info@solutioncomptabilite.com",
        "phone": "(514) 880-2776",
        "website": "solutioncomptabilite.com",
        "billing_address": { ... },
        "notes": "President / Solution Comptabilite",
        "created_time": "2026-01-08T15:55:19-0500",
        ...
    }
}
```

## Autres outils disponibles

Liste des outils Zoho Books MCP pour les contacts:
- `ZohoBooks_create_contact` - Créer un contact
- `ZohoBooks_update_contact` - Modifier un contact
- `ZohoBooks_get_contact` - Obtenir les détails d'un contact
- `ZohoBooks_list_contacts` - Lister tous les contacts

Tous suivent la même structure avec `ZohoBooks_` prefix et `query_params` + `body`.

## Troubleshooting

### Erreur: "Method not found"
- Vérifier que le nom inclut le préfixe `ZohoBooks_`
- Exemple: `ZohoBooks_create_contact`, pas `create_contact`

### Erreur: "Error while executing tool"
- Vérifier que `organization_id` est dans `query_params`, pas dans `body`
- Vérifier que les URLs et clés MCP dans `.env` sont valides

### Réponse vide ou None
- Parser le JSON depuis `result.content[0].text`
- Ne pas s'attendre à `result.contact` directement

## Historique des corrections

**2026-01-08:** Documentation créée après résolution du problème de création de contact.
- ✅ Identifié que les outils nécessitent le préfixe `ZohoBooks_`
- ✅ Documenté la structure `query_params` + `body`
- ✅ Contact "Sébastien Vachon" créé avec succès (ID: 89554000000145003)
