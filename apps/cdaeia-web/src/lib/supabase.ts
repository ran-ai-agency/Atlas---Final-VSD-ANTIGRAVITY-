import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Create Supabase client only if credentials are available
export const supabase = supabaseUrl && supabaseAnonKey
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

// Types for database tables
export interface DiagnosticRecord {
  id?: string;
  company_name: string;
  company_neq?: string;
  email?: string;
  responses: Record<string, unknown>;
  total_score: number;
  max_score: number;
  percentage: number;
  eligibility_status: 'eligible' | 'partial' | 'not_eligible';
  credit_current: number | null;
  credit_optimized: number | null;
  credit_gain: number;
  created_at?: string;
}

// Save a diagnostic result
export async function saveDiagnostic(record: DiagnosticRecord): Promise<{ id: string } | null> {
  if (!supabase) {
    console.warn('Supabase not configured - diagnostic not saved');
    return null;
  }

  const { data, error } = await supabase
    .from('diagnostics')
    .insert([record])
    .select('id')
    .single();

  if (error) {
    console.error('Error saving diagnostic:', error);
    return null;
  }

  return data;
}

// Get diagnostic by ID
export async function getDiagnostic(id: string): Promise<DiagnosticRecord | null> {
  if (!supabase) return null;

  const { data, error } = await supabase
    .from('diagnostics')
    .select('*')
    .eq('id', id)
    .single();

  if (error) {
    console.error('Error fetching diagnostic:', error);
    return null;
  }

  return data;
}

// Get all diagnostics (for admin dashboard)
export async function getAllDiagnostics(): Promise<DiagnosticRecord[]> {
  if (!supabase) return [];

  const { data, error } = await supabase
    .from('diagnostics')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) {
    console.error('Error fetching diagnostics:', error);
    return [];
  }

  return data || [];
}

// SQL to create the table in Supabase:
/*
CREATE TABLE diagnostics (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  company_name TEXT NOT NULL,
  company_neq TEXT,
  email TEXT,
  responses JSONB NOT NULL,
  total_score INTEGER NOT NULL,
  max_score INTEGER NOT NULL DEFAULT 100,
  percentage DECIMAL(5,2) NOT NULL,
  eligibility_status TEXT NOT NULL CHECK (eligibility_status IN ('eligible', 'partial', 'not_eligible')),
  credit_current DECIMAL(12,2),
  credit_optimized DECIMAL(12,2),
  credit_gain DECIMAL(12,2) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE diagnostics ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts (for public form)
CREATE POLICY "Allow anonymous inserts" ON diagnostics
  FOR INSERT WITH CHECK (true);

-- Allow reading own diagnostic (by ID in URL)
CREATE POLICY "Allow reading by id" ON diagnostics
  FOR SELECT USING (true);
*/
