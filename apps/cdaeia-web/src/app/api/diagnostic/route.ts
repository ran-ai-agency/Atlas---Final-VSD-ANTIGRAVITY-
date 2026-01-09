import { NextRequest, NextResponse } from 'next/server';
import { saveDiagnostic, getDiagnostic, DiagnosticRecord } from '@/lib/supabase';

// POST - Save a new diagnostic
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      companyName,
      companyNeq,
      email,
      responses,
      result,
    } = body;

    if (!companyName || !responses || !result) {
      return NextResponse.json(
        { error: 'Donnees manquantes' },
        { status: 400 }
      );
    }

    const record: DiagnosticRecord = {
      company_name: companyName,
      company_neq: companyNeq,
      email,
      responses,
      total_score: result.totalScore,
      max_score: result.maxScore,
      percentage: result.percentage,
      eligibility_status: result.eligibilityStatus,
      credit_current: result.creditCurrent?.totalCredit || null,
      credit_optimized: result.creditOptimized?.totalCredit || null,
      credit_gain: result.creditGain,
    };

    const saved = await saveDiagnostic(record);

    if (!saved) {
      // Supabase not configured or error - still return success but without ID
      return NextResponse.json({
        success: true,
        message: 'Diagnostic complete (sauvegarde non disponible)',
        id: null,
      });
    }

    return NextResponse.json({
      success: true,
      id: saved.id,
    });
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Une erreur est survenue' },
      { status: 500 }
    );
  }
}

// GET - Retrieve a diagnostic by ID
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    if (!id) {
      return NextResponse.json(
        { error: 'ID manquant' },
        { status: 400 }
      );
    }

    const diagnostic = await getDiagnostic(id);

    if (!diagnostic) {
      return NextResponse.json(
        { error: 'Diagnostic non trouve' },
        { status: 404 }
      );
    }

    return NextResponse.json({ diagnostic });
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Une erreur est survenue' },
      { status: 500 }
    );
  }
}
