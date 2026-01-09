'use client';

import React, { useState } from 'react';
import { pdf } from '@react-pdf/renderer';
import { DiagnosticPDF } from '@/lib/pdf-generator';
import { DiagnosticResult, DiagnosticResponses } from '@/lib/cdaeia-types';
import { Button } from '@/components/ui/button';
import { Download, Loader2 } from 'lucide-react';

interface PDFDownloadButtonProps {
  result: DiagnosticResult;
  responses: DiagnosticResponses;
}

export function PDFDownloadButton({ result, responses }: PDFDownloadButtonProps) {
  const [isGenerating, setIsGenerating] = useState(false);

  const handleDownload = async () => {
    setIsGenerating(true);
    try {
      const blob = await pdf(<DiagnosticPDF result={result} responses={responses} />).toBlob();

      // Create download link
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      // Generate filename with company name and date
      const companyName = (responses.company_name as string) || 'entreprise';
      const date = new Date().toISOString().split('T')[0];
      const sanitizedName = companyName.toLowerCase().replace(/[^a-z0-9]/g, '_');
      link.download = `diagnostic_cdaeia_${sanitizedName}_${date}.pdf`;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Erreur lors de la generation du PDF:', error);
      alert('Une erreur est survenue lors de la generation du PDF. Veuillez reessayer.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Button
      variant="outline"
      onClick={handleDownload}
      disabled={isGenerating}
      className="gap-2"
    >
      {isGenerating ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin" />
          Generation...
        </>
      ) : (
        <>
          <Download className="w-4 h-4" />
          Telecharger PDF
        </>
      )}
    </Button>
  );
}
