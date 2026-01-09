"""
CDAEIA Diagnostic Tool - Questionnaire d'Évaluation
====================================================

Ce module contient toutes les questions du diagnostic CDAEIA
organisées par section, avec leurs règles de validation et scoring.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class QuestionType(Enum):
    TEXT = "text"
    NUMBER = "number"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    BOOLEAN = "boolean"
    DATE = "date"
    EMPLOYEE_LIST = "employee_list"
    PROJECT_LIST = "project_list"


@dataclass
class Option:
    value: str
    label: str
    description: Optional[str] = None


@dataclass
class Question:
    id: str
    section: str
    text: str
    type: QuestionType
    required: bool = True
    help_text: Optional[str] = None
    options: List[Option] = field(default_factory=list)
    validation: Optional[Dict[str, Any]] = None
    conditional: Optional[Dict[str, Any]] = None  # Afficher si condition remplie
    scoring_weight: int = 0  # Poids dans le score final


# =============================================================================
# SECTION 1: PROFIL DE L'ENTREPRISE
# =============================================================================

SECTION_1_PROFIL = [
    Question(
        id="company_name",
        section="profil",
        text="Quel est le nom légal de votre entreprise?",
        type=QuestionType.TEXT,
        required=True,
    ),
    Question(
        id="company_neq",
        section="profil",
        text="Quel est votre NEQ (Numéro d'entreprise du Québec)?",
        type=QuestionType.TEXT,
        required=False,
        help_text="Format: 10 chiffres (ex: 1234567890)",
        validation={"pattern": r"^\d{10}$"}
    ),
    Question(
        id="company_address",
        section="profil",
        text="Quelle est l'adresse de votre établissement principal au Québec?",
        type=QuestionType.TEXT,
        required=True,
    ),
    Question(
        id="fiscal_year_end",
        section="profil",
        text="Quelle est la date de fin de votre exercice financier?",
        type=QuestionType.DATE,
        required=True,
        help_text="Format: AAAA-MM-JJ",
    ),
    Question(
        id="industry",
        section="profil",
        text="Dans quel secteur d'activité principal opérez-vous?",
        type=QuestionType.SELECT,
        required=True,
        options=[
            Option("saas", "SaaS / Logiciel en tant que service"),
            Option("software_dev", "Développement de logiciels"),
            Option("it_consulting", "Consultation en TI"),
            Option("data_analytics", "Analyse de données / BI"),
            Option("cybersecurity", "Cybersécurité"),
            Option("fintech", "FinTech"),
            Option("healthtech", "HealthTech"),
            Option("ai_ml", "Intelligence artificielle / ML"),
            Option("cloud_services", "Services cloud / Infrastructure"),
            Option("ecommerce_tech", "Technologies e-commerce"),
            Option("other_tech", "Autre (secteur technologique)"),
            Option("other_non_tech", "Autre (secteur non-technologique)"),
        ]
    ),
    Question(
        id="year_founded",
        section="profil",
        text="En quelle année votre entreprise a-t-elle été fondée?",
        type=QuestionType.NUMBER,
        required=False,
        validation={"min": 1900, "max": 2026}
    ),
    Question(
        id="total_employees",
        section="profil",
        text="Combien d'employés compte votre entreprise au total?",
        type=QuestionType.NUMBER,
        required=True,
        validation={"min": 1},
        help_text="Incluez tous les employés, temps plein et temps partiel."
    ),
    Question(
        id="is_subsidiary",
        section="profil",
        text="Votre entreprise est-elle une filiale d'une société étrangère?",
        type=QuestionType.BOOLEAN,
        required=True,
        help_text="Important: Les filiales étrangères voient leur crédit réduit de 50%."
    ),
    Question(
        id="is_tax_exempt",
        section="profil",
        text="Votre entreprise est-elle exonérée d'impôt?",
        type=QuestionType.BOOLEAN,
        required=True,
        help_text="Les OBNL et organismes exonérés ne sont pas éligibles au CDAEIA."
    ),
    Question(
        id="is_crown_corp",
        section="profil",
        text="Votre entreprise est-elle une société d'État ou contrôlée par une société d'État?",
        type=QuestionType.BOOLEAN,
        required=True,
    ),
]


# =============================================================================
# SECTION 2: TESTS DE REVENUS
# =============================================================================

SECTION_2_REVENUS = [
    Question(
        id="total_revenue",
        section="revenus",
        text="Quel est votre revenu brut total pour le dernier exercice financier complété?",
        type=QuestionType.CURRENCY,
        required=True,
        validation={"min": 0},
        help_text="Revenus bruts avant déductions, tel qu'indiqué dans vos états financiers."
    ),
    Question(
        id="it_revenue",
        section="revenus",
        text="De ce montant, combien provient d'activités du secteur des technologies de l'information?",
        type=QuestionType.CURRENCY,
        required=True,
        validation={"min": 0},
        help_text="""Inclut:
• Développement de logiciels (sur mesure ou produits)
• Services SaaS et abonnements logiciels
• Consultation en TI
• Intégration de systèmes
• Services cloud et hébergement
• Cybersécurité
• Analyse de données et BI
• Services d'IA/ML
• Support et maintenance TI"""
    ),
    Question(
        id="software_revenue",
        section="revenus",
        text="Combien provient spécifiquement de l'édition de logiciels?",
        type=QuestionType.CURRENCY,
        required=True,
        validation={"min": 0},
        help_text="Inclut: licences logicielles, abonnements SaaS, ventes de produits logiciels."
    ),
    Question(
        id="system_design_revenue",
        section="revenus",
        text="Combien provient de la conception de systèmes informatiques?",
        type=QuestionType.CURRENCY,
        required=True,
        validation={"min": 0},
        help_text="Inclut: développement sur mesure, intégration, architecture de systèmes."
    ),
    Question(
        id="data_hosting_revenue",
        section="revenus",
        text="Combien provient du traitement et de l'hébergement de données?",
        type=QuestionType.CURRENCY,
        required=True,
        validation={"min": 0},
        help_text="Inclut: services cloud, data centers, traitement de données, hébergement."
    ),
    Question(
        id="export_revenue_pct",
        section="revenus",
        text="Quel pourcentage de vos services IT est utilisé à l'extérieur du Québec?",
        type=QuestionType.PERCENTAGE,
        required=False,
        validation={"min": 0, "max": 100},
        help_text="Clients hors Québec (Canada et international)."
    ),
]


# =============================================================================
# SECTION 3: EFFECTIFS
# =============================================================================

SECTION_3_EFFECTIFS = [
    Question(
        id="tech_employees_count",
        section="effectifs",
        text="Combien d'employés travaillent dans des rôles techniques/TI?",
        type=QuestionType.NUMBER,
        required=True,
        validation={"min": 0},
        help_text="Développeurs, analystes, data scientists, ingénieurs, etc."
    ),
    Question(
        id="tech_employees_fulltime",
        section="effectifs",
        text="Parmi ceux-ci, combien sont à temps plein (26h+/semaine, 40+ semaines/an)?",
        type=QuestionType.NUMBER,
        required=True,
        validation={"min": 0},
        help_text="Seuls les employés à temps plein peuvent être éligibles au CDAEIA."
    ),
    Question(
        id="employees_detail",
        section="effectifs",
        text="Veuillez détailler vos employés techniques:",
        type=QuestionType.EMPLOYEE_LIST,
        required=True,
        help_text="""Pour chaque employé, indiquez:
• Titre du poste
• Département
• Temps plein? (Oui/Non)
• Salaire annuel
• Répartition du temps par type d'activité"""
    ),
    Question(
        id="total_tech_payroll",
        section="effectifs",
        text="Quelle est la masse salariale annuelle totale de vos employés techniques?",
        type=QuestionType.CURRENCY,
        required=True,
        validation={"min": 0},
        help_text="Salaires bruts annuels, sans les avantages sociaux."
    ),
    Question(
        id="avg_tech_salary",
        section="effectifs",
        text="Quel est le salaire annuel moyen de vos employés techniques?",
        type=QuestionType.CURRENCY,
        required=True,
        validation={"min": 0},
    ),
    Question(
        id="has_ai_specialists",
        section="effectifs",
        text="Avez-vous des employés spécialisés en IA/ML/Data Science?",
        type=QuestionType.BOOLEAN,
        required=True,
    ),
    Question(
        id="ai_specialists_count",
        section="effectifs",
        text="Combien de spécialistes IA/ML/Data Science avez-vous?",
        type=QuestionType.NUMBER,
        required=True,
        conditional={"field": "has_ai_specialists", "value": True},
        validation={"min": 0},
    ),
]


# =============================================================================
# SECTION 4: ALLOCATION DU TEMPS
# =============================================================================

SECTION_4_TEMPS = [
    Question(
        id="time_tracking_system",
        section="temps",
        text="Avez-vous un système de suivi du temps pour vos employés techniques?",
        type=QuestionType.SELECT,
        required=True,
        options=[
            Option("detailed", "Oui, détaillé par type d'activité", "Ex: Toggl, Harvest, Jira Time"),
            Option("basic", "Oui, mais basique (heures seulement)", "Ex: feuilles de temps simples"),
            Option("none", "Non, pas de suivi formel"),
        ],
        help_text="Important: Le CDAEIA exige de pouvoir prouver l'allocation du temps."
    ),
    Question(
        id="avg_time_ai_dev",
        section="temps",
        text="En moyenne, quel % du temps de vos employés tech est consacré au développement IA?",
        type=QuestionType.PERCENTAGE,
        required=True,
        validation={"min": 0, "max": 100},
        help_text="Création de modèles ML, entraînement, fine-tuning, développement d'algorithmes IA."
    ),
    Question(
        id="avg_time_ai_integration",
        section="temps",
        text="Quel % du temps est consacré à l'intégration de composantes IA?",
        type=QuestionType.PERCENTAGE,
        required=True,
        validation={"min": 0, "max": 100},
        help_text="Intégration d'API ML, déploiement de modèles, MLOps."
    ),
    Question(
        id="avg_time_ai_data",
        section="temps",
        text="Quel % du temps est consacré à la préparation de données pour l'IA?",
        type=QuestionType.PERCENTAGE,
        required=True,
        validation={"min": 0, "max": 100},
        help_text="ETL pour ML, feature engineering, pipelines de données, labeling."
    ),
    Question(
        id="avg_time_ai_analytics",
        section="temps",
        text="Quel % du temps est consacré à l'analytique avancée/prédictive?",
        type=QuestionType.PERCENTAGE,
        required=True,
        validation={"min": 0, "max": 100},
        help_text="Modèles prédictifs, forecasting, analyse statistique avancée."
    ),
    Question(
        id="avg_time_maintenance",
        section="temps",
        text="Quel % du temps est consacré à la maintenance de systèmes?",
        type=QuestionType.PERCENTAGE,
        required=True,
        validation={"min": 0, "max": 100},
        help_text="⚠️ NON ÉLIGIBLE: Corrections de bugs, patches, mises à jour, maintenance."
    ),
    Question(
        id="avg_time_support",
        section="temps",
        text="Quel % du temps est consacré au support technique?",
        type=QuestionType.PERCENTAGE,
        required=True,
        validation={"min": 0, "max": 100},
        help_text="⚠️ NON ÉLIGIBLE: Helpdesk, troubleshooting, support client."
    ),
    Question(
        id="avg_time_admin",
        section="temps",
        text="Quel % du temps est consacré à l'administration/réunions?",
        type=QuestionType.PERCENTAGE,
        required=True,
        validation={"min": 0, "max": 100},
        help_text="⚠️ NON ÉLIGIBLE: Réunions, emails, documentation non-technique."
    ),
    Question(
        id="avg_time_dev_legacy",
        section="temps",
        text="Quel % du temps est consacré au développement sans composante IA?",
        type=QuestionType.PERCENTAGE,
        required=True,
        validation={"min": 0, "max": 100},
        help_text="⚠️ NON ÉLIGIBLE: Développement de fonctionnalités sans intégration IA."
    ),
]


# =============================================================================
# SECTION 5: INTÉGRATION IA
# =============================================================================

SECTION_5_IA = [
    Question(
        id="has_ai_products",
        section="ia",
        text="Avez-vous des produits ou services qui intègrent de l'intelligence artificielle?",
        type=QuestionType.BOOLEAN,
        required=True,
    ),
    Question(
        id="ai_technologies",
        section="ia",
        text="Quelles technologies IA utilisez-vous?",
        type=QuestionType.MULTI_SELECT,
        required=True,
        conditional={"field": "has_ai_products", "value": True},
        options=[
            Option("ml_classical", "Machine Learning classique", "Régression, classification, clustering"),
            Option("deep_learning", "Deep Learning / Réseaux neuronaux", "CNN, RNN, Transformers"),
            Option("nlp", "NLP (Traitement du langage naturel)", "Analyse de texte, chatbots, extraction"),
            Option("computer_vision", "Computer Vision", "Reconnaissance d'images, OCR, détection"),
            Option("predictive_analytics", "Analytique prédictive", "Forecasting, scoring, recommandations"),
            Option("llm", "LLM / IA générative", "GPT, Claude, génération de contenu"),
            Option("speech", "Reconnaissance vocale / TTS", "Speech-to-text, Text-to-speech"),
            Option("recommendation", "Systèmes de recommandation", "Personnalisation, suggestions"),
            Option("automation", "Automatisation intelligente", "RPA avec prise de décision IA"),
            Option("anomaly_detection", "Détection d'anomalies", "Fraude, cybersécurité, maintenance prédictive"),
        ]
    ),
    Question(
        id="ai_projects",
        section="ia",
        text="Décrivez vos projets/produits qui intègrent de l'IA:",
        type=QuestionType.PROJECT_LIST,
        required=True,
        conditional={"field": "has_ai_products", "value": True},
        help_text="""Pour chaque projet, indiquez:
• Nom du projet/produit
• Description
• Technologies IA utilisées
• Est-ce en production?
• % des revenus associés
• Niveau d'intégration IA (superficiel/modéré/substantiel)"""
    ),
    Question(
        id="ai_maturity",
        section="ia",
        text="Comment décririez-vous la maturité de vos initiatives IA?",
        type=QuestionType.SELECT,
        required=True,
        options=[
            Option("experimental", "Expérimental", "POC, tests, exploration"),
            Option("pilot", "Pilote", "Projets limités en production"),
            Option("scaling", "En expansion", "Plusieurs projets IA en production"),
            Option("mature", "Mature", "IA intégrée dans les opérations principales"),
            Option("ai_first", "IA-native", "L'IA est au coeur de notre proposition de valeur"),
        ]
    ),
    Question(
        id="ai_revenue_percentage",
        section="ia",
        text="Quel pourcentage de vos revenus provient de produits/services intégrant l'IA?",
        type=QuestionType.PERCENTAGE,
        required=True,
        validation={"min": 0, "max": 100},
    ),
    Question(
        id="ai_development_approach",
        section="ia",
        text="Comment développez-vous vos solutions IA?",
        type=QuestionType.MULTI_SELECT,
        required=True,
        options=[
            Option("internal", "Développement interne", "Équipe interne de data scientists/ML engineers"),
            Option("api", "APIs tierces", "OpenAI, Claude, Google AI, AWS ML"),
            Option("opensource", "Modèles open source", "Hugging Face, PyTorch, TensorFlow"),
            Option("vendor", "Solutions vendeurs", "Salesforce Einstein, MS Azure AI"),
            Option("outsourced", "Sous-traitance", "Partenaires externes pour le développement IA"),
        ]
    ),
]


# =============================================================================
# SECTION 6: DOCUMENTATION ET PRÉPARATION
# =============================================================================

SECTION_6_DOCUMENTATION = [
    Question(
        id="has_technical_docs",
        section="documentation",
        text="Avez-vous une documentation technique de vos projets IA?",
        type=QuestionType.SELECT,
        required=True,
        options=[
            Option("comprehensive", "Complète", "Architecture, modèles, datasets, métriques"),
            Option("partial", "Partielle", "Quelques documents, pas systématique"),
            Option("minimal", "Minimale", "Peu ou pas de documentation"),
        ]
    ),
    Question(
        id="has_model_documentation",
        section="documentation",
        text="Vos modèles IA sont-ils documentés (algorithmes, données d'entraînement, performance)?",
        type=QuestionType.BOOLEAN,
        required=True,
        help_text="Investissement Québec demande des preuves que l'IA est substantielle."
    ),
    Question(
        id="can_prove_ai_impact",
        section="documentation",
        text="Pouvez-vous démontrer l'impact mesurable de l'IA sur vos produits/services?",
        type=QuestionType.BOOLEAN,
        required=True,
        help_text="Ex: amélioration de performance, automatisation de tâches, personnalisation."
    ),
    Question(
        id="has_time_records",
        section="documentation",
        text="Conservez-vous des historiques de feuilles de temps pour vos employés?",
        type=QuestionType.SELECT,
        required=True,
        options=[
            Option("6_years_plus", "Oui, 6 ans ou plus"),
            Option("3_5_years", "Oui, 3-5 ans"),
            Option("1_2_years", "Oui, 1-2 ans"),
            Option("none", "Non, pas d'historique"),
        ],
        help_text="Les données doivent être conservées au moins 6 ans pour audit."
    ),
    Question(
        id="previous_cdae",
        section="documentation",
        text="Avez-vous déjà réclamé le crédit CDAE par le passé?",
        type=QuestionType.BOOLEAN,
        required=True,
    ),
    Question(
        id="previous_cdae_years",
        section="documentation",
        text="Pour quelles années avez-vous réclamé le CDAE?",
        type=QuestionType.TEXT,
        required=False,
        conditional={"field": "previous_cdae", "value": True},
        help_text="Ex: 2022, 2023, 2024"
    ),
    Question(
        id="has_iq_attestation",
        section="documentation",
        text="Avez-vous déjà obtenu des attestations d'Investissement Québec?",
        type=QuestionType.BOOLEAN,
        required=True,
    ),
    Question(
        id="audit_readiness",
        section="documentation",
        text="Sur une échelle de 1 à 5, comment évaluez-vous votre préparation à un audit?",
        type=QuestionType.SELECT,
        required=True,
        options=[
            Option("1", "1 - Pas prêt", "Documentation insuffisante, processus non établis"),
            Option("2", "2 - Peu prêt", "Quelques éléments en place, beaucoup à faire"),
            Option("3", "3 - Moyennement prêt", "Base correcte, améliorations nécessaires"),
            Option("4", "4 - Bien prêt", "Bonne documentation, processus établis"),
            Option("5", "5 - Très prêt", "Documentation complète, processus rigoureux"),
        ]
    ),
]


# =============================================================================
# QUESTIONNAIRE COMPLET
# =============================================================================

QUESTIONNAIRE_SECTIONS = {
    "profil": {
        "title": "Profil de l'Entreprise",
        "description": "Informations générales sur votre entreprise",
        "questions": SECTION_1_PROFIL,
        "icon": "building",
    },
    "revenus": {
        "title": "Tests de Revenus",
        "description": "Analyse de la structure de vos revenus (tests 75% et 50%)",
        "questions": SECTION_2_REVENUS,
        "icon": "dollar-sign",
    },
    "effectifs": {
        "title": "Effectifs",
        "description": "Détail de vos employés techniques",
        "questions": SECTION_3_EFFECTIFS,
        "icon": "users",
    },
    "temps": {
        "title": "Allocation du Temps",
        "description": "Répartition du temps de travail par type d'activité",
        "questions": SECTION_4_TEMPS,
        "icon": "clock",
    },
    "ia": {
        "title": "Intégration IA",
        "description": "Évaluation de vos composantes d'intelligence artificielle",
        "questions": SECTION_5_IA,
        "icon": "cpu",
    },
    "documentation": {
        "title": "Documentation et Préparation",
        "description": "État de votre documentation et préparation aux audits",
        "questions": SECTION_6_DOCUMENTATION,
        "icon": "file-text",
    },
}


def get_all_questions() -> List[Question]:
    """Retourne toutes les questions du questionnaire."""
    all_questions = []
    for section in QUESTIONNAIRE_SECTIONS.values():
        all_questions.extend(section["questions"])
    return all_questions


def get_questions_by_section(section_id: str) -> List[Question]:
    """Retourne les questions d'une section spécifique."""
    section = QUESTIONNAIRE_SECTIONS.get(section_id)
    if section:
        return section["questions"]
    return []


def validate_response(question: Question, value: Any) -> tuple[bool, Optional[str]]:
    """
    Valide une réponse à une question.
    Retourne (is_valid, error_message).
    """
    # Vérification required
    if question.required and (value is None or value == ""):
        return False, "Ce champ est obligatoire."

    if value is None or value == "":
        return True, None  # Champ optionnel vide = OK

    # Validation par type
    if question.type == QuestionType.NUMBER:
        try:
            num_value = float(value)
            if question.validation:
                if "min" in question.validation and num_value < question.validation["min"]:
                    return False, f"La valeur doit être au moins {question.validation['min']}."
                if "max" in question.validation and num_value > question.validation["max"]:
                    return False, f"La valeur doit être au maximum {question.validation['max']}."
        except ValueError:
            return False, "Veuillez entrer un nombre valide."

    elif question.type == QuestionType.PERCENTAGE:
        try:
            pct_value = float(value)
            if pct_value < 0 or pct_value > 100:
                return False, "Le pourcentage doit être entre 0 et 100."
        except ValueError:
            return False, "Veuillez entrer un pourcentage valide."

    elif question.type == QuestionType.CURRENCY:
        try:
            float(value)
        except ValueError:
            return False, "Veuillez entrer un montant valide."

    elif question.type == QuestionType.SELECT:
        valid_values = [opt.value for opt in question.options]
        if value not in valid_values:
            return False, "Veuillez sélectionner une option valide."

    elif question.type == QuestionType.MULTI_SELECT:
        if isinstance(value, list):
            valid_values = [opt.value for opt in question.options]
            for v in value:
                if v not in valid_values:
                    return False, f"Option invalide: {v}"

    return True, None


# =============================================================================
# EMPLOYEE TEMPLATE
# =============================================================================

EMPLOYEE_TEMPLATE = {
    "job_title": "",
    "department": "",
    "is_full_time": True,
    "annual_salary": 0,
    "time_allocation": {
        "ai_dev": 0,           # Développement IA (qualifiant)
        "ai_integration": 0,   # Intégration IA (qualifiant)
        "ai_data": 0,          # Données pour IA (qualifiant)
        "ai_analytics": 0,     # Analytique avancée (qualifiant)
        "maintenance": 0,      # Maintenance (NON qualifiant)
        "support": 0,          # Support (NON qualifiant)
        "admin": 0,            # Admin (NON qualifiant)
        "dev_legacy": 0,       # Dev sans IA (NON qualifiant)
        "other": 0,            # Autre
    }
}


# =============================================================================
# PROJECT TEMPLATE
# =============================================================================

PROJECT_TEMPLATE = {
    "name": "",
    "description": "",
    "technologies": [],  # Liste des technologies IA
    "is_in_production": False,
    "revenue_percentage": 0,
    "ai_integration_level": "none",  # none, superficial, moderate, substantial
}


if __name__ == "__main__":
    # Test: afficher le nombre de questions
    all_questions = get_all_questions()
    print(f"Total de questions: {len(all_questions)}")

    for section_id, section in QUESTIONNAIRE_SECTIONS.items():
        print(f"\n{section['title']}: {len(section['questions'])} questions")
