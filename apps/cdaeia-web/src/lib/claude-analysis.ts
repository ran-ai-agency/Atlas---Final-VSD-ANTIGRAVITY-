import Anthropic from '@anthropic-ai/sdk';
import { DiagnosticResponses, DiagnosticResult } from './cdaeia-types';

// Initialize Anthropic client only if API key is available
const anthropic = process.env.ANTHROPIC_API_KEY
  ? new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })
  : null;

export interface AIAnalysis {
  summary: string;
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  detailedRecommendations: {
    title: string;
    description: string;
    implementation: string;
    expectedOutcome: string;
  }[];
  riskAssessment: string;
  timeline: string;
}

const SYSTEM_PROMPT = `Tu es un expert en fiscalité québécoise spécialisé dans le crédit d'impôt CDAEIA (Crédit d'impôt pour le Développement des Affaires Électroniques intégrant l'Intelligence Artificielle).

Tu analyses les données d'un diagnostic CDAEIA pour une PME technologique et fournis:
1. Un résumé exécutif de la situation
2. Les forces de l'entreprise pour le CDAEIA
3. Les faiblesses à corriger
4. Les opportunités d'optimisation
5. Des recommandations détaillées et actionnables
6. Une évaluation des risques
7. Un calendrier suggéré

Critères CDAEIA à rappeler:
- Test 75%: Au moins 75% des revenus du secteur TI
- Test 50%: Au moins 50% des revenus des sous-secteurs qualifiants (logiciels, systèmes, hébergement)
- Minimum 6 employés éligibles à temps plein
- 75% du temps sur activités IA qualifiantes
- Activités qualifiantes: développement IA, intégration IA, préparation données IA, analytique avancée
- Activités NON qualifiantes: maintenance, support, administration

Taux 2026: 30% total (22% remboursable + 8% non-remboursable)
Seuil d'exclusion: 18 571$ par employé

Réponds en français, de manière professionnelle mais accessible.`;

export async function analyzeWithClaude(
  responses: DiagnosticResponses,
  result: DiagnosticResult
): Promise<AIAnalysis | null> {
  if (!anthropic) {
    console.warn('Anthropic API not configured - AI analysis disabled');
    return null;
  }

  const userPrompt = `Analyse ce diagnostic CDAEIA et fournis des recommandations détaillées.

## Profil de l'entreprise
- Nom: ${responses.company_name || 'N/A'}
- Secteur: ${responses.industry || 'N/A'}
- Total employés: ${responses.total_employees || 'N/A'}
- Employés tech temps plein: ${responses.tech_employees_fulltime || 'N/A'}
- Masse salariale tech: ${responses.total_tech_payroll || 0}$

## Revenus
- Revenus totaux: ${responses.total_revenue || 0}$
- Revenus IT: ${responses.it_revenue || 0}$ (${((responses.it_revenue as number || 0) / (responses.total_revenue as number || 1) * 100).toFixed(1)}%)
- Revenus logiciels: ${responses.software_revenue || 0}$
- Revenus conception systèmes: ${responses.system_design_revenue || 0}$
- Revenus hébergement données: ${responses.data_hosting_revenue || 0}$

## Allocation du temps (moyenne)
- Développement IA: ${responses.avg_time_ai_dev || 0}%
- Intégration IA: ${responses.avg_time_ai_integration || 0}%
- Préparation données IA: ${responses.avg_time_ai_data || 0}%
- Analytique avancée: ${responses.avg_time_ai_analytics || 0}%
- Maintenance (non éligible): ${responses.avg_time_maintenance || 0}%
- Support (non éligible): ${responses.avg_time_support || 0}%
- Admin (non éligible): ${responses.avg_time_admin || 0}%

## Intégration IA
- Produits/services IA: ${responses.has_ai_products ? 'Oui' : 'Non'}
- Technologies: ${(responses.ai_technologies as string[] || []).join(', ') || 'Aucune'}
- Maturité: ${responses.ai_maturity || 'N/A'}
- % revenus IA: ${responses.ai_revenue_percentage || 0}%

## Documentation
- Documentation technique: ${responses.has_technical_docs || 'N/A'}
- Suivi du temps: ${responses.time_tracking_system || 'N/A'}
- Historique feuilles de temps: ${responses.has_time_records || 'N/A'}
- CDAE réclamé avant: ${responses.previous_cdae ? 'Oui' : 'Non'}

## Résultat du diagnostic
- Score: ${result.totalScore}/${result.maxScore} (${result.percentage.toFixed(1)}%)
- Statut: ${result.eligibilityStatus}
- Crédit actuel estimé: ${result.creditCurrent?.totalCredit || 0}$
- Crédit optimisé potentiel: ${result.creditOptimized?.totalCredit || 0}$
- Gain potentiel: ${result.creditGain}$

## Problèmes critiques identifiés
${result.criticalIssues.map(i => `- ${i}`).join('\n') || 'Aucun'}

## Avertissements
${result.warnings.map(w => `- ${w}`).join('\n') || 'Aucun'}

Fournis ton analyse au format JSON avec cette structure exacte:
{
  "summary": "Résumé exécutif de 2-3 phrases",
  "strengths": ["Force 1", "Force 2", ...],
  "weaknesses": ["Faiblesse 1", "Faiblesse 2", ...],
  "opportunities": ["Opportunité 1", "Opportunité 2", ...],
  "detailedRecommendations": [
    {
      "title": "Titre de la recommandation",
      "description": "Description détaillée",
      "implementation": "Étapes d'implémentation",
      "expectedOutcome": "Résultat attendu"
    }
  ],
  "riskAssessment": "Évaluation des risques en cas d'audit",
  "timeline": "Calendrier suggéré pour les actions"
}`;

  try {
    const message = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 2000,
      messages: [
        {
          role: 'user',
          content: userPrompt,
        },
      ],
      system: SYSTEM_PROMPT,
    });

    // Extract JSON from response
    const content = message.content[0];
    if (content.type !== 'text') {
      throw new Error('Unexpected response type');
    }

    // Try to parse JSON from the response
    const jsonMatch = content.text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('No JSON found in response');
    }

    const analysis: AIAnalysis = JSON.parse(jsonMatch[0]);
    return analysis;
  } catch (error) {
    console.error('Error calling Claude API:', error);
    return null;
  }
}
