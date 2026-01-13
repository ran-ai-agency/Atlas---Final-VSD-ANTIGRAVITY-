# WORKFLOW DIRECTIVE: TÂCHES COMMUNES & ADMIN

Ce document regroupe les processus standards gérés par ÉLIA pour toutes les verticales (Sans-Soucis et GR).

## RÔLES PRINCIPAUX
- **[AV] Assistant Virtuel**
- **[CEO] Pour la validation stratégique**

---

## 📅 GESTION DU CALENDRIER

### CAS #1 : Rappel de Réunion Intelligent
**Déclencheur:** 30 minutes avant chaque réunion.
**Action:** Envoyer un briefing complet à Marie sur Zoho Cliq.

**Processus Antigravity:**
1.  **Lire l'événement:** Récupérer titre, participants, description depuis Zoho Calendar.
2.  **Enrichir (CRM):** Rechercher les profils des participants dans Zoho CRM.
3.  **Analyser Historique:** Lire les derniers emails (Zoho Mail) et notes (Notion) liés à ces contacts.
4.  **Générer Briefing:**
    -   Contexte: "Qui est-ce ?"
    -   Historique récent: "Dernier échange le..."
    -   Objectif: "But supposé de la réunion"
    -   Documents: Liens vers les fichiers pertinents.
5.  **Notifier:** Envoyer le message formaté sur le canal Cliq privé de Marie.

---

## 📧 GESTION DES EMAILS

### CAS #2 : Tri et Résumé Matinal "Zero Inbox"
**Déclencheur:** Chaque matin à 8h00.
**Action:** Analyser la Inbox et préparer un rapport de priorités.

**Processus Antigravity:**
1.  **Scan:** Lire les emails non lus reçus depuis la veille.
2.  **Classification:**
    -   *Urgent:* Clients VIP, Problèmes bloquants.
    -   *Important:* Opportunités GR, Partenaires.
    -   *Info:* Newsletters, Notifs systèmes.
3.  **Résumé IA:** Pour chaque email Urgent/Important, générer une phrase de synthèse ("Action requise : valider le devis").
4.  **Rapport:** Envoyer un email récapitulatif à Marie ("Ton briefing matinal : 3 urgences, 5 opportunités").

---

## 🛠️ OUTILS UTILISÉS
-   `zoho_calendar_mcp`
-   `zoho_mail_mcp`
-   `zoho_crm_mcp`
-   `zoho_cliq_mcp`

---
*Référence: Cas #1, #2 du document ELIA 100 Use Cases*
