# Knowledge Items Recommandés pour Atlas

> Ce document liste les Knowledge Items à ajouter dans le panneau "Knowledge" d'AntiGravity
> pour optimiser les performances de l'agent Atlas.

---

## 🎯 Comment ajouter un Knowledge Item

1. Ouvrir **Agent Manager** (Ctrl+E ou Cmd+E)
2. Cliquer sur **"Knowledge"** dans le menu gauche
3. Cliquer sur **"+ Add"** ou **"New Knowledge Item"**
4. Copier le contenu de chaque section ci-dessous

---

## Knowledge Item 1: Architecture DOE

**Titre:** `Architecture DOE Atlas`
**Tags:** `architecture`, `core`, `doe`

```markdown
# Architecture DOE (Directive-Orchestration-Execution)

Atlas utilise une architecture 3 couches pour maximiser la fiabilité:

## Layer 1: Directive (What to do)
- SOPs en Markdown dans `directives/`
- Définit: goals, inputs, tools/scripts, outputs, edge cases
- Instructions en langage naturel

## Layer 2: Orchestration (Decision making)
- C'est l'agent AI (moi)
- Lire les directives, appeler les scripts, gérer les erreurs
- Route intelligemment entre les outils

## Layer 3: Execution (Doing the work)  
- Scripts Python déterministes dans `execution/`
- Variables d'environnement dans `.env`
- API calls, data processing, file operations

## Pourquoi ça marche
90% précision par étape = 59% succès sur 5 étapes
Solution: pousser la complexité dans du code déterministe
```

---

## Knowledge Item 2: Rôles Atlas

**Titre:** `Rôles et Responsabilités Atlas`
**Tags:** `roles`, `identity`, `responses`

```markdown
# Rôles Atlas - Ran.AI Agency

Chaque réponse doit être préfixée par le rôle approprié:

| Rôle | Préfixe | Contexte |
|------|---------|----------|
| CEO | [CEO] | Stratégie, vision, décisions, agenda, priorités |
| CFO | [CFO] | Finance, facturation, Zoho Books, trésorerie |
| CMO | [CMO] | Marketing, réseaux sociaux, branding |
| CTO | [CTO] | Technologie, développement, code |
| COO | [COO] | Opérations, processus, automatisation |
| EA | [EA] | Assistant exécutif, emails, calendrier |

## Format de réponse
Toujours commencer par: `[RÔLE] Contenu de la réponse...`

Exemple: `[EA] Voici votre agenda pour aujourd'hui...`
```

---

## Knowledge Item 3: Intégrations MCP

**Titre:** `Intégrations MCP Zoho One & Notion`
**Tags:** `integrations`, `mcp`, `zoho`, `notion`

```markdown
# Intégrations MCP Atlas

## Zoho One (Suite Complete)
Endpoints MCP Hosted sur zohomcp.ca:

| Application | Usage |
|-------------|-------|
| Zoho CRM | Contacts, leads, pipeline |
| Zoho Books | Facturation, comptabilité |
| Zoho Cliq | Messagerie équipe |
| Zoho Calendar | Événements, RDV |
| Zoho Mail | Emails professionnels |
| Zoho WorkDrive | Fichiers, documents |

## Notion
- Endpoint: mcp.notion.com
- Usage: Documentation, Knowledge Base, SOPs

## Priorité des sources
1. Zoho CRM → contacts, leads
2. Zoho Books → facturation
3. Zoho Calendar → planification
4. Notion → documentation, contexte
5. WorkDrive → fichiers partagés
```

---

## Knowledge Item 4: Organisation des fichiers

**Titre:** `Structure Répertoire Atlas`
**Tags:** `files`, `structure`, `organization`

```markdown
# Structure du Projet Atlas

## Répertoires principaux
- `.tmp/` - Fichiers intermédiaires (jamais commit)
- `execution/` - Scripts Python (outils déterministes)
- `directives/` - SOPs en Markdown (instructions)
- `.env` - Variables d'environnement et API keys
- `apps/` - Applications web développées
- `ui/` - Interfaces utilisateur

## Fichiers critiques
- `GEMINI.md` / `CLAUDE.md` - Instructions agent
- `credentials.json` - OAuth Google
- `token.json` - Tokens d'authentification

## Principe clé
Fichiers locaux = processing uniquement
Livrables = services cloud (Google Sheets, Slides, etc.)
```

---

## Knowledge Item 5: Projet ELIA

**Titre:** `Projet ELIA - Marie Boudreau`
**Tags:** `elia`, `client`, `projet`

```markdown
# Projet ELIA

## Client
Marie Boudreau - Sans Souci / GR International

## Objectif
Implémenter Atlas comme équipe de direction IA pour:
- Automatisation des processus
- Gestion des réservations
- Communication clients
- Suivi financier

## Infrastructure
- Orchestrateur: AntiGravity (Atlas)
- CRM/Finance: Zoho One
- Knowledge Base: Notion

## Fichiers clés
- `directives/elia/` - Toutes les directives ELIA
- `directives/projet_elia_marie_boudreau.md` - Brief projet
- `directives/proposition_elia_v2.md` - Proposition commerciale

## Timeline
Démarrage prévu: après réunion du 19 janvier 2026
```

---

## Knowledge Item 6: Self-Annealing

**Titre:** `Processus Self-Annealing`
**Tags:** `errors`, `learning`, `improvement`

```markdown
# Self-Annealing Loop

Quand quelque chose casse:

1. **Fix it** - Corriger l'erreur
2. **Update the tool** - Améliorer le script
3. **Test tool** - S'assurer que ça marche
4. **Update directive** - Documenter le nouveau flow
5. **System is now stronger** - Le système s'améliore

## Principes
- Lire le message d'erreur et stack trace
- Vérifier avec l'utilisateur avant de dépenser des tokens/crédits
- Les erreurs sont des opportunités d'apprentissage

## Mise à jour des directives
Les directives sont des documents vivants.
Quand on découvre:
- Contraintes API
- Meilleures approches  
- Erreurs communes
- Attentes de timing

→ TOUJOURS mettre à jour la directive
```

---

## 📋 Checklist d'ajout

- [ ] Knowledge Item 1: Architecture DOE
- [ ] Knowledge Item 2: Rôles Atlas
- [ ] Knowledge Item 3: Intégrations MCP
- [ ] Knowledge Item 4: Structure Répertoire
- [ ] Knowledge Item 5: Projet ELIA
- [ ] Knowledge Item 6: Self-Annealing

---

> **Note:** Ces Knowledge Items permettront à l'agent de mieux comprendre le contexte
> du projet Atlas sans avoir à re-expliquer l'architecture à chaque session.
