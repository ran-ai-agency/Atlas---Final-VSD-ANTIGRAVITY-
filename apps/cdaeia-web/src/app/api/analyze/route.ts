import { NextRequest, NextResponse } from 'next/server';
import { analyzeWithClaude } from '@/lib/claude-analysis';
import { DiagnosticResponses, DiagnosticResult } from '@/lib/cdaeia-types';

interface AnalyzeRequest {
  responses: DiagnosticResponses;
  result: DiagnosticResult;
}

export async function POST(request: NextRequest) {
  try {
    // Check if Anthropic is configured
    if (!process.env.ANTHROPIC_API_KEY) {
      return NextResponse.json(
        { error: 'Service d\'analyse IA non configure.' },
        { status: 503 }
      );
    }

    const body: AnalyzeRequest = await request.json();
    const { responses, result } = body;

    if (!responses || !result) {
      return NextResponse.json(
        { error: 'Donnees manquantes' },
        { status: 400 }
      );
    }

    const analysis = await analyzeWithClaude(responses, result);

    if (!analysis) {
      return NextResponse.json(
        { error: 'Erreur lors de l\'analyse' },
        { status: 500 }
      );
    }

    return NextResponse.json({ analysis });
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Une erreur est survenue' },
      { status: 500 }
    );
  }
}
