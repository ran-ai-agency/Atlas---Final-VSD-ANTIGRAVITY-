'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { DiagnosticResult, DiagnosticResponses, EligibilityStatus, Priority } from '@/lib/cdaeia-types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn, formatCurrency, formatPercentage } from '@/lib/utils';
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  TrendingUp,
  DollarSign,
  Download,
  Mail,
  RefreshCw,
  ChevronRight,
  Target,
  AlertCircle,
  Lightbulb,
  Loader2
} from 'lucide-react';

// Dynamic import for PDF component to avoid SSR issues
const PDFDownloadButton = dynamic(
  () => import('./PDFDownloadButton').then(mod => mod.PDFDownloadButton),
  {
    ssr: false,
    loading: () => (
      <Button variant="outline" disabled className="gap-2">
        <Loader2 className="w-4 h-4 animate-spin" />
        Chargement...
      </Button>
    ),
  }
);

// Dynamic import for Email form
const EmailReportForm = dynamic(
  () => import('./EmailReportForm').then(mod => mod.EmailReportForm),
  { ssr: false }
);

// Dynamic import for AI Analysis
const AIAnalysisCard = dynamic(
  () => import('./AIAnalysisCard').then(mod => mod.AIAnalysisCard),
  { ssr: false }
);

interface DiagnosticResultsProps {
  result: DiagnosticResult;
  responses: DiagnosticResponses;
  onRestart: () => void;
  onRequestConsultation?: () => void;
}

const STATUS_CONFIG: Record<EligibilityStatus, { icon: React.ReactNode; color: string; bgColor: string; label: string }> = {
  eligible: {
    icon: <CheckCircle className="w-8 h-8" />,
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    label: 'ELIGIBLE'
  },
  partial: {
    icon: <AlertTriangle className="w-8 h-8" />,
    color: 'text-amber-600',
    bgColor: 'bg-amber-100',
    label: 'PARTIELLEMENT ELIGIBLE'
  },
  not_eligible: {
    icon: <XCircle className="w-8 h-8" />,
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    label: 'NON ELIGIBLE'
  }
};

const PRIORITY_CONFIG: Record<Priority, { color: string; label: string }> = {
  high: { color: 'bg-red-100 text-red-700 border-red-200', label: 'Haute' },
  medium: { color: 'bg-amber-100 text-amber-700 border-amber-200', label: 'Moyenne' },
  low: { color: 'bg-blue-100 text-blue-700 border-blue-200', label: 'Basse' }
};

export function DiagnosticResults({
  result,
  responses,
  onRestart,
  onRequestConsultation
}: DiagnosticResultsProps) {
  const statusConfig = STATUS_CONFIG[result.eligibilityStatus];
  const companyName = responses.company_name as string || 'Votre entreprise';

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Diagnostic CDAEIA
        </h1>
        <p className="text-gray-600">
          Resultats pour {companyName}
        </p>
      </div>

      {/* Main Score Card */}
      <Card className={cn('border-2', statusConfig.color.replace('text-', 'border-'))}>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row items-center gap-6">
            {/* Status Icon */}
            <div className={cn('p-4 rounded-full', statusConfig.bgColor, statusConfig.color)}>
              {statusConfig.icon}
            </div>

            {/* Score */}
            <div className="flex-1 text-center md:text-left">
              <div className="text-4xl font-bold text-gray-900 mb-1">
                {result.totalScore} / {result.maxScore}
              </div>
              <div className={cn('text-lg font-semibold', statusConfig.color)}>
                {statusConfig.label}
              </div>
              <p className="text-gray-600 mt-2">
                {result.statusMessage}
              </p>
            </div>

            {/* Progress Circle */}
            <div className="text-center">
              <div className="relative w-24 h-24">
                <svg className="w-24 h-24 transform -rotate-90">
                  <circle
                    cx="48"
                    cy="48"
                    r="40"
                    stroke="#e5e7eb"
                    strokeWidth="8"
                    fill="none"
                  />
                  <circle
                    cx="48"
                    cy="48"
                    r="40"
                    stroke={result.percentage >= 70 ? '#22c55e' : result.percentage >= 50 ? '#f59e0b' : '#ef4444'}
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${2 * Math.PI * 40}`}
                    strokeDashoffset={`${2 * Math.PI * 40 * (1 - result.percentage / 100)}`}
                    className="transition-all duration-1000"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold">{Math.round(result.percentage)}%</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Credit Estimation */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Current Credit */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <DollarSign className="w-5 h-5 text-gray-600" />
              Credit Actuel Estime
            </CardTitle>
            <CardDescription>Base sur votre situation actuelle</CardDescription>
          </CardHeader>
          <CardContent>
            {result.creditCurrent ? (
              <div className="space-y-3">
                <div className="text-3xl font-bold text-gray-900">
                  {formatCurrency(result.creditCurrent.totalCredit)}
                  <span className="text-lg font-normal text-gray-500">/an</span>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Employes eligibles</span>
                    <span className="font-medium">{result.creditCurrent.eligibleEmployees}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Masse salariale eligible</span>
                    <span className="font-medium">{formatCurrency(result.creditCurrent.netEligibleSalary)}</span>
                  </div>
                  <div className="flex justify-between text-green-600">
                    <span>Portion remboursable (22%)</span>
                    <span className="font-medium">{formatCurrency(result.creditCurrent.refundablePortion)}</span>
                  </div>
                  <div className="flex justify-between text-blue-600">
                    <span>Portion non-remboursable (8%)</span>
                    <span className="font-medium">{formatCurrency(result.creditCurrent.nonRefundablePortion)}</span>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">Non applicable</p>
            )}
          </CardContent>
        </Card>

        {/* Optimized Credit */}
        <Card className="border-green-200 bg-green-50/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <TrendingUp className="w-5 h-5 text-green-600" />
              Credit Optimise Potentiel
            </CardTitle>
            <CardDescription>Apres mise en oeuvre des recommandations</CardDescription>
          </CardHeader>
          <CardContent>
            {result.creditOptimized ? (
              <div className="space-y-3">
                <div className="text-3xl font-bold text-green-600">
                  {formatCurrency(result.creditOptimized.totalCredit)}
                  <span className="text-lg font-normal text-green-500">/an</span>
                </div>
                {result.creditGain > 0 && (
                  <div className="p-3 bg-green-100 rounded-lg">
                    <div className="flex items-center gap-2 text-green-700">
                      <TrendingUp className="w-5 h-5" />
                      <span className="font-semibold">
                        Gain potentiel: +{formatCurrency(result.creditGain)}/an
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-500">Non applicable</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Score Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            Detail des Scores par Critere
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {result.scoreBreakdown.map((breakdown) => {
            const percentage = breakdown.maxScore > 0
              ? (breakdown.score / breakdown.maxScore) * 100
              : 0;
            const statusIcon = breakdown.status === 'pass'
              ? <CheckCircle className="w-4 h-4 text-green-600" />
              : breakdown.status === 'warning'
              ? <AlertTriangle className="w-4 h-4 text-amber-600" />
              : <XCircle className="w-4 h-4 text-red-600" />;

            return (
              <div key={breakdown.criterion} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {statusIcon}
                    <span className="font-medium">{breakdown.criterion}</span>
                  </div>
                  <span className="text-sm font-medium">
                    {breakdown.score} / {breakdown.maxScore}
                  </span>
                </div>
                <Progress
                  value={percentage}
                  className={cn(
                    'h-2',
                    breakdown.status === 'pass' ? '[&>div]:bg-green-500' :
                    breakdown.status === 'warning' ? '[&>div]:bg-amber-500' :
                    '[&>div]:bg-red-500'
                  )}
                />
                <p className="text-sm text-gray-600">{breakdown.details}</p>
              </div>
            );
          })}
        </CardContent>
      </Card>

      {/* Critical Issues */}
      {result.criticalIssues.length > 0 && (
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-700">
              <AlertCircle className="w-5 h-5" />
              Problemes Critiques
            </CardTitle>
            <CardDescription>
              Ces problemes doivent etre resolus pour devenir eligible
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {result.criticalIssues.map((issue, index) => (
                <li key={index} className="flex items-start gap-2 text-red-700">
                  <XCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>{issue}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Warnings */}
      {result.warnings.length > 0 && (
        <Card className="border-amber-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-amber-700">
              <AlertTriangle className="w-5 h-5" />
              Avertissements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {result.warnings.map((warning, index) => (
                <li key={index} className="flex items-start gap-2 text-amber-700">
                  <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>{warning}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Recommendations */}
      {result.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-amber-500" />
              Recommandations
            </CardTitle>
            <CardDescription>
              Actions pour ameliorer votre eligibilite et maximiser vos credits
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {result.recommendations.slice(0, 5).map((rec) => {
              const priorityConfig = PRIORITY_CONFIG[rec.priority];
              return (
                <div
                  key={rec.id}
                  className="p-4 border rounded-lg hover:shadow-sm transition-shadow"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={cn(
                          'px-2 py-0.5 text-xs font-medium rounded border',
                          priorityConfig.color
                        )}>
                          Priorite {priorityConfig.label}
                        </span>
                        <span className="text-sm text-gray-500">
                          Impact: +{rec.expectedImpact} pts
                        </span>
                      </div>
                      <h4 className="font-medium text-gray-900">{rec.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                      {rec.actionItems.length > 0 && (
                        <ul className="mt-2 space-y-1">
                          {rec.actionItems.slice(0, 3).map((action, i) => (
                            <li key={i} className="flex items-center gap-2 text-sm text-gray-600">
                              <ChevronRight className="w-3 h-3" />
                              {action}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                    <div className="text-right text-sm text-gray-500">
                      ~{rec.estimatedWeeks} sem.
                    </div>
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>
      )}

      {/* AI Analysis */}
      <AIAnalysisCard result={result} responses={responses} />

      {/* Email Form */}
      <EmailReportForm result={result} responses={responses} />

      {/* Actions */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">
                Prochaines etapes
              </h3>
              <p className="text-sm text-gray-600">
                Telechargez votre rapport complet ou demandez une consultation gratuite
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button variant="outline" onClick={onRestart} className="gap-2">
                <RefreshCw className="w-4 h-4" />
                Nouveau diagnostic
              </Button>
              <PDFDownloadButton result={result} responses={responses} />
              {onRequestConsultation && (
                <Button onClick={onRequestConsultation} className="gap-2">
                  <Mail className="w-4 h-4" />
                  Demander une consultation
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Footer */}
      <div className="text-center text-sm text-gray-500 py-4">
        <p>
          Ce diagnostic est fourni a titre informatif et ne constitue pas un avis fiscal ou juridique.
        </p>
        <p className="mt-1">
          Ran.AI Agency - Experts en transformation IA | info@ran-ai-agency.ca
        </p>
      </div>
    </div>
  );
}
