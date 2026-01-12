'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Brain,
  RefreshCw,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  Target,
  Lightbulb,
  Building2,
  DollarSign
} from 'lucide-react';

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

interface AggregateAnalysis {
  marketInsights: string;
  commonStrengths: string[];
  commonWeaknesses: string[];
  industryTrends: string[];
  optimizationOpportunities: string[];
  recommendedActions: string[];
}

interface Stats {
  totalDiagnostics: number;
  avgScore: number;
  eligibleCount: number;
  partialCount: number;
  notEligibleCount: number;
  totalPotentialGain: number;
}

export default function AnalyseIAPage() {
  const [diagnostics, setDiagnostics] = useState<DiagnosticSummary[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<AggregateAnalysis | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [diagRes, statsRes] = await Promise.all([
        fetch('/api/admin/diagnostics?limit=100'),
        fetch('/api/admin/stats')
      ]);

      if (diagRes.ok) {
        const diagData = await diagRes.json();
        setDiagnostics(diagData.diagnostics || []);
      }

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const runAggregateAnalysis = async () => {
    if (diagnostics.length === 0) return;
    setAnalyzing(true);
    setAnalysis(null);

    try {
      const response = await fetch('/api/admin/aggregate-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          diagnostics,
          stats
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Analysis result:', data);
        setAnalysis(data);
      } else {
        console.error('Analysis failed:', response.status);
      }
    } catch (err) {
      console.error('Error running analysis:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  // Calculate distribution for chart
  const distribution = {
    excellent: diagnostics.filter(d => d.percentage >= 80).length,
    good: diagnostics.filter(d => d.percentage >= 60 && d.percentage < 80).length,
    moderate: diagnostics.filter(d => d.percentage >= 40 && d.percentage < 60).length,
    low: diagnostics.filter(d => d.percentage < 40).length,
  };

  const maxDistribution = Math.max(...Object.values(distribution), 1);

  // Top companies by potential gain
  const topByGain = [...diagnostics]
    .sort((a, b) => b.credit_gain - a.credit_gain)
    .slice(0, 5);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analyse IA Avancee</h1>
          <p className="text-gray-600">Intelligence artificielle sur l'ensemble des donnees</p>
        </div>
        <Button
          onClick={runAggregateAnalysis}
          disabled={analyzing || diagnostics.length === 0}
          className="bg-purple-600 hover:bg-purple-700"
        >
          {analyzing ? (
            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Brain className="w-4 h-4 mr-2" />
          )}
          Lancer l'analyse globale
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BarChart3 className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Diagnostics analyses</p>
                <p className="text-2xl font-bold">{diagnostics.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Target className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Score moyen</p>
                <p className="text-2xl font-bold">{stats?.avgScore.toFixed(0) || 0}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-amber-100 rounded-lg">
                <TrendingUp className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Taux d'eligibilite</p>
                <p className="text-2xl font-bold">
                  {stats && stats.totalDiagnostics > 0
                    ? ((stats.eligibleCount / stats.totalDiagnostics) * 100).toFixed(0)
                    : 0}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <DollarSign className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Gain potentiel total</p>
                <p className="text-2xl font-bold">
                  {formatCurrency(stats?.totalPotentialGain || 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Distribution & Top Companies */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Score Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Distribution des scores
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <DistributionBar
                label="Excellent (80%+)"
                count={distribution.excellent}
                max={maxDistribution}
                color="bg-green-500"
              />
              <DistributionBar
                label="Bon (60-79%)"
                count={distribution.good}
                max={maxDistribution}
                color="bg-blue-500"
              />
              <DistributionBar
                label="Modere (40-59%)"
                count={distribution.moderate}
                max={maxDistribution}
                color="bg-amber-500"
              />
              <DistributionBar
                label="Faible (<40%)"
                count={distribution.low}
                max={maxDistribution}
                color="bg-red-500"
              />
            </div>
          </CardContent>
        </Card>

        {/* Top Companies by Potential */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Building2 className="w-5 h-5" />
              Top entreprises par gain potentiel
            </CardTitle>
          </CardHeader>
          <CardContent>
            {topByGain.length === 0 ? (
              <p className="text-gray-500 text-center py-4">Aucune donnee</p>
            ) : (
              <div className="space-y-3">
                {topByGain.map((d, i) => (
                  <div key={d.id} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center text-sm font-medium">
                        {i + 1}
                      </span>
                      <span className="font-medium text-sm">{d.company_name}</span>
                    </div>
                    <span className="text-green-600 font-semibold">
                      +{formatCurrency(d.credit_gain)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* AI Analysis Results */}
      {analysis && (
        <Card className="border-purple-200 bg-purple-50/30">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2 text-purple-700">
              <Brain className="w-5 h-5" />
              Analyse IA Globale
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Market Insights */}
            <div>
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-amber-500" />
                Apercu du marche
              </h4>
              <p className="text-gray-700 bg-white p-3 rounded-lg">{analysis.marketInsights}</p>
            </div>

            {/* Strengths & Weaknesses */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold text-green-700 mb-2 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Forces communes
                </h4>
                <ul className="space-y-2">
                  {analysis.commonStrengths.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm bg-white p-2 rounded">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-amber-700 mb-2 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" />
                  Faiblesses communes
                </h4>
                <ul className="space-y-2">
                  {analysis.commonWeaknesses.map((w, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm bg-white p-2 rounded">
                      <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                      {w}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Industry Trends */}
            <div>
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-blue-500" />
                Tendances observees
              </h4>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {analysis.industryTrends.map((t, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm bg-white p-2 rounded">
                    <TrendingUp className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                    {t}
                  </li>
                ))}
              </ul>
            </div>

            {/* Optimization Opportunities */}
            <div>
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <Target className="w-4 h-4 text-purple-500" />
                Opportunites d'optimisation
              </h4>
              <ul className="space-y-2">
                {analysis.optimizationOpportunities.map((o, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm bg-white p-3 rounded">
                    <span className="bg-purple-100 text-purple-700 rounded-full w-5 h-5 flex items-center justify-center flex-shrink-0 text-xs font-medium">
                      {i + 1}
                    </span>
                    {o}
                  </li>
                ))}
              </ul>
            </div>

            {/* Recommended Actions */}
            <div className="pt-4 border-t border-purple-200">
              <h4 className="font-semibold mb-3">Actions recommandees</h4>
              <ol className="space-y-2">
                {analysis.recommendedActions.map((a, i) => (
                  <li key={i} className="flex items-start gap-3 bg-white p-3 rounded-lg border border-purple-100">
                    <span className="bg-purple-600 text-white rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 text-sm font-medium">
                      {i + 1}
                    </span>
                    <span className="text-gray-700">{a}</span>
                  </li>
                ))}
              </ol>
            </div>
          </CardContent>
        </Card>
      )}

      {/* No Data State */}
      {diagnostics.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Brain className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Aucune donnee a analyser</h3>
            <p className="text-gray-500">Les diagnostics soumis apparaitront ici pour l'analyse.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function DistributionBar({
  label,
  count,
  max,
  color
}: {
  label: string;
  count: number;
  max: number;
  color: string;
}) {
  const percentage = max > 0 ? (count / max) * 100 : 0;

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium">{count}</span>
      </div>
      <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('fr-CA', {
    style: 'currency',
    currency: 'CAD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}
