# Application Diagnostic CDAEIA - Spécifications

## Vue d'Ensemble

**Nom:** CDAEIA Diagnostic Tool
**Type:** Application web (SaaS)
**Objectif:** Automatiser et accélérer le diagnostic d'éligibilité CDAEIA pour les PME tech québécoises

---

## Proposition de Valeur

| Avant (Manuel) | Après (Application) |
|----------------|---------------------|
| 2-4 semaines par diagnostic | 1-3 jours |
| Processus inconsistant | Standardisé et reproductible |
| Dépend de l'expertise individuelle | Intelligence embarquée |
| Rapports manuels | Génération automatique |
| Difficile à scaler | Scalable à l'infini |

---

## Fonctionnalités Principales

### Module 1: Évaluation d'Éligibilité

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUESTIONNAIRE INTELLIGENT                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Section 1: Profil Entreprise                                   │
│  ├── Informations générales                                     │
│  ├── Structure organisationnelle                                │
│  └── Données financières                                        │
│                                                                  │
│  Section 2: Tests de Revenus                                    │
│  ├── Test 75% revenus IT                                        │
│  └── Test 50% sous-secteurs                                     │
│                                                                  │
│  Section 3: Effectifs                                           │
│  ├── Nombre d'employés tech                                     │
│  ├── Postes et responsabilités                                  │
│  └── Allocation du temps par activité                           │
│                                                                  │
│  Section 4: Intégration IA                                      │
│  ├── Technologies IA utilisées                                  │
│  ├── Projets/Produits avec IA                                   │
│  └── Niveau de maturité IA                                      │
│                                                                  │
│  Section 5: Documentation                                       │
│  ├── Systèmes de suivi existants                               │
│  └── Documentation technique disponible                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SCORE D'ÉLIGIBILITÉ                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│            ████████████████░░░░░░░░  72/100                     │
│                                                                  │
│  ✓ Test 75% revenus IT        20/20                             │
│  ✓ Test 50% sous-secteurs     18/20                             │
│  ⚠ Effectifs éligibles        12/15  (5 sur 6 requis)          │
│  ⚠ Allocation temps 75%       15/25  (moyenne 68%)             │
│  ✗ Intégration IA             7/20   (superficielle)           │
│                                                                  │
│  STATUT: PARTIELLEMENT ÉLIGIBLE                                 │
│  CRÉDIT POTENTIEL: 85 000$ → 145 000$ (après optimisation)     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Module 2: Plan de Restructuration

```
┌─────────────────────────────────────────────────────────────────┐
│              RECOMMANDATIONS PERSONNALISÉES                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PRIORITÉ HAUTE (Impact immédiat)                               │
│  ─────────────────────────────────                              │
│  1. Recruter 1 employé tech supplémentaire                      │
│     Impact: +15 points │ Effort: Moyen │ Délai: 4-8 semaines   │
│                                                                  │
│  2. Intégrer ML dans le module de recommandations               │
│     Impact: +10 points │ Effort: Élevé │ Délai: 8-12 semaines  │
│                                                                  │
│  PRIORITÉ MOYENNE (Optimisation)                                │
│  ─────────────────────────────────                              │
│  3. Réaffecter Jean Dupont de maintenance vers dev IA           │
│     Impact: +5 points │ Effort: Faible │ Délai: 2 semaines     │
│                                                                  │
│  4. Documenter les modèles IA existants                         │
│     Impact: +3 points │ Effort: Faible │ Délai: 1 semaine      │
│                                                                  │
│  CALENDRIER SUGGÉRÉ                                             │
│  ─────────────────────────────────                              │
│  [Timeline visuel Gantt simplifié]                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Module 3: Génération de Documentation

```
┌─────────────────────────────────────────────────────────────────┐
│              GÉNÉRATEUR DE DOCUMENTS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Documents générés automatiquement:                             │
│                                                                  │
│  📄 Rapport de Diagnostic CDAEIA                    [Télécharger]│
│     └── 30-50 pages, personnalisé                               │
│                                                                  │
│  📄 Sommaire Exécutif (pour dirigeants)            [Télécharger]│
│     └── 2 pages, visuels                                        │
│                                                                  │
│  📄 Fiche Technique IA (pour IQ)                   [Télécharger]│
│     └── Documentation des composantes IA                        │
│                                                                  │
│  📄 Template Suivi du Temps                        [Télécharger]│
│     └── Excel/Sheets pré-configuré                              │
│                                                                  │
│  📄 Checklist Préparation Audit                    [Télécharger]│
│     └── Liste des documents à préparer                          │
│                                                                  │
│  📄 Plan d'Action (avec jalons)                    [Télécharger]│
│     └── Export vers Notion/Asana/Trello                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Module 4: Calculateur de Crédit

```
┌─────────────────────────────────────────────────────────────────┐
│              CALCULATEUR CDAEIA                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SITUATION ACTUELLE                                             │
│  ─────────────────────────────────                              │
│  Employés éligibles:           8                                │
│  Masse salariale brute:        640 000$                         │
│  Seuil d'exclusion:           -148 568$                         │
│  Masse salariale nette:        491 432$                         │
│                                                                  │
│  Crédit 2026 (30%):           147 430$                          │
│    ├── Remboursable (22%):    108 115$                          │
│    └── Non-remboursable (8%):  39 315$                          │
│                                                                  │
│  APRÈS OPTIMISATION                                             │
│  ─────────────────────────────────                              │
│  Employés éligibles:           10 (+2)                          │
│  Masse salariale brute:        800 000$                         │
│  Seuil d'exclusion:           -185 710$                         │
│  Masse salariale nette:        614 290$                         │
│                                                                  │
│  Crédit 2026 (30%):           184 287$  (+36 857$)             │
│                                                                  │
│  [Simuler d'autres scénarios]                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Architecture Technique

### Stack Technologique Recommandé

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
├─────────────────────────────────────────────────────────────────┤
│  Next.js 14+ (App Router)                                       │
│  ├── React 18+ avec TypeScript                                  │
│  ├── Tailwind CSS + shadcn/ui                                   │
│  ├── React Hook Form (formulaires)                              │
│  └── Recharts (visualisations)                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                  │
├─────────────────────────────────────────────────────────────────┤
│  Option A: Next.js API Routes (simple)                          │
│  Option B: FastAPI Python (si logique complexe)                 │
│                                                                  │
│  Services:                                                       │
│  ├── Scoring Engine (calcul d'éligibilité)                     │
│  ├── Recommendation Engine (suggestions)                        │
│  ├── Report Generator (PDF/DOCX)                               │
│  └── Calculator Service (crédits)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE                                  │
├─────────────────────────────────────────────────────────────────┤
│  Supabase (PostgreSQL + Auth + Storage)                         │
│  ├── Companies (profils entreprises)                           │
│  ├── Assessments (diagnostics)                                  │
│  ├── Employees (employés analysés)                             │
│  ├── Projects (projets IA)                                      │
│  ├── Recommendations (suggestions générées)                     │
│  └── Documents (rapports générés)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       SERVICES TIERS                            │
├─────────────────────────────────────────────────────────────────┤
│  ├── Claude API (analyse IA des descriptions de projets)       │
│  ├── PDF Generation (react-pdf ou Puppeteer)                   │
│  ├── Stripe (paiements si SaaS)                                │
│  └── SendGrid/Resend (emails)                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Alternative: MVP Rapide (No-Code/Low-Code)

```
┌─────────────────────────────────────────────────────────────────┐
│                     MVP EN 2-4 SEMAINES                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Typeform/Tally    →  Questionnaire intelligent                 │
│       │                                                         │
│       ▼                                                         │
│  Airtable          →  Base de données                          │
│       │                                                         │
│       ▼                                                         │
│  Make/n8n          →  Automatisation + Calculs                 │
│       │                                                         │
│       ▼                                                         │
│  Google Docs API   →  Génération de rapports                   │
│       │                                                         │
│       ▼                                                         │
│  Notion/Coda       →  Dashboard client                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Modèle de Données

### Entités Principales

```sql
-- Entreprises clientes
CREATE TABLE companies (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    neq VARCHAR(20),
    address TEXT,
    fiscal_year_end DATE,
    industry VARCHAR(100),
    total_employees INT,
    tech_employees INT,
    total_revenue DECIMAL(15,2),
    it_revenue DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Diagnostics/Évaluations
CREATE TABLE assessments (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    status ENUM('draft', 'in_progress', 'completed', 'archived'),
    fiscal_year INT,

    -- Scores
    score_total INT,
    score_revenue_75 INT,
    score_revenue_50 INT,
    score_employees INT,
    score_time_allocation INT,
    score_ai_integration INT,

    -- Résultats
    eligibility_status ENUM('eligible', 'partial', 'not_eligible'),
    estimated_credit_current DECIMAL(15,2),
    estimated_credit_optimized DECIMAL(15,2),

    -- Métadonnées
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_by UUID
);

-- Employés de l'entreprise
CREATE TABLE employees (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    assessment_id UUID REFERENCES assessments(id),

    job_title VARCHAR(255),
    department VARCHAR(100),
    is_full_time BOOLEAN,
    annual_salary DECIMAL(15,2),

    -- Allocation du temps (%)
    time_ai_dev INT DEFAULT 0,
    time_ai_integration INT DEFAULT 0,
    time_ai_data INT DEFAULT 0,
    time_ai_analytics INT DEFAULT 0,
    time_maintenance INT DEFAULT 0,
    time_support INT DEFAULT 0,
    time_admin INT DEFAULT 0,
    time_other INT DEFAULT 0,

    -- Calculs
    total_qualifying_time INT GENERATED ALWAYS AS (
        time_ai_dev + time_ai_integration + time_ai_data + time_ai_analytics
    ) STORED,
    is_eligible BOOLEAN GENERATED ALWAYS AS (
        total_qualifying_time >= 75
    ) STORED,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Projets/Produits IA
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    assessment_id UUID REFERENCES assessments(id),

    name VARCHAR(255),
    description TEXT,

    -- Technologies IA
    uses_ml BOOLEAN DEFAULT FALSE,
    uses_deep_learning BOOLEAN DEFAULT FALSE,
    uses_nlp BOOLEAN DEFAULT FALSE,
    uses_computer_vision BOOLEAN DEFAULT FALSE,
    uses_predictive_analytics BOOLEAN DEFAULT FALSE,
    uses_automation BOOLEAN DEFAULT FALSE,
    uses_llm BOOLEAN DEFAULT FALSE,

    -- Évaluation
    ai_integration_level ENUM('none', 'superficial', 'moderate', 'substantial'),
    is_in_production BOOLEAN,
    revenue_percentage DECIMAL(5,2),

    -- Score IA (calculé par l'algorithme)
    ai_score INT,
    ai_analysis TEXT, -- Analyse par Claude

    created_at TIMESTAMP DEFAULT NOW()
);

-- Recommandations générées
CREATE TABLE recommendations (
    id UUID PRIMARY KEY,
    assessment_id UUID REFERENCES assessments(id),

    category ENUM('employee', 'project', 'process', 'documentation'),
    priority ENUM('high', 'medium', 'low'),

    title VARCHAR(255),
    description TEXT,
    expected_impact INT, -- Points de score
    effort_level ENUM('low', 'medium', 'high'),
    estimated_weeks INT,

    status ENUM('pending', 'in_progress', 'completed', 'dismissed'),

    created_at TIMESTAMP DEFAULT NOW()
);

-- Documents générés
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    assessment_id UUID REFERENCES assessments(id),

    type ENUM('full_report', 'executive_summary', 'tech_sheet', 'action_plan', 'time_template'),
    file_url TEXT,
    file_name VARCHAR(255),

    generated_at TIMESTAMP DEFAULT NOW()
);

-- Réponses au questionnaire (JSON flexible)
CREATE TABLE questionnaire_responses (
    id UUID PRIMARY KEY,
    assessment_id UUID REFERENCES assessments(id),
    section VARCHAR(50),
    question_id VARCHAR(50),
    response JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Algorithme de Scoring

### Logique de Calcul

```python
# scoring_engine.py

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class EligibilityStatus(Enum):
    ELIGIBLE = "eligible"
    PARTIAL = "partial"
    NOT_ELIGIBLE = "not_eligible"

@dataclass
class ScoringResult:
    total_score: int
    max_score: int = 100

    # Sous-scores
    score_revenue_75: int = 0  # /20
    score_revenue_50: int = 0  # /20
    score_employees: int = 0   # /15
    score_time_allocation: int = 0  # /25
    score_ai_integration: int = 0  # /20

    # Résultats
    eligibility_status: EligibilityStatus = EligibilityStatus.NOT_ELIGIBLE
    estimated_credit_current: float = 0
    estimated_credit_optimized: float = 0

    # Détails
    issues: List[str] = None
    recommendations: List[dict] = None


def calculate_eligibility_score(company_data: dict) -> ScoringResult:
    """
    Calcule le score d'éligibilité CDAEIA basé sur les données de l'entreprise.
    """
    result = ScoringResult(total_score=0, issues=[], recommendations=[])

    # ═══════════════════════════════════════════════════════════
    # TEST 1: Revenus IT (75%) - Maximum 20 points
    # ═══════════════════════════════════════════════════════════

    it_revenue_pct = (company_data['it_revenue'] / company_data['total_revenue']) * 100

    if it_revenue_pct >= 75:
        result.score_revenue_75 = 20
    elif it_revenue_pct >= 70:
        result.score_revenue_75 = 15
        result.issues.append(f"Revenus IT à {it_revenue_pct:.1f}% (75% requis)")
    elif it_revenue_pct >= 60:
        result.score_revenue_75 = 10
        result.issues.append(f"Revenus IT insuffisants: {it_revenue_pct:.1f}%")
    else:
        result.score_revenue_75 = 0
        result.issues.append(f"CRITIQUE: Revenus IT à {it_revenue_pct:.1f}% (75% requis)")

    # ═══════════════════════════════════════════════════════════
    # TEST 2: Sous-secteurs (50%) - Maximum 20 points
    # ═══════════════════════════════════════════════════════════

    subsector_revenue = (
        company_data.get('software_revenue', 0) +
        company_data.get('system_design_revenue', 0) +
        company_data.get('data_hosting_revenue', 0)
    )
    subsector_pct = (subsector_revenue / company_data['total_revenue']) * 100

    if subsector_pct >= 50:
        result.score_revenue_50 = 20
    elif subsector_pct >= 45:
        result.score_revenue_50 = 15
    elif subsector_pct >= 40:
        result.score_revenue_50 = 10
    else:
        result.score_revenue_50 = 5
        result.issues.append(f"Revenus sous-secteurs: {subsector_pct:.1f}% (50% requis)")

    # ═══════════════════════════════════════════════════════════
    # TEST 3: Effectifs (minimum 6) - Maximum 15 points
    # ═══════════════════════════════════════════════════════════

    eligible_employees = [e for e in company_data['employees'] if e['is_eligible']]
    num_eligible = len(eligible_employees)

    if num_eligible >= 6:
        result.score_employees = 15
    elif num_eligible == 5:
        result.score_employees = 10
        result.issues.append("5 employés éligibles (6 requis)")
        result.recommendations.append({
            "title": "Recruter 1 employé tech supplémentaire",
            "impact": 5,
            "effort": "medium",
            "priority": "high"
        })
    elif num_eligible >= 3:
        result.score_employees = 5
        result.issues.append(f"Seulement {num_eligible} employés éligibles (6 requis)")
    else:
        result.score_employees = 0
        result.issues.append(f"CRITIQUE: {num_eligible} employés éligibles (6 requis)")

    # ═══════════════════════════════════════════════════════════
    # TEST 4: Allocation du temps (75%) - Maximum 25 points
    # ═══════════════════════════════════════════════════════════

    if eligible_employees:
        avg_qualifying_time = sum(e['total_qualifying_time'] for e in eligible_employees) / len(eligible_employees)
    else:
        avg_qualifying_time = 0

    if avg_qualifying_time >= 75:
        result.score_time_allocation = 25
    elif avg_qualifying_time >= 70:
        result.score_time_allocation = 20
    elif avg_qualifying_time >= 60:
        result.score_time_allocation = 15
        result.issues.append(f"Temps IA moyen: {avg_qualifying_time:.1f}% (75% requis)")
    elif avg_qualifying_time >= 50:
        result.score_time_allocation = 10
    else:
        result.score_time_allocation = 5
        result.issues.append(f"Temps IA insuffisant: {avg_qualifying_time:.1f}%")

    # Identifier les employés à réaffecter
    for emp in company_data['employees']:
        if 50 <= emp['total_qualifying_time'] < 75:
            result.recommendations.append({
                "title": f"Réaffecter {emp['job_title']} vers activités IA",
                "description": f"Actuellement {emp['total_qualifying_time']}% IA, besoin de +{75 - emp['total_qualifying_time']}%",
                "impact": 3,
                "effort": "low",
                "priority": "medium"
            })

    # ═══════════════════════════════════════════════════════════
    # TEST 5: Intégration IA - Maximum 20 points
    # ═══════════════════════════════════════════════════════════

    projects = company_data.get('projects', [])

    if not projects:
        result.score_ai_integration = 0
        result.issues.append("CRITIQUE: Aucun projet IA documenté")
    else:
        # Compter les projets par niveau d'intégration
        substantial = len([p for p in projects if p['ai_integration_level'] == 'substantial'])
        moderate = len([p for p in projects if p['ai_integration_level'] == 'moderate'])
        superficial = len([p for p in projects if p['ai_integration_level'] == 'superficial'])

        # Score basé sur le meilleur projet + bonus pour plusieurs
        if substantial >= 1:
            result.score_ai_integration = 15 + min(substantial - 1, 5)  # 15 + bonus
        elif moderate >= 1:
            result.score_ai_integration = 10 + min(moderate - 1, 5)
            result.issues.append("Intégration IA modérée - amélioration recommandée")
        elif superficial >= 1:
            result.score_ai_integration = 5
            result.issues.append("Intégration IA superficielle - non éligible")
        else:
            result.score_ai_integration = 0

        # Compter les technologies IA
        ai_techs = set()
        for p in projects:
            if p.get('uses_ml'): ai_techs.add('ml')
            if p.get('uses_deep_learning'): ai_techs.add('dl')
            if p.get('uses_nlp'): ai_techs.add('nlp')
            if p.get('uses_computer_vision'): ai_techs.add('cv')
            if p.get('uses_predictive_analytics'): ai_techs.add('analytics')
            if p.get('uses_llm'): ai_techs.add('llm')

        if len(ai_techs) < 2:
            result.recommendations.append({
                "title": "Diversifier les technologies IA",
                "description": f"Actuellement {len(ai_techs)} technologie(s). Considérer NLP, ML, ou analytics.",
                "impact": 5,
                "effort": "high",
                "priority": "medium"
            })

    # ═══════════════════════════════════════════════════════════
    # CALCUL FINAL
    # ═══════════════════════════════════════════════════════════

    result.total_score = (
        result.score_revenue_75 +
        result.score_revenue_50 +
        result.score_employees +
        result.score_time_allocation +
        result.score_ai_integration
    )

    # Déterminer le statut d'éligibilité
    critical_criteria_met = (
        result.score_revenue_75 >= 15 and  # Test 75% passé
        result.score_employees >= 10 and   # Minimum 5-6 employés
        result.score_ai_integration >= 10  # Au moins intégration modérée
    )

    if result.total_score >= 80 and critical_criteria_met:
        result.eligibility_status = EligibilityStatus.ELIGIBLE
    elif result.total_score >= 50 and result.score_revenue_75 >= 10:
        result.eligibility_status = EligibilityStatus.PARTIAL
    else:
        result.eligibility_status = EligibilityStatus.NOT_ELIGIBLE

    # ═══════════════════════════════════════════════════════════
    # CALCUL DU CRÉDIT
    # ═══════════════════════════════════════════════════════════

    result.estimated_credit_current = calculate_credit(
        eligible_employees,
        year=2026
    )

    # Estimation après optimisation (tous les employés à 75%+)
    optimized_employees = optimize_employees(company_data['employees'])
    result.estimated_credit_optimized = calculate_credit(
        optimized_employees,
        year=2026
    )

    return result


def calculate_credit(employees: list, year: int = 2026) -> float:
    """
    Calcule le crédit CDAEIA basé sur les employés éligibles.
    """
    EXCLUSION_THRESHOLD = 18571  # Seuil d'exclusion 2025 (indexé)

    # Taux par année
    rates = {
        2025: {'refundable': 0.23, 'non_refundable': 0.07},
        2026: {'refundable': 0.22, 'non_refundable': 0.08},
        2027: {'refundable': 0.21, 'non_refundable': 0.09},
        2028: {'refundable': 0.20, 'non_refundable': 0.10},
    }

    rate = rates.get(year, rates[2028])
    total_rate = rate['refundable'] + rate['non_refundable']

    eligible = [e for e in employees if e.get('is_eligible', False)]

    total_eligible_salary = sum(e['annual_salary'] for e in eligible)
    total_exclusion = len(eligible) * EXCLUSION_THRESHOLD

    net_eligible_salary = max(0, total_eligible_salary - total_exclusion)

    return net_eligible_salary * total_rate


def optimize_employees(employees: list) -> list:
    """
    Simule l'optimisation des employés pour maximiser l'éligibilité.
    """
    optimized = []
    for emp in employees:
        opt_emp = emp.copy()
        # Simuler réallocation vers 75% IA si proche
        if emp['total_qualifying_time'] >= 50:
            opt_emp['total_qualifying_time'] = 75
            opt_emp['is_eligible'] = True
        optimized.append(opt_emp)
    return optimized
```

---

## Interface Utilisateur

### Wireframes Principaux

#### 1. Dashboard Principal

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🏢 CDAEIA Diagnostic Tool                    [Mon Compte] [Déconnexion]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Bienvenue, Roland                                                          │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  3              │  │  $485,000       │  │  78%            │             │
│  │  Diagnostics    │  │  Crédits        │  │  Score moyen    │             │
│  │  actifs         │  │  identifiés     │  │                 │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  DIAGNOSTICS RÉCENTS                                        [+ Nouveau]    │
│  ─────────────────────────────────────────────────────────────────────     │
│                                                                             │
│  │ Entreprise       │ Statut      │ Score │ Crédit Est. │ Actions   │      │
│  ├──────────────────┼─────────────┼───────┼─────────────┼───────────┤      │
│  │ TechCo Inc.      │ ✓ Complété  │ 82    │ 145,000$    │ [Voir]    │      │
│  │ DataSoft         │ ⏳ En cours │ --    │ --          │ [Continuer]│      │
│  │ AI Solutions     │ ✓ Complété  │ 71    │ 98,000$     │ [Voir]    │      │
│  │ CloudApp         │ ⏳ En cours │ --    │ --          │ [Continuer]│      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 2. Questionnaire (Étape par Étape)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Diagnostic CDAEIA - TechCo Inc.                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Étape 2 de 5: Tests de Revenus                                            │
│  ████████████░░░░░░░░░░░░░░░░░░░░  40%                                     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Quel est votre revenu brut total pour le dernier exercice?        │   │
│  │                                                                     │   │
│  │  $ [_______________] CAD                                           │   │
│  │                                                                     │   │
│  │  ──────────────────────────────────────────────────────────────    │   │
│  │                                                                     │   │
│  │  De ce montant, combien provient d'activités IT?                   │   │
│  │                                                                     │   │
│  │  $ [_______________] CAD                                           │   │
│  │                                                                     │   │
│  │  ⓘ Inclut: développement logiciel, SaaS, consultation IT,         │   │
│  │     intégration systèmes, services cloud, cybersécurité, etc.      │   │
│  │                                                                     │   │
│  │  ──────────────────────────────────────────────────────────────    │   │
│  │                                                                     │   │
│  │  Résultat préliminaire:                                            │   │
│  │  ┌─────────────────────────────────────────────┐                   │   │
│  │  │  Test 75%: 82% ✓ CONFORME                   │                   │   │
│  │  └─────────────────────────────────────────────┘                   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [← Précédent]                                         [Suivant →]         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 3. Résultats du Diagnostic

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Résultats du Diagnostic - TechCo Inc.                      [Télécharger]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │         SCORE D'ÉLIGIBILITÉ: 72/100                                │   │
│  │         ████████████████████░░░░░░░░                               │   │
│  │                                                                     │   │
│  │         Statut: PARTIELLEMENT ÉLIGIBLE                             │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  DÉTAIL DES SCORES                                                         │
│  ┌────────────────────────────┬───────┬────────────────────────────────┐   │
│  │ Critère                    │ Score │ Statut                         │   │
│  ├────────────────────────────┼───────┼────────────────────────────────┤   │
│  │ Test 75% revenus IT        │ 20/20 │ ✓ 82% - Conforme              │   │
│  │ Test 50% sous-secteurs     │ 18/20 │ ✓ 55% - Conforme              │   │
│  │ Effectifs (min. 6)         │ 10/15 │ ⚠ 5 employés (1 manquant)     │   │
│  │ Allocation temps 75%       │ 15/25 │ ⚠ Moyenne 68%                 │   │
│  │ Intégration IA             │ 9/20  │ ⚠ Modérée (à renforcer)       │   │
│  └────────────────────────────┴───────┴────────────────────────────────┘   │
│                                                                             │
│  CRÉDIT ESTIMÉ                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Situation actuelle:        85,000$/an                             │   │
│  │  Après optimisation:       145,000$/an                             │   │
│  │  Gain potentiel:          +60,000$/an                              │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [Voir Recommandations]    [Générer Rapport]    [Planifier Appel]         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Plan de Développement

### Phase 1: MVP (4-6 semaines)

| Semaine | Livrables |
|---------|-----------|
| 1-2 | Setup projet, DB, auth, questionnaire Section 1-2 |
| 3-4 | Questionnaire complet, algorithme de scoring v1 |
| 5-6 | Dashboard résultats, génération rapport PDF basique |

**Coût estimé:**
- DIY: 0$ (votre temps)
- Freelance: 5,000-10,000$

### Phase 2: Amélioration (4 semaines)

| Semaine | Livrables |
|---------|-----------|
| 7-8 | Moteur de recommandations, calculateur interactif |
| 9-10 | Rapports avancés, intégration Claude pour analyse IA |

### Phase 3: Scale (Ongoing)

- Multi-utilisateurs (équipe)
- Intégrations (Zoho, QuickBooks)
- Version partenaire CPA
- API pour intégrations tierces

---

## Modèle Économique

### Option A: Outil Interne (Productivité)

- Pas de revenus directs
- Accélère vos diagnostics de 10x
- Permet de baisser les prix ou augmenter les marges

### Option B: SaaS B2B

| Plan | Prix/mois | Inclus |
|------|-----------|--------|
| **Starter** | 99$ | 5 diagnostics/mois, rapports basiques |
| **Pro** | 299$ | 20 diagnostics/mois, rapports complets, API |
| **Enterprise** | 999$ | Illimité, white-label, support dédié |

### Option C: Pay-per-Use

| Service | Prix |
|---------|------|
| Auto-évaluation (client final) | Gratuit |
| Diagnostic Express (sans accompagnement) | 500$ |
| Diagnostic + Rapport complet | 1,500$ |
| Diagnostic + Accompagnement Ran.AI | 2,500$+ |

---

## Prochaines Étapes

1. **Décider de l'approche:** MVP no-code ou développement custom?
2. **Valider le questionnaire:** Tester avec 2-3 entreprises réelles
3. **Développer le scoring:** Affiner l'algorithme avec des cas réels
4. **Créer le MVP:** 4-6 semaines de développement

---

*Spécifications créées le 9 janvier 2026*
