"""
CDAEIA Diagnostic Tool
======================

Application pour automatiser le diagnostic d'éligibilité CDAEIA
pour les PME technologiques québécoises.

Modules:
- questionnaire: Questions et validation
- scoring_engine: Calcul des scores et recommandations
- report_generator: Génération des rapports

Usage:
    from cdaeia_diagnostic import run_diagnostic

    responses = {...}  # Réponses au questionnaire
    result = run_diagnostic(responses)
"""

from .questionnaire import (
    QUESTIONNAIRE_SECTIONS,
    get_all_questions,
    get_questions_by_section,
    validate_response,
    Question,
    QuestionType,
)

from .scoring_engine import (
    calculate_score,
    result_to_dict,
    ScoringResult,
    EligibilityStatus,
    Priority,
    Recommendation,
    CreditCalculation,
)

from .report_generator import (
    generate_markdown_report,
    generate_executive_summary,
    generate_action_plan,
    save_report,
)


def run_diagnostic(responses: dict) -> dict:
    """
    Point d'entrée principal pour exécuter un diagnostic CDAEIA complet.

    Args:
        responses: Dictionnaire des réponses au questionnaire

    Returns:
        Dictionnaire contenant:
        - result: Résultat du scoring (ScoringResult)
        - result_dict: Version dictionnaire du résultat
        - report_md: Rapport complet en Markdown
        - summary_md: Sommaire exécutif en Markdown
        - action_plan_md: Plan d'action en Markdown
    """
    # Calculer le score
    result = calculate_score(responses)

    # Générer les rapports
    report_md = generate_markdown_report(result, responses)
    summary_md = generate_executive_summary(result, responses)
    action_plan_md = generate_action_plan(result)

    return {
        "result": result,
        "result_dict": result_to_dict(result),
        "report_md": report_md,
        "summary_md": summary_md,
        "action_plan_md": action_plan_md,
    }


__version__ = "1.0.0"
__author__ = "Ran.AI Agency"
