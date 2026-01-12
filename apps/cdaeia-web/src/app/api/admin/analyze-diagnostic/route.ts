import { NextRequest, NextResponse } from 'next/server';
import Anthropic from '@anthropic-ai/sdk';

interface DiagnosticData {
  id: string;
  company_name: string;
  company_neq: string | null;
  email: string | null;
  responses: Record<string, unknown>;
  total_score: number;
  max_score: number;
  percentage: number;
  eligibility_status: 'eligible' | 'partial' | 'not_eligible';
  credit_current: number | null;
  credit_optimized: number | null;
  credit_gain: number;
  created_at: string;
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
    const diagnostic: DiagnosticData = body.diagnostic;

    if (!diagnostic) {
      return NextResponse.json(
        { error: 'Donnees du diagnostic manquantes' },
        { status: 400 }
      );
    }

    const anthropic = new Anthropic({
      apiKey,
    });

    const prompt = `Tu es un expert en credits d'impot pour la recherche et developpement (RS&DE) et le Credit d'Impot a l'Investissement et l'Innovation (C3i) au Quebec.

Analyse ce diagnostic d'eligibilite CDAEIA pour l'entreprise "${diagnostic.company_name}":

**Score d'eligibilite:** ${diagnostic.percentage.toFixed(0)}% (${diagnostic.total_score}/${diagnostic.max_score})
**Statut:** ${diagnostic.eligibility_status === 'eligible' ? 'Eligible' : diagnostic.eligibility_status === 'partial' ? 'Partiellement eligible' : 'Non eligible'}
**Credit actuel estime:** ${diagnostic.credit_current ? `${diagnostic.credit_current.toLocaleString('fr-CA')} $` : 'N/A'}
**Credit apres optimisation:** ${diagnostic.credit_optimized ? `${diagnostic.credit_optimized.toLocaleString('fr-CA')} $` : 'N/A'}
**Gain potentiel:** ${diagnostic.credit_gain.toLocaleString('fr-CA')} $

**Reponses au questionnaire:**
${JSON.stringify(diagnostic.responses, null, 2)}

Fournis une analyse structuree en JSON avec les champs suivants:
{
  "summary": "Resume executif de 2-3 phrases",
  "strengths": ["Liste des points forts (3-5 items)"],
  "weaknesses": ["Liste des points a ameliorer (3-5 items)"],
  "recommendations": ["Recommandations specifiques pour optimiser les credits (3-5 items)"],
  "nextSteps": ["Prochaines etapes concretes (3-5 items)"]
}

Reponds UNIQUEMENT avec le JSON, sans texte additionnel.`;

    const message = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1500,
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
