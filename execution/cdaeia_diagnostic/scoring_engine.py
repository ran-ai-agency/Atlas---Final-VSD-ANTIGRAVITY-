"""
CDAEIA Diagnostic Tool - Moteur de Scoring
============================================

Ce module calcule le score d'éligibilité CDAEIA basé sur les réponses
au questionnaire et génère des recommandations personnalisées.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import json


class EligibilityStatus(Enum):
    ELIGIBLE = "eligible"
    PARTIAL = "partial"
    NOT_ELIGIBLE = "not_eligible"


class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EffortLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Recommendation:
    id: str
    category: str  # employee, project, process, documentation
    priority: Priority
    title: str
    description: str
    expected_impact: int  # Points de score
    effort_level: EffortLevel
    estimated_weeks: int
    action_items: List[str] = field(default_factory=list)


@dataclass
class ScoreBreakdown:
    """Détail du score pour un critère."""
    criterion: str
    score: int
    max_score: int
    status: str  # pass, warning, fail
    details: str
    value: Any = None


@dataclass
class CreditCalculation:
    """Calcul détaillé du crédit CDAEIA."""
    eligible_employees: int
    total_eligible_salary: float
    exclusion_threshold: float
    net_eligible_salary: float
    credit_rate: float
    refundable_portion: float
    non_refundable_portion: float
    total_credit: float


@dataclass
class ScoringResult:
    """Résultat complet du diagnostic."""
    # Scores
    total_score: int
    max_score: int = 100
    percentage: float = 0.0

    # Détail par critère
    score_breakdown: List[ScoreBreakdown] = field(default_factory=list)

    # Statut global
    eligibility_status: EligibilityStatus = EligibilityStatus.NOT_ELIGIBLE
    status_message: str = ""

    # Calculs de crédit
    credit_current: Optional[CreditCalculation] = None
    credit_optimized: Optional[CreditCalculation] = None
    credit_gain: float = 0.0

    # Problèmes identifiés
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Recommandations
    recommendations: List[Recommendation] = field(default_factory=list)

    # Métadonnées
    assessment_date: str = ""
    company_name: str = ""


# =============================================================================
# CONSTANTES CDAEIA
# =============================================================================

# Seuil d'exclusion par employé (montant personnel de base)
EXCLUSION_THRESHOLD_2025 = 18571

# Taux de crédit par année
CREDIT_RATES = {
    2025: {"refundable": 0.23, "non_refundable": 0.07, "total": 0.30},
    2026: {"refundable": 0.22, "non_refundable": 0.08, "total": 0.30},
    2027: {"refundable": 0.21, "non_refundable": 0.09, "total": 0.30},
    2028: {"refundable": 0.20, "non_refundable": 0.10, "total": 0.30},
}

# Poids des critères dans le score
SCORE_WEIGHTS = {
    "revenue_75": 20,      # Test 75% revenus IT
    "revenue_50": 20,      # Test 50% sous-secteurs
    "employees": 15,       # Minimum 6 employés
    "time_allocation": 25, # 75% temps sur IA
    "ai_integration": 20,  # Intégration IA substantielle
}


# =============================================================================
# MOTEUR DE SCORING
# =============================================================================

def calculate_score(responses: Dict[str, Any]) -> ScoringResult:
    """
    Calcule le score d'éligibilité CDAEIA complet.

    Args:
        responses: Dictionnaire des réponses au questionnaire

    Returns:
        ScoringResult avec tous les détails du diagnostic
    """
    result = ScoringResult(
        total_score=0,
        company_name=responses.get("company_name", ""),
    )

    # Vérifications préliminaires (disqualifiantes)
    if responses.get("is_tax_exempt", False):
        result.eligibility_status = EligibilityStatus.NOT_ELIGIBLE
        result.critical_issues.append("Les entreprises exonérées d'impôt ne sont pas éligibles au CDAEIA.")
        return result

    if responses.get("is_crown_corp", False):
        result.eligibility_status = EligibilityStatus.NOT_ELIGIBLE
        result.critical_issues.append("Les sociétés d'État ne sont pas éligibles au CDAEIA.")
        return result

    # ═══════════════════════════════════════════════════════════════════════
    # CRITÈRE 1: Test 75% Revenus IT
    # ═══════════════════════════════════════════════════════════════════════
    score_revenue_75 = _evaluate_revenue_75_test(responses, result)
    result.score_breakdown.append(score_revenue_75)

    # ═══════════════════════════════════════════════════════════════════════
    # CRITÈRE 2: Test 50% Sous-secteurs
    # ═══════════════════════════════════════════════════════════════════════
    score_revenue_50 = _evaluate_revenue_50_test(responses, result)
    result.score_breakdown.append(score_revenue_50)

    # ═══════════════════════════════════════════════════════════════════════
    # CRITÈRE 3: Effectifs (minimum 6 employés)
    # ═══════════════════════════════════════════════════════════════════════
    score_employees = _evaluate_employees(responses, result)
    result.score_breakdown.append(score_employees)

    # ═══════════════════════════════════════════════════════════════════════
    # CRITÈRE 4: Allocation du temps (75%)
    # ═══════════════════════════════════════════════════════════════════════
    score_time = _evaluate_time_allocation(responses, result)
    result.score_breakdown.append(score_time)

    # ═══════════════════════════════════════════════════════════════════════
    # CRITÈRE 5: Intégration IA
    # ═══════════════════════════════════════════════════════════════════════
    score_ai = _evaluate_ai_integration(responses, result)
    result.score_breakdown.append(score_ai)

    # ═══════════════════════════════════════════════════════════════════════
    # CALCUL DU SCORE TOTAL
    # ═══════════════════════════════════════════════════════════════════════
    result.total_score = sum(s.score for s in result.score_breakdown)
    result.percentage = (result.total_score / result.max_score) * 100

    # ═══════════════════════════════════════════════════════════════════════
    # DÉTERMINATION DU STATUT
    # ═══════════════════════════════════════════════════════════════════════
    result.eligibility_status = _determine_eligibility_status(result)
    result.status_message = _get_status_message(result)

    # ═══════════════════════════════════════════════════════════════════════
    # CALCUL DU CRÉDIT
    # ═══════════════════════════════════════════════════════════════════════
    result.credit_current = _calculate_credit(responses, optimized=False)
    result.credit_optimized = _calculate_credit(responses, optimized=True)

    if result.credit_current and result.credit_optimized:
        result.credit_gain = result.credit_optimized.total_credit - result.credit_current.total_credit

    # ═══════════════════════════════════════════════════════════════════════
    # GÉNÉRATION DES RECOMMANDATIONS
    # ═══════════════════════════════════════════════════════════════════════
    result.recommendations = _generate_recommendations(responses, result)

    # Trier les recommandations par priorité
    priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
    result.recommendations.sort(key=lambda r: priority_order[r.priority])

    return result


# =============================================================================
# FONCTIONS D'ÉVALUATION PAR CRITÈRE
# =============================================================================

def _evaluate_revenue_75_test(responses: Dict, result: ScoringResult) -> ScoreBreakdown:
    """Évalue le test des 75% de revenus IT."""
    total_revenue = responses.get("total_revenue", 0) or 0
    it_revenue = responses.get("it_revenue", 0) or 0

    if total_revenue == 0:
        return ScoreBreakdown(
            criterion="Test 75% Revenus IT",
            score=0,
            max_score=SCORE_WEIGHTS["revenue_75"],
            status="fail",
            details="Revenus non renseignés",
            value=0
        )

    percentage = (it_revenue / total_revenue) * 100

    if percentage >= 75:
        score = SCORE_WEIGHTS["revenue_75"]
        status = "pass"
        details = f"{percentage:.1f}% des revenus proviennent du secteur IT (≥75% requis)"
    elif percentage >= 70:
        score = int(SCORE_WEIGHTS["revenue_75"] * 0.75)
        status = "warning"
        details = f"{percentage:.1f}% des revenus IT - Proche du seuil de 75%"
        result.warnings.append(f"Revenus IT à {percentage:.1f}%, légèrement sous le seuil de 75%.")
    elif percentage >= 60:
        score = int(SCORE_WEIGHTS["revenue_75"] * 0.5)
        status = "warning"
        details = f"{percentage:.1f}% des revenus IT - En dessous du seuil requis"
        result.warnings.append(f"Revenus IT insuffisants: {percentage:.1f}% (75% requis).")
    else:
        score = 0
        status = "fail"
        details = f"Seulement {percentage:.1f}% des revenus IT (75% requis)"
        result.critical_issues.append(f"CRITIQUE: Revenus IT à {percentage:.1f}% - Le seuil de 75% n'est pas atteint.")

    return ScoreBreakdown(
        criterion="Test 75% Revenus IT",
        score=score,
        max_score=SCORE_WEIGHTS["revenue_75"],
        status=status,
        details=details,
        value=percentage
    )


def _evaluate_revenue_50_test(responses: Dict, result: ScoringResult) -> ScoreBreakdown:
    """Évalue le test des 50% de sous-secteurs qualifiants."""
    total_revenue = responses.get("total_revenue", 0) or 0
    software_revenue = responses.get("software_revenue", 0) or 0
    system_design_revenue = responses.get("system_design_revenue", 0) or 0
    data_hosting_revenue = responses.get("data_hosting_revenue", 0) or 0

    subsector_revenue = software_revenue + system_design_revenue + data_hosting_revenue

    if total_revenue == 0:
        return ScoreBreakdown(
            criterion="Test 50% Sous-secteurs",
            score=0,
            max_score=SCORE_WEIGHTS["revenue_50"],
            status="fail",
            details="Revenus non renseignés",
            value=0
        )

    percentage = (subsector_revenue / total_revenue) * 100

    if percentage >= 50:
        score = SCORE_WEIGHTS["revenue_50"]
        status = "pass"
        details = f"{percentage:.1f}% des revenus des sous-secteurs qualifiants (≥50% requis)"
    elif percentage >= 45:
        score = int(SCORE_WEIGHTS["revenue_50"] * 0.75)
        status = "warning"
        details = f"{percentage:.1f}% - Proche du seuil de 50%"
        result.warnings.append(f"Revenus sous-secteurs à {percentage:.1f}%, légèrement sous 50%.")
    elif percentage >= 40:
        score = int(SCORE_WEIGHTS["revenue_50"] * 0.5)
        status = "warning"
        details = f"{percentage:.1f}% - En dessous du seuil requis"
    else:
        score = int(SCORE_WEIGHTS["revenue_50"] * 0.25)
        status = "fail"
        details = f"Seulement {percentage:.1f}% des sous-secteurs qualifiants"
        result.critical_issues.append(f"Revenus sous-secteurs insuffisants: {percentage:.1f}% (50% requis).")

    return ScoreBreakdown(
        criterion="Test 50% Sous-secteurs",
        score=score,
        max_score=SCORE_WEIGHTS["revenue_50"],
        status=status,
        details=details,
        value=percentage
    )


def _evaluate_employees(responses: Dict, result: ScoringResult) -> ScoreBreakdown:
    """Évalue le critère des effectifs (minimum 6 employés éligibles)."""
    tech_fulltime = responses.get("tech_employees_fulltime", 0) or 0

    # Calculer combien sont éligibles (75%+ temps IA)
    # Pour l'instant, on utilise la moyenne d'allocation
    avg_qualifying_time = _calculate_avg_qualifying_time(responses)

    # Estimation: si la moyenne est >= 75%, tous les temps pleins sont potentiellement éligibles
    # Sinon, on estime une proportion
    if avg_qualifying_time >= 75:
        estimated_eligible = tech_fulltime
    elif avg_qualifying_time >= 60:
        estimated_eligible = int(tech_fulltime * 0.7)
    elif avg_qualifying_time >= 50:
        estimated_eligible = int(tech_fulltime * 0.5)
    else:
        estimated_eligible = int(tech_fulltime * 0.3)

    if estimated_eligible >= 6:
        score = SCORE_WEIGHTS["employees"]
        status = "pass"
        details = f"{estimated_eligible} employés éligibles estimés (≥6 requis)"
    elif estimated_eligible == 5:
        score = int(SCORE_WEIGHTS["employees"] * 0.67)
        status = "warning"
        details = f"5 employés éligibles estimés - 1 de moins que le minimum requis"
        result.warnings.append("Seulement 5 employés éligibles estimés (6 requis).")
    elif estimated_eligible >= 3:
        score = int(SCORE_WEIGHTS["employees"] * 0.33)
        status = "warning"
        details = f"{estimated_eligible} employés éligibles estimés - Sous le minimum"
    else:
        score = 0
        status = "fail"
        details = f"Seulement {estimated_eligible} employés éligibles estimés (6 requis)"
        result.critical_issues.append(f"CRITIQUE: Seulement {estimated_eligible} employés éligibles (minimum 6 requis).")

    return ScoreBreakdown(
        criterion="Effectifs (min. 6)",
        score=score,
        max_score=SCORE_WEIGHTS["employees"],
        status=status,
        details=details,
        value=estimated_eligible
    )


def _evaluate_time_allocation(responses: Dict, result: ScoringResult) -> ScoreBreakdown:
    """Évalue l'allocation du temps (75% sur activités IA)."""
    avg_qualifying = _calculate_avg_qualifying_time(responses)

    if avg_qualifying >= 75:
        score = SCORE_WEIGHTS["time_allocation"]
        status = "pass"
        details = f"{avg_qualifying:.1f}% du temps en moyenne sur activités IA (≥75% requis)"
    elif avg_qualifying >= 70:
        score = int(SCORE_WEIGHTS["time_allocation"] * 0.8)
        status = "warning"
        details = f"{avg_qualifying:.1f}% - Proche du seuil de 75%"
        result.warnings.append(f"Temps IA moyen à {avg_qualifying:.1f}%, légèrement sous 75%.")
    elif avg_qualifying >= 60:
        score = int(SCORE_WEIGHTS["time_allocation"] * 0.6)
        status = "warning"
        details = f"{avg_qualifying:.1f}% - Réallocation nécessaire"
        result.warnings.append(f"Temps IA insuffisant: {avg_qualifying:.1f}% (75% requis).")
    elif avg_qualifying >= 50:
        score = int(SCORE_WEIGHTS["time_allocation"] * 0.4)
        status = "warning"
        details = f"{avg_qualifying:.1f}% - Réorganisation significative nécessaire"
    else:
        score = int(SCORE_WEIGHTS["time_allocation"] * 0.2)
        status = "fail"
        details = f"Seulement {avg_qualifying:.1f}% du temps sur IA"
        result.critical_issues.append(f"Temps IA très insuffisant: {avg_qualifying:.1f}% (75% requis).")

    return ScoreBreakdown(
        criterion="Allocation temps (75%)",
        score=score,
        max_score=SCORE_WEIGHTS["time_allocation"],
        status=status,
        details=details,
        value=avg_qualifying
    )


def _evaluate_ai_integration(responses: Dict, result: ScoringResult) -> ScoreBreakdown:
    """Évalue le niveau d'intégration IA."""
    has_ai = responses.get("has_ai_products", False)
    ai_techs = responses.get("ai_technologies", []) or []
    ai_maturity = responses.get("ai_maturity", "")
    ai_revenue_pct = responses.get("ai_revenue_percentage", 0) or 0

    if not has_ai:
        score = 0
        status = "fail"
        details = "Aucun produit/service intégrant l'IA"
        result.critical_issues.append("CRITIQUE: Aucune intégration IA déclarée.")
        return ScoreBreakdown(
            criterion="Intégration IA",
            score=score,
            max_score=SCORE_WEIGHTS["ai_integration"],
            status=status,
            details=details,
            value=0
        )

    # Score basé sur plusieurs facteurs
    tech_score = min(len(ai_techs) * 2, 8)  # Max 8 points pour technologies

    maturity_scores = {
        "ai_first": 8,
        "mature": 6,
        "scaling": 4,
        "pilot": 2,
        "experimental": 1,
    }
    maturity_score = maturity_scores.get(ai_maturity, 0)

    # Score basé sur le % de revenus IA
    if ai_revenue_pct >= 50:
        revenue_score = 4
    elif ai_revenue_pct >= 30:
        revenue_score = 3
    elif ai_revenue_pct >= 10:
        revenue_score = 2
    else:
        revenue_score = 1

    total_ai_score = tech_score + maturity_score + revenue_score
    score = min(total_ai_score, SCORE_WEIGHTS["ai_integration"])

    if score >= 16:
        status = "pass"
        details = f"Intégration IA substantielle ({len(ai_techs)} technologies, maturité: {ai_maturity})"
    elif score >= 12:
        status = "pass"
        details = f"Bonne intégration IA ({len(ai_techs)} technologies)"
    elif score >= 8:
        status = "warning"
        details = f"Intégration IA modérée - Renforcement recommandé"
        result.warnings.append("Intégration IA modérée - Considérez renforcer vos capacités IA.")
    else:
        status = "warning"
        details = f"Intégration IA faible ou superficielle"
        result.warnings.append("Intégration IA insuffisante pour qualification CDAEIA.")

    return ScoreBreakdown(
        criterion="Intégration IA",
        score=score,
        max_score=SCORE_WEIGHTS["ai_integration"],
        status=status,
        details=details,
        value={"technologies": len(ai_techs), "maturity": ai_maturity, "revenue_pct": ai_revenue_pct}
    )


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def _calculate_avg_qualifying_time(responses: Dict) -> float:
    """Calcule le % moyen du temps sur activités IA qualifiantes."""
    time_ai_dev = responses.get("avg_time_ai_dev", 0) or 0
    time_ai_integration = responses.get("avg_time_ai_integration", 0) or 0
    time_ai_data = responses.get("avg_time_ai_data", 0) or 0
    time_ai_analytics = responses.get("avg_time_ai_analytics", 0) or 0

    return time_ai_dev + time_ai_integration + time_ai_data + time_ai_analytics


def _determine_eligibility_status(result: ScoringResult) -> EligibilityStatus:
    """Détermine le statut d'éligibilité basé sur le score et les critères."""
    # Critères critiques
    has_critical_issues = len(result.critical_issues) > 0

    # Vérifier si les critères de base sont passés
    revenue_75_passed = any(s.criterion == "Test 75% Revenus IT" and s.status == "pass" for s in result.score_breakdown)
    employees_ok = any(s.criterion == "Effectifs (min. 6)" and s.score >= SCORE_WEIGHTS["employees"] * 0.5 for s in result.score_breakdown)
    ai_ok = any(s.criterion == "Intégration IA" and s.score >= SCORE_WEIGHTS["ai_integration"] * 0.5 for s in result.score_breakdown)

    if has_critical_issues:
        return EligibilityStatus.NOT_ELIGIBLE
    elif result.total_score >= 80 and revenue_75_passed and employees_ok and ai_ok:
        return EligibilityStatus.ELIGIBLE
    elif result.total_score >= 50 and revenue_75_passed:
        return EligibilityStatus.PARTIAL
    else:
        return EligibilityStatus.NOT_ELIGIBLE


def _get_status_message(result: ScoringResult) -> str:
    """Génère le message de statut."""
    if result.eligibility_status == EligibilityStatus.ELIGIBLE:
        return "Votre entreprise semble éligible au CDAEIA. Une validation détaillée est recommandée."
    elif result.eligibility_status == EligibilityStatus.PARTIAL:
        return "Votre entreprise est partiellement éligible. Des ajustements sont nécessaires pour maximiser le crédit."
    else:
        return "Votre entreprise ne semble pas éligible au CDAEIA en l'état actuel. Des changements significatifs sont requis."


def _calculate_credit(responses: Dict, optimized: bool = False) -> CreditCalculation:
    """Calcule le crédit CDAEIA estimé."""
    tech_fulltime = responses.get("tech_employees_fulltime", 0) or 0
    total_payroll = responses.get("total_tech_payroll", 0) or 0
    avg_qualifying = _calculate_avg_qualifying_time(responses)

    year = 2026
    rates = CREDIT_RATES[year]

    # Estimation des employés éligibles
    if optimized:
        # Scénario optimisé: on suppose que tous les employés atteignent 75%
        eligible_employees = tech_fulltime
    else:
        # Scénario actuel
        if avg_qualifying >= 75:
            eligible_employees = tech_fulltime
        elif avg_qualifying >= 60:
            eligible_employees = int(tech_fulltime * 0.7)
        elif avg_qualifying >= 50:
            eligible_employees = int(tech_fulltime * 0.5)
        else:
            eligible_employees = int(tech_fulltime * 0.3)

    # Calcul de la masse salariale éligible
    if tech_fulltime > 0:
        avg_salary = total_payroll / tech_fulltime
        total_eligible_salary = eligible_employees * avg_salary
    else:
        total_eligible_salary = 0

    # Seuil d'exclusion
    exclusion = eligible_employees * EXCLUSION_THRESHOLD_2025

    # Masse salariale nette
    net_salary = max(0, total_eligible_salary - exclusion)

    # Calcul du crédit
    refundable = net_salary * rates["refundable"]
    non_refundable = net_salary * rates["non_refundable"]
    total_credit = refundable + non_refundable

    return CreditCalculation(
        eligible_employees=eligible_employees,
        total_eligible_salary=total_eligible_salary,
        exclusion_threshold=exclusion,
        net_eligible_salary=net_salary,
        credit_rate=rates["total"],
        refundable_portion=refundable,
        non_refundable_portion=non_refundable,
        total_credit=total_credit
    )


# =============================================================================
# GÉNÉRATION DES RECOMMANDATIONS
# =============================================================================

def _generate_recommendations(responses: Dict, result: ScoringResult) -> List[Recommendation]:
    """Génère des recommandations personnalisées basées sur l'analyse."""
    recommendations = []
    rec_id = 0

    # Analyser chaque critère et générer des recommandations appropriées

    # --- Recommandations sur les effectifs ---
    tech_fulltime = responses.get("tech_employees_fulltime", 0) or 0
    if tech_fulltime < 6:
        rec_id += 1
        recommendations.append(Recommendation(
            id=f"rec_{rec_id}",
            category="employee",
            priority=Priority.HIGH,
            title=f"Recruter {6 - tech_fulltime} employé(s) tech supplémentaire(s)",
            description=f"Vous avez actuellement {tech_fulltime} employés tech à temps plein. Le CDAEIA exige un minimum de 6 employés éligibles.",
            expected_impact=15,
            effort_level=EffortLevel.MEDIUM,
            estimated_weeks=8,
            action_items=[
                "Définir les profils recherchés (privilégier les spécialistes IA/ML)",
                "Publier les offres d'emploi",
                "Considérer des contractors qui peuvent devenir employés",
            ]
        ))
    elif tech_fulltime == 6:
        rec_id += 1
        recommendations.append(Recommendation(
            id=f"rec_{rec_id}",
            category="employee",
            priority=Priority.MEDIUM,
            title="Sécuriser votre marge d'employés éligibles",
            description="Vous êtes exactement au minimum de 6 employés. Considérez recruter 1-2 personnes supplémentaires pour avoir une marge de sécurité.",
            expected_impact=5,
            effort_level=EffortLevel.MEDIUM,
            estimated_weeks=8,
            action_items=[
                "Planifier le recrutement d'un 7ème employé tech",
                "Préparer un plan de contingence si un employé quitte",
            ]
        ))

    # --- Recommandations sur l'allocation du temps ---
    avg_qualifying = _calculate_avg_qualifying_time(responses)
    if avg_qualifying < 75:
        rec_id += 1
        gap = 75 - avg_qualifying
        recommendations.append(Recommendation(
            id=f"rec_{rec_id}",
            category="process",
            priority=Priority.HIGH,
            title=f"Réallouer {gap:.0f}% du temps vers des activités IA",
            description=f"Actuellement {avg_qualifying:.1f}% du temps est sur des activités IA qualifiantes. Vous devez atteindre 75%.",
            expected_impact=25,
            effort_level=EffortLevel.MEDIUM,
            estimated_weeks=4,
            action_items=[
                "Identifier les employés proches du seuil de 75%",
                "Réduire les tâches de maintenance assignées aux employés éligibles",
                "Transférer la maintenance vers du support externe ou des employés non-éligibles",
                "Augmenter les projets de développement IA",
            ]
        ))

    maintenance_time = responses.get("avg_time_maintenance", 0) or 0
    if maintenance_time > 15:
        rec_id += 1
        recommendations.append(Recommendation(
            id=f"rec_{rec_id}",
            category="process",
            priority=Priority.MEDIUM,
            title="Réduire ou externaliser la maintenance",
            description=f"{maintenance_time}% du temps est consacré à la maintenance, qui n'est plus éligible au CDAEIA.",
            expected_impact=10,
            effort_level=EffortLevel.MEDIUM,
            estimated_weeks=8,
            action_items=[
                "Identifier les tâches de maintenance récurrentes",
                "Évaluer l'externalisation vers un prestataire",
                "Automatiser les tâches de maintenance répétitives",
                "Créer une équipe de maintenance séparée (non comptée pour CDAEIA)",
            ]
        ))

    # --- Recommandations sur l'intégration IA ---
    ai_techs = responses.get("ai_technologies", []) or []
    ai_maturity = responses.get("ai_maturity", "")

    if len(ai_techs) < 2:
        rec_id += 1
        recommendations.append(Recommendation(
            id=f"rec_{rec_id}",
            category="project",
            priority=Priority.HIGH,
            title="Diversifier les technologies IA",
            description=f"Vous utilisez seulement {len(ai_techs)} technologie(s) IA. Diversifier renforce votre dossier CDAEIA.",
            expected_impact=10,
            effort_level=EffortLevel.HIGH,
            estimated_weeks=12,
            action_items=[
                "Identifier des opportunités d'intégrer NLP (chatbots, analyse de texte)",
                "Considérer l'analytique prédictive pour vos données",
                "Explorer l'automatisation intelligente de processus",
                "Évaluer les LLM/IA générative pour vos cas d'usage",
            ]
        ))

    if ai_maturity in ["experimental", "pilot"]:
        rec_id += 1
        recommendations.append(Recommendation(
            id=f"rec_{rec_id}",
            category="project",
            priority=Priority.HIGH,
            title="Faire passer vos projets IA en production",
            description="Vos initiatives IA sont encore au stade expérimental/pilote. Le CDAEIA valorise l'IA intégrée en production.",
            expected_impact=10,
            effort_level=EffortLevel.HIGH,
            estimated_weeks=16,
            action_items=[
                "Identifier le projet IA pilote le plus mature",
                "Créer un plan de mise en production",
                "Définir des métriques de succès mesurables",
                "Documenter l'impact business de l'IA",
            ]
        ))

    # --- Recommandations sur la documentation ---
    has_technical_docs = responses.get("has_technical_docs", "")
    if has_technical_docs in ["minimal", "partial"]:
        rec_id += 1
        recommendations.append(Recommendation(
            id=f"rec_{rec_id}",
            category="documentation",
            priority=Priority.MEDIUM,
            title="Améliorer la documentation technique",
            description="Investissement Québec exige des preuves solides de l'intégration IA. Votre documentation est insuffisante.",
            expected_impact=5,
            effort_level=EffortLevel.LOW,
            estimated_weeks=4,
            action_items=[
                "Documenter l'architecture de vos systèmes IA",
                "Créer des fiches techniques pour chaque modèle ML",
                "Documenter les datasets utilisés pour l'entraînement",
                "Mesurer et documenter les métriques de performance IA",
            ]
        ))

    time_tracking = responses.get("time_tracking_system", "")
    if time_tracking == "none":
        rec_id += 1
        recommendations.append(Recommendation(
            id=f"rec_{rec_id}",
            category="documentation",
            priority=Priority.HIGH,
            title="Implémenter un système de suivi du temps",
            description="Sans suivi du temps, vous ne pouvez pas prouver que 75% du temps est sur des activités IA.",
            expected_impact=15,
            effort_level=EffortLevel.LOW,
            estimated_weeks=2,
            action_items=[
                "Choisir un outil (Toggl, Clockify, Harvest, Jira Time)",
                "Définir les catégories d'activités (qualifiantes vs non-qualifiantes)",
                "Former les employés au suivi du temps",
                "Implémenter des rapports mensuels",
            ]
        ))
    elif time_tracking == "basic":
        rec_id += 1
        recommendations.append(Recommendation(
            id=f"rec_{rec_id}",
            category="documentation",
            priority=Priority.MEDIUM,
            title="Améliorer le suivi du temps avec des catégories",
            description="Votre suivi du temps est basique. Ajoutez des catégories pour distinguer les activités IA.",
            expected_impact=5,
            effort_level=EffortLevel.LOW,
            estimated_weeks=2,
            action_items=[
                "Ajouter des catégories: Développement IA, Intégration IA, Maintenance, Support, Admin",
                "Former les employés aux nouvelles catégories",
                "Générer des rapports par catégorie",
            ]
        ))

    return recommendations


# =============================================================================
# EXPORT ET UTILITAIRES
# =============================================================================

def result_to_dict(result: ScoringResult) -> Dict:
    """Convertit le résultat en dictionnaire pour JSON/export."""
    return {
        "total_score": result.total_score,
        "max_score": result.max_score,
        "percentage": result.percentage,
        "eligibility_status": result.eligibility_status.value,
        "status_message": result.status_message,
        "score_breakdown": [
            {
                "criterion": s.criterion,
                "score": s.score,
                "max_score": s.max_score,
                "status": s.status,
                "details": s.details,
            }
            for s in result.score_breakdown
        ],
        "credit_current": {
            "eligible_employees": result.credit_current.eligible_employees if result.credit_current else 0,
            "total_credit": result.credit_current.total_credit if result.credit_current else 0,
        } if result.credit_current else None,
        "credit_optimized": {
            "eligible_employees": result.credit_optimized.eligible_employees if result.credit_optimized else 0,
            "total_credit": result.credit_optimized.total_credit if result.credit_optimized else 0,
        } if result.credit_optimized else None,
        "credit_gain": result.credit_gain,
        "critical_issues": result.critical_issues,
        "warnings": result.warnings,
        "recommendations": [
            {
                "id": r.id,
                "priority": r.priority.value,
                "title": r.title,
                "description": r.description,
                "expected_impact": r.expected_impact,
                "effort_level": r.effort_level.value,
                "estimated_weeks": r.estimated_weeks,
                "action_items": r.action_items,
            }
            for r in result.recommendations
        ],
    }


if __name__ == "__main__":
    # Test avec des données exemple
    test_responses = {
        "company_name": "TechCo Inc.",
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

    print(f"\n{'='*60}")
    print(f"DIAGNOSTIC CDAEIA - {result.company_name}")
    print(f"{'='*60}")
    print(f"\nScore: {result.total_score}/{result.max_score} ({result.percentage:.1f}%)")
    print(f"Statut: {result.eligibility_status.value.upper()}")
    print(f"\n{result.status_message}")

    print(f"\n{'─'*60}")
    print("DÉTAIL DES SCORES")
    print(f"{'─'*60}")
    for s in result.score_breakdown:
        status_icon = "✓" if s.status == "pass" else "⚠" if s.status == "warning" else "✗"
        print(f"{status_icon} {s.criterion}: {s.score}/{s.max_score}")
        print(f"   {s.details}")

    if result.credit_current:
        print(f"\n{'─'*60}")
        print("CRÉDIT ESTIMÉ")
        print(f"{'─'*60}")
        print(f"Situation actuelle: {result.credit_current.total_credit:,.0f}$ ({result.credit_current.eligible_employees} employés)")
        if result.credit_optimized:
            print(f"Après optimisation: {result.credit_optimized.total_credit:,.0f}$ ({result.credit_optimized.eligible_employees} employés)")
            print(f"Gain potentiel: +{result.credit_gain:,.0f}$")

    if result.critical_issues:
        print(f"\n{'─'*60}")
        print("PROBLÈMES CRITIQUES")
        print(f"{'─'*60}")
        for issue in result.critical_issues:
            print(f"❌ {issue}")

    if result.recommendations:
        print(f"\n{'─'*60}")
        print("RECOMMANDATIONS")
        print(f"{'─'*60}")
        for rec in result.recommendations[:5]:  # Top 5
            priority_icon = "🔴" if rec.priority == Priority.HIGH else "🟡" if rec.priority == Priority.MEDIUM else "🟢"
            print(f"\n{priority_icon} {rec.title}")
            print(f"   Impact: +{rec.expected_impact} points | Effort: {rec.effort_level.value} | Délai: {rec.estimated_weeks} semaines")
