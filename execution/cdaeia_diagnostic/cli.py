#!/usr/bin/env python3
"""
CDAEIA Diagnostic Tool - Interface en Ligne de Commande
========================================================

Permet d'exécuter un diagnostic CDAEIA depuis le terminal.

Usage:
    python cli.py                    # Mode interactif
    python cli.py --input data.json  # Depuis un fichier JSON
    python cli.py --demo             # Démonstration avec données test
"""

import argparse
import json
import os
import sys
from datetime import datetime

# Fix encoding pour Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from scoring_engine import calculate_score, EligibilityStatus, Priority
from report_generator import (
    generate_markdown_report,
    generate_executive_summary,
    generate_action_plan,
    save_report,
)
from questionnaire import QUESTIONNAIRE_SECTIONS, QuestionType


def print_header():
    """Affiche l'en-tête du programme."""
    print("\n" + "=" * 60)
    print("   CDAEIA DIAGNOSTIC TOOL")
    print("   Ran.AI Agency - Experts en transformation IA")
    print("=" * 60)


def print_section_header(title: str):
    """Affiche un en-tête de section."""
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}\n")


def run_interactive_questionnaire() -> dict:
    """
    Exécute le questionnaire en mode interactif.
    """
    responses = {}

    print_header()
    print("\nBienvenue dans l'outil de diagnostic CDAEIA!")
    print("Répondez aux questions suivantes pour évaluer votre éligibilité.\n")

    for section_id, section in QUESTIONNAIRE_SECTIONS.items():
        print_section_header(f"SECTION: {section['title']}")
        print(f"{section['description']}\n")

        for question in section["questions"]:
            # Vérifier les conditions
            if question.conditional:
                cond_field = question.conditional.get("field")
                cond_value = question.conditional.get("value")
                if responses.get(cond_field) != cond_value:
                    continue

            # Afficher la question
            print(f"\n📌 {question.text}")
            if question.help_text:
                print(f"   ℹ️  {question.help_text}")

            # Collecter la réponse selon le type
            if question.type == QuestionType.BOOLEAN:
                while True:
                    answer = input("   (oui/non): ").strip().lower()
                    if answer in ["oui", "o", "yes", "y", "1", "true"]:
                        responses[question.id] = True
                        break
                    elif answer in ["non", "n", "no", "0", "false"]:
                        responses[question.id] = False
                        break
                    elif answer == "" and not question.required:
                        responses[question.id] = None
                        break
                    print("   ⚠️  Répondez par 'oui' ou 'non'")

            elif question.type == QuestionType.SELECT:
                print("   Options:")
                for i, opt in enumerate(question.options, 1):
                    print(f"   {i}. {opt.label}")
                    if opt.description:
                        print(f"      ({opt.description})")

                while True:
                    answer = input("   Choix (numéro): ").strip()
                    if answer == "" and not question.required:
                        responses[question.id] = None
                        break
                    try:
                        idx = int(answer) - 1
                        if 0 <= idx < len(question.options):
                            responses[question.id] = question.options[idx].value
                            break
                    except ValueError:
                        pass
                    print(f"   ⚠️  Entrez un numéro entre 1 et {len(question.options)}")

            elif question.type == QuestionType.MULTI_SELECT:
                print("   Options (entrez les numéros séparés par des virgules):")
                for i, opt in enumerate(question.options, 1):
                    print(f"   {i}. {opt.label}")

                while True:
                    answer = input("   Choix: ").strip()
                    if answer == "" and not question.required:
                        responses[question.id] = []
                        break

                    try:
                        indices = [int(x.strip()) - 1 for x in answer.split(",")]
                        if all(0 <= idx < len(question.options) for idx in indices):
                            responses[question.id] = [question.options[idx].value for idx in indices]
                            break
                    except ValueError:
                        pass
                    print("   ⚠️  Entrez des numéros séparés par des virgules")

            elif question.type in [QuestionType.NUMBER, QuestionType.CURRENCY, QuestionType.PERCENTAGE]:
                while True:
                    prompt = "   Valeur"
                    if question.type == QuestionType.CURRENCY:
                        prompt += " ($)"
                    elif question.type == QuestionType.PERCENTAGE:
                        prompt += " (%)"
                    prompt += ": "

                    answer = input(prompt).strip().replace("$", "").replace(",", "").replace("%", "")

                    if answer == "" and not question.required:
                        responses[question.id] = None
                        break

                    try:
                        value = float(answer)

                        # Validation
                        if question.validation:
                            if "min" in question.validation and value < question.validation["min"]:
                                print(f"   ⚠️  La valeur doit être au moins {question.validation['min']}")
                                continue
                            if "max" in question.validation and value > question.validation["max"]:
                                print(f"   ⚠️  La valeur doit être au maximum {question.validation['max']}")
                                continue

                        responses[question.id] = value
                        break
                    except ValueError:
                        print("   ⚠️  Entrez un nombre valide")

            else:  # TEXT, DATE, etc.
                answer = input("   Réponse: ").strip()
                if answer == "" and not question.required:
                    responses[question.id] = None
                else:
                    responses[question.id] = answer

        print(f"\n✅ Section '{section['title']}' complétée!")

    return responses


def display_results(result, responses: dict):
    """Affiche les résultats du diagnostic."""
    print_header()
    print_section_header(f"RÉSULTATS - {responses.get('company_name', 'Entreprise')}")

    # Score global
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

    icon = status_icons.get(result.eligibility_status, "❓")
    label = status_labels.get(result.eligibility_status, "INCONNU")

    print(f"  SCORE: {result.total_score}/{result.max_score} ({result.percentage:.1f}%)")
    print(f"  STATUT: {icon} {label}")
    print(f"\n  {result.status_message}")

    # Détail des scores
    print_section_header("DÉTAIL DES SCORES")
    for breakdown in result.score_breakdown:
        status_char = "✓" if breakdown.status == "pass" else "⚠" if breakdown.status == "warning" else "✗"
        bar_filled = int((breakdown.score / breakdown.max_score) * 20) if breakdown.max_score > 0 else 0
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        print(f"  {status_char} {breakdown.criterion}: {breakdown.score}/{breakdown.max_score}")
        print(f"    [{bar}]")
        print(f"    {breakdown.details}\n")

    # Crédit estimé
    if result.credit_current:
        print_section_header("CRÉDIT CDAEIA ESTIMÉ")
        print(f"  Situation actuelle:")
        print(f"    • Employés éligibles: {result.credit_current.eligible_employees}")
        print(f"    • Crédit annuel: {result.credit_current.total_credit:,.0f}$")

        if result.credit_optimized and result.credit_gain > 0:
            print(f"\n  Après optimisation:")
            print(f"    • Employés éligibles: {result.credit_optimized.eligible_employees}")
            print(f"    • Crédit annuel: {result.credit_optimized.total_credit:,.0f}$")
            print(f"\n  💰 GAIN POTENTIEL: +{result.credit_gain:,.0f}$/an")

    # Problèmes critiques
    if result.critical_issues:
        print_section_header("⚠️ PROBLÈMES CRITIQUES")
        for issue in result.critical_issues:
            print(f"  ❌ {issue}")

    # Top 5 recommandations
    if result.recommendations:
        print_section_header("TOP 5 RECOMMANDATIONS")
        for i, rec in enumerate(result.recommendations[:5], 1):
            priority_icon = "🔴" if rec.priority == Priority.HIGH else "🟡" if rec.priority == Priority.MEDIUM else "🟢"
            print(f"  {i}. {priority_icon} {rec.title}")
            print(f"     Impact: +{rec.expected_impact} pts | Effort: {rec.effort_level.value} | Délai: {rec.estimated_weeks} sem.")
            print()


def save_all_reports(result, responses: dict, output_dir: str = ".tmp"):
    """Sauvegarde tous les rapports."""
    os.makedirs(output_dir, exist_ok=True)

    company_slug = responses.get("company_name", "entreprise").lower().replace(" ", "_")[:20]
    date_str = datetime.now().strftime("%Y%m%d")

    # Rapport complet
    report = generate_markdown_report(result, responses)
    report_path = os.path.join(output_dir, f"diagnostic_cdaeia_{company_slug}_{date_str}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  📄 Rapport complet: {report_path}")

    # Sommaire exécutif
    summary = generate_executive_summary(result, responses)
    summary_path = os.path.join(output_dir, f"sommaire_{company_slug}_{date_str}.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"  📄 Sommaire exécutif: {summary_path}")

    # Plan d'action
    action_plan = generate_action_plan(result)
    action_path = os.path.join(output_dir, f"plan_action_{company_slug}_{date_str}.md")
    with open(action_path, "w", encoding="utf-8") as f:
        f.write(action_plan)
    print(f"  📄 Plan d'action: {action_path}")

    # Données JSON
    from scoring_engine import result_to_dict
    data = {
        "responses": responses,
        "result": result_to_dict(result),
        "generated_at": datetime.now().isoformat(),
    }
    json_path = os.path.join(output_dir, f"diagnostic_data_{company_slug}_{date_str}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  📄 Données JSON: {json_path}")

    return {
        "report": report_path,
        "summary": summary_path,
        "action_plan": action_path,
        "json": json_path,
    }


def run_demo():
    """Exécute une démonstration avec des données test."""
    demo_responses = {
        "company_name": "TechCo Demo Inc.",
        "company_neq": "1234567890",
        "industry": "saas",
        "fiscal_year_end": "2025-12-31",
        "total_employees": 25,
        "is_tax_exempt": False,
        "is_crown_corp": False,
        "is_subsidiary": False,
        "total_revenue": 2000000,
        "it_revenue": 1700000,
        "software_revenue": 800000,
        "system_design_revenue": 400000,
        "data_hosting_revenue": 200000,
        "tech_employees_count": 12,
        "tech_employees_fulltime": 8,
        "total_tech_payroll": 640000,
        "avg_tech_salary": 80000,
        "has_ai_specialists": True,
        "ai_specialists_count": 3,
        "time_tracking_system": "basic",
        "avg_time_ai_dev": 25,
        "avg_time_ai_integration": 20,
        "avg_time_ai_data": 10,
        "avg_time_ai_analytics": 10,
        "avg_time_maintenance": 15,
        "avg_time_support": 10,
        "avg_time_admin": 5,
        "avg_time_dev_legacy": 5,
        "has_ai_products": True,
        "ai_technologies": ["ml_classical", "nlp", "predictive_analytics", "llm"],
        "ai_maturity": "scaling",
        "ai_revenue_percentage": 40,
        "has_technical_docs": "partial",
        "has_model_documentation": True,
        "can_prove_ai_impact": True,
        "has_time_records": "3_5_years",
        "previous_cdae": True,
        "previous_cdae_years": "2022, 2023, 2024",
        "has_iq_attestation": True,
        "audit_readiness": "3",
    }

    return demo_responses


def main():
    parser = argparse.ArgumentParser(
        description="CDAEIA Diagnostic Tool - Évaluez votre éligibilité au crédit d'impôt IA du Québec"
    )
    parser.add_argument(
        "--input", "-i",
        help="Fichier JSON contenant les réponses au questionnaire"
    )
    parser.add_argument(
        "--output", "-o",
        default=".tmp",
        help="Répertoire de sortie pour les rapports (défaut: .tmp)"
    )
    parser.add_argument(
        "--demo", "-d",
        action="store_true",
        help="Exécuter une démonstration avec des données test"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Ne pas sauvegarder les rapports"
    )

    args = parser.parse_args()

    # Collecter les réponses
    if args.demo:
        print_header()
        print("\n🎮 Mode démonstration activé")
        responses = run_demo()
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            responses = json.load(f)
        print_header()
        print(f"\n📂 Données chargées depuis: {args.input}")
    else:
        responses = run_interactive_questionnaire()

    # Calculer le score
    print("\n⏳ Analyse en cours...")
    result = calculate_score(responses)

    # Afficher les résultats
    display_results(result, responses)

    # Sauvegarder les rapports
    if not args.no_save:
        print_section_header("RAPPORTS GÉNÉRÉS")
        save_all_reports(result, responses, args.output)

    print("\n" + "=" * 60)
    print("  Merci d'avoir utilisé CDAEIA Diagnostic Tool!")
    print("  Contact: info@ran-ai-agency.ca | 514-918-1241")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
