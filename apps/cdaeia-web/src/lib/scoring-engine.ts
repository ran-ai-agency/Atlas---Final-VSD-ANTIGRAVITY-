// Moteur de scoring CDAEIA (port TypeScript)
import {
  DiagnosticResult,
  DiagnosticResponses,
  ScoreBreakdown,
  CreditCalculation,
  Recommendation,
  EligibilityStatus,
  Priority,
  EffortLevel,
} from './cdaeia-types';

// Constantes CDAEIA
const EXCLUSION_THRESHOLD_2025 = 18571;

const CREDIT_RATES: Record<number, { refundable: number; nonRefundable: number; total: number }> = {
  2025: { refundable: 0.23, nonRefundable: 0.07, total: 0.30 },
  2026: { refundable: 0.22, nonRefundable: 0.08, total: 0.30 },
  2027: { refundable: 0.21, nonRefundable: 0.09, total: 0.30 },
  2028: { refundable: 0.20, nonRefundable: 0.10, total: 0.30 },
};

const SCORE_WEIGHTS = {
  revenue_75: 20,
  revenue_50: 20,
  employees: 15,
  time_allocation: 25,
  ai_integration: 20,
};

export function calculateScore(responses: DiagnosticResponses): DiagnosticResult {
  const result: DiagnosticResult = {
    totalScore: 0,
    maxScore: 100,
    percentage: 0,
    eligibilityStatus: 'not_eligible',
    statusMessage: '',
    scoreBreakdown: [],
    creditCurrent: null,
    creditOptimized: null,
    creditGain: 0,
    criticalIssues: [],
    warnings: [],
    recommendations: [],
  };

  // Vérifications préliminaires
  if (responses.is_tax_exempt === true) {
    result.criticalIssues.push('Les entreprises exonérées d\'impôt ne sont pas éligibles au CDAEIA.');
    result.statusMessage = 'Non éligible - Entreprise exonérée d\'impôt';
    return result;
  }

  if (responses.is_crown_corp === true) {
    result.criticalIssues.push('Les sociétés d\'État ne sont pas éligibles au CDAEIA.');
    result.statusMessage = 'Non éligible - Société d\'État';
    return result;
  }

  // Évaluer chaque critère
  result.scoreBreakdown.push(evaluateRevenue75(responses, result));
  result.scoreBreakdown.push(evaluateRevenue50(responses, result));
  result.scoreBreakdown.push(evaluateEmployees(responses, result));
  result.scoreBreakdown.push(evaluateTimeAllocation(responses, result));
  result.scoreBreakdown.push(evaluateAIIntegration(responses, result));

  // Calcul du score total
  result.totalScore = result.scoreBreakdown.reduce((sum, s) => sum + s.score, 0);
  result.percentage = (result.totalScore / result.maxScore) * 100;

  // Déterminer le statut
  result.eligibilityStatus = determineEligibilityStatus(result);
  result.statusMessage = getStatusMessage(result);

  // Calculer le crédit
  result.creditCurrent = calculateCredit(responses, false);
  result.creditOptimized = calculateCredit(responses, true);
  if (result.creditCurrent && result.creditOptimized) {
    result.creditGain = result.creditOptimized.totalCredit - result.creditCurrent.totalCredit;
  }

  // Générer les recommandations
  result.recommendations = generateRecommendations(responses, result);

  return result;
}

function evaluateRevenue75(responses: DiagnosticResponses, result: DiagnosticResult): ScoreBreakdown {
  const totalRevenue = (responses.total_revenue as number) || 0;
  const itRevenue = (responses.it_revenue as number) || 0;

  if (totalRevenue === 0) {
    return {
      criterion: 'Test 75% Revenus IT',
      score: 0,
      maxScore: SCORE_WEIGHTS.revenue_75,
      status: 'fail',
      details: 'Revenus non renseignés',
      value: 0,
    };
  }

  const percentage = (itRevenue / totalRevenue) * 100;
  let score: number;
  let status: 'pass' | 'warning' | 'fail';
  let details: string;

  if (percentage >= 75) {
    score = SCORE_WEIGHTS.revenue_75;
    status = 'pass';
    details = `${percentage.toFixed(1)}% des revenus proviennent du secteur IT (≥75% requis)`;
  } else if (percentage >= 70) {
    score = Math.floor(SCORE_WEIGHTS.revenue_75 * 0.75);
    status = 'warning';
    details = `${percentage.toFixed(1)}% des revenus IT - Proche du seuil de 75%`;
    result.warnings.push(`Revenus IT à ${percentage.toFixed(1)}%, légèrement sous le seuil de 75%.`);
  } else if (percentage >= 60) {
    score = Math.floor(SCORE_WEIGHTS.revenue_75 * 0.5);
    status = 'warning';
    details = `${percentage.toFixed(1)}% des revenus IT - En dessous du seuil requis`;
    result.warnings.push(`Revenus IT insuffisants: ${percentage.toFixed(1)}% (75% requis).`);
  } else {
    score = 0;
    status = 'fail';
    details = `Seulement ${percentage.toFixed(1)}% des revenus IT (75% requis)`;
    result.criticalIssues.push(`CRITIQUE: Revenus IT à ${percentage.toFixed(1)}% - Le seuil de 75% n'est pas atteint.`);
  }

  return {
    criterion: 'Test 75% Revenus IT',
    score,
    maxScore: SCORE_WEIGHTS.revenue_75,
    status,
    details,
    value: percentage,
  };
}

function evaluateRevenue50(responses: DiagnosticResponses, result: DiagnosticResult): ScoreBreakdown {
  const totalRevenue = (responses.total_revenue as number) || 0;
  const softwareRevenue = (responses.software_revenue as number) || 0;
  const systemDesignRevenue = (responses.system_design_revenue as number) || 0;
  const dataHostingRevenue = (responses.data_hosting_revenue as number) || 0;

  const subsectorRevenue = softwareRevenue + systemDesignRevenue + dataHostingRevenue;

  if (totalRevenue === 0) {
    return {
      criterion: 'Test 50% Sous-secteurs',
      score: 0,
      maxScore: SCORE_WEIGHTS.revenue_50,
      status: 'fail',
      details: 'Revenus non renseignés',
      value: 0,
    };
  }

  const percentage = (subsectorRevenue / totalRevenue) * 100;
  let score: number;
  let status: 'pass' | 'warning' | 'fail';
  let details: string;

  if (percentage >= 50) {
    score = SCORE_WEIGHTS.revenue_50;
    status = 'pass';
    details = `${percentage.toFixed(1)}% des revenus des sous-secteurs qualifiants (≥50% requis)`;
  } else if (percentage >= 45) {
    score = Math.floor(SCORE_WEIGHTS.revenue_50 * 0.75);
    status = 'warning';
    details = `${percentage.toFixed(1)}% - Proche du seuil de 50%`;
    result.warnings.push(`Revenus sous-secteurs à ${percentage.toFixed(1)}%, légèrement sous 50%.`);
  } else if (percentage >= 40) {
    score = Math.floor(SCORE_WEIGHTS.revenue_50 * 0.5);
    status = 'warning';
    details = `${percentage.toFixed(1)}% - En dessous du seuil requis`;
  } else {
    score = Math.floor(SCORE_WEIGHTS.revenue_50 * 0.25);
    status = 'fail';
    details = `Seulement ${percentage.toFixed(1)}% des sous-secteurs qualifiants`;
    result.criticalIssues.push(`Revenus sous-secteurs insuffisants: ${percentage.toFixed(1)}% (50% requis).`);
  }

  return {
    criterion: 'Test 50% Sous-secteurs',
    score,
    maxScore: SCORE_WEIGHTS.revenue_50,
    status,
    details,
    value: percentage,
  };
}

function evaluateEmployees(responses: DiagnosticResponses, result: DiagnosticResult): ScoreBreakdown {
  const techFulltime = (responses.tech_employees_fulltime as number) || 0;
  const avgQualifyingTime = calculateAvgQualifyingTime(responses);

  let estimatedEligible: number;
  if (avgQualifyingTime >= 75) {
    estimatedEligible = techFulltime;
  } else if (avgQualifyingTime >= 60) {
    estimatedEligible = Math.floor(techFulltime * 0.7);
  } else if (avgQualifyingTime >= 50) {
    estimatedEligible = Math.floor(techFulltime * 0.5);
  } else {
    estimatedEligible = Math.floor(techFulltime * 0.3);
  }

  let score: number;
  let status: 'pass' | 'warning' | 'fail';
  let details: string;

  if (estimatedEligible >= 6) {
    score = SCORE_WEIGHTS.employees;
    status = 'pass';
    details = `${estimatedEligible} employés éligibles estimés (≥6 requis)`;
  } else if (estimatedEligible === 5) {
    score = Math.floor(SCORE_WEIGHTS.employees * 0.67);
    status = 'warning';
    details = '5 employés éligibles estimés - 1 de moins que le minimum';
    result.warnings.push('Seulement 5 employés éligibles estimés (6 requis).');
  } else if (estimatedEligible >= 3) {
    score = Math.floor(SCORE_WEIGHTS.employees * 0.33);
    status = 'warning';
    details = `${estimatedEligible} employés éligibles estimés - Sous le minimum`;
  } else {
    score = 0;
    status = 'fail';
    details = `Seulement ${estimatedEligible} employés éligibles estimés (6 requis)`;
    result.criticalIssues.push(`CRITIQUE: Seulement ${estimatedEligible} employés éligibles (minimum 6 requis).`);
  }

  return {
    criterion: 'Effectifs (min. 6)',
    score,
    maxScore: SCORE_WEIGHTS.employees,
    status,
    details,
    value: estimatedEligible,
  };
}

function evaluateTimeAllocation(responses: DiagnosticResponses, result: DiagnosticResult): ScoreBreakdown {
  const avgQualifying = calculateAvgQualifyingTime(responses);

  let score: number;
  let status: 'pass' | 'warning' | 'fail';
  let details: string;

  if (avgQualifying >= 75) {
    score = SCORE_WEIGHTS.time_allocation;
    status = 'pass';
    details = `${avgQualifying.toFixed(1)}% du temps en moyenne sur activités IA (≥75% requis)`;
  } else if (avgQualifying >= 70) {
    score = Math.floor(SCORE_WEIGHTS.time_allocation * 0.8);
    status = 'warning';
    details = `${avgQualifying.toFixed(1)}% - Proche du seuil de 75%`;
    result.warnings.push(`Temps IA moyen à ${avgQualifying.toFixed(1)}%, légèrement sous 75%.`);
  } else if (avgQualifying >= 60) {
    score = Math.floor(SCORE_WEIGHTS.time_allocation * 0.6);
    status = 'warning';
    details = `${avgQualifying.toFixed(1)}% - Réallocation nécessaire`;
    result.warnings.push(`Temps IA insuffisant: ${avgQualifying.toFixed(1)}% (75% requis).`);
  } else if (avgQualifying >= 50) {
    score = Math.floor(SCORE_WEIGHTS.time_allocation * 0.4);
    status = 'warning';
    details = `${avgQualifying.toFixed(1)}% - Réorganisation significative nécessaire`;
  } else {
    score = Math.floor(SCORE_WEIGHTS.time_allocation * 0.2);
    status = 'fail';
    details = `Seulement ${avgQualifying.toFixed(1)}% du temps sur IA`;
    result.criticalIssues.push(`Temps IA très insuffisant: ${avgQualifying.toFixed(1)}% (75% requis).`);
  }

  return {
    criterion: 'Allocation temps (75%)',
    score,
    maxScore: SCORE_WEIGHTS.time_allocation,
    status,
    details,
    value: avgQualifying,
  };
}

function evaluateAIIntegration(responses: DiagnosticResponses, result: DiagnosticResult): ScoreBreakdown {
  const hasAI = responses.has_ai_products as boolean;
  const aiTechs = (responses.ai_technologies as string[]) || [];
  const aiMaturity = responses.ai_maturity as string;
  const aiRevenuePct = (responses.ai_revenue_percentage as number) || 0;

  if (!hasAI) {
    result.criticalIssues.push('CRITIQUE: Aucune intégration IA déclarée.');
    return {
      criterion: 'Intégration IA',
      score: 0,
      maxScore: SCORE_WEIGHTS.ai_integration,
      status: 'fail',
      details: 'Aucun produit/service intégrant l\'IA',
      value: 0,
    };
  }

  // Score basé sur plusieurs facteurs
  const techScore = Math.min(aiTechs.length * 2, 8);

  const maturityScores: Record<string, number> = {
    ai_first: 8,
    mature: 6,
    scaling: 4,
    pilot: 2,
    experimental: 1,
  };
  const maturityScore = maturityScores[aiMaturity] || 0;

  let revenueScore: number;
  if (aiRevenuePct >= 50) revenueScore = 4;
  else if (aiRevenuePct >= 30) revenueScore = 3;
  else if (aiRevenuePct >= 10) revenueScore = 2;
  else revenueScore = 1;

  const totalAIScore = techScore + maturityScore + revenueScore;
  const score = Math.min(totalAIScore, SCORE_WEIGHTS.ai_integration);

  let status: 'pass' | 'warning' | 'fail';
  let details: string;

  if (score >= 16) {
    status = 'pass';
    details = `Intégration IA substantielle (${aiTechs.length} technologies, maturité: ${aiMaturity})`;
  } else if (score >= 12) {
    status = 'pass';
    details = `Bonne intégration IA (${aiTechs.length} technologies)`;
  } else if (score >= 8) {
    status = 'warning';
    details = 'Intégration IA modérée - Renforcement recommandé';
    result.warnings.push('Intégration IA modérée - Considérez renforcer vos capacités IA.');
  } else {
    status = 'warning';
    details = 'Intégration IA faible ou superficielle';
    result.warnings.push('Intégration IA insuffisante pour qualification CDAEIA.');
  }

  return {
    criterion: 'Intégration IA',
    score,
    maxScore: SCORE_WEIGHTS.ai_integration,
    status,
    details,
    value: { technologies: aiTechs.length, maturity: aiMaturity, revenuePct: aiRevenuePct },
  };
}

function calculateAvgQualifyingTime(responses: DiagnosticResponses): number {
  const timeAIDev = (responses.avg_time_ai_dev as number) || 0;
  const timeAIIntegration = (responses.avg_time_ai_integration as number) || 0;
  const timeAIData = (responses.avg_time_ai_data as number) || 0;
  const timeAIAnalytics = (responses.avg_time_ai_analytics as number) || 0;

  return timeAIDev + timeAIIntegration + timeAIData + timeAIAnalytics;
}

function determineEligibilityStatus(result: DiagnosticResult): EligibilityStatus {
  const hasCriticalIssues = result.criticalIssues.length > 0;

  const revenue75Passed = result.scoreBreakdown.some(
    s => s.criterion === 'Test 75% Revenus IT' && s.status === 'pass'
  );
  const employeesOk = result.scoreBreakdown.some(
    s => s.criterion === 'Effectifs (min. 6)' && s.score >= SCORE_WEIGHTS.employees * 0.5
  );
  const aiOk = result.scoreBreakdown.some(
    s => s.criterion === 'Intégration IA' && s.score >= SCORE_WEIGHTS.ai_integration * 0.5
  );

  if (hasCriticalIssues) {
    return 'not_eligible';
  } else if (result.totalScore >= 80 && revenue75Passed && employeesOk && aiOk) {
    return 'eligible';
  } else if (result.totalScore >= 50 && revenue75Passed) {
    return 'partial';
  } else {
    return 'not_eligible';
  }
}

function getStatusMessage(result: DiagnosticResult): string {
  switch (result.eligibilityStatus) {
    case 'eligible':
      return 'Votre entreprise semble éligible au CDAEIA. Une validation détaillée est recommandée.';
    case 'partial':
      return 'Votre entreprise est partiellement éligible. Des ajustements sont nécessaires pour maximiser le crédit.';
    default:
      return 'Votre entreprise ne semble pas éligible au CDAEIA en l\'état actuel.';
  }
}

function calculateCredit(responses: DiagnosticResponses, optimized: boolean): CreditCalculation {
  const techFulltime = (responses.tech_employees_fulltime as number) || 0;
  const totalPayroll = (responses.total_tech_payroll as number) || 0;
  const avgQualifying = calculateAvgQualifyingTime(responses);

  const year = 2026;
  const rates = CREDIT_RATES[year];

  let eligibleEmployees: number;
  if (optimized) {
    eligibleEmployees = techFulltime;
  } else {
    if (avgQualifying >= 75) eligibleEmployees = techFulltime;
    else if (avgQualifying >= 60) eligibleEmployees = Math.floor(techFulltime * 0.7);
    else if (avgQualifying >= 50) eligibleEmployees = Math.floor(techFulltime * 0.5);
    else eligibleEmployees = Math.floor(techFulltime * 0.3);
  }

  const avgSalary = techFulltime > 0 ? totalPayroll / techFulltime : 0;
  const totalEligibleSalary = eligibleEmployees * avgSalary;
  const exclusionThreshold = eligibleEmployees * EXCLUSION_THRESHOLD_2025;
  const netEligibleSalary = Math.max(0, totalEligibleSalary - exclusionThreshold);

  const refundablePortion = netEligibleSalary * rates.refundable;
  const nonRefundablePortion = netEligibleSalary * rates.nonRefundable;
  const totalCredit = refundablePortion + nonRefundablePortion;

  return {
    eligibleEmployees,
    totalEligibleSalary,
    exclusionThreshold,
    netEligibleSalary,
    creditRate: rates.total,
    refundablePortion,
    nonRefundablePortion,
    totalCredit,
  };
}

function generateRecommendations(responses: DiagnosticResponses, result: DiagnosticResult): Recommendation[] {
  const recommendations: Recommendation[] = [];
  let recId = 0;

  const techFulltime = (responses.tech_employees_fulltime as number) || 0;
  const avgQualifying = calculateAvgQualifyingTime(responses);
  const maintenanceTime = (responses.avg_time_maintenance as number) || 0;
  const aiTechs = (responses.ai_technologies as string[]) || [];
  const aiMaturity = responses.ai_maturity as string;
  const hasTechnicalDocs = responses.has_technical_docs as string;
  const timeTracking = responses.time_tracking_system as string;

  // Recommandations effectifs
  if (techFulltime < 6) {
    recId++;
    recommendations.push({
      id: `rec_${recId}`,
      category: 'employee',
      priority: 'high',
      title: `Recruter ${6 - techFulltime} employé(s) tech supplémentaire(s)`,
      description: `Vous avez ${techFulltime} employés tech. Le CDAEIA exige minimum 6 employés éligibles.`,
      expectedImpact: 15,
      effortLevel: 'medium',
      estimatedWeeks: 8,
      actionItems: [
        'Définir les profils recherchés (privilégier les spécialistes IA/ML)',
        'Publier les offres d\'emploi',
        'Considérer des contractors qui peuvent devenir employés',
      ],
    });
  }

  // Recommandations temps
  if (avgQualifying < 75) {
    recId++;
    const gap = 75 - avgQualifying;
    recommendations.push({
      id: `rec_${recId}`,
      category: 'process',
      priority: 'high',
      title: `Réallouer ${gap.toFixed(0)}% du temps vers des activités IA`,
      description: `Actuellement ${avgQualifying.toFixed(1)}% du temps sur activités IA. Objectif: 75%.`,
      expectedImpact: 25,
      effortLevel: 'medium',
      estimatedWeeks: 4,
      actionItems: [
        'Identifier les employés proches du seuil de 75%',
        'Réduire les tâches de maintenance',
        'Transférer la maintenance vers du support externe',
        'Augmenter les projets de développement IA',
      ],
    });
  }

  if (maintenanceTime > 15) {
    recId++;
    recommendations.push({
      id: `rec_${recId}`,
      category: 'process',
      priority: 'medium',
      title: 'Réduire ou externaliser la maintenance',
      description: `${maintenanceTime}% du temps en maintenance (non éligible CDAEIA).`,
      expectedImpact: 10,
      effortLevel: 'medium',
      estimatedWeeks: 8,
      actionItems: [
        'Identifier les tâches de maintenance récurrentes',
        'Évaluer l\'externalisation',
        'Automatiser les tâches répétitives',
      ],
    });
  }

  // Recommandations IA
  if (aiTechs.length < 2) {
    recId++;
    recommendations.push({
      id: `rec_${recId}`,
      category: 'project',
      priority: 'high',
      title: 'Diversifier les technologies IA',
      description: `${aiTechs.length} technologie(s) IA. Diversifier renforce votre dossier.`,
      expectedImpact: 10,
      effortLevel: 'high',
      estimatedWeeks: 12,
      actionItems: [
        'Intégrer NLP (chatbots, analyse de texte)',
        'Ajouter l\'analytique prédictive',
        'Explorer l\'automatisation intelligente',
        'Évaluer les LLM/IA générative',
      ],
    });
  }

  if (aiMaturity === 'experimental' || aiMaturity === 'pilot') {
    recId++;
    recommendations.push({
      id: `rec_${recId}`,
      category: 'project',
      priority: 'high',
      title: 'Faire passer vos projets IA en production',
      description: 'Vos initiatives IA sont au stade expérimental/pilote. Le CDAEIA valorise l\'IA en production.',
      expectedImpact: 10,
      effortLevel: 'high',
      estimatedWeeks: 16,
      actionItems: [
        'Identifier le projet IA pilote le plus mature',
        'Créer un plan de mise en production',
        'Définir des métriques de succès mesurables',
      ],
    });
  }

  // Recommandations documentation
  if (hasTechnicalDocs === 'minimal' || hasTechnicalDocs === 'partial') {
    recId++;
    recommendations.push({
      id: `rec_${recId}`,
      category: 'documentation',
      priority: 'medium',
      title: 'Améliorer la documentation technique',
      description: 'Investissement Québec exige des preuves de l\'intégration IA.',
      expectedImpact: 5,
      effortLevel: 'low',
      estimatedWeeks: 4,
      actionItems: [
        'Documenter l\'architecture des systèmes IA',
        'Créer des fiches techniques pour chaque modèle',
        'Documenter les datasets utilisés',
      ],
    });
  }

  if (timeTracking === 'none') {
    recId++;
    recommendations.push({
      id: `rec_${recId}`,
      category: 'documentation',
      priority: 'high',
      title: 'Implémenter un système de suivi du temps',
      description: 'Sans suivi du temps, impossible de prouver le 75% IA.',
      expectedImpact: 15,
      effortLevel: 'low',
      estimatedWeeks: 2,
      actionItems: [
        'Choisir un outil (Toggl, Clockify, Harvest)',
        'Définir les catégories d\'activités',
        'Former les employés',
      ],
    });
  } else if (timeTracking === 'basic') {
    recId++;
    recommendations.push({
      id: `rec_${recId}`,
      category: 'documentation',
      priority: 'medium',
      title: 'Améliorer le suivi du temps avec des catégories',
      description: 'Ajoutez des catégories pour distinguer les activités IA.',
      expectedImpact: 5,
      effortLevel: 'low',
      estimatedWeeks: 2,
      actionItems: [
        'Ajouter des catégories: Dev IA, Intégration, Maintenance, Support',
        'Former les employés aux nouvelles catégories',
      ],
    });
  }

  // Recommandations par défaut (toujours affichées)
  if (recommendations.length === 0) {
    recId++;
    recommendations.push({
      id: `rec_${recId}`,
      category: 'documentation',
      priority: 'medium',
      title: 'Preparer la documentation pour la demande',
      description: 'Rassemblez les documents necessaires pour votre demande de credit CDAEIA aupres d\'Investissement Quebec.',
      expectedImpact: 5,
      effortLevel: 'medium',
      estimatedWeeks: 2,
      actionItems: [
        'Preparer les T4 des employes admissibles',
        'Documenter les projets IA avec descriptions techniques',
        'Compiler les feuilles de temps par projet',
        'Preparer l\'organigramme de l\'equipe technique',
      ],
    });

    recId++;
    recommendations.push({
      id: `rec_${recId}`,
      category: 'process',
      priority: 'low',
      title: 'Planifier la demande de credit',
      description: 'Le CDAEIA entre en vigueur en janvier 2026. Planifiez votre demande en avance.',
      expectedImpact: 5,
      effortLevel: 'low',
      estimatedWeeks: 1,
      actionItems: [
        'Contacter un CPA specialise en credits d\'impot',
        'Revoir les criteres d\'eligibilite avec votre equipe',
        'Planifier une consultation avec Ran.AI Agency',
      ],
    });
  }

  // Ajouter une recommandation de suivi
  recId++;
  recommendations.push({
    id: `rec_${recId}`,
    category: 'process',
    priority: 'low',
    title: 'Consultation gratuite avec Ran.AI Agency',
    description: 'Discutez de vos resultats avec nos experts pour maximiser votre credit d\'impot CDAEIA.',
    expectedImpact: 10,
    effortLevel: 'low',
    estimatedWeeks: 1,
    actionItems: [
      'Planifier un appel de 30 minutes',
      'Revoir ce rapport ensemble',
      'Identifier les opportunites d\'optimisation',
    ],
  });

  // Trier par priorité
  const priorityOrder: Record<Priority, number> = { high: 0, medium: 1, low: 2 };
  recommendations.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

  return recommendations;
}
