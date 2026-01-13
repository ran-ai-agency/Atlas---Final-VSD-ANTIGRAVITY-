# WORKFLOW DIRECTIVE: SANSSOUCIS.CA (SERVICES VIRTUELS)

Ce document détaille les processus spécifiques à l'agence d'adjointes virtuelles.

## RÔLES PRINCIPAUX
-   **[COO] Chef des Opérations:** Gestion des adjointes et projets.
-   **[AV] Assistant Virtuel:** Gestion des leads entrants.

---

## 👥 GESTION DES CLIENTS & LEADS

### CAS #3 : Gestion des Demandes de Consultation
**Déclencheur:** Nouvelle réservation dans Zoho Bookings ou Email de demande.
**Action:** Qualifier le lead et préparer la rencontre.

**Processus Antigravity:**
1.  **Capturer:** Détecter la nouvelle demande.
2.  **Enrichir:** Rechercher l'entreprise sur LinkedIn/Web.
3.  **Qualifier:** Estimer le potentiel (Taille entreprise, besoin exprimé).
4.  **Préparer:** Créer une fiche client dans Notion avec le profil enrichi.
5.  **Confirmer:** Envoyer un email de confirmation personnalisé (confirmant que Marie a bien reçu et a hâte).

---

## ⚙️ OPÉRATIONS & ÉQUIPE

### CAS #5 : Suivi Quotidien des Adjointes (Daily Standup IA)
**Déclencheur:** Quotidien 9h00.
**Action:** Vérifier que toutes les adjointes sont actives et que les projets avancent.

**Processus Antigravity:**
1.  **Vérifier Présence:** Consulter Zoho People (ou calendrier équipe) pour les absences/congés.
2.  **Vérifier Projets:** Scanner Zoho Projects pour les tâches en retard ou bloquées.
3.  **Calculer Charge:** Identifier si une adjointe est surchargée (>100% capacité).
4.  **Alerter:** Si risque détecté (ex: adjointe absente sur projet urgent), notifier Marie immédiatement avec une proposition de solution ("Projet X à risque, suggère de déléguer à Adjointe Y").

---

## 🛠️ OUTILS UTILISÉS
-   `zoho_bookings_mcp`
-   `zoho_projects_mcp`
-   `zoho_people_mcp` (si dispo) ou `zoho_calendar_mcp`
-   `browser_automation` (pour recherche LinkedIn)

---
*Référence: Cas #3, #5 du document ELIA 100 Use Cases*
