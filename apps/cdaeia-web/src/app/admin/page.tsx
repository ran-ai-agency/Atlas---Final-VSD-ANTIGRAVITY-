'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import {
  FileText,
  DollarSign,
  TrendingUp,
  Users,
  CheckCircle,
  AlertTriangle,
  XCircle,
  ArrowRight,
  Brain,
  RefreshCw
} from 'lucide-react';

interface DashboardStats {
  totalDiagnostics: number;
  eligibleCount: number;
  partialCount: number;
  notEligibleCount: number;
  avgScore: number;
  totalCreditCurrent: number;
  totalCreditOptimized: number;
  totalPotentialGain: number;
  recentDiagnostics: DiagnosticSummary[];
}

interface DiagnosticSummary {
  id: string;
  company_name: string;
  eligibility_status: string;
  percentage: number;
  credit_current: number | null;
  created_at: string;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/admin/stats');
      if (!response.ok) throw new Error('Erreur lors du chargement');
      const data = await response.json();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Erreur de chargement</h2>
        <p className="text-gray-600 mb-4">{error}</p>
        <Button onClick={fetchStats}>Reessayer</Button>
      </div>
    );
  }

  if (!stats) return null;

  const eligibilityRate = stats.totalDiagnostics > 0
    ? ((stats.eligibleCount / stats.totalDiagnostics) * 100).toFixed(1)
    : '0';

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard Admin</h1>
          <p className="text-gray-600">Vue d'ensemble des diagnostics CDAEIA</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={fetchStats}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Actualiser
          </Button>
          <Link href="/admin/analyse-ia">
            <Button>
              <Brain className="w-4 h-4 mr-2" />
              Analyse IA
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Diagnostics"
          value={stats.totalDiagnostics.toString()}
          icon={<FileText className="w-5 h-5" />}
          color="blue"
        />
        <KPICard
          title="Score Moyen"
          value={`${stats.avgScore.toFixed(0)}%`}
          icon={<TrendingUp className="w-5 h-5" />}
          color="purple"
        />
        <KPICard
          title="Credits Identifies"
          value={formatCurrency(stats.totalCreditCurrent)}
          icon={<DollarSign className="w-5 h-5" />}
          color="green"
        />
        <KPICard
          title="Gain Potentiel"
          value={formatCurrency(stats.totalPotentialGain)}
          icon={<TrendingUp className="w-5 h-5" />}
          color="amber"
        />
      </div>

      {/* Eligibility Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Repartition par eligibilite</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <EligibilityBar
                label="Eligible"
                count={stats.eligibleCount}
                total={stats.totalDiagnostics}
                color="bg-green-500"
                icon={<CheckCircle className="w-4 h-4 text-green-600" />}
              />
              <EligibilityBar
                label="Partiellement eligible"
                count={stats.partialCount}
                total={stats.totalDiagnostics}
                color="bg-amber-500"
                icon={<AlertTriangle className="w-4 h-4 text-amber-600" />}
              />
              <EligibilityBar
                label="Non eligible"
                count={stats.notEligibleCount}
                total={stats.totalDiagnostics}
                color="bg-red-500"
                icon={<XCircle className="w-4 h-4 text-red-600" />}
              />
            </div>

            <div className="mt-6 pt-4 border-t">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Taux d'eligibilite</span>
                <span className="text-2xl font-bold text-green-600">{eligibilityRate}%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Resume financier</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Credits actuels identifies</span>
                  <span className="font-semibold">{formatCurrency(stats.totalCreditCurrent)}</span>
                </div>
                <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full"
                    style={{
                      width: stats.totalCreditOptimized > 0
                        ? `${(stats.totalCreditCurrent / stats.totalCreditOptimized) * 100}%`
                        : '0%'
                    }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Credits apres optimisation</span>
                  <span className="font-semibold">{formatCurrency(stats.totalCreditOptimized)}</span>
                </div>
                <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-green-500 rounded-full w-full" />
                </div>
              </div>

              <div className="pt-4 border-t">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Gain potentiel total</span>
                  <span className="text-2xl font-bold text-green-600">
                    +{formatCurrency(stats.totalPotentialGain)}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Diagnostics */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg">Diagnostics recents</CardTitle>
          <Link href="/admin/soumissions">
            <Button variant="outline" size="sm">
              Voir tout
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
        </CardHeader>
        <CardContent>
          {stats.recentDiagnostics.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Users className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Aucun diagnostic pour le moment</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b text-left text-sm text-gray-500">
                    <th className="pb-3 font-medium">Entreprise</th>
                    <th className="pb-3 font-medium">Statut</th>
                    <th className="pb-3 font-medium">Score</th>
                    <th className="pb-3 font-medium">Credit</th>
                    <th className="pb-3 font-medium">Date</th>
                    <th className="pb-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {stats.recentDiagnostics.map((diagnostic) => (
                    <tr key={diagnostic.id} className="hover:bg-gray-50">
                      <td className="py-3 font-medium">{diagnostic.company_name}</td>
                      <td className="py-3">
                        <StatusBadge status={diagnostic.eligibility_status} />
                      </td>
                      <td className="py-3">{diagnostic.percentage.toFixed(0)}%</td>
                      <td className="py-3">
                        {diagnostic.credit_current
                          ? formatCurrency(diagnostic.credit_current)
                          : '-'}
                      </td>
                      <td className="py-3 text-gray-500 text-sm">
                        {formatDate(diagnostic.created_at)}
                      </td>
                      <td className="py-3">
                        <Link href={`/admin/soumissions/${diagnostic.id}`}>
                          <Button variant="ghost" size="sm">
                            Voir
                          </Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Helper Components
function KPICard({
  title,
  value,
  icon,
  color
}: {
  title: string;
  value: string;
  icon: React.ReactNode;
  color: 'blue' | 'green' | 'purple' | 'amber';
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    amber: 'bg-amber-50 text-amber-600',
  };

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500 mb-1">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
          </div>
          <div className={`p-3 rounded-full ${colorClasses[color]}`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function EligibilityBar({
  label,
  count,
  total,
  color,
  icon
}: {
  label: string;
  count: number;
  total: number;
  color: string;
  icon: React.ReactNode;
}) {
  const percentage = total > 0 ? (count / total) * 100 : 0;

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-medium">{label}</span>
        </div>
        <span className="text-sm text-gray-600">{count} ({percentage.toFixed(0)}%)</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { label: string; className: string }> = {
    eligible: {
      label: 'Eligible',
      className: 'bg-green-100 text-green-700'
    },
    partial: {
      label: 'Partiel',
      className: 'bg-amber-100 text-amber-700'
    },
    not_eligible: {
      label: 'Non eligible',
      className: 'bg-red-100 text-red-700'
    }
  };

  const { label, className } = config[status] || config.not_eligible;

  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${className}`}>
      {label}
    </span>
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

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('fr-CA', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}
