import { NextRequest, NextResponse } from 'next/server';
import Anthropic from '@anthropic-ai/sdk';

interface DiagnosticSummary {
  id: string;
  company_name: string;
  eligibility_status: string;
  percentage: number;
  credit_current: number | null;
  credit_optimized: number | null;
  credit_gain: number;
  responses: Record<string, unknown>;
}

interface Stats {
  totalDiagnostics: number;
  avgScore: number;
  eligibleCount: number;
  partialCount: number;
  notEligibleCount: number;
  totalPotentialGain: number;
}

export async function POST(request: NextRequest) {
  try {
    const apiKey = process.env.ANTHROPIC_API_KEY;

    if (!apiKey) {
      return NextResponse.json(
        { error: 'Service d\'analyse IA non configure.' },
        { status: 503 }
      );
    }

    const body = await request.json();
    const diagnostics: DiagnosticSummary[] = body.diagnostics;
    const stats: Stats = body.stats;

    if (!diagnostics || diagnostics.length === 0) {
      return NextResponse.json(
        { error: 'Aucun diagnostic a analyser' },
        { status: 400 }
      );
    }

    const anthropic = new Anthropic({
      apiKey,
    });

    // Prepare summary of all diagnostics
    const diagnosticsSummary = diagnostics.map(d => ({
      company: d.company_name,
      score: d.percentage,
      status: d.eligibility_status,
      gain: d.credit_gain,
      responses: d.responses
    }));

    const prompt = `Tu es un expert en credits d'impot pour la recherche et developpement (RS&DE) et le Credit d'Impot a l'Investissement et l'Innovation (C3i) au Quebec.

Analyse cet ensemble de ${diagnostics.length} diagnostics d'eligibilite CDAEIA:

**Statistiques globales:**
- Total diagnostics: ${stats.totalDiagnostics}
- Score moyen: ${stats.avgScore.toFixed(1)}%
- Eligibles: ${stats.eligibleCount} (${((stats.eligibleCount / stats.totalDiagnostics) * 100).toFixed(0)}%)
- Partiellement eligibles: ${stats.partialCount}
- Non eligibles: ${stats.notEligibleCount}
- Gain potentiel total: ${stats.totalPotentialGain.toLocaleString('fr-CA')} $

**Donnees des diagnostics:**
${JSON.stringify(diagnosticsSummary, null, 2)}

Fournis une analyse agregee en JSON avec les champs suivants:
{
  "marketInsights": "Apercu global du marche et des entreprises analysees (2-3 phrases)",
  "commonStrengths": ["Forces communes identifiees parmi les entreprises (3-5 items)"],
  "commonWeaknesses": ["Faiblesses recurrentes observees (3-5 items)"],
  "industryTrends": ["Tendances observees dans les donnees (3-4 items)"],
  "optimizationOpportunities": ["Opportunites d'optimisation des credits identifiees (3-5 items)"],
  "recommendedActions": ["Actions strategiques recommandees pour maximiser les credits (3-5 items)"]
}

Base ton analyse sur les patterns reels observes dans les donnees. Sois specifique et actionnable.

Reponds UNIQUEMENT avec le JSON, sans texte additionnel.`;

    const message = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 2000,
      messages: [
        {
          role: 'user',
          content: prompt,
        },
      ],
    });

    // Extract text content
    const textContent = message.content.find(block => block.type === 'text');
    if (!textContent || textContent.type !== 'text') {
      throw new Error('No text response from AI');
    }

    // Parse JSON response - remove markdown code blocks if present
    let jsonText = textContent.text.trim();
    if (jsonText.startsWith('```json')) {
      jsonText = jsonText.slice(7);
    } else if (jsonText.startsWith('```')) {
      jsonText = jsonText.slice(3);
    }
    if (jsonText.endsWith('```')) {
      jsonText = jsonText.slice(0, -3);
    }
    jsonText = jsonText.trim();

    const analysis = JSON.parse(jsonText);

    return NextResponse.json(analysis);
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Une erreur est survenue lors de l\'analyse' },
      { status: 500 }
    );
  }
}
