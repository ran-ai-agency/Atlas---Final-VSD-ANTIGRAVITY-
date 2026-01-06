# Directive: Analyse des courriels récents

## Objectif
Analyser les courriels récents de l'utilisateur pour identifier les tendances, les priorités et les actions requises.

## Inputs
- days: Nombre de jours à analyser (défaut: 7)
- limit: Nombre maximum d'emails à analyser par dossier (défaut: 100)

## Outils
- **Zoho Mail MCP** - Accès aux emails via MCP Server

## Configuration MCP
Variables dans `.env`:
- `MCP_ZOHO_MAIL_URL` - URL du MCP Zoho Mail
- `MCP_ZOHO_MAIL_KEY` - Clé API du MCP

## Outputs
- Rapport d'analyse avec:
  - Statistiques générales (nombre d'emails, expéditeurs principaux)
  - Classification par priorité/urgence
  - Résumé des sujets importants
  - Actions recommandées

## Étapes
1. Appeler Zoho Mail MCP pour lister les dossiers
2. Récupérer les emails récents de chaque dossier via MCP
3. Analyser le contenu et les métadonnées
4. Classifier par importance et urgence
5. Générer un rapport structuré

## Cas limites
- Pas d'accès au compte mail: Vérifier la configuration MCP dans `.env`
- Aucun email récent: Retourner un message informatif
- Erreur MCP: Retry puis message d'erreur

## Notes
- Utilise le MCP Zoho Mail (jamais l'API directe)
- Analyse basée sur sujet, expéditeur, et contenu du corps
- Classification heuristique basée sur mots-clés et patterns
- Support pour les emails en français et anglais