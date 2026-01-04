# Directive: GR International - Exploration des Événements

## Objectif
Explorer le site GR International chaque vendredi à 7h pour identifier les événements pertinents et fournir un résumé avec recommandations d'inscription.

## Contexte Utilisateur
- **Membre de**: GR International
- **Rôle**: Secrétaire-trésorier du groupe Vaudreuil 1
- **Localisation**: Région de Montréal/Vaudreuil

## Inputs
- **URL de base**: `https://www.grinternational.ca/membres/`
- **Page Schedule**: `https://www.grinternational.ca/schedule/`
- **Page Events**: `https://www.grinternational.ca/events/`
- **Identifiants**: Stockés dans `.env` (GR_EMAIL, GR_PASSWORD)
- **Période de recherche**: 2 semaines à venir

## Critères de Sélection des Événements

### Priorité Haute (Toujours inclure)
1. **Activités porte-ouvertes** ("Open House", "Portes ouvertes", "Guest Day")
2. **Événements de votre groupe** (Vaudreuil 1)
3. **Événements sur Zoom/Virtuels** (pas de contrainte géographique)

### Priorité Moyenne (Inclure si pertinent)
4. **Groupes visitables** - Événements d'autres groupes où vous pouvez assister en tant que visiteur
5. **Formations et conférences** en ligne
6. **Événements régionaux** Québec/Montréal

### Filtres Géographiques (pour présentiel uniquement)
- **Inclure**: Montréal, Laval, Rive-Sud, Rive-Nord, Vaudreuil-Soulanges, Ouest-de-l'Île
- **Exclure**: Événements présentiels à plus de 60km de Montréal
- **Zoom/Virtuel**: Toujours éligible, peu importe la localisation

### Filtres Temporels
- Préférence pour les événements en matinée ou midi
- Événements en soirée: inclure mais noter comme "soirée"

## Scripts/Outils
- `execution/gr_international_scraper.py` - Navigation et extraction des événements
- `execution/gr_event_analyzer.py` - Analyse et scoring des événements (à créer si nécessaire)

## Outputs
Rapport hebdomadaire contenant:

### 1. Résumé Exécutif
- Nombre d'événements trouvés
- Nombre d'événements recommandés
- Prochaine action suggérée

### 2. Événements Recommandés (triés par priorité)
Pour chaque événement:
- **Nom de l'événement**
- **Groupe organisateur**
- **Date et heure**
- **Format**: Présentiel / Zoom
- **Lieu** (si présentiel)
- **Type**: Porte-ouverte / Réunion régulière / Formation / Conférence
- **Score de pertinence**: ★★★★★
- **Lien d'inscription**
- **Notes**: Pourquoi cet événement est recommandé

### 3. Autres Événements (pour information)
Liste condensée des autres événements non prioritaires

## Étapes d'Exécution

1. **Authentification**
   - Se connecter au portail membres avec les identifiants
   - Vérifier que la session est active

2. **Extraction - Page Schedule**
   - Filtrer par: Région Québec, Français/Anglais, Prochaines 2 semaines
   - Extraire tous les événements correspondants

3. **Extraction - Page Events**
   - Parcourir les catégories: GR Events, Open Houses, Conferences, Training
   - Identifier les événements spéciaux

4. **Analyse et Scoring**
   - Appliquer les critères de priorité
   - Calculer le score de pertinence (1-5 étoiles)
   - Trier par date puis par score

5. **Génération du Rapport**
   - Formater le rapport en Markdown
   - Sauvegarder dans `.tmp/gr_events_report_YYYY-MM-DD.md`
   - Afficher le résumé à l'utilisateur

6. **Actions Suggérées**
   - Proposer les inscriptions recommandées
   - Attendre confirmation avant d'inscrire

## Cas Limites

- **Site inaccessible**: Réessayer 3 fois avec délai de 30 secondes, puis notifier l'utilisateur
- **Session expirée**: Re-authentifier automatiquement
- **Aucun événement trouvé**: Vérifier les filtres, élargir la recherche si nécessaire
- **Événement complet**: Mentionner "COMPLET" et suggérer liste d'attente si disponible
- **Conflit d'horaire**: Détecter si deux événements recommandés sont au même moment

## Fréquence
- **Automatique**: Chaque vendredi à 7h00 (heure de Montréal)
- **Manuel**: Sur demande avec commande "Explorer GR International"

## Notes et Apprentissages
- Le site utilise des formulaires Zoho pour les inscriptions
- Les événements sont parfois annoncés sur les groupes Facebook locaux
- Vérifier aussi `https://grnouvelles.zohosites.com/blogs/` pour les annonces
- Le filtre "Rapid Search" sur /schedule/ permet de filtrer par format (présentiel/virtuel)

## Apprentissages Techniques

### Structure du Site
- Le site utilise des appels AJAX vers `/reseautagedaffaires/ajax_region_scheduled.php` pour charger les événements
- Les résultats apparaissent dans `#reunion_content` après sélection d'une province/région
- Le formulaire de recherche rapide a plusieurs sections par pays (Canada, USA, France, Europe)
- Il faut sélectionner Quebec dans le dropdown Province/Territory, puis optionnellement une région

### Pages Importantes
- `/schedule/` - Horaires des réunions (recherche par région)
- `/events/` - Événements spéciaux (catégories: Open Houses, Guest Days, Conferences, etc.)
- `/membres/` - Portail membres (authentification requise)

### Authentification
- Le lien membre avec token (`GR_MEMBER_URL`) fonctionne pour l'accès rapide
- Sinon utiliser email/password via le formulaire de connexion

### Types d'Événements Détectés
- "Portes ouvertes" / "Open House" → Score +2 (haute priorité)
- "Virtuel" / "Zoom" → Score +1 (accessible partout)
- "Formation" / "Training" → Score +1 (opportunité d'apprentissage)
- Événements du groupe "Vaudreuil" → Score +2 (votre groupe)

### Variabilité des Résultats
- Le site charge le contenu dynamiquement via AJAX
- Les résultats peuvent varier selon le moment du scan
- La page `/events/` peut afficher "No events" si aucun événement spécial n'est programmé
- Les portes ouvertes apparaissent principalement dans la section "GR Events" > "Open Houses"

### Rapport Amélioré
Le rapport génère maintenant:
- Des explications détaillées pour chaque événement recommandé
- Les raisons spécifiques de participation
- Une section "Actions Recommandées" avec séparation Zoom/Présentiel
- Des indicateurs d'urgence basés sur les dates

### Structure de la Page /evenements/
- URL principale: `https://www.grinternational.ca/evenements/`
- Menu latéral `#event_side_menu` avec catégories (Portes ouvertes, Lancements, Formations, etc.)
- Structure des événements:
  ```html
  <div class="event" id="event_XXXX">
    <div class="day">7</div>  <!-- Jour du mois -->
    <div class="titre">
      Titre de l'événement
      <span class="red">Groupe / Région / Province / Pays</span>
    </div>
    <div class="description">Description courte...</div>
    <div class="plus">[ <a href="...">En savoir plus...</a> ]</div>
  </div>
  ```
- Pagination disponible pour voir plus d'événements

### Extraction Optimisée
1. Naviguer vers `/evenements/`
2. Cliquer sur "Tous les événements" dans le menu latéral
3. Pour chaque `div.event`, extraire:
   - `div.titre` → Titre + Groupe/Région
   - `div.day` → Jour du mois
   - `div.description` → Description courte
   - `a[href*="En savoir plus"]` → Lien vers page détail
4. Visiter chaque page de détail pour date/heure complètes

## Historique des Mises à Jour
- 2026-01-03: Création initiale de la directive
- 2026-01-03: Implémentation Playwright avec authentification token et extraction AJAX
- 2026-01-03: Amélioration du rapport avec détails et recommandations personnalisées
- 2026-01-03: Configuration tâche planifiée Windows (vendredis 7h00)
- 2026-01-03: Refonte extraction - utilise maintenant /evenements/ avec structure div.event, extraction des vrais titres via div.titre
