-- CDAEIA Diagnostic Database Schema
-- Execute this in Supabase SQL Editor: https://supabase.com/dashboard/project/zupnncewkclcnigpcsmu/sql

-- Create diagnostics table
CREATE TABLE IF NOT EXISTS diagnostics (
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

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_diagnostics_created_at ON diagnostics(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_diagnostics_company_name ON diagnostics(company_name);
CREATE INDEX IF NOT EXISTS idx_diagnostics_eligibility ON diagnostics(eligibility_status);

-- Enable Row Level Security
ALTER TABLE diagnostics ENABLE ROW LEVEL SECURITY;

-- Policy: Allow anyone to insert (for the public form)
CREATE POLICY "Allow anonymous inserts" ON diagnostics
  FOR INSERT
  WITH CHECK (true);

-- Policy: Allow anyone to read (diagnostics are not sensitive)
CREATE POLICY "Allow public read" ON diagnostics
  FOR SELECT
  USING (true);

-- Optional: Create a view for dashboard statistics
CREATE OR REPLACE VIEW diagnostic_stats AS
SELECT
  COUNT(*) as total_diagnostics,
  COUNT(CASE WHEN eligibility_status = 'eligible' THEN 1 END) as eligible_count,
  COUNT(CASE WHEN eligibility_status = 'partial' THEN 1 END) as partial_count,
  COUNT(CASE WHEN eligibility_status = 'not_eligible' THEN 1 END) as not_eligible_count,
  AVG(percentage) as avg_score,
  SUM(credit_current) as total_credit_current,
  SUM(credit_optimized) as total_credit_optimized,
  SUM(credit_gain) as total_potential_gain
FROM diagnostics;

-- Grant access to the view
GRANT SELECT ON diagnostic_stats TO anon, authenticated;
