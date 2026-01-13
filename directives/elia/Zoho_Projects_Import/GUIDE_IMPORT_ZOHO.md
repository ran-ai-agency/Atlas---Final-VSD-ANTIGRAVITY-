# 📘 GUIDE D'IMPORT ZOHO PROJECTS - ÉLIA

## 📋 Vue d'ensemble

Ce package contient tous les fichiers nécessaires pour importer le projet ÉLIA dans Zoho Projects.

### 📦 Fichiers inclus

1. **elia_tasks_import.csv** - 38 tâches complètes avec dépendances
2. **elia_milestones.csv** - 9 jalons (milestones) par phase
3. **elia_tasklists.csv** - 10 listes de tâches organisées
4. **elia_project_overview.json** - Vue d'ensemble complète du projet
5. **elia_budget_breakdown.csv** - Détail budgétaire complet
6. **GUIDE_IMPORT_ZOHO.md** - Ce guide

---

## 🚀 PROCÉDURE D'IMPORT PAS-À-PAS

### ÉTAPE 1 : Créer le projet dans Zoho Projects

1. Connectez-vous à Zoho Projects : https://projects.zohocloud.ca/
2. Cliquez sur **"+ Nouveau projet"**
3. Configurez le projet :

   **Informations de base :**
   - Nom du projet : `ÉLIA - Développement Équipe de Direction IA`
   - Code projet : `ELIA-SS-2025`
   - Client : `Sans-Soucis AV`
   - Contact client : `Marie Boudreau`
   - Type : `Client externe`

   **Dates :**
   - Date de début : `1er novembre 2025`
   - Date de fin : `7 mars 2026`
   - Durée : `18 semaines`

   **Budget :**
   - Budget total : `9 250 CAD`
   - Type de facturation : `Forfait fixe`

   **Équipe :**
   - Chef de projet : `Roland Ranaivoarison`
   - Membres : Ajoutez les collaborateurs Ran.AI Agency

4. Cliquez sur **"Créer"**

---

### ÉTAPE 2 : Importer les listes de tâches (Task Lists)

1. Dans le projet créé, allez dans **Tâches** → **Listes de tâches**
2. Cliquez sur **"Actions"** → **"Importer"**
3. Sélectionnez le fichier : `elia_tasklists.csv`
4. Mappez les colonnes :
   - Task List Name → Nom
   - Description → Description
   - Phase → Étiquette/Tag personnalisé

5. Cliquez sur **"Importer"**
6. Vérifiez que les 10 listes sont créées :
   - ✅ Préparation
   - ✅ Infrastructure
   - ✅ Agents Spécialisés
   - ✅ Formation & Tests
   - ✅ Support
   - ✅ Control Center
   - ✅ Workflows n8n
   - ✅ Intégrations
   - ✅ Optimisation
   - ✅ Clôture

---

### ÉTAPE 3 : Importer les jalons (Milestones)

1. Allez dans **Tâches** → **Jalons** ou **Milestones**
2. Cliquez sur **"Importer"** ou **"Actions"** → **"Importer"**
3. Sélectionnez le fichier : `elia_milestones.csv`
4. Mappez les colonnes :
   - Milestone Name → Nom du jalon
   - Description → Description
   - Start Date → Date de début
   - End Date → Date de fin
   - Phase → Étiquette/Tag
   - Status → Statut
   - Owner → Propriétaire

5. Cliquez sur **"Importer"**
6. Vérifiez que les 9 jalons sont créés

---

### ÉTAPE 4 : Importer les tâches principales

1. Allez dans **Tâches** → **Toutes les tâches**
2. Cliquez sur **"Actions"** → **"Importer des tâches"**
3. Sélectionnez le fichier : `elia_tasks_import.csv`

4. **Mappez soigneusement les colonnes** :
   - Task Name → Nom de la tâche
   - Description → Description
   - Priority → Priorité
   - Status → Statut
   - Start Date → Date de début
   - End Date → Date de fin
   - Duration (Days) → Durée
   - Milestone → Jalon associé
   - Assigned To → Assigné à
   - Phase → Étiquette personnalisée
   - Dependencies → Dépendances (Task ID)
   - Estimated Hours → Heures estimées
   - Task List → Liste de tâches

5. **⚠️ IMPORTANT - Dépendances** :
   - Les dépendances utilisent les numéros de tâches
   - Première importation : Zoho assignera des IDs automatiques
   - Vous devrez peut-être ajuster manuellement les dépendances après import

6. Cliquez sur **"Importer"**

7. **Post-import** : Vérifiez et ajustez les dépendances :
   - Tâche 2 dépend de Tâche 1
   - Tâche 3 dépend de Tâche 1
   - Tâche 4 dépend de Tâche 3
   - etc. (voir tableau de dépendances ci-dessous)

---

### ÉTAPE 5 : Configuration des dépendances manuelles

Si les dépendances ne s'importent pas correctement, voici le mapping :

| Tâche | Dépend de |
|-------|-----------|
| Configuration environnements | Kick-off meeting client |
| Documentation initiale | Kick-off meeting client |
| Configuration Genspark IA | Documentation initiale |
| Setup AI Drive | Documentation initiale |
| Configuration accès verticales | Configuration Genspark IA, Setup AI Drive |
| Développement Agent GR International | Configuration accès verticales |
| Développement Agent Marketing | Configuration accès verticales |
| Développement Agent Écriture | Configuration accès verticales |
| Développement Agent Contrats | Configuration accès verticales |
| Développement Agent Projet PVA | Configuration accès verticales |
| Développement Agent Création Visuelle | Configuration accès verticales |
| Création liste 100 questions | Tous les 6 agents |
| Tests validation 25 scénarios | Création liste 100 questions |
| Formation initiale client | Tests validation |
| Guide d'utilisation initial | Création liste 100 questions |
| Support 30 jours Phase 1 | Formation initiale client |
| Architecture Control Center Notion | Formation initiale client |
| Intégration Notion ↔ Genspark | Architecture Control Center |
| Dashboards executives | Architecture Control Center |
| Workflow 1: GR International | Intégration Notion ↔ Genspark |
| Workflow 2: Marketing | Intégration Notion ↔ Genspark |
| Workflow 3: Gestion financière | Workflow 1 ET 2 |
| Workflow 4: Projet PVA | Workflow 1 ET 2 |
| Workflow 5: Clients & Support | Workflow 1 ET 2 |
| Workflows complémentaires | Workflow 3, 4 ET 5 |
| Intégration Zoho CRM | Workflows complémentaires |
| Intégration QuickBooks | Workflows complémentaires |
| Intégration Canva | Intégration Zoho CRM ET QuickBooks |
| Optimisation prompts avancés | Intégration Canva |
| Audit inter-phases complet | Optimisation prompts |
| Formation avancée client | Optimisation prompts |
| Documentation avancée | Optimisation prompts |
| Support 60 jours Phase 2 | Formation avancée client |
| Validation finale client | Audit inter-phases, Formation avancée |
| Documentation finale & handover | Validation finale client |
| Mesure ROI & success metrics | Validation finale client |
| Plan évolution & scaling | Validation finale client |

**Pour ajouter une dépendance manuellement :**
1. Ouvrez la tâche
2. Section "Dépendances" ou "Dependencies"
3. Ajoutez la/les tâche(s) prérequise(s)
4. Sauvegardez

---

### ÉTAPE 6 : Configuration des vues personnalisées

#### Vue Gantt (Diagramme de Gantt)

1. Allez dans **Tâches** → **Vue Gantt**
2. Configurez l'affichage :
   - Grouper par : **Jalon (Milestone)**
   - Afficher : **Chemin critique**
   - Zoom : **Semaines**

#### Vue Kanban

1. Allez dans **Tâches** → **Vue Kanban**
2. Configurez les colonnes :
   - Open (À faire)
   - In Progress (En cours)
   - Testing (Tests)
   - Completed (Terminé)

3. Groupez par : **Phase** ou **Liste de tâches**

#### Dashboard personnalisé

1. Créez un nouveau dashboard : **"ÉLIA Control Dashboard"**
2. Ajoutez les widgets :
   - **Progression des tâches** (% complétion)
   - **Jalons à venir**
   - **Tâches critiques**
   - **Heures consommées vs estimées**
   - **Budget dépensé vs alloué**
   - **Charge de travail par membre**

---

### ÉTAPE 7 : Configuration des champs personnalisés

Créez ces champs personnalisés pour mieux tracker ÉLIA :

1. **Phase du projet** (Liste déroulante)
   - Phase 0: Préparation
   - Phase 1: Fondation & Setup
   - Phase 2: Optimisation & Autonomie
   - Phase 3: Déploiement & Clôture

2. **Type de livrable** (Liste déroulante)
   - Agent IA
   - Workflow n8n
   - Intégration
   - Formation
   - Documentation
   - Support

3. **Verticale concernée** (Case à cocher multiple)
   - GR International
   - Marketing
   - Livres
   - Projet PVA
   - Clients
   - Création visuelle

4. **Statut validation client** (Liste déroulante)
   - En attente
   - Validé
   - Révisions demandées
   - Approuvé final

---

### ÉTAPE 8 : Configuration des rappels et notifications

1. Allez dans **Paramètres** → **Notifications**
2. Activez :
   - ✅ Rappels tâches dues dans 24h
   - ✅ Notifications tâches critiques
   - ✅ Alertes dépassement jalons
   - ✅ Notifications budget (alerte à 80%)

3. Configurez les emails récapitulatifs :
   - Quotidien pour Roland (chef de projet)
   - Hebdomadaire pour l'équipe
   - Résumé jalon pour le client

---

### ÉTAPE 9 : Import du budget

1. Allez dans **Finance** → **Budget**
2. Configurez le budget du projet : **9 250 CAD**
3. Importez les détails avec `elia_budget_breakdown.csv` ou saisissez manuellement :

   **Phase 0 :** 1 500 CAD
   **Phase 1 :** 4 800 CAD (agents) + 1 000 CAD (formation) = 5 800 CAD
   **Phase 2 :** 600 CAD + 1 500 CAD + 300 CAD = 2 400 CAD
   **Support :** 3 000 CAD (réparti sur Phases 1 & 2)
   **Abonnements :** 480 CAD (4 mois)

---

### ÉTAPE 10 : Configuration du suivi du temps

1. Activez le **suivi du temps** dans les paramètres du projet
2. Configurez les catégories :
   - Développement
   - Configuration
   - Tests
   - Formation
   - Support
   - Réunions client

3. Définissez les taux horaires :
   - Consultation : 150 CAD/h
   - Développement : 125 CAD/h
   - Formation : 100 CAD/h
   - Support : 50 CAD/h

---

## 📊 VALIDATION POST-IMPORT

### Checklist de validation

- [ ] 38 tâches importées correctement
- [ ] 9 jalons créés et datés
- [ ] 10 listes de tâches organisées
- [ ] Dépendances entre tâches configurées
- [ ] Dates cohérentes (1er nov 2025 → 7 mars 2026)
- [ ] Assignations à Roland Ranaivoarison
- [ ] Heures estimées totales : ~370 heures
- [ ] Budget : 9 250 CAD configuré
- [ ] Champs personnalisés créés
- [ ] Notifications activées
- [ ] Vue Gantt affiche chemin critique
- [ ] Dashboard personnalisé créé

### KPIs à monitorer

Configurez le tracking de ces métriques clés :

| KPI | Cible | Mesure |
|-----|-------|--------|
| Temps hebdomadaire libéré | 40.5h/sem | Manuel (client feedback) |
| ROI 6 mois | 218% | Calculé post-déploiement |
| Agents opérationnels | 6 | Count agents déployés |
| Workflows actifs | 10+ | Count workflows n8n |
| Tests validés | 100 | % completion tests |
| Satisfaction client | 9/10 | Survey mensuel |
| Budget respecté | ±5% | Zoho tracking auto |

---

## 🔄 WORKFLOW PROJET RECOMMANDÉ

### Réunions récurrentes à créer

1. **Daily Standup (Phase active)**
   - Fréquence : Quotidien 15 min
   - Participants : Équipe Ran.AI
   - Objectif : Blocages, progrès

2. **Weekly Client Check-in**
   - Fréquence : Hebdomadaire 30 min
   - Participants : Roland + Marie Boudreau
   - Objectif : Revue progrès, validation

3. **Sprint Review (fin de chaque Milestone)**
   - Fréquence : Toutes les 1-2 semaines
   - Participants : Équipe + Client
   - Objectif : Démo, validation livrables

4. **Retrospective Phase**
   - Fréquence : Fin Phase 1 et Phase 2
   - Participants : Équipe Ran.AI
   - Objectif : Leçons apprises, optimisation

### Process de gestion des changements

Si besoin d'ajouter/modifier des tâches :

1. Documenter le changement demandé
2. Évaluer impact (temps, budget, scope)
3. Obtenir approbation client si hors scope
4. Mettre à jour Zoho Projects
5. Communiquer à l'équipe

---

## 🆘 TROUBLESHOOTING

### Problème : Les dépendances ne s'importent pas

**Solution :**
- Import Zoho peut avoir des limites sur les dépendances
- Ajoutez-les manuellement en suivant le tableau ÉTAPE 5
- Ou utilisez la vue Gantt en mode édition pour tracer les liens

### Problème : Dates décalées

**Solution :**
- Vérifiez le fuseau horaire du projet (doit être EST)
- Utilisez la fonction "Replanifier le projet" dans Paramètres
- Ajustez manuellement les dates si nécessaire

### Problème : Heures estimées non importées

**Solution :**
- Zoho peut nécessiter activation du module Time Tracking
- Allez dans Paramètres → Modules → Activer "Suivi du temps"
- Ré-importez les tâches ou saisissez manuellement

### Problème : Assignations échouent

**Solution :**
- Assurez-vous que les membres existent dans le portail
- Vérifiez l'orthographe exacte des noms
- Assignez manuellement après import

---

## 📞 SUPPORT

**Contact Ran.AI Agency :**
- Email : info@ran-ai-agency.ca
- Site : ran-ai-agency.ca
- LinkedIn : linkedin.com/in/roland-ranaivoarison-23243022

**Ressources Zoho :**
- Documentation : https://help.zoho.com/portal/en/kb/projects
- Support : https://help.zoho.com/portal/en/newticket

---

## 🎯 PROCHAINES ÉTAPES APRÈS IMPORT

1. ✅ **Valider l'import complet**
2. 📅 **Planifier kick-off meeting** avec Marie Boudreau
3. 📧 **Envoyer invitation projet** aux membres équipe
4. 📊 **Configurer rapports automatiques** hebdomadaires
5. 🔔 **Activer notifications** pour toute l'équipe
6. 📝 **Créer template de rapport** de progrès client
7. 🎥 **Enregistrer vidéo démo** Zoho Projects pour le client

---

## 📚 DOCUMENTS COMPLÉMENTAIRES

Dans ce package, consultez aussi :

- `elia_project_overview.json` - Vue technique complète
- `elia_budget_breakdown.csv` - Détail financier
- `ÉLIA_presentation_marie_boudreau_final.pdf` - Proposition client originale (AI Drive)

---

**Version du guide :** 1.0
**Dernière mise à jour :** 29 octobre 2025
**Créé par :** ATLAS 4.1 Ultra - Ran.AI Agency

---

✅ **Vous êtes maintenant prêt à importer ÉLIA dans Zoho Projects !**

*Bonne configuration et excellent déploiement !*

🚀 **Ran.AI Agency - Accélérons votre croissance avec l'IA agentique**
