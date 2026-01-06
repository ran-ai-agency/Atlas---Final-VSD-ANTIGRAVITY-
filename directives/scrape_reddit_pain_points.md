# Directive : Scraper Reddit pour Identifier les Pain Points

## Objectif

Scraper Reddit de manière systématique pour identifier les problèmes les plus critiques rencontrés par les PAs (Personal Assistants) et solopreneurs, afin de déterminer quels problèmes peuvent être résolus par l'agence d'IA Atlas (équipe de direction IA : CEO, CMO, CFO, COO).

## Contexte Stratégique

**Cible principale :** Solopreneurs, freelancers, petites entreprises, assistants personnels

**Proposition de valeur Atlas :** Équipe de direction IA complète offrant stratégie globale + exécution automatisée

**Composition de l'Équipe de Direction IA :**
- **CEO** - Vision stratégique, décisions critiques, alignement global
- **CMO** - Marketing, acquisition clients, branding, contenu
- **CFO** - Finance, cash flow, budgeting, planification financière
- **COO** - Opérations, processus, scaling, efficacité
- **CTO** - Technologie, innovation, infrastructure, automatisation technique
- **Assistant Virtuel** - Workflows administratifs, tâches répétitives, système agentic pour économie de temps

**Différenciateur clé :** Pas juste des outils isolés, mais une intelligence stratégique coordonnée (6 agents) + exécution automatisée des tâches chronophages via l'Assistant Virtuel

## Inputs Requis

### 1. Configuration des Subreddits Cibles
```json
{
  "priority_subreddits": [
    "solopreneur",
    "Entrepreneur", 
    "smallbusiness",
    "freelance",
    "productivity",
    "digitalnomad",
    "startups",
    "business"
  ],
  "secondary_subreddits": [
    "marketing",
    "accounting",
    "sales",
    "remotework",
    "sidehustle"
  ]
}
```

### 2. Paramètres de Scraping
- **Période :** 90 derniers jours (pour capturer tendances récentes)
- **Tri :** Par "top" (most upvoted) et "hot" (trending)
- **Seuil minimum :** Posts avec 10+ upvotes ou 5+ commentaires
- **Limite initiale :** 100 posts par subreddit (ajustable)

### 3. Mots-clés de Détection de Pain Points
```python
pain_keywords = [
    # Frustration
    "struggling with", "frustrated", "overwhelmed", "stuck",
    "can't figure out", "wasting time", "too much time",
    
    # Besoin d'aide
    "need help", "how do I", "best way to", "advice needed",
    "recommendations for", "what tools",
    
    # Problèmes spécifiques
    "automate", "manual process", "repetitive", "time-consuming",
    "losing money", "cash flow", "can't afford",
    "no time for", "wearing too many hats",
    
    # Domaines stratégiques
    "marketing strategy", "financial planning", "operations",
    "scaling", "growth", "hiring",
    
    # Technologie (CTO)
    "tech stack", "integration", "API", "software", "platform",
    "tools don't work together", "technical debt", "automation tools",
    "which software", "tech solution",
    
    # Tâches administratives (Assistant Virtuel)
    "data entry", "scheduling", "email management", "admin work",
    "paperwork", "invoicing", "bookkeeping", "calendar management",
    "follow-ups", "copy-paste", "spreadsheet work", "manual updates"
]
```

## Outils à Utiliser

### Scripts d'Exécution
1. **`execution/reddit_scraper.py`** - Scraping principal via PRAW
2. **`execution/reddit_pain_analyzer.py`** - Analyse NLP des posts
3. **`execution/reddit_categorizer.py`** - Catégorisation par domaine Atlas
4. **`execution/reddit_reporter.py`** - Génération du rapport final

### APIs et Bibliothèques
- **PRAW** (Python Reddit API Wrapper) - Accès Reddit API
- **OpenAI API** - Analyse sémantique et catégorisation
- **Pandas** - Manipulation de données
- **Google Sheets API** - Export des résultats (deliverable)

### Credentials Requis
- Reddit API credentials (`.env` : `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`)
- OpenAI API key (`.env` : `OPENAI_API_KEY`)
- Google Sheets credentials (`credentials.json`, `token.json`)

## Processus d'Exécution

### Phase 1 : Scraping Initial (Approche 1 - Ciblée)

**Étape 1.1 : Configuration**
```bash
python execution/reddit_scraper.py --mode init
```
- Vérifie les credentials Reddit API
- Initialise la connexion PRAW
- Crée le dossier `.tmp/reddit_scraping/`

**Étape 1.2 : Scraping par Subreddit**
```bash
python execution/reddit_scraper.py --subreddits priority --timeframe 90d --limit 100
```
- Collecte les posts des subreddits prioritaires
- Sauvegarde en `.tmp/reddit_scraping/raw_posts_{timestamp}.json`
- Format de sortie :
```json
{
  "post_id": "abc123",
  "subreddit": "solopreneur",
  "title": "...",
  "selftext": "...",
  "score": 145,
  "num_comments": 32,
  "created_utc": 1704412800,
  "url": "...",
  "comments": [...]
}
```

**Étape 1.3 : Extraction des Commentaires**
- Pour chaque post avec 10+ commentaires
- Extraire les top 5 commentaires (par score)
- Capturer les solutions proposées et frustrations exprimées

### Phase 2 : Analyse et Catégorisation

**Étape 2.1 : Détection de Pain Points**
```bash
python execution/reddit_pain_analyzer.py --input .tmp/reddit_scraping/raw_posts_*.json
```

Processus d'analyse :
1. **Filtrage par mots-clés** : Identifier les posts contenant pain_keywords
2. **Analyse de sentiment** : Scorer l'intensité de la frustration (1-10)
3. **Extraction d'entités** : Identifier les problèmes spécifiques mentionnés
4. **Clustering** : Regrouper les problèmes similaires

Sortie : `.tmp/reddit_scraping/pain_points_{timestamp}.json`

**Étape 2.2 : Catégorisation par Domaine Atlas**
```bash
python execution/reddit_categorizer.py --input .tmp/reddit_scraping/pain_points_*.json
```

Mapping vers les agents Atlas :
- **CEO (Stratégie)** : Vision, scaling, pivots, décisions stratégiques, alignement d'équipe
- **CMO (Marketing)** : Acquisition clients, branding, content marketing, social media, SEO
- **CFO (Finance)** : Cash flow, pricing, budgeting, financial planning, rentabilité
- **COO (Opérations)** : Workflows, processus, hiring, management, efficacité opérationnelle
- **CTO (Technologie)** : Infrastructure tech, automatisation technique, outils, intégrations, innovation
- **Assistant Virtuel (Exécution)** : Tâches administratives, workflows répétitifs, data entry, scheduling, email management, recherche

Sortie : `.tmp/reddit_scraping/categorized_problems_{timestamp}.json`

**Étape 2.3 : Scoring de Priorité**

Algorithme de scoring :
```python
priority_score = (
    frequency * 0.3 +           # Combien de fois mentionné
    pain_intensity * 0.3 +      # Niveau de frustration (1-10)
    atlas_fit * 0.25 +          # Adéquation avec capacités Atlas (1-10)
    market_size * 0.15          # Taille du marché potentiel (1-10)
)
```

### Phase 3 : Génération du Rapport

**Étape 3.1 : Création du Rapport Structuré**
```bash
python execution/reddit_reporter.py --output google_sheets
```

**Structure du rapport (Google Sheet) :**

**Onglet 1 : Top 20 Pain Points**
| Rang | Problème | Fréquence | Intensité | Agent Atlas | Score Priorité | Exemples (liens) |
|------|----------|-----------|-----------|-------------|----------------|------------------|

**Onglet 2 : Analyse par Agent**
- CEO : Top 10 problèmes stratégiques
- CMO : Top 10 problèmes marketing
- CFO : Top 10 problèmes financiers
- COO : Top 10 problèmes opérationnels
- CTO : Top 10 problèmes technologiques
- Assistant Virtuel : Top 10 tâches chronophages/répétitives

**Onglet 3 : Solution Blueprints**
| Problème | Workflow Actuel (manuel) | Solution Atlas | Bénéfices Quantifiés |
|----------|--------------------------|----------------|----------------------|

**Onglet 4 : Competitive Intelligence**
| Problème | Solutions Existantes | Limitations | Avantage Atlas |
|----------|---------------------|-------------|----------------|

**Onglet 5 : Raw Data**
- Tous les posts scrapés avec métadonnées

## Outputs Attendus

### Deliverable Principal
**Google Sheet** : "Reddit Pain Points Analysis - [Date]"
- Lien partageable
- Mise à jour automatique possible
- Visualisations intégrées (graphiques)

### Fichiers Intermédiaires (`.tmp/reddit_scraping/`)
- `raw_posts_{timestamp}.json` - Posts bruts
- `pain_points_{timestamp}.json` - Pain points extraits
- `categorized_problems_{timestamp}.json` - Problèmes catégorisés
- `priority_ranking_{timestamp}.json` - Classement final

### Insights Stratégiques
Document Markdown : `.tmp/reddit_scraping/strategic_insights_{timestamp}.md`
```markdown
# Insights Stratégiques - Reddit Pain Points

## Top 3 Opportunités Immédiates
1. [Problème] - [Solution Atlas] - [Taille marché estimée]

## Patterns Émergents
- [Pattern 1]
- [Pattern 2]

## Positionnement Recommandé
[Messaging clé pour Atlas]

## Quick Wins
[Problèmes faciles à résoudre pour prouver la valeur]
```

## Gestion des Erreurs et Edge Cases

### Rate Limiting Reddit API
- **Limite :** 60 requêtes/minute
- **Solution :** Implémenter backoff exponentiel dans `reddit_scraper.py`
- **Fallback :** Si rate limit atteint, sauvegarder état et reprendre automatiquement

### Posts Supprimés/Privés
- Ignorer et logger dans `.tmp/reddit_scraping/errors.log`
- Continuer avec les posts accessibles

### Analyse NLP Échoue
- Si OpenAI API échoue, utiliser analyse par mots-clés basique
- Logger les posts problématiques pour revue manuelle

### Subreddit Inaccessible
- Vérifier si privé ou banni
- Passer au suivant et notifier dans le rapport

## Métriques de Succès

### Quantitatif
- ✅ Minimum 500 posts scrapés au total
- ✅ Au moins 100 pain points uniques identifiés
- ✅ 80%+ des pain points catégorisés avec confiance >0.7
- ✅ Top 20 pain points avec minimum 5 exemples chacun

### Qualitatif
- ✅ Insights actionnables pour chaque agent Atlas
- ✅ Au moins 3 "solution blueprints" détaillés
- ✅ Positionnement compétitif clair vs solutions existantes

## Itérations et Améliorations

### Après Premier Run
1. **Analyser les faux positifs** : Problèmes détectés mais non pertinents
2. **Affiner les mots-clés** : Ajouter/retirer selon résultats
3. **Ajuster le scoring** : Optimiser les poids de l'algorithme de priorité
4. **Élargir si nécessaire** : Ajouter des subreddits si gaps identifiés

### Mise à Jour de la Directive
Documenter ici les learnings :
- Nouveaux subreddits pertinents découverts
- Mots-clés qui fonctionnent/ne fonctionnent pas
- Timing optimal (jours/heures avec plus d'activité)
- Patterns de langage spécifiques à la cible

## Timeline Estimée

- **Setup initial** : 30 minutes (credentials, installation packages)
- **Scraping (500 posts)** : 1-2 heures (selon rate limits)
- **Analyse NLP** : 30-45 minutes (selon volume)
- **Catégorisation** : 15-20 minutes
- **Génération rapport** : 10 minutes

**Total : 2.5-4 heures pour un cycle complet**

## Prochaines Étapes Après Exécution

1. **Revue du rapport** avec l'équipe pour validation
2. **Sélection de 3-5 pain points** pour développement de solutions pilotes
3. **Création de landing pages** ciblées par pain point
4. **Développement de case studies** montrant Atlas en action
5. **Monitoring continu** : Re-scraper tous les 30 jours pour tendances

## Notes Importantes

- **Respect des ToS Reddit** : Pas de scraping abusif, respecter rate limits
- **Privacy** : Ne pas collecter d'informations personnelles identifiables
- **Éthique** : Utiliser les insights pour aider, pas manipuler
- **Données sensibles** : Ne jamais commit les posts bruts dans Git (`.tmp/` est gitignored)

---

**Dernière mise à jour :** 2026-01-04
**Propriétaire :** Atlas - Ran AI Agency
**Status :** ✅ Directive initiale créée, prête pour implémentation
