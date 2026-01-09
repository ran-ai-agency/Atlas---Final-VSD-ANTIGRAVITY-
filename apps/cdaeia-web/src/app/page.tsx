'use client';

import React, { useState } from 'react';
import { DiagnosticWizard } from '@/components/questionnaire';
import { DiagnosticResults } from '@/components/results';
import { DiagnosticResult, DiagnosticResponses } from '@/lib/cdaeia-types';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  CheckCircle,
  TrendingUp,
  FileText,
  Clock,
  ArrowRight,
  Building2,
  DollarSign,
  Cpu
} from 'lucide-react';

type AppState = 'landing' | 'questionnaire' | 'results';

export default function Home() {
  const [appState, setAppState] = useState<AppState>('landing');
  const [result, setResult] = useState<DiagnosticResult | null>(null);
  const [responses, setResponses] = useState<DiagnosticResponses>({});
  const [diagnosticId, setDiagnosticId] = useState<string | null>(null);

  const handleStartDiagnostic = () => {
    setAppState('questionnaire');
  };

  const handleComplete = async (diagnosticResult: DiagnosticResult, diagnosticResponses: DiagnosticResponses) => {
    setResult(diagnosticResult);
    setResponses(diagnosticResponses);
    setAppState('results');

    // Save diagnostic to Supabase in the background
    try {
      const companyName = diagnosticResponses['company_name'] as string || 'Entreprise non specifiee';
      const companyNeq = diagnosticResponses['company_neq'] as string;
      const email = diagnosticResponses['email'] as string;

      const response = await fetch('/api/diagnostic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          companyName,
          companyNeq,
          email,
          responses: diagnosticResponses,
          result: diagnosticResult,
        }),
      });

      const data = await response.json();
      if (data.id) {
        setDiagnosticId(data.id);
        console.log('Diagnostic saved with ID:', data.id);
      }
    } catch (error) {
      console.error('Failed to save diagnostic:', error);
      // Non-blocking - user still sees results even if save fails
    }
  };

  const handleRestart = () => {
    setResult(null);
    setResponses({});
    setDiagnosticId(null);
    setAppState('landing');
  };

  const handleRequestConsultation = () => {
    const subject = encodeURIComponent('Demande de consultation CDAEIA');
    const body = encodeURIComponent(
      `Bonjour,\n\nJ'ai complete le diagnostic CDAEIA en ligne et j'aimerais planifier une consultation pour discuter de mes resultats.\n\nMerci,`
    );
    window.open(`mailto:info@ran-ai-agency.ca?subject=${subject}&body=${body}`, '_blank');
  };

  // Landing Page
  if (appState === 'landing') {
    return (
      <div className="py-12 px-4 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="max-w-4xl mx-auto text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-6">
            <Cpu className="w-4 h-4" />
            Nouveau credit d'impot 2026
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Diagnostic CDAEIA
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Evaluez gratuitement votre eligibilite au nouveau{' '}
            <span className="font-semibold text-blue-600">
              Credit d'impot pour le Developpement des Affaires Electroniques integrant l'IA
            </span>
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              onClick={handleStartDiagnostic}
              className="gap-2 text-lg px-8 py-6"
            >
              Commencer le diagnostic
              <ArrowRight className="w-5 h-5" />
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="gap-2 text-lg px-8 py-6"
              onClick={() => window.open('https://www.ran-ai-agency.ca', '_blank')}
            >
              En savoir plus
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <Card>
            <CardContent className="pt-6 text-center">
              <div className="text-4xl font-bold text-blue-600 mb-2">30%</div>
              <div className="text-gray-600">Credit d'impot sur les salaires eligibles</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 text-center">
              <div className="text-4xl font-bold text-green-600 mb-2">22%</div>
              <div className="text-gray-600">Portion remboursable directement</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6 text-center">
              <div className="text-4xl font-bold text-purple-600 mb-2">2026</div>
              <div className="text-gray-600">En vigueur des janvier</div>
            </CardContent>
          </Card>
        </div>

        {/* Features */}
        <div className="max-w-4xl mx-auto mb-16">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-8">
            Ce que vous obtiendrez
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FeatureCard
              icon={<CheckCircle className="w-6 h-6 text-green-600" />}
              title="Evaluation d'eligibilite"
              description="Verifiez si votre entreprise repond aux criteres du CDAEIA: tests de revenus, effectifs, allocation du temps."
            />
            <FeatureCard
              icon={<DollarSign className="w-6 h-6 text-blue-600" />}
              title="Estimation du credit"
              description="Calculez votre credit d'impot potentiel base sur votre masse salariale et vos activites IA."
            />
            <FeatureCard
              icon={<TrendingUp className="w-6 h-6 text-purple-600" />}
              title="Recommandations"
              description="Recevez des conseils personnalises pour maximiser votre credit et ameliorer votre eligibilite."
            />
            <FeatureCard
              icon={<FileText className="w-6 h-6 text-amber-600" />}
              title="Rapport detaille"
              description="Obtenez un rapport complet avec plan d'action et prochaines etapes concretes."
            />
          </div>
        </div>

        {/* Who is this for */}
        <div className="max-w-4xl mx-auto mb-16">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-8">
            Pour qui?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="border-2 border-dashed">
              <CardContent className="pt-6">
                <Building2 className="w-8 h-8 text-blue-600 mb-4" />
                <h3 className="font-semibold text-gray-900 mb-2">PME technologiques</h3>
                <p className="text-sm text-gray-600">
                  Entreprises de logiciels, SaaS, consultation TI avec 6+ employes
                </p>
              </CardContent>
            </Card>
            <Card className="border-2 border-dashed">
              <CardContent className="pt-6">
                <Cpu className="w-8 h-8 text-purple-600 mb-4" />
                <h3 className="font-semibold text-gray-900 mb-2">Integrant l'IA</h3>
                <p className="text-sm text-gray-600">
                  Developpement ML, NLP, computer vision, analytique predictive
                </p>
              </CardContent>
            </Card>
            <Card className="border-2 border-dashed">
              <CardContent className="pt-6">
                <DollarSign className="w-8 h-8 text-green-600 mb-4" />
                <h3 className="font-semibold text-gray-900 mb-2">Cherchant des credits</h3>
                <p className="text-sm text-gray-600">
                  Optimiser la fiscalite et financer la croissance de l'entreprise
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Time estimate */}
        <div className="max-w-2xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 text-gray-600">
            <Clock className="w-5 h-5" />
            <span>Le diagnostic prend environ 10-15 minutes</span>
          </div>
        </div>
      </div>
    );
  }

  // Questionnaire
  if (appState === 'questionnaire') {
    return (
      <div className="py-8 px-4 sm:px-6 lg:px-8">
        <DiagnosticWizard onComplete={handleComplete} />
      </div>
    );
  }

  // Results
  if (appState === 'results' && result) {
    return (
      <div className="py-8 px-4 sm:px-6 lg:px-8">
        <DiagnosticResults
          result={result}
          responses={responses}
          onRestart={handleRestart}
          onRequestConsultation={handleRequestConsultation}
        />
      </div>
    );
  }

  return null;
}

// Feature Card Component
function FeatureCard({
  icon,
  title,
  description
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0">{icon}</div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
            <p className="text-sm text-gray-600">{description}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
