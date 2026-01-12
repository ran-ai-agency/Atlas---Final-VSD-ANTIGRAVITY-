'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Settings,
  Database,
  Brain,
  Mail,
  Shield,
  CheckCircle,
  XCircle,
  RefreshCw,
  ExternalLink
} from 'lucide-react';

interface ServiceStatus {
  name: string;
  status: 'connected' | 'disconnected' | 'checking';
  details?: string;
}

export default function ParametresPage() {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'Supabase (Base de donnees)', status: 'checking' },
    { name: 'Claude API (Analyse IA)', status: 'checking' },
    { name: 'SMTP (Envoi emails)', status: 'disconnected', details: 'Non configure' },
  ]);
  const [checking, setChecking] = useState(false);

  const checkServices = async () => {
    setChecking(true);
    setServices(prev => prev.map(s => ({ ...s, status: 'checking' as const })));

    // Check Supabase
    try {
      const res = await fetch('/api/admin/stats');
      setServices(prev => prev.map(s =>
        s.name.includes('Supabase')
          ? { ...s, status: res.ok ? 'connected' : 'disconnected', details: res.ok ? 'Connecte' : 'Erreur de connexion' }
          : s
      ));
    } catch {
      setServices(prev => prev.map(s =>
        s.name.includes('Supabase')
          ? { ...s, status: 'disconnected', details: 'Non accessible' }
          : s
      ));
    }

    // Check Claude API
    try {
      const res = await fetch('/api/admin/check-ai');
      const data = await res.json();
      setServices(prev => prev.map(s =>
        s.name.includes('Claude')
          ? { ...s, status: data.configured ? 'connected' : 'disconnected', details: data.message }
          : s
      ));
    } catch {
      setServices(prev => prev.map(s =>
        s.name.includes('Claude')
          ? { ...s, status: 'disconnected', details: 'Non accessible' }
          : s
      ));
    }

    // SMTP is not configured
    setServices(prev => prev.map(s =>
      s.name.includes('SMTP')
        ? { ...s, status: 'disconnected', details: 'Configuration requise' }
        : s
    ));

    setChecking(false);
  };

  React.useEffect(() => {
    checkServices();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'disconnected':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'checking':
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return null;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'connected':
        return <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700">Connecte</span>;
      case 'disconnected':
        return <span className="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-700">Deconnecte</span>;
      case 'checking':
        return <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-700">Verification...</span>;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Parametres</h1>
          <p className="text-gray-600">Configuration du systeme CDAEIA Admin</p>
        </div>
        <Button variant="outline" onClick={checkServices} disabled={checking}>
          {checking ? (
            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4 mr-2" />
          )}
          Verifier les services
        </Button>
      </div>

      {/* Services Status */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Database className="w-5 h-5" />
            Etat des services
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {services.map((service, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  {getStatusIcon(service.status)}
                  <div>
                    <p className="font-medium">{service.name}</p>
                    {service.details && (
                      <p className="text-sm text-gray-500">{service.details}</p>
                    )}
                  </div>
                </div>
                {getStatusBadge(service.status)}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Configuration Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Supabase Config */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Database className="w-5 h-5 text-green-600" />
              Supabase
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-600">
              Base de donnees PostgreSQL pour stocker les diagnostics.
            </p>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Variable d'environnement:</span>
                <code className="bg-gray-100 px-2 py-0.5 rounded text-xs">NEXT_PUBLIC_SUPABASE_URL</code>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Cle API:</span>
                <code className="bg-gray-100 px-2 py-0.5 rounded text-xs">NEXT_PUBLIC_SUPABASE_ANON_KEY</code>
              </div>
            </div>
            <Button variant="outline" size="sm" className="w-full" asChild>
              <a href="https://supabase.com/dashboard" target="_blank" rel="noopener noreferrer">
                <ExternalLink className="w-4 h-4 mr-2" />
                Ouvrir Supabase
              </a>
            </Button>
          </CardContent>
        </Card>

        {/* Claude API Config */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-600" />
              Claude API (Anthropic)
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-600">
              Intelligence artificielle pour l'analyse des diagnostics.
            </p>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Variable d'environnement:</span>
                <code className="bg-gray-100 px-2 py-0.5 rounded text-xs">ANTHROPIC_API_KEY</code>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Modele:</span>
                <code className="bg-gray-100 px-2 py-0.5 rounded text-xs">claude-sonnet-4-20250514</code>
              </div>
            </div>
            <Button variant="outline" size="sm" className="w-full" asChild>
              <a href="https://console.anthropic.com" target="_blank" rel="noopener noreferrer">
                <ExternalLink className="w-4 h-4 mr-2" />
                Ouvrir Anthropic Console
              </a>
            </Button>
          </CardContent>
        </Card>

        {/* Email Config */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Mail className="w-5 h-5 text-blue-600" />
              Service Email
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-600">
              Configuration SMTP pour l'envoi des rapports par email.
            </p>
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <p className="text-sm text-amber-700">
                Non configure. Ajoutez les variables SMTP pour activer l'envoi d'emails.
              </p>
            </div>
            <div className="space-y-2 text-sm text-gray-500">
              <code className="block bg-gray-100 px-2 py-1 rounded text-xs">SMTP_HOST</code>
              <code className="block bg-gray-100 px-2 py-1 rounded text-xs">SMTP_PORT</code>
              <code className="block bg-gray-100 px-2 py-1 rounded text-xs">SMTP_USER</code>
              <code className="block bg-gray-100 px-2 py-1 rounded text-xs">SMTP_PASSWORD</code>
            </div>
          </CardContent>
        </Card>

        {/* Security */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Shield className="w-5 h-5 text-red-600" />
              Securite
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-600">
              Configuration de la securite et de l'authentification admin.
            </p>
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <p className="text-sm text-amber-700">
                L'acces admin n'est pas securise. Implementez une authentification pour la production.
              </p>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-gray-500">Authentification:</span>
                <span className="text-amber-600 font-medium">Non active</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500">Protection CSRF:</span>
                <span className="text-green-600 font-medium">Active (Next.js)</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Informations systeme
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Version</p>
              <p className="font-medium">1.0.0</p>
            </div>
            <div>
              <p className="text-gray-500">Framework</p>
              <p className="font-medium">Next.js 14</p>
            </div>
            <div>
              <p className="text-gray-500">Base de donnees</p>
              <p className="font-medium">Supabase PostgreSQL</p>
            </div>
            <div>
              <p className="text-gray-500">IA</p>
              <p className="font-medium">Claude Sonnet 4</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
