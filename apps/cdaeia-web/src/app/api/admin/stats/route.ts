import { NextResponse } from 'next/server';
import { getAllDiagnostics } from '@/lib/supabase';

export async function GET() {
  try {
    const diagnostics = await getAllDiagnostics();

    // Calculate statistics
    const totalDiagnostics = diagnostics.length;
    const eligibleCount = diagnostics.filter(d => d.eligibility_status === 'eligible').length;
    const partialCount = diagnostics.filter(d => d.eligibility_status === 'partial').length;
    const notEligibleCount = diagnostics.filter(d => d.eligibility_status === 'not_eligible').length;

    const avgScore = totalDiagnostics > 0
      ? diagnostics.reduce((sum, d) => sum + d.percentage, 0) / totalDiagnostics
      : 0;

    const totalCreditCurrent = diagnostics.reduce((sum, d) => sum + (d.credit_current || 0), 0);
    const totalCreditOptimized = diagnostics.reduce((sum, d) => sum + (d.credit_optimized || 0), 0);
    const totalPotentialGain = diagnostics.reduce((sum, d) => sum + (d.credit_gain || 0), 0);

    // Get recent diagnostics (last 5)
    const recentDiagnostics = diagnostics.slice(0, 5).map(d => ({
      id: d.id,
      company_name: d.company_name,
      eligibility_status: d.eligibility_status,
      percentage: d.percentage,
      credit_current: d.credit_current,
      created_at: d.created_at,
    }));

    return NextResponse.json({
      totalDiagnostics,
      eligibleCount,
      partialCount,
      notEligibleCount,
      avgScore,
      totalCreditCurrent,
      totalCreditOptimized,
      totalPotentialGain,
      recentDiagnostics,
    });
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Une erreur est survenue' },
      { status: 500 }
    );
  }
}
