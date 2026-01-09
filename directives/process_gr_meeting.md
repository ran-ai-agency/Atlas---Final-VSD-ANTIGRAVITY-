# Directive: Traitement Post-Réunion GR International

## Contexte
Chaque jeudi, Roland participe à une réunion GR International Vaudreuil-Dorion 1. Après chaque réunion, il faut documenter, analyser et synchroniser l'information dans Notion.

## Objectif
Créer une analyse complète de chaque réunion GR avec insights stratégiques, actions recommandées, et assurer la cohérence des noms de participants entre tous les documents.

## Inputs
1. **Fichier chat de la réunion** (fourni par l'utilisateur)
   - Format: Texte brut avec messages de chat Zoom
   - Contient: Commentaires des participants, contacts partagés, interactions

2. **Notes détaillées de réunion** (déjà dans Notion ou à créer)
   - Format: Page Notion dans database "Réunions & Sessions"
   - Contient: Déroulement, présentations, mises à jour membres, références

## Processus

### Étape 1: Créer/Mettre à jour la page de réunion détaillée
**Script**: `execution/create_gr_meeting_page.py` (à créer)

1. Créer une nouvelle page dans la database Notion "Réunions & Sessions"
2. Titre: "Réunion GR International Vaudreuil-Dorion 1 - [DATE]"
3. Ajouter le contenu du chat dans une section "Chat de la réunion"
4. Structure minimale:
   - Heading: "Chat de la réunion"
   - Heading: "Boîte à outils: [Présentateur] - [Sujet]"
   - Liste des contacts partagés avec liens

**Commande**:
```bash
python execution/create_gr_meeting_page.py --chat-file [fichier] --date [YYYY-MM-DD]
```

### Étape 2: Générer l'analyse stratégique
**Script**: Manuel via Claude (pour l'instant)

Créer un second document d'analyse avec:

1. **📊 Insights Clés** (5-7 points)
   - Participation active
   - Boîte à outils (présentateur, réception)
   - Diversité des services
   - Positionnement unique de Roland
   - Opportunités de collaboration

2. **🎯 Prochaines Étapes** (4-5 actions)
   - Réseautage ciblé (RDA avec 3-5 membres)
   - Préparation boîte à outils
   - Stratégie de suivi
   - Identification prospects chauds
   - Documentation learnings (CRM)

3. **✅ Actions Immédiates** (5-7 todos)
   - Ajouter membres clés dans Zoho CRM
   - Contacter membres spécifiques
   - Messages LinkedIn personnalisés
   - Qualifier prospects (outils utilisés)
   - Préparer matériel

4. **💡 Réflexion Stratégique**
   - Pipeline calculation (ex: 15 membres × 10 groupes = 150+ entrepreneurs)
   - Positionnement Q1-Q2 2026
   - Objectifs (ex: 2-3 clients signés d'ici fin mars)
   - Avantages concurrentiels

5. **🔗 Documents connexes**
   - Lien vers pitch utilisé
   - Liens vers autres documents du même jour
   - Calendrier des prochaines boîtes à outils

**Format JSON à créer**: `.tmp/meeting_analysis.json`

### Étape 3: Synchroniser les noms des participants
**Script**: `execution/sync_participant_names.py` (à créer)

Cette étape est CRITIQUE car les noms peuvent varier entre documents.

**Liste de référence des participants GR International Vaudreuil-Dorion 1**:
```json
{
  "participants": [
    {"prenom": "Roland", "nom": "Ranaivoarison", "entreprise": "Ran.AI Agency"},
    {"prenom": "Mylène", "nom": "Sauvé", "entreprise": "Zen Au Quotidien", "role": "VP"},
    {"prenom": "Nathalie", "nom": "Cormier", "entreprise": "Coach Neuro-Activ", "role": "Présidente"},
    {"prenom": "Audrey", "nom": "Gagnon", "entreprise": "D.A.G Studio"},
    {"prenom": "Jessica", "nom": "Legault", "entreprise": "Confiance Propre"},
    {"prenom": "Caroline", "nom": "Cyr", "entreprise": "Primerica"},
    {"prenom": "Véronique", "nom": "Ferland", "entreprise": "Arbonne"},
    {"prenom": "Suzanne", "nom": "Boisvert", "entreprise": "Thermomix"},
    {"prenom": "Kim", "nom": "Leblanc", "entreprise": "MONAT"},
    {"prenom": "Léo", "nom": "Lemay", "entreprise": "Odotrack"},
    {"prenom": "Lyne", "nom": "Savoie", "entreprise": "Cashback", "role": "Gestionnaire district"},
    {"prenom": "Yannick", "nom": "Comtois", "entreprise": "Multi-Prêts", "role": "Visiteur/Invité"}
  ]
}
```

**Erreurs courantes à corriger**:
- "Véronique Perreault" → "Véronique Ferland"
- "Jessica Lebeau" → "Jessica Legault"
- "Yannick Courtois" → "Yannick Comtois"
- "Lynn Savoie" → "Lyne Savoie"

**Algorithme**:
1. Télécharger tous les blocs des 2 pages Notion (réunion + analyse)
2. Pour chaque bloc, extraire le texte
3. Détecter les noms incorrects via regex
4. Appliquer les corrections
5. Mettre à jour via API Notion (PATCH /blocks/{id})
6. Rate limiting: 0.3s entre chaque requête

**Commande**:
```bash
python execution/sync_participant_names.py --page1-id [ID] --page2-id [ID]
```

### Étape 4: Ajouter cross-references
**Script**: Manuel via Claude (pour l'instant)

Créer `.tmp/cross_reference.json` avec:
- Liste des documents connexes du même jour
- Lien vers le pitch utilisé
- Calendrier des prochaines boîtes à outils GR
- Synergies identifiées entre membres

Ajouter via:
```bash
curl -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children" \
  -H "Authorization: Bearer {token}" \
  -d @.tmp/cross_reference.json
```

## Outputs

### 1. Page Notion "Réunion détaillée"
- **Database**: Réunions & Sessions
- **Titre**: "Réunion GR International Vaudreuil-Dorion 1 - [DATE]"
- **Contenu**:
  - Chat complet de la réunion
  - Contacts partagés
  - Optionnel: Déroulement détaillé, présentations, références

### 2. Page Notion "Analyse"
- **Database**: Réunions & Sessions (ou même page avec section)
- **Titre**: "Réunion GR International Vaudreuil-Dorion 1 - [DATE]" (même page)
- **Contenu**:
  - Insights clés
  - Prochaines étapes
  - Actions immédiates
  - Réflexion stratégique
  - Documents connexes

### 3. Fichiers temporaires (`.tmp/`)
- `meeting_notion_payload.json` - Payload pour créer la page
- `meeting_analysis.json` - Analyse à ajouter
- `cross_reference.json` - Documents connexes
- `page1_blocks.json` - Blocs téléchargés page 1
- `page2_blocks.json` - Blocs téléchargés page 2
- `all_name_corrections.json` - Liste des corrections appliquées

## Outils utilisés

### APIs
- **Notion API**:
  - `POST /pages` - Créer page
  - `PATCH /pages/{id}` - Mettre à jour propriétés
  - `PATCH /blocks/{id}/children` - Ajouter contenu
  - `PATCH /blocks/{id}` - Modifier bloc existant
  - `GET /blocks/{id}/children` - Télécharger blocs

### Scripts Python
- `execution/create_gr_meeting_page.py` (à créer)
- `execution/sync_participant_names.py` (à créer)

### Variables d'environnement
```
NOTION_TOKEN=your_notion_token_here
NOTION_GR_DATABASE_ID=1c441b52-d187-80f9-b3f9-ff470d73a72d
```

## Edge Cases

### 1. Nouveau participant
Si un nouveau membre apparaît:
1. L'ajouter à `participants_reference.json`
2. Vérifier orthographe via LinkedIn/site web
3. Mettre à jour la directive

### 2. Participant absent
Si un membre régulier est absent:
- Le mentionner dans "Insights Clés" si pertinent
- Ne pas l'ajouter aux actions immédiates

### 3. Visiteur/Invité
Membres non-réguliers:
- Les identifier avec "Visiteur" ou "Invité" dans le rôle
- Ne pas les ajouter automatiquement au CRM
- Les mentionner dans "Opportunités" si pertinent

### 4. Erreur API Notion (429 - Rate limit)
Si rate limit atteint:
- Attendre 60 secondes
- Réessayer avec backoff exponentiel
- Maximum 3 tentatives

### 5. Noms avec accents/caractères spéciaux
- Toujours utiliser UTF-8
- Conserver les accents originaux (Mylène, pas Mylene)
- Vérifier encodage dans curl avec `--data-binary @file.json`

## Timing

- **Réunion GR**: Jeudis matins
- **Traitement**: Immédiatement après la réunion
- **Durée estimée**: 20-30 minutes (automatisé: 5-10 minutes)

## Métriques de succès

- ✅ Page de réunion créée dans les 2h suivant la réunion
- ✅ Analyse complète avec 5+ insights et 5+ actions
- ✅ 100% des noms de participants corrects et cohérents
- ✅ Cross-references ajoutées vers documents connexes
- ✅ Actions CRM créées pour 3-5 membres prioritaires

## Prochaines améliorations

1. **Script d'automatisation complet** (à créer)
   - Input: Fichier chat + date
   - Output: Pages Notion complètes et synchronisées

2. **Template d'analyse dynamique** (à créer)
   - Génération automatique des insights via LLM
   - Détection automatique des opportunités

3. **Intégration Zoho CRM** (à créer)
   - Ajouter automatiquement les membres comme leads
   - Créer tâches de suivi dans Zoho

4. **Dashboard hebdomadaire** (à créer)
   - Visualisation des métriques GR
   - Suivi des références partagées
   - Pipeline de prospects GR

## Notes

- Cette directive documente le processus manuel effectué le 8 janvier 2026
- Les scripts Python mentionnés sont à créer pour automatiser
- Le processus actuel prend ~30 minutes manuellement
- Objectif: Réduire à 5-10 minutes avec automatisation complète
