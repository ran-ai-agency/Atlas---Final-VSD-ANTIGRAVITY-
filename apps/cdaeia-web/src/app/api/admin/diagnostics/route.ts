import { NextRequest, NextResponse } from 'next/server';
import { getAllDiagnostics } from '@/lib/supabase';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);

    // Get query parameters for filtering
    const status = searchParams.get('status');
    const search = searchParams.get('search');
    const sortBy = searchParams.get('sortBy') || 'created_at';
    const sortOrder = searchParams.get('sortOrder') || 'desc';
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '10');

    let diagnostics = await getAllDiagnostics();

    // Apply status filter
    if (status && status !== 'all') {
      diagnostics = diagnostics.filter(d => d.eligibility_status === status);
    }

    // Apply search filter
    if (search) {
      const searchLower = search.toLowerCase();
      diagnostics = diagnostics.filter(d =>
        d.company_name.toLowerCase().includes(searchLower) ||
        (d.company_neq && d.company_neq.toLowerCase().includes(searchLower)) ||
        (d.email && d.email.toLowerCase().includes(searchLower))
      );
    }

    // Apply sorting
    diagnostics.sort((a, b) => {
      let aVal: unknown = a[sortBy as keyof typeof a];
      let bVal: unknown = b[sortBy as keyof typeof b];

      // Handle null values
      if (aVal === null || aVal === undefined) aVal = sortOrder === 'asc' ? Infinity : -Infinity;
      if (bVal === null || bVal === undefined) bVal = sortOrder === 'asc' ? Infinity : -Infinity;

      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortOrder === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
      }

      return 0;
    });

    // Calculate pagination
    const total = diagnostics.length;
    const totalPages = Math.ceil(total / limit);
    const offset = (page - 1) * limit;
    const paginatedDiagnostics = diagnostics.slice(offset, offset + limit);

    return NextResponse.json({
      diagnostics: paginatedDiagnostics,
      pagination: {
        page,
        limit,
        total,
        totalPages,
      },
    });
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Une erreur est survenue' },
      { status: 500 }
    );
  }
}
