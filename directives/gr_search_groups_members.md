# Directive: Recherche et Extraction des Groupes et Membres GR International

## Objectif
Extraire toutes les informations disponibles sur les groupes et leurs membres depuis la section de recherche du site GR International, et sauvegarder ces données dans des fichiers JSON pour analyse ultérieure.

## Contexte
GR International dispose d'une section de recherche permettant de trouver des groupes par région et d'explorer les membres de chaque groupe. Ces informations sont précieuses pour le networking et la stratégie de développement de réseau.

## Outils Requis
- **Script d'exécution**: `execution/gr_search_groups_members.py`
- **Credentials**: `.env` (GR_EMAIL, GR_PASSWORD, GR_MEMBER_URL)
- **Librairie**: Playwright pour la navigation web

## Inputs
- Aucun paramètre externe requis
- Utilise automatiquement les credentials du fichier `.env`

## Processus d'Exécution

### 1. Authentification
- Se connecter au site GR International via le lien membre (GR_MEMBER_URL)
- Fallback vers login classique si le token expire

### 2. Navigation vers la Section Recherche
- Localiser la section de recherche de groupes
- Identifier les filtres disponibles (région, pays, type)

### 3. Extraction des Groupes
Pour chaque groupe trouvé, extraire:
- **Nom du groupe**
- **Région/Ville**
- **Jour de réunion**
- **Heure de réunion**
- **Format** (Présentiel/Zoom/Hybride)
- **URL de la page du groupe**
- **Statut** (Actif/En formation/etc.)
- **Nombre de membres** (si disponible)

### 4. Extraction des Membres
Pour chaque groupe, accéder à la liste des membres et extraire:
- **Nom complet**
- **Prénom**
- **Nom de famille**
- **Entreprise**
- **Poste/Titre**
- **Catégorie d'affaires**
- **Téléphone** (si disponible)
- **Email** (si disponible)
- **LinkedIn** (si disponible)
- **Site web** (si disponible)
- **Rôle dans le groupe** (Président, Secrétaire-Trésorier, Membre, etc.)

### 5. Structure des Données

#### Fichier: `.tmp/gr_groups_complete.json`
```json
[
  {
    "group_id": "vaudreuil-1",
    "group_name": "GR Vaudreuil 1",
    "region": "Vaudreuil-Dorion",
    "province": "Quebec",
    "country": "Canada",
    "meeting_day": "Jeudi",
    "meeting_time": "7h30",
    "format": "Presentiel",
    "status": "Actif",
    "member_count": 25,
    "group_url": "https://...",
    "members": [...]
  }
]
```

#### Fichier: `.tmp/gr_members_complete.json`
```json
[
  {
    "member_id": "unique_id",
    "first_name": "Roland",
    "last_name": "Ranaivoarison",
    "full_name": "Roland Ranaivoarison",
    "company": "Ran.AI Agency",
    "title": "CEO",
    "category": "Services IA",
    "group": "GR Vaudreuil 1",
    "group_role": "Secrétaire-Trésorier",
    "phone": "514-918-1241",
    "email": "contact@example.com",
    "linkedin": "https://linkedin.com/in/...",
    "website": "https://www.ran-ai-agency.ca",
    "location": "Vaudreuil-Dorion"
  }
]
```

## Outputs

1. **Fichier JSON des groupes**: `.tmp/gr_groups_complete.json`
2. **Fichier JSON des membres**: `.tmp/gr_members_complete.json`
3. **Rapport d'analyse**: `.tmp/gr_network_analysis.md` (optionnel)
4. **Screenshots**: `.tmp/gr_search_*.png` pour debug

## Gestion d'Erreurs

### Erreurs Communes
- **Token expiré**: Utiliser le login classique
- **Page non chargée**: Attendre plus longtemps (wait_for_timeout)
- **Sélecteurs changés**: Utiliser plusieurs stratégies de sélection
- **Données manquantes**: Marquer comme "Non spécifié" plutôt que d'échouer

### Retry Logic
- 3 tentatives maximum par page
- Pause de 2 secondes entre tentatives
- Sauvegarder les données partielles en cas d'échec

## Considérations

### Respect du Site
- Pause de 1-2 secondes entre requêtes
- Ne pas surcharger le serveur
- Utiliser headless mode par défaut

### Confidentialité
- Les données sont stockées localement dans `.tmp/`
- Ne jamais committer les fichiers JSON contenant des données personnelles
- Utiliser ces données uniquement pour networking légitime

### Performance
- Pagination: traiter maximum 50 groupes à la fois
- Pour chaque groupe, limiter à 100 membres maximum
- Durée estimée: 10-20 minutes pour l'extraction complète

## Utilisation

```bash
# Extraction complète
python execution/gr_search_groups_members.py

# Mode visible (pour debug)
python execution/gr_search_groups_members.py --visible

# Région spécifique
python execution/gr_search_groups_members.py --region Quebec
```

## Améliorations Futures

1. **Filtrage avancé**: Ajouter des filtres par catégorie d'affaires
2. **Export CSV**: En plus du JSON
3. **Analyse de réseau**: Identifier les connexions entre membres
4. **Mise à jour incrémentale**: Détecter les changements depuis la dernière extraction
5. **Intégration CRM**: Synchroniser avec Zoho CRM

## Notes de Maintenance

- **Dernière mise à jour**: 2026-01-08
- **Fréquence recommandée**: Mensuelle
- **Dépendances**: playwright, python-dotenv
- **Limitations connues**: Certaines données membres peuvent nécessiter l'authentification premium
