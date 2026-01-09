# Scripts Zoho Calendar Dépréciés

## Avertissement

**⚠️ IMPORTANT: Ces scripts sont DÉPRÉCIÉS depuis le 8 janvier 2026**

Selon la nouvelle politique de gestion du calendrier ([directives/calendar_policy.md](../directives/calendar_policy.md)):
- **Zoho Calendar** : Lecture seule (consultation uniquement)
- **Google Calendar** : Toutes opérations d'écriture (create, update, delete)

## Scripts concernés

Les scripts suivants effectuent des opérations d'écriture sur Zoho Calendar et **NE DOIVENT PLUS ÊTRE UTILISÉS**:

### 1. Scripts de création d'événements
- `add_ca_election_event.py` - Crée des événements dans Zoho Calendar
- `create_zoho_event.py` - Utilitaire générique de création d'événements

**Alternative**: Utiliser Google Calendar API ou MCP pour créer des événements.

### 2. Scripts de mise à jour d'événements
- `fix_calendar_issues.py` - Met à jour et supprime des événements
- `update_recurring_event.py` - Met à jour des événements récurrents

**Alternative**: Utiliser Google Calendar API ou MCP pour mettre à jour des événements.

### 3. Scripts de suppression d'événements
- `cleanup_zoho_native_duplicates.py` - Supprime des doublons d'événements
- `cleanup_zoho_calendar_duplicates.py` - Supprime des doublons d'événements

**Alternative**: Utiliser Google Calendar API ou MCP pour supprimer des événements.

## Scripts de lecture (toujours valides)

Ces scripts effectuent uniquement de la **lecture** et peuvent continuer à être utilisés:
- `list_zoho_calendar_today.py` - Liste les événements du jour
- `test_zoho_calendar_mcp.py` - Teste la connexion MCP (lecture)
- `sync_zoho_to_google_calendar.py` - Synchronisation unidirectionnelle (lecture Zoho → écriture Google)

## Migration recommandée

Si vous avez besoin de fonctionnalités similaires:

1. **Créer un événement** → Utiliser Google Calendar
2. **Mettre à jour un événement** → Utiliser Google Calendar
3. **Supprimer un événement** → Utiliser Google Calendar
4. **Consulter Zoho Calendar** → Continuer à utiliser Zoho MCP (lecture seule)

## Scripts à créer (si nécessaire)

Pour remplacer les scripts dépréciés, créer de nouveaux scripts utilisant Google Calendar:
- `execution/create_google_event.py` - Créer événements dans Google Calendar
- `execution/update_google_event.py` - Mettre à jour événements dans Google Calendar
- `execution/cleanup_google_calendar_duplicates.py` - Nettoyer doublons Google Calendar

## Raison de la dépréciation

**Date de changement**: 8 janvier 2026

**Contexte**: Consolidation de la gestion du calendrier sur Google Calendar comme système principal d'écriture, Zoho Calendar devenant une source de lecture uniquement pour consultation et synchronisation.

**Réalité technique**: Le serveur MCP Zoho Calendar officiel n'expose que 4 outils en **lecture seule**:
- `fetchEvent` - Récupérer un événement spécifique
- `findTimeSlots` - Trouver des créneaux disponibles
- `getAllCalendar` - Lister tous les calendriers
- `getEventsInRange` - Obtenir les événements dans une plage de dates

**Les outils suivants N'EXISTENT PAS dans le MCP Zoho Calendar:**
- ❌ `addEvent` / `createEvent`
- ❌ `updateEvent`
- ❌ `deleteEvent`

Les scripts dépréciés utilisaient probablement des endpoints API Zoho directs (non-MCP) ou une ancienne version du MCP qui n'est plus maintenue.

**Avantages**:
- Centralisation des opérations d'écriture
- Meilleure intégration avec Google Workspace
- Simplification de la gestion des permissions
- Réduction de la complexité de synchronisation bidirectionnelle

## Action recommandée

**NE PAS SUPPRIMER CES SCRIPTS** - ils peuvent servir de référence pour:
- Comprendre la structure des événements Zoho
- Migrer la logique vers Google Calendar
- Debugging/consultation historique

**Conservation**: Ces scripts sont conservés dans le dépôt mais marqués comme dépréciés.

---

**Dernière mise à jour**: 8 janvier 2026
**Politique de référence**: [directives/calendar_policy.md](../directives/calendar_policy.md)
