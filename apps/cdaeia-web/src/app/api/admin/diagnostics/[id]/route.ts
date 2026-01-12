import { NextRequest, NextResponse } from 'next/server';
import { getDiagnostic } from '@/lib/supabase';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

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

    return NextResponse.json(diagnostic);
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Une erreur est survenue' },
      { status: 500 }
    );
  }
}
