'use client';

import React, { useState } from 'react';
import { DiagnosticResult, DiagnosticResponses } from '@/lib/cdaeia-types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Sparkles,
  Loader2,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  Target,
  Shield,
  Calendar,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

interface AIAnalysis {
  summary: string;
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  detailedRecommendations: {
    title: string;
    description: string;
    implementation: string;
    expectedOutcome: string;
  }[];
  riskAssessment: string;
  timeline: string;
}

interface AIAnalysisCardProps {
  result: DiagnosticResult;
  responses: DiagnosticResponses;
}

export function AIAnalysisCard({ result, responses }: AIAnalysisCardProps) {
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null);
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [expandedRec, setExpandedRec] = useState<number | null>(null);

  const handleAnalyze = async () => {
    setStatus('loading');
    setErrorMessage('');

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ responses, result }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Erreur lors de l\'analyse');
      }

      setAnalysis(data.analysis);
      setStatus('success');
    } catch (error) {
      console.error('Error:', error);
      const message = error instanceof Error ? error.message : 'Une erreur est survenue';
      setErrorMessage(message);
      setStatus('error');
    }
  };

  if (status === 'idle') {
    return (
      <Card className="border-purple-200 bg-gradient-to-r from-purple-50 to-indigo-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            Analyse IA Approfondie
          </CardTitle>
          <CardDescription>
            Obtenez une analyse personnalisee de votre situation par notre IA specialisee CDAEIA
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={handleAnalyze} className="gap-2 bg-purple-600 hover:bg-purple-700">
            <Sparkles className="w-4 h-4" />
            Lancer l'analyse IA
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (status === 'loading') {
    return (
      <Card className="border-purple-200">
        <CardContent className="pt-6">
          <div className="flex flex-col items-center justify-center py-8">
            <Loader2 className="w-8 h-8 text-purple-600 animate-spin mb-4" />
            <p className="text-gray-600">Analyse en cours...</p>
            <p className="text-sm text-gray-500 mt-2">
              Notre IA analyse votre situation et prepare des recommandations personnalisees
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (status === 'error') {
    return (
      <Card className="border-red-200">
        <CardContent className="pt-6">
          <div className="flex items-center gap-3 text-red-600">
            <AlertTriangle className="w-5 h-5" />
            <span>{errorMessage}</span>
          </div>
          <Button onClick={handleAnalyze} variant="outline" className="mt-4">
            Reessayer
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!analysis) return null;

  return (
    <div className="space-y-6">
      {/* Summary */}
      <Card className="border-purple-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            Analyse IA - Resume Executif
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 leading-relaxed">{analysis.summary}</p>
        </CardContent>
      </Card>

      {/* Strengths, Weaknesses, Opportunities */}
      <div className="grid md:grid-cols-3 gap-4">
        {/* Strengths */}
        <Card className="border-green-200">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base text-green-700">
              <CheckCircle className="w-4 h-4" />
              Forces
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {analysis.strengths.map((strength, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <CheckCircle className="w-3 h-3 text-green-500 mt-1 flex-shrink-0" />
                  <span>{strength}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Weaknesses */}
        <Card className="border-amber-200">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base text-amber-700">
              <AlertTriangle className="w-4 h-4" />
              Faiblesses
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {analysis.weaknesses.map((weakness, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <AlertTriangle className="w-3 h-3 text-amber-500 mt-1 flex-shrink-0" />
                  <span>{weakness}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Opportunities */}
        <Card className="border-blue-200">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base text-blue-700">
              <TrendingUp className="w-4 h-4" />
              Opportunites
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {analysis.opportunities.map((opportunity, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <TrendingUp className="w-3 h-3 text-blue-500 mt-1 flex-shrink-0" />
                  <span>{opportunity}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5 text-purple-600" />
            Recommandations Detaillees
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {analysis.detailedRecommendations.map((rec, index) => (
            <div
              key={index}
              className="border rounded-lg overflow-hidden"
            >
              <button
                className="w-full p-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
                onClick={() => setExpandedRec(expandedRec === index ? null : index)}
              >
                <span className="font-medium">{rec.title}</span>
                {expandedRec === index ? (
                  <ChevronUp className="w-4 h-4 text-gray-500" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-gray-500" />
                )}
              </button>
              {expandedRec === index && (
                <div className="px-4 pb-4 space-y-3 border-t bg-gray-50">
                  <div className="pt-3">
                    <h4 className="text-sm font-medium text-gray-700 mb-1">Description</h4>
                    <p className="text-sm text-gray-600">{rec.description}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-1">Implementation</h4>
                    <p className="text-sm text-gray-600">{rec.implementation}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-1">Resultat Attendu</h4>
                    <p className="text-sm text-gray-600">{rec.expectedOutcome}</p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Risk Assessment & Timeline */}
      <div className="grid md:grid-cols-2 gap-4">
        <Card className="border-orange-200">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <Shield className="w-4 h-4 text-orange-600" />
              Evaluation des Risques
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">{analysis.riskAssessment}</p>
          </CardContent>
        </Card>

        <Card className="border-indigo-200">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <Calendar className="w-4 h-4 text-indigo-600" />
              Calendrier Suggere
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">{analysis.timeline}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
