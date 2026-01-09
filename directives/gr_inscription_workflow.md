# Directive: GR International - Workflow d'inscription aux événements

## Objectif
Automatiser le processus complet d'inscription aux événements GR International, de la sélection jusqu'à la confirmation.

## Workflow en 4 étapes

### Étape 1: Sélection des événements
L'utilisateur choisit les événements auxquels il souhaite participer parmi le rapport hebdomadaire.

**Input:** Liste des événements sélectionnés (noms ou URLs)

### Étape 2: Inscription automatique
Pour chaque événement sélectionné:
1. Naviguer vers la page de l'événement
2. Cliquer sur "Je veux participer à cet événement"
3. Remplir le formulaire avec les informations du `.env`
4. Soumettre le formulaire
5. Capturer un screenshot de confirmation

**Script:** `execution/gr_register_event.py`

### Étape 3: Vérification des confirmations email
Après les inscriptions, vérifier la réception des emails de confirmation:
1. Attendre 60 secondes pour laisser le temps aux emails d'arriver
2. Rechercher les emails de "GR International" sur le compte Sympatico
3. Confirmer la réception pour chaque événement inscrit

**Script:** `execution/search_emails.py`
**Compte email:** roland.ranaivo@sympatico.ca (Account ID: 219196000000029010)

### Étape 4: Ajout au calendrier Google
Pour chaque inscription confirmée:
1. Créer l'événement dans Google Calendar
2. Ajouter les détails (lieu, lien Zoom, description)
3. Configurer les rappels (1 jour avant + 30-60 min avant)

**Credentials:** `credentials.json` et `token.json`

## Informations utilisateur (depuis .env)

| Champ | Variable |
|-------|----------|
| Prénom | GR_PRENOM |
| Nom | GR_NOM |
| Email | GR_EMAIL |
| Téléphone | GR_TELEPHONE |
| Compagnie | GR_COMPAGNIE |
| Site Web | GR_SITEWEB |
| Ville | GR_VILLE |
| Membre GR | GR_MEMBRE (true) |

## Script principal

`execution/gr_full_registration.py`

**Usage:**
```bash
# Inscription à un événement par URL
python execution/gr_full_registration.py --url "https://www.grinternational.ca/evenements/..."

# Inscription à plusieurs événements
python execution/gr_full_registration.py --url "URL1" --url "URL2"

# Avec nom d'événement personnalisé
python execution/gr_full_registration.py --event "Nom de l'événement" --url "URL" --date "2026-01-21" --time "08:00"
```

## Cas limites

- **Formulaire déjà soumis:** Vérifier si "déjà inscrit" apparaît
- **Email non reçu après 2 minutes:** Alerter l'utilisateur, suggérer de vérifier spam
- **Erreur de soumission:** Capturer screenshot, réessayer une fois
- **Conflit de calendrier:** Alerter si un événement existe déjà à la même heure

## Intégration avec le scan hebdomadaire

La directive `gr_international_events.md` génère le rapport chaque vendredi.
Quand l'utilisateur sélectionne des événements, cette directive prend le relais.

## Historique
- 2026-01-09: Création de la directive
- 2026-01-09: Workflow testé avec succès (2 événements Élite)
