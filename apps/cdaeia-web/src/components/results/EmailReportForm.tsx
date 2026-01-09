'use client';

import React, { useState } from 'react';
import { DiagnosticResult, DiagnosticResponses } from '@/lib/cdaeia-types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Mail, CheckCircle, Loader2, AlertCircle } from 'lucide-react';

interface EmailReportFormProps {
  result: DiagnosticResult;
  responses: DiagnosticResponses;
}

export function EmailReportForm({ result, responses }: EmailReportFormProps) {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !email.includes('@')) {
      setErrorMessage('Veuillez entrer une adresse email valide');
      setStatus('error');
      return;
    }

    setStatus('loading');
    setErrorMessage('');

    try {
      const response = await fetch('/api/send-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          companyName: responses.company_name as string || 'Votre entreprise',
          result: {
            totalScore: result.totalScore,
            maxScore: result.maxScore,
            percentage: result.percentage,
            eligibilityStatus: result.eligibilityStatus,
            statusMessage: result.statusMessage,
            creditCurrent: result.creditCurrent,
            creditOptimized: result.creditOptimized,
            creditGain: result.creditGain,
          },
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Erreur lors de l\'envoi');
      }

      setStatus('success');
    } catch (error) {
      console.error('Error sending email:', error);
      const message = error instanceof Error ? error.message : 'Une erreur est survenue. Veuillez reessayer.';
      setErrorMessage(message);
      setStatus('error');
    }
  };

  if (status === 'success') {
    return (
      <Card className="border-green-200 bg-green-50">
        <CardContent className="pt-6">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <div>
              <p className="font-medium text-green-800">Email envoye avec succes!</p>
              <p className="text-sm text-green-600">
                Verifiez votre boite de reception a {email}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Mail className="w-5 h-5" />
          Recevoir le rapport par email
        </CardTitle>
        <CardDescription>
          Recevez un resume de votre diagnostic directement dans votre boite mail
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Adresse email</Label>
            <Input
              id="email"
              type="email"
              placeholder="votre@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={status === 'loading'}
            />
          </div>

          {status === 'error' && errorMessage && (
            <div className="flex items-center gap-2 text-red-600 text-sm">
              <AlertCircle className="w-4 h-4" />
              {errorMessage}
            </div>
          )}

          <Button type="submit" disabled={status === 'loading'} className="w-full gap-2">
            {status === 'loading' ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Envoi en cours...
              </>
            ) : (
              <>
                <Mail className="w-4 h-4" />
                Envoyer le rapport
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
