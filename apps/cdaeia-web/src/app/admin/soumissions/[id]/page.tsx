'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import {
  ArrowLeft,
  Building2,
  Mail,
  Calendar,
  DollarSign,
  TrendingUp,
  CheckCircle,
  AlertTriangle,
  XCircle,
  FileText,
  Brain,
  RefreshCw,
  Send
} from 'lucide-react';

interface DiagnosticDetail {
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

interface AIAnalysis {
  summary: string;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  nextSteps: string[];
}

export default function SoumissionDetailPage() {
  const params = useParams();
  const id = params?.id as string;

  const [diagnostic, setDiagnostic] = useState<DiagnosticDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysis | null>(null);
  const [analyzingAI, setAnalyzingAI] = useState(false);

  useEffect(() => {
    if (id) {
      fetchDiagnostic();
    }
  }, [id]);

  const fetchDiagnostic = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/admin/diagnostics/${id}`);
      if (!response.ok) throw new Error('Erreur');
      const data = await response.json();
      setDiagnostic(data);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const runAIAnalysis = async () => {
    if (!diagnostic) return;
    setAnalyzingAI(true);
    try {
      const response = await fetch('/api/admin/analyze-diagnostic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ diagnostic }),
      });
      if (!response.ok) throw new Error('Erreur');
      const data = await response.json();
      setAiAnalysis(data);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setAnalyzingAI(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!diagnostic) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Diagnostic non trouve</h2>
        <Link href="/admin/soumissions">
          <Button>Retour a la liste</Button>
        </Link>
      </div>
    );
  }

  const statusConfig: Record<string, { label: string; className: string; icon: React.ReactNode }> = {
    eligible: {
      label: 'Eligible',
      className: 'bg-green-100 text-green-700 border-green-200',
      icon: <CheckCircle className="w-5 h-5" />
    },
    partial: {
      label: 'Partiellement eligible',
      className: 'bg-amber-100 text-amber-700 border-amber-200',
      icon: <AlertTriangle className="w-5 h-5" />
    },
    not_eligible: {
      label: 'Non eligible',
      className: 'bg-red-100 text-red-700 border-red-200',
      icon: <XCircle className="w-5 h-5" />
    }
  };

  const status = statusConfig[diagnostic.eligibility_status] || statusConfig.not_eligible;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/admin/soumissions">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Retour
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{diagnostic.company_name}</h1>
            <p className="text-gray-600">Diagnostic #{diagnostic.id.slice(0, 8)}</p>
          </div>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={runAIAnalysis} disabled={analyzingAI}>
            {analyzingAI ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Brain className="w-4 h-4 mr-2" />
            )}
            Analyse IA
          </Button>
          {diagnostic.email && (
            <Button>
              <Send className="w-4 h-4 mr-2" />
              Contacter
            </Button>
          )}
        </div>
      </div>

      {/* Status Banner */}
      <div className={`p-4 rounded-lg border ${status.className}`}>
        <div className="flex items-center gap-3">
          {status.icon}
          <div>
            <div className="font-semibold">{status.label}</div>
            <div className="text-sm opacity-80">
              Score: {diagnostic.percentage.toFixed(0)}% ({diagnostic.total_score}/{diagnostic.max_score})
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Company Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Building2 className="w-5 h-5" />
                Informations de l'entreprise
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <InfoItem label="Nom" value={diagnostic.company_name} />
                <InfoItem label="NEQ" value={diagnostic.company_neq || 'Non fourni'} />
                <InfoItem
                  label="Email"
                  value={diagnostic.email || 'Non fourni'}
                  icon={diagnostic.email ? <Mail className="w-4 h-4 text-gray-400" /> : undefined}
                />
                <InfoItem
                  label="Date du diagnostic"
                  value={formatDate(diagnostic.created_at)}
                  icon={<Calendar className="w-4 h-4 text-gray-400" />}
                />
              </div>
            </CardContent>
          </Card>

          {/* Responses */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Reponses au questionnaire
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(diagnostic.responses).map(([key, value]) => (
                  <div key={key} className="border-b pb-3 last:border-0">
                    <div className="text-sm text-gray-500 mb-1">
                      {formatQuestionKey(key)}
                    </div>
                    <div className="font-medium">
                      {formatResponseValue(value)}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* AI Analysis */}
          {aiAnalysis && (
            <Card className="border-purple-200 bg-purple-50/50">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2 text-purple-700">
                  <Brain className="w-5 h-5" />
                  Analyse IA Avancee
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h4 className="font-semibold mb-2">Resume</h4>
                  <p className="text-gray-700">{aiAnalysis.summary}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold text-green-700 mb-2">Points forts</h4>
                    <ul className="space-y-1">
                      {aiAnalysis.strengths.map((s, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm">
                          <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold text-amber-700 mb-2">Points a ameliorer</h4>
                    <ul className="space-y-1">
                      {aiAnalysis.weaknesses.map((w, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm">
                          <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                          {w}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-blue-700 mb-2">Recommandations</h4>
                  <ul className="space-y-2">
                    {aiAnalysis.recommendations.map((r, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm bg-white p-2 rounded">
                        <span className="bg-blue-100 text-blue-700 rounded-full w-5 h-5 flex items-center justify-center flex-shrink-0 text-xs font-medium">
                          {i + 1}
                        </span>
                        {r}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold mb-2">Prochaines etapes</h4>
                  <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700">
                    {aiAnalysis.nextSteps.map((step, i) => (
                      <li key={i}>{step}</li>
                    ))}
                  </ol>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column - Financial Summary */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <DollarSign className="w-5 h-5" />
                Resume financier
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <div className="text-sm text-gray-500 mb-1">Credit actuel estime</div>
                <div className="text-3xl font-bold text-gray-900">
                  {diagnostic.credit_current
                    ? formatCurrency(diagnostic.credit_current)
                    : 'N/A'}
                </div>
              </div>

              <div>
                <div className="text-sm text-gray-500 mb-1">Credit apres optimisation</div>
                <div className="text-3xl font-bold text-blue-600">
                  {diagnostic.credit_optimized
                    ? formatCurrency(diagnostic.credit_optimized)
                    : 'N/A'}
                </div>
              </div>

              <div className="pt-4 border-t">
                <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                  <TrendingUp className="w-4 h-4" />
                  Gain potentiel
                </div>
                <div className="text-2xl font-bold text-green-600">
                  +{formatCurrency(diagnostic.credit_gain)}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Score detaille</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="relative pt-1">
                <div className="flex mb-2 items-center justify-between">
                  <div className="text-sm font-semibold text-gray-700">
                    {diagnostic.percentage.toFixed(0)}%
                  </div>
                </div>
                <div className="overflow-hidden h-4 text-xs flex rounded-full bg-gray-200">
                  <div
                    style={{ width: `${diagnostic.percentage}%` }}
                    className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center transition-all duration-500 ${
                      diagnostic.percentage >= 80 ? 'bg-green-500' :
                      diagnostic.percentage >= 50 ? 'bg-amber-500' : 'bg-red-500'
                    }`}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0</span>
                  <span>50</span>
                  <span>100</span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t text-sm text-gray-600">
                <div className="flex justify-between mb-2">
                  <span>Score obtenu</span>
                  <span className="font-medium">{diagnostic.total_score}</span>
                </div>
                <div className="flex justify-between">
                  <span>Score maximum</span>
                  <span className="font-medium">{diagnostic.max_score}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function InfoItem({
  label,
  value,
  icon
}: {
  label: string;
  value: string;
  icon?: React.ReactNode;
}) {
  return (
    <div>
      <div className="text-sm text-gray-500 mb-1">{label}</div>
      <div className="font-medium flex items-center gap-2">
        {icon}
        {value}
      </div>
    </div>
  );
}

function formatQuestionKey(key: string): string {
  return key
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, str => str.toUpperCase());
}

function formatResponseValue(value: unknown): string {
  if (value === null || value === undefined) return 'Non repondu';
  if (typeof value === 'boolean') return value ? 'Oui' : 'Non';
  if (Array.isArray(value)) return value.join(', ');
  if (typeof value === 'number') {
    if (value >= 1000) return formatCurrency(value);
    return value.toString();
  }
  return String(value);
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
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}
