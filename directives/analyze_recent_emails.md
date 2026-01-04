# Directive: Analyse des courriels récents

## Objectif
Analyser les courriels récents de l'utilisateur pour identifier les tendances, les priorités et les actions requises.

## Inputs
- account_id: ID du compte Zoho Mail (optionnel, utilise le compte principal par défaut)
- days: Nombre de jours à analyser (défaut: 7)
- limit: Nombre maximum d'emails à analyser par dossier (défaut: 100)

## Scripts/Outils
- `execution/analyze_recent_emails.py` - Script principal d'analyse des emails

## Outputs
- Rapport d'analyse avec:
  - Statistiques générales (nombre d'emails, expéditeurs principaux)
  - Classification par priorité/urgence
  - Résumé des sujets importants
  - Actions recommandées

## Etapes
1. Se connecter à Zoho Mail via l'API
2. Lister les dossiers principaux (Inbox, Sent, etc.)
3. Récupérer les emails récents de chaque dossier
4. Analyser le contenu et les métadonnées
5. Classifier par importance et urgence
6. Générer un rapport structuré

## Cas limites
- Pas d'accès au compte mail: Vérifier la configuration OAuth
- Aucun email récent: Retourner un message informatif
- Erreur API: Retry avec backoff, puis fallback vers résumé partiel

## Notes
- Utilise l'API Zoho Mail pour éviter les limitations IMAP
- Analyse basée sur sujet, expéditeur, et contenu du corps
- Classification heuristique basée sur mots-clés et patterns
- Support pour les emails en français et anglais