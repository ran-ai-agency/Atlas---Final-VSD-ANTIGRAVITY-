"""
CDAEIA Diagnostic Tool - Générateur de Rapports
=================================================

Ce module génère des rapports PDF et Markdown à partir des résultats
du diagnostic CDAEIA.
"""

from datetime import datetime
from typing import Dict, Any, Optional
import os

from scoring_engine import ScoringResult, EligibilityStatus, Priority, result_to_dict


def generate_markdown_report(result: ScoringResult, responses: Dict[str, Any]) -> str:
    """
    Génère un rapport complet en format Markdown.

    Args:
        result: Résultat du scoring
        responses: Réponses au questionnaire

    Returns:
        Contenu Markdown du rapport
    """
    today = datetime.now().strftime("%d %B %Y")

    # Déterminer les icônes de statut
    status_icons = {
        EligibilityStatus.ELIGIBLE: "✅",
        EligibilityStatus.PARTIAL: "⚠️",
        EligibilityStatus.NOT_ELIGIBLE: "❌",
    }
    status_labels = {
        EligibilityStatus.ELIGIBLE: "ÉLIGIBLE",
        EligibilityStatus.PARTIAL: "PARTIELLEMENT ÉLIGIBLE",
        EligibilityStatus.NOT_ELIGIBLE: "NON ÉLIGIBLE",
    }

    status_icon = status_icons.get(result.eligibility_status, "❓")
    status_label = status_labels.get(result.eligibility_status, "INCONNU")

    report = f"""# Rapport de Diagnostic CDAEIA

**Client:** {responses.get('company_name', 'N/A')}
**Date:** {today}
**Préparé par:** Ran.AI Agency

---

## Sommaire Exécutif

### Score d'Éligibilité

| Métrique | Valeur |
|----------|--------|
| **Score Total** | **{result.total_score} / {result.max_score}** |
| **Pourcentage** | {result.percentage:.1f}% |
| **Statut** | {status_icon} **{status_label}** |

### Crédit CDAEIA Estimé

| Scénario | Crédit Annuel |
|----------|---------------|
| Situation actuelle | **{result.credit_current.total_credit:,.0f}$** |
| Après optimisation | **{result.credit_optimized.total_credit:,.0f}$** |
| **Gain potentiel** | **+{result.credit_gain:,.0f}$** |

### Message

> {result.status_message}

---

## 1. Profil de l'Entreprise

| Information | Valeur |
|-------------|--------|
| Nom | {responses.get('company_name', 'N/A')} |
| NEQ | {responses.get('company_neq', 'N/A')} |
| Secteur | {responses.get('industry', 'N/A')} |
| Fin d'exercice | {responses.get('fiscal_year_end', 'N/A')} |
| Total employés | {responses.get('total_employees', 'N/A')} |
| Employés tech | {responses.get('tech_employees_fulltime', 'N/A')} |

---

## 2. Détail des Scores par Critère

"""

    # Ajouter le détail de chaque critère
    for breakdown in result.score_breakdown:
        status_char = "✓" if breakdown.status == "pass" else "⚠" if breakdown.status == "warning" else "✗"
        bar_filled = int((breakdown.score / breakdown.max_score) * 20) if breakdown.max_score > 0 else 0
        bar = "█" * bar_filled + "░" * (20 - bar_filled)

        report += f"""### {breakdown.criterion}

| Métrique | Valeur |
|----------|--------|
| Score | **{breakdown.score} / {breakdown.max_score}** |
| Statut | {status_char} |
| Progression | `{bar}` |

**Détail:** {breakdown.details}

"""

    # Section sur les problèmes critiques
    if result.critical_issues:
        report += """---

## 3. Problèmes Critiques

Les problèmes suivants doivent être résolus pour devenir éligible au CDAEIA:

"""
        for issue in result.critical_issues:
            report += f"- ❌ **{issue}**\n"

    # Section sur les avertissements
    if result.warnings:
        report += """
### Avertissements

"""
        for warning in result.warnings:
            report += f"- ⚠️ {warning}\n"

    # Section sur le calcul du crédit
    if result.credit_current:
        report += f"""
---

## 4. Calcul du Crédit CDAEIA

### Situation Actuelle

```
Employés éligibles:              {result.credit_current.eligible_employees}
Masse salariale brute:           {result.credit_current.total_eligible_salary:,.0f}$
Seuil d'exclusion:              -{result.credit_current.exclusion_threshold:,.0f}$
                                 ──────────────
Masse salariale nette:           {result.credit_current.net_eligible_salary:,.0f}$

Taux de crédit (2026):           30%
  - Portion remboursable (22%):  {result.credit_current.refundable_portion:,.0f}$
  - Portion non-remb. (8%):      {result.credit_current.non_refundable_portion:,.0f}$
                                 ──────────────
CRÉDIT TOTAL:                    {result.credit_current.total_credit:,.0f}$
```

"""

    if result.credit_optimized and result.credit_gain > 0:
        report += f"""### Scénario Optimisé

```
Employés éligibles:              {result.credit_optimized.eligible_employees}
Masse salariale nette:           {result.credit_optimized.net_eligible_salary:,.0f}$
                                 ──────────────
CRÉDIT OPTIMISÉ:                 {result.credit_optimized.total_credit:,.0f}$

GAIN POTENTIEL:                 +{result.credit_gain:,.0f}$/an
```

"""

    # Section recommandations
    if result.recommendations:
        report += """---

## 5. Recommandations

"""
        # Grouper par priorité
        high_priority = [r for r in result.recommendations if r.priority == Priority.HIGH]
        medium_priority = [r for r in result.recommendations if r.priority == Priority.MEDIUM]
        low_priority = [r for r in result.recommendations if r.priority == Priority.LOW]

        if high_priority:
            report += """### Priorité Haute (Action immédiate requise)

"""
            for i, rec in enumerate(high_priority, 1):
                report += f"""#### {i}. {rec.title}

**Impact:** +{rec.expected_impact} points | **Effort:** {rec.effort_level.value} | **Délai:** {rec.estimated_weeks} semaines

{rec.description}

**Actions:**
"""
                for action in rec.action_items:
                    report += f"- [ ] {action}\n"
                report += "\n"

        if medium_priority:
            report += """### Priorité Moyenne (À planifier)

"""
            for i, rec in enumerate(medium_priority, 1):
                report += f"""#### {i}. {rec.title}

**Impact:** +{rec.expected_impact} points | **Effort:** {rec.effort_level.value} | **Délai:** {rec.estimated_weeks} semaines

{rec.description}

"""

        if low_priority:
            report += """### Priorité Basse (Optimisation)

"""
            for rec in low_priority:
                report += f"- **{rec.title}** - Impact: +{rec.expected_impact} points\n"

    # Section plan d'action
    report += """---

## 6. Plan d'Action Suggéré

### Actions Immédiates (30 jours)

"""
    immediate_actions = [r for r in result.recommendations if r.priority == Priority.HIGH][:3]
    for i, rec in enumerate(immediate_actions, 1):
        report += f"{i}. [ ] {rec.title}\n"

    report += """
### Actions Moyen Terme (90 jours)

"""
    medium_actions = [r for r in result.recommendations if r.priority == Priority.MEDIUM][:3]
    for i, rec in enumerate(medium_actions, 1):
        report += f"{i}. [ ] {rec.title}\n"

    # Conclusion
    report += f"""
---

## 7. Prochaines Étapes

1. **Réviser ce rapport** avec votre équipe de direction
2. **Prioriser les recommandations** selon vos ressources
3. **Implémenter le suivi du temps** si pas déjà en place
4. **Planifier un appel de suivi** avec Ran.AI Agency

### Contact

**Ran.AI Agency**
- Téléphone: 514-918-1241
- Email: info@ran-ai-agency.ca
- Web: ran-ai-agency.ca

---

## Annexes

### A. Glossaire CDAEIA

| Terme | Définition |
|-------|------------|
| CDAEIA | Crédit d'impôt pour le Développement des Affaires Électroniques intégrant l'Intelligence Artificielle |
| Seuil d'exclusion | Premiers 18 571$ de salaire par employé non éligibles |
| Test 75% | Au moins 75% des revenus doivent provenir du secteur TI |
| Test 50% | Au moins 50% des revenus des sous-secteurs qualifiants |
| Activité qualifiante | Développement/intégration IA, analytique avancée, données pour IA |

### B. Contacts Utiles

- **Investissement Québec:** 1-844-474-6367
- **Revenu Québec:** 1-800-267-6299

---

*Ce rapport est fourni à titre informatif et ne constitue pas un avis fiscal ou juridique. Consultez un professionnel qualifié pour votre situation spécifique.*

*Généré le {today} par Ran.AI Agency*
"""

    return report


def generate_executive_summary(result: ScoringResult, responses: Dict[str, Any]) -> str:
    """
    Génère un sommaire exécutif de 2 pages.
    """
    today = datetime.now().strftime("%d %B %Y")

    status_labels = {
        EligibilityStatus.ELIGIBLE: "ÉLIGIBLE",
        EligibilityStatus.PARTIAL: "PARTIELLEMENT ÉLIGIBLE",
        EligibilityStatus.NOT_ELIGIBLE: "NON ÉLIGIBLE",
    }

    summary = f"""# Sommaire Exécutif - Diagnostic CDAEIA

**{responses.get('company_name', 'N/A')}** | {today}

---

## Résultat

### Score: {result.total_score}/100 ({result.percentage:.0f}%)

### Statut: {status_labels.get(result.eligibility_status, 'INCONNU')}

---

## Crédit d'Impôt Estimé

| | Actuel | Potentiel |
|-|--------|-----------|
| **Crédit annuel** | {result.credit_current.total_credit:,.0f}$ | {result.credit_optimized.total_credit:,.0f}$ |

**Gain possible: +{result.credit_gain:,.0f}$/an**

---

## Top 3 Actions Prioritaires

"""
    top_recommendations = [r for r in result.recommendations if r.priority == Priority.HIGH][:3]
    for i, rec in enumerate(top_recommendations, 1):
        summary += f"""### {i}. {rec.title}
Impact: +{rec.expected_impact} points | Délai: {rec.estimated_weeks} semaines

"""

    summary += f"""---

## Prochaine Étape

Planifiez un appel avec Ran.AI Agency pour discuter de la mise en œuvre.

**Contact:** 514-918-1241 | info@ran-ai-agency.ca

---

*Ran.AI Agency - Experts en transformation IA*
"""

    return summary


def generate_action_plan(result: ScoringResult) -> str:
    """
    Génère un plan d'action détaillé exportable.
    """
    today = datetime.now().strftime("%Y-%m-%d")

    plan = f"""# Plan d'Action CDAEIA

Date: {today}

---

## Priorité Haute

"""
    high_priority = [r for r in result.recommendations if r.priority == Priority.HIGH]
    for rec in high_priority:
        plan += f"""### {rec.title}

- **Impact:** +{rec.expected_impact} points
- **Effort:** {rec.effort_level.value}
- **Délai:** {rec.estimated_weeks} semaines
- **Statut:** [ ] À faire

**Actions:**
"""
        for action in rec.action_items:
            plan += f"- [ ] {action}\n"
        plan += "\n---\n\n"

    plan += """## Priorité Moyenne

"""
    medium_priority = [r for r in result.recommendations if r.priority == Priority.MEDIUM]
    for rec in medium_priority:
        plan += f"""### {rec.title}

- **Impact:** +{rec.expected_impact} points
- **Délai:** {rec.estimated_weeks} semaines
- **Statut:** [ ] À faire

---

"""

    return plan


def save_report(content: str, filename: str, output_dir: str = ".tmp") -> str:
    """
    Sauvegarde le rapport dans un fichier.
    """
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


if __name__ == "__main__":
    # Test avec des données exemple
    from scoring_engine import calculate_score

    test_responses = {
        "company_name": "TechCo Inc.",
        "company_neq": "1234567890",
        "industry": "saas",
        "fiscal_year_end": "2025-12-31",
        "total_employees": 25,
        "is_tax_exempt": False,
        "is_crown_corp": False,
        "total_revenue": 2000000,
        "it_revenue": 1700000,
        "software_revenue": 800000,
        "system_design_revenue": 400000,
        "data_hosting_revenue": 200000,
        "tech_employees_fulltime": 8,
        "total_tech_payroll": 640000,
        "avg_time_ai_dev": 30,
        "avg_time_ai_integration": 20,
        "avg_time_ai_data": 10,
        "avg_time_ai_analytics": 10,
        "avg_time_maintenance": 15,
        "avg_time_support": 5,
        "avg_time_admin": 10,
        "has_ai_products": True,
        "ai_technologies": ["ml_classical", "nlp", "predictive_analytics"],
        "ai_maturity": "scaling",
        "ai_revenue_percentage": 40,
        "has_technical_docs": "partial",
        "time_tracking_system": "basic",
    }

    result = calculate_score(test_responses)

    # Générer le rapport complet
    report = generate_markdown_report(result, test_responses)
    filepath = save_report(report, "diagnostic_cdaeia_techco.md")
    print(f"Rapport sauvegardé: {filepath}")

    # Générer le sommaire exécutif
    summary = generate_executive_summary(result, test_responses)
    summary_path = save_report(summary, "sommaire_executif_techco.md")
    print(f"Sommaire sauvegardé: {summary_path}")

    # Générer le plan d'action
    action_plan = generate_action_plan(result)
    action_path = save_report(action_plan, "plan_action_techco.md")
    print(f"Plan d'action sauvegardé: {action_path}")
