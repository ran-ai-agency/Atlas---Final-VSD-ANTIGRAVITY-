# Directive: GR International - Inscription aux Evenements

## Objectif
Automatiser l'inscription aux evenements GR International en remplissant et soumettant le formulaire "Je veux participer a cet evenement".

## Contexte Utilisateur
- **Nom**: Roland Ranaivoarison
- **Entreprise**: Ran.AI Agency
- **Courriel**: roland.ranaivo@sympatico.ca
- **Telephone**: 514-918-1241
- **Ville**: Vaudreuil-Dorion
- **Site Web**: https://www.ran-ai-agency.ca/
- **Membre GR**: Oui
- **Refere par**: GR

## Inputs
- **URL de l'evenement**: URL de la page de detail de l'evenement (depuis le rapport hebdomadaire)
- **Mode**: `dry_run` (test sans soumission) ou `submit` (soumission reelle)
- **Profil**: Charge automatiquement depuis `.env`

## Script d'Execution
- `execution/gr_event_register.py` - Automatisation de l'inscription avec Playwright

## Workflow d'Inscription

### Etape 1: Preparation
1. Charger le profil depuis les variables d'environnement
2. Valider que tous les champs obligatoires sont remplis
3. Demarrer le navigateur Playwright

### Etape 2: Authentification
1. Naviguer vers le portail membres via `GR_MEMBER_URL`
2. Verifier que la session est active

### Etape 3: Navigation vers l'evenement
1. Ouvrir l'URL de l'evenement
2. Extraire le nom de l'evenement pour confirmation

### Etape 4: Ouverture du formulaire
1. Localiser le bouton "Je veux participer a cet evenement"
2. Cliquer pour ouvrir le formulaire d'inscription
3. Prendre une capture d'ecran du formulaire vide

### Etape 5: Remplissage du formulaire
Champs a remplir automatiquement:

| Champ | Selecteur | Valeur |
|-------|-----------|--------|
| Prenom | `input[name="Prenom"]` | `GR_PRENOM` |
| Nom | `input[name="Nom"]` | `GR_NOM` |
| Compagnie | `input[name="Compagnie"]` | `GR_COMPAGNIE` |
| Courriel | `input[name="Courriel"]` | `GR_EMAIL` |
| Telephone | `input[name="Telephone"]` | `GR_TELEPHONE` |
| Ville | `input[name="Ville"]` | `GR_VILLE` |
| Site Web | `input[name="SiteWeb"]` | `GR_SITEWEB` |

### Etape 6: Soumission (si mode submit)
1. Localiser le bouton de soumission (Envoyer/Soumettre/Confirmer)
2. Cliquer pour soumettre
3. Attendre la confirmation
4. Prendre une capture d'ecran du resultat

## Modes d'Execution

### Mode Dry Run (Test)
```bash
python execution/gr_event_register.py "URL_EVENEMENT"
```
- Remplit le formulaire sans soumettre
- Prend des captures d'ecran pour verification
- Affiche un resume des donnees remplies

### Mode Submit (Reel)
```bash
python execution/gr_event_register.py "URL_EVENEMENT" --submit
```
- Remplit ET soumet le formulaire
- Envoie reellement l'inscription
- Prend une capture d'ecran de confirmation

### Mode Visible (Debug)
```bash
python execution/gr_event_register.py "URL_EVENEMENT" --visible
```
- Affiche le navigateur pour voir les actions en temps reel

## Outputs

### Fichiers generes
- `.tmp/registration_form.png` - Capture du formulaire vide
- `.tmp/registration_filled.png` - Capture du formulaire rempli
- `.tmp/registration_result.png` - Capture de confirmation (si soumis)

### Resultat retourne
```json
{
  "success": true,
  "event_url": "https://...",
  "event_name": "Nom de l'evenement",
  "message": "Inscription reussie!",
  "dry_run": false
}
```

## Cas Limites

### Formulaire non trouve
- Message: "Bouton 'Je veux participer' non trouve"
- Action: Verifier si l'evenement est complet ou si l'URL est correcte

### Champs manquants
- Message: "Profil incomplet"
- Action: Verifier les variables GR_* dans .env

### Evenement complet
- Detecter le message "Evenement complet" ou "Places limitees"
- Suggerer liste d'attente si disponible

### Session expiree
- Re-authentifier automatiquement via GR_MEMBER_URL
- Reessayer l'inscription

## Integration avec le Rapport Hebdomadaire

### Workflow recommande
1. Executer `gr_international_scraper.py` pour generer le rapport
2. Consulter les evenements recommandes dans `.tmp/gr_events_report_*.md`
3. Selectionner les evenements souhaites
4. Pour chaque evenement:
   - Executer en mode dry_run pour verification
   - Si OK, executer en mode submit pour inscription reelle

### Inscription multiple
```python
from gr_event_register import GREventRegistration

urls = [
    "https://www.grinternational.ca/evenements/...",
    "https://www.grinternational.ca/evenements/...",
]

registration = GREventRegistration(headless=True)
results = registration.register_multiple(urls, dry_run=False)
```

## Variables d'Environnement Requises

```env
# Authentification
GR_MEMBER_URL=https://www.grinternational.ca/membres/index.php?c=...

# Profil d'inscription
GR_PRENOM=Roland
GR_NOM=Ranaivoarison
GR_COMPAGNIE=Ran.AI Agency
GR_EMAIL=roland.ranaivo@sympatico.ca
GR_TELEPHONE=514-918-1241
GR_VILLE=Vaudreuil-Dorion
GR_SITEWEB=https://www.ran-ai-agency.ca/
GR_REFERE_PAR=GR
GR_MEMBRE=true
```

## Securite et Bonnes Pratiques

1. **Toujours tester en dry_run d'abord** avant de soumettre reellement
2. **Verifier les captures d'ecran** pour s'assurer que les bons champs sont remplis
3. **Ne pas s'inscrire en double** - verifier si deja inscrit
4. **Respecter les delais** - attendre entre les inscriptions multiples

## Historique des Mises a Jour
- 2026-01-03: Creation initiale de la directive
- 2026-01-03: Implementation du script gr_event_register.py
- 2026-01-03: Profil utilisateur configure dans .env
