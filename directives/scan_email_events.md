# Directive: Scanner d'événements dans les emails

## Objectif
Détecter automatiquement les événements (webinars, conférences, workshops, meetups, etc.) dans les emails et envoyer des alertes.

## Inputs
- `limit`: Nombre d'emails à scanner (défaut: 200)
- `send_alert`: Envoyer une notification Cliq (défaut: false)

## Scripts/Outils
- `execution/scan_email_events.py` - Script principal de scan

## Outputs
- `.tmp/email_events.json` - Liste des événements détectés en JSON
- Notification Cliq (si activée) avec le résumé des événements

## Types d'événements détectés
- **Webinar**: webinar, webinaire, online event, virtual event, live session, info session
- **Conference**: conference, conférence, summit, sommet, forum
- **Workshop**: workshop, atelier, formation, training, masterclass
- **Meetup**: meetup, networking, réseautage, afterwork, rencontre
- **Demo**: demo, démonstration, product launch, lancement

## Étapes
1. Se connecter à Zoho Mail via MCP
2. Récupérer les emails récents
3. Analyser chaque email pour détecter des mots-clés d'événements
4. Extraire les dates et heures mentionnées
5. Calculer un score de pertinence (1-10)
6. Sauvegarder les résultats en JSON
7. (Optionnel) Envoyer une alerte Cliq

## Exécution manuelle
```bash
cd "c:\Users\ranai\Documents\Atlas - Final (VSD AntiGravity)"
python execution/scan_email_events.py
```

## Exécution avec alerte Cliq
```bash
SEND_CLIQ_ALERT=true python execution/scan_email_events.py
```

## Configuration MCP requise
Variables d'environnement dans `.env`:
- `MCP_ZOHO_MAIL_URL` - URL du MCP Zoho Mail
- `MCP_ZOHO_MAIL_KEY` - Clé API du MCP
- `MCP_ZOHO_CLIQ_URL` - URL du MCP Zoho Cliq (pour alertes)
- `MCP_ZOHO_CLIQ_KEY` - Clé API Cliq

## Politique de gestion du calendrier
**IMPORTANT**: Pour créer, modifier ou supprimer des événements calendrier, utiliser **Google Calendar**.
- Zoho Calendar : **Lecture seule** (consultation uniquement)
- Google Calendar : Toutes opérations d'écriture

Voir [directives/calendar_policy.md](calendar_policy.md) pour plus de détails.

## Automatisation
Pour des alertes automatiques, configurer un webhook Modal ou une tâche planifiée Windows:

### Option 1: Tâche planifiée Windows (quotidienne)
```powershell
schtasks /create /tn "Email Events Scanner" /tr "python c:\Users\ranai\Documents\Atlas - Final (VSD AntiGravity)\execution\scan_email_events.py" /sc daily /st 08:00 /f
```

### Option 2: Webhook Modal
Voir `directives/add_webhook.md` pour configurer un endpoint automatisé.

## Score de pertinence
- Base: 5 points
- +2 si mot-clé événement dans le sujet
- +1 si date détectée
- +1 si source connue (Eventbrite, Zoom, Microsoft, etc.)

## Cas limites
- Emails avec encodage spécial: caractères nettoyés automatiquement
- Erreur MCP: retry puis abandon avec message d'erreur
- Pas d'événements: message informatif retourné

## Notes
- Utilise le MCP Zoho Mail avec clé en query parameter
- Account ID hardcodé: 219196000000002002
- Détection basée sur mots-clés et patterns regex
