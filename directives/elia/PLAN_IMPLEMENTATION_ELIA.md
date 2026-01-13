# PLAN D'IMPLÉMENTATION DÉTAILLÉ : PROJET ÉLIA (2026)

> **Date de début :** 19 Janvier 2026
> **Architecture :** Antigravity + Zoho One + Notion
> **Responsable :** Ran.AI Agency (CTO)

---

## 🏗️ PHASE 1 : INFRASTRUCTURE & FRAMEWORKS (Semaine du 19 Jan)
*Objectif : Mettre en place les fondations techniques solides.*

### 1.1 Installation Antigravity
1.  **Initialisation de l'environnement Python :**
    -   Création du venv dédié : `python -m venv venv_elia`
    -   Installation des dépendances : `pip install -r requirements.txt` (incluant `anthropic`, `zoho-api`, `notion-client`).
2.  **Configuration Sécurité :**
    -   Création du fichier `.env` local.
    -   Injection des clés API (Claude Opus 4.5, Zoho Client ID/Secret, Notion Internal Token).

### 1.2 Structure des Dossiers (Workspaces)
Création de la ségrégation stricte pour gérer les deux casquettes de Marie :
```text
directives/elia/
├── common/             # Tâches partagées (Email, Admin, Agenda personnel)
├── sans_soucis/        # Workspace "Services Virtuels" (Clients, Adjointes)
└── gr_international/   # Workspace "Réseautage" (Membres, Événements)
```
*Cette structure permet à ELIA de "changer de casquette" en chargeant le bon dossier contextuel.*

### 1.3 Versionnage GitHub (Historique & Backup)
**Objectif :** Sauvegarder toutes les versions d'ELIA pour traçabilité et rollback.

1.  **Création du Repository :**
    -   Nom suggéré : `elia-sanssoucis` (privé).
    -   Organisation : `ran-ai-agency` ou compte personnel Marie.

2.  **Structure Git :**
    ```text
    elia-sanssoucis/
    ├── directives/         # Tous les fichiers de directive
    ├── execution/          # Scripts Python
    ├── .env.example        # Template des variables (sans secrets)
    ├── README.md           # Documentation d'utilisation
    └── CHANGELOG.md        # Journal des versions
    ```

3.  **Workflow de Versionnage :**
    -   **Commit régulier :** À chaque modification significative des directives ou prompts.
    -   **Tags de version :** `v1.0.0` (Go-Live), `v1.1.0` (Ajout feature), etc.
    -   **Branches :** `main` (stable) et `dev` (développement).

4.  **Backup Automatique (Optionnel) :**
    -   Script n8n ou cron pour push automatique hebdomadaire.

## 🔗 PHASE 2 : CONNECTIVITÉ ZOHO (LES MAINS)
*Objectif : Donner à ELIA la capacité d'agir dans l'écosystème Zoho One.*

### 2.1 Inventaire & Setup des MCPs Zoho
Nous devons configurer chaque connecteur (Model Context Protocol) :

1.  **Zoho Mail MCP :**
    -   Scopes : `ZohoMail.messages.READ`, `ZohoMail.messages.CREATE`, `ZohoMail.messages.UPDATE`.
    -   Test : Lecture des 5 derniers emails non lus.

2.  **Zoho Calendar MCP :**
    -   Scopes : `ZohoCalendar.event.ALL`.
    -   Test : Création d'un événement test le 19 janv.

3.  **Zoho CRM MCP (Double Instance) :**
    -   Configuration des vues personnalisées pour "Sans-Soucis (Prospects)" et "GR (Membres)".

4.  **Zoho Projects MCP :**
    -   Accès aux portails Sans-Soucis pour le suivi des adjointes.

5.  **Zoho Cliq MCP :**
    -   Création du bot "ELIA" pour les notifications temps réel.

---

## 🧠 PHASE 3 : CERVEAU NOTION & BASES DE CONNAISSANCES
*Objectif : Organiser la mémoire et les procédures.*

### 3.1 Architecture Notion
Mise en place de 3 bases de données maîtresses :
1.  **ELIA_MEMORY:** Mémoire long terme (Préférences de Marie, Faits clés).
2.  **ELIA_SOP (Procédures):** Les modes opératoires pour les tâches complexes.
3.  **ELIA_LOGS:** Journal d'activité (Ce qu'elle a fait, quand et pourquoi).

### 3.2 Ingestion Documentaire
Importation des documents existants dans la base vectorielle ou Notion :
-   Procédures actuelles des adjointes.
-   Documents GR International.
-   Liste des 100 Cas d'utilisation (pour référence).

---

## ⚙️ PHASE 4 : DÉVELOPPEMENT & ORCHESTRATION (Semaines du 26 Jan & 2 Fév)
*Objectif : Coder les comportements.*

### 4.1 Développement des Agents
Configuration des fichiers `SYSTEM_PROMPT` pour chaque persona :
-   `AGENT_AV.md` : Focus sur réactivité et organisation.
-   `AGENT_COO.md` : Focus sur gestion de projet et suivi.
-   `AGENT_GR.md` : Focus sur relationnel et networking.

### 4.2 Implémentation des Workflows (Les 100 Cas)
Développement itératif par bloc de priorité :
1.  **Bloc A (Vital):** Gestion Email (Tri) + Agenda (Rappels) + Consultations.
2.  **Bloc B (GR):** Gestion des demandes de rencontre.
3.  **Bloc C (Ops):** Suivi quotidien des adjointes.

---

## 🧪 PHASE 5 : TESTS & FORMATION (Semaine du 9 Fév)
*Objectif : Validation terrain ("Marie in the loop").*

### 5.1 "Crash Test" Supervisé
-   **Session Live :** Marie pose des questions réelles ("Quel est mon planning ?", "Qui m'a écrit ?").
-   **Correction :** Ajustement immédiat des prompts si la réponse est inexacte.

### 5.2 Formation "Double Voie"
-   **Formation Technique :** Comment utiliser l'interface (LibreChat ou Cliq).
-   **Formation Comportementale :** Apprendre à "prompter" ELIA efficacement (Cadre de délégation).

---

## 📅 CALENDRIER DÉTAILLÉ

| Semaine | Phase | Livrables Clés |
| :--- | :--- | :--- |
| **19 Jan** | **Validation & Infra** | Réunion Marie, Setup Antigravity, Connexion Zoho/Notion. |
| **26 Jan** | **Dev Verticale 1 (Common)** | Gestion Emails, Calendrier, Admin général. |
| **02 Fév** | **Dev Verticale 2 (SS + GR)** | Workflows spécifiques (Adjointes + Membres). |
| **09 Fév** | **Tests & Formation** | Sessions Zoom, Ajustements, Documentation utilisateur. |
| **16 Fév** | **GO-LIVE** | ELIA autonome en production. |

---
*Document généré le 12 Janvier 2026 pour le déploiement ELIA.*
