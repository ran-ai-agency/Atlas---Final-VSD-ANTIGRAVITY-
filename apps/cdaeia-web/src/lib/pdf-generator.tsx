import React from 'react';
import {
  Document,
  Page,
  Text,
  View,
  StyleSheet,
  Font,
} from '@react-pdf/renderer';
import { DiagnosticResult, DiagnosticResponses, EligibilityStatus, Priority } from './cdaeia-types';

// Styles pour le PDF
const styles = StyleSheet.create({
  page: {
    padding: 40,
    fontSize: 10,
    fontFamily: 'Helvetica',
  },
  header: {
    marginBottom: 20,
    borderBottom: '2 solid #2563eb',
    paddingBottom: 15,
  },
  logo: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2563eb',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 12,
    color: '#6b7280',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 10,
    marginTop: 20,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 20,
    marginBottom: 10,
    backgroundColor: '#f3f4f6',
    padding: 8,
  },
  row: {
    flexDirection: 'row',
    marginBottom: 5,
  },
  label: {
    width: '40%',
    color: '#6b7280',
  },
  value: {
    width: '60%',
    fontWeight: 'bold',
  },
  scoreBox: {
    backgroundColor: '#eff6ff',
    padding: 15,
    marginVertical: 10,
    borderRadius: 5,
    borderLeft: '4 solid #2563eb',
  },
  scoreTitle: {
    fontSize: 12,
    color: '#1e40af',
    marginBottom: 5,
  },
  scoreValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1e40af',
  },
  statusEligible: {
    backgroundColor: '#dcfce7',
    color: '#166534',
    padding: 10,
    marginVertical: 10,
    borderRadius: 5,
  },
  statusPartial: {
    backgroundColor: '#fef3c7',
    color: '#92400e',
    padding: 10,
    marginVertical: 10,
    borderRadius: 5,
  },
  statusNotEligible: {
    backgroundColor: '#fee2e2',
    color: '#991b1b',
    padding: 10,
    marginVertical: 10,
    borderRadius: 5,
  },
  statusText: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  creditBox: {
    backgroundColor: '#f0fdf4',
    padding: 15,
    marginVertical: 10,
    borderRadius: 5,
    borderLeft: '4 solid #22c55e',
  },
  creditTitle: {
    fontSize: 11,
    color: '#166534',
    marginBottom: 5,
  },
  creditValue: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#166534',
  },
  table: {
    marginVertical: 10,
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#f3f4f6',
    padding: 8,
    fontWeight: 'bold',
  },
  tableRow: {
    flexDirection: 'row',
    padding: 8,
    borderBottom: '1 solid #e5e7eb',
  },
  tableCell: {
    flex: 1,
  },
  tableCellSmall: {
    width: 60,
    textAlign: 'center',
  },
  criticalIssue: {
    backgroundColor: '#fee2e2',
    padding: 8,
    marginVertical: 3,
    borderRadius: 3,
    color: '#991b1b',
  },
  warning: {
    backgroundColor: '#fef3c7',
    padding: 8,
    marginVertical: 3,
    borderRadius: 3,
    color: '#92400e',
  },
  recommendation: {
    backgroundColor: '#f9fafb',
    padding: 10,
    marginVertical: 5,
    borderRadius: 5,
    borderLeft: '3 solid #6b7280',
  },
  recTitle: {
    fontSize: 11,
    fontWeight: 'bold',
    marginBottom: 3,
  },
  recDescription: {
    fontSize: 9,
    color: '#4b5563',
    marginBottom: 5,
  },
  recMeta: {
    flexDirection: 'row',
    gap: 10,
  },
  priorityHigh: {
    backgroundColor: '#fee2e2',
    color: '#991b1b',
    padding: '2 6',
    borderRadius: 3,
    fontSize: 8,
  },
  priorityMedium: {
    backgroundColor: '#fef3c7',
    color: '#92400e',
    padding: '2 6',
    borderRadius: 3,
    fontSize: 8,
  },
  priorityLow: {
    backgroundColor: '#dbeafe',
    color: '#1e40af',
    padding: '2 6',
    borderRadius: 3,
    fontSize: 8,
  },
  actionItem: {
    fontSize: 9,
    marginLeft: 10,
    marginTop: 2,
    color: '#4b5563',
  },
  footer: {
    position: 'absolute',
    bottom: 30,
    left: 40,
    right: 40,
    borderTop: '1 solid #e5e7eb',
    paddingTop: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  footerText: {
    fontSize: 8,
    color: '#9ca3af',
  },
  pageNumber: {
    fontSize: 8,
    color: '#9ca3af',
  },
  disclaimer: {
    fontSize: 8,
    color: '#9ca3af',
    marginTop: 20,
    padding: 10,
    backgroundColor: '#f9fafb',
    borderRadius: 3,
  },
});

const STATUS_LABELS: Record<EligibilityStatus, string> = {
  eligible: 'ELIGIBLE AU CDAEIA',
  partial: 'PARTIELLEMENT ELIGIBLE',
  not_eligible: 'NON ELIGIBLE',
};

const PRIORITY_LABELS: Record<Priority, string> = {
  high: 'Haute',
  medium: 'Moyenne',
  low: 'Basse',
};

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('fr-CA', {
    style: 'currency',
    currency: 'CAD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(): string {
  return new Intl.DateTimeFormat('fr-CA', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date());
}

interface DiagnosticPDFProps {
  result: DiagnosticResult;
  responses: DiagnosticResponses;
}

export function DiagnosticPDF({ result, responses }: DiagnosticPDFProps) {
  const companyName = (responses.company_name as string) || 'N/A';
  const statusStyle =
    result.eligibilityStatus === 'eligible'
      ? styles.statusEligible
      : result.eligibilityStatus === 'partial'
      ? styles.statusPartial
      : styles.statusNotEligible;

  return (
    <Document>
      {/* Page 1 - Sommaire */}
      <Page size="A4" style={styles.page}>
        <View style={styles.header}>
          <Text style={styles.logo}>Ran.AI Agency</Text>
          <Text style={styles.subtitle}>Experts en transformation IA</Text>
        </View>

        <Text style={styles.title}>Rapport de Diagnostic CDAEIA</Text>

        <View style={styles.row}>
          <Text style={styles.label}>Client:</Text>
          <Text style={styles.value}>{companyName}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Date:</Text>
          <Text style={styles.value}>{formatDate()}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>NEQ:</Text>
          <Text style={styles.value}>{(responses.company_neq as string) || 'N/A'}</Text>
        </View>

        <Text style={styles.sectionTitle}>Score d'Eligibilite</Text>

        <View style={styles.scoreBox}>
          <Text style={styles.scoreTitle}>Score Total</Text>
          <Text style={styles.scoreValue}>
            {result.totalScore} / {result.maxScore} ({Math.round(result.percentage)}%)
          </Text>
        </View>

        <View style={statusStyle}>
          <Text style={styles.statusText}>{STATUS_LABELS[result.eligibilityStatus]}</Text>
          <Text style={{ marginTop: 5, fontSize: 10 }}>{result.statusMessage}</Text>
        </View>

        <Text style={styles.sectionTitle}>Credit d'Impot Estime</Text>

        <View style={{ flexDirection: 'row', gap: 10 }}>
          <View style={[styles.creditBox, { flex: 1 }]}>
            <Text style={styles.creditTitle}>Situation Actuelle</Text>
            <Text style={styles.creditValue}>
              {result.creditCurrent ? formatCurrency(result.creditCurrent.totalCredit) : 'N/A'}
            </Text>
            <Text style={{ fontSize: 9, color: '#166534' }}>par annee</Text>
          </View>
          <View style={[styles.creditBox, { flex: 1, borderLeftColor: '#16a34a' }]}>
            <Text style={styles.creditTitle}>Apres Optimisation</Text>
            <Text style={styles.creditValue}>
              {result.creditOptimized ? formatCurrency(result.creditOptimized.totalCredit) : 'N/A'}
            </Text>
            <Text style={{ fontSize: 9, color: '#166534' }}>
              Gain: +{formatCurrency(result.creditGain)}/an
            </Text>
          </View>
        </View>

        <Text style={styles.sectionTitle}>Detail des Scores</Text>

        <View style={styles.table}>
          <View style={styles.tableHeader}>
            <Text style={[styles.tableCell, { flex: 2 }]}>Critere</Text>
            <Text style={styles.tableCellSmall}>Score</Text>
            <Text style={styles.tableCellSmall}>Statut</Text>
          </View>
          {result.scoreBreakdown.map((breakdown, index) => (
            <View key={index} style={styles.tableRow}>
              <Text style={[styles.tableCell, { flex: 2 }]}>{breakdown.criterion}</Text>
              <Text style={styles.tableCellSmall}>
                {breakdown.score}/{breakdown.maxScore}
              </Text>
              <Text style={styles.tableCellSmall}>
                {breakdown.status === 'pass' ? 'OK' : breakdown.status === 'warning' ? '!' : 'X'}
              </Text>
            </View>
          ))}
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Ran.AI Agency | 514-918-1241 | info@ran-ai-agency.ca
          </Text>
          <Text
            style={styles.pageNumber}
            render={({ pageNumber, totalPages }) => `Page ${pageNumber} / ${totalPages}`}
          />
        </View>
      </Page>

      {/* Page 2 - Problemes et Recommandations */}
      <Page size="A4" style={styles.page}>
        <View style={styles.header}>
          <Text style={styles.logo}>Ran.AI Agency</Text>
          <Text style={styles.subtitle}>Diagnostic CDAEIA - {companyName}</Text>
        </View>

        {result.criticalIssues.length > 0 && (
          <>
            <Text style={styles.sectionTitle}>Problemes Critiques</Text>
            {result.criticalIssues.map((issue, index) => (
              <View key={index} style={styles.criticalIssue}>
                <Text>{issue}</Text>
              </View>
            ))}
          </>
        )}

        {result.warnings.length > 0 && (
          <>
            <Text style={styles.sectionTitle}>Avertissements</Text>
            {result.warnings.map((warning, index) => (
              <View key={index} style={styles.warning}>
                <Text>{warning}</Text>
              </View>
            ))}
          </>
        )}

        <Text style={styles.sectionTitle}>Recommandations</Text>
        {result.recommendations.slice(0, 6).map((rec, index) => (
          <View key={index} style={styles.recommendation}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
              <Text style={styles.recTitle}>{rec.title}</Text>
              <Text
                style={
                  rec.priority === 'high'
                    ? styles.priorityHigh
                    : rec.priority === 'medium'
                    ? styles.priorityMedium
                    : styles.priorityLow
                }
              >
                Priorite {PRIORITY_LABELS[rec.priority]}
              </Text>
            </View>
            <Text style={styles.recDescription}>{rec.description}</Text>
            <Text style={{ fontSize: 8, color: '#6b7280' }}>
              Impact: +{rec.expectedImpact} pts | Delai: ~{rec.estimatedWeeks} semaines
            </Text>
            {rec.actionItems.slice(0, 3).map((action, i) => (
              <Text key={i} style={styles.actionItem}>
                - {action}
              </Text>
            ))}
          </View>
        ))}

        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Ran.AI Agency | 514-918-1241 | info@ran-ai-agency.ca
          </Text>
          <Text
            style={styles.pageNumber}
            render={({ pageNumber, totalPages }) => `Page ${pageNumber} / ${totalPages}`}
          />
        </View>
      </Page>

      {/* Page 3 - Detail du Credit */}
      <Page size="A4" style={styles.page}>
        <View style={styles.header}>
          <Text style={styles.logo}>Ran.AI Agency</Text>
          <Text style={styles.subtitle}>Diagnostic CDAEIA - {companyName}</Text>
        </View>

        <Text style={styles.sectionTitle}>Calcul Detaille du Credit</Text>

        {result.creditCurrent && (
          <View style={{ marginBottom: 20 }}>
            <Text style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 10 }}>
              Situation Actuelle
            </Text>
            <View style={styles.row}>
              <Text style={styles.label}>Employes eligibles:</Text>
              <Text style={styles.value}>{result.creditCurrent.eligibleEmployees}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Masse salariale brute:</Text>
              <Text style={styles.value}>
                {formatCurrency(result.creditCurrent.totalEligibleSalary)}
              </Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Seuil d'exclusion:</Text>
              <Text style={styles.value}>
                -{formatCurrency(result.creditCurrent.exclusionThreshold)}
              </Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Masse salariale nette:</Text>
              <Text style={styles.value}>
                {formatCurrency(result.creditCurrent.netEligibleSalary)}
              </Text>
            </View>
            <View style={[styles.row, { marginTop: 10 }]}>
              <Text style={styles.label}>Portion remboursable (22%):</Text>
              <Text style={[styles.value, { color: '#16a34a' }]}>
                {formatCurrency(result.creditCurrent.refundablePortion)}
              </Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Portion non-remboursable (8%):</Text>
              <Text style={styles.value}>
                {formatCurrency(result.creditCurrent.nonRefundablePortion)}
              </Text>
            </View>
            <View style={[styles.row, { marginTop: 5, backgroundColor: '#f0fdf4', padding: 5 }]}>
              <Text style={[styles.label, { fontWeight: 'bold' }]}>CREDIT TOTAL:</Text>
              <Text style={[styles.value, { color: '#16a34a', fontSize: 14 }]}>
                {formatCurrency(result.creditCurrent.totalCredit)}/an
              </Text>
            </View>
          </View>
        )}

        {result.creditOptimized && result.creditGain > 0 && (
          <View style={{ marginBottom: 20 }}>
            <Text style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 10 }}>
              Scenario Optimise
            </Text>
            <View style={styles.row}>
              <Text style={styles.label}>Employes eligibles:</Text>
              <Text style={styles.value}>{result.creditOptimized.eligibleEmployees}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.label}>Masse salariale nette:</Text>
              <Text style={styles.value}>
                {formatCurrency(result.creditOptimized.netEligibleSalary)}
              </Text>
            </View>
            <View style={[styles.row, { backgroundColor: '#dcfce7', padding: 5 }]}>
              <Text style={[styles.label, { fontWeight: 'bold' }]}>CREDIT OPTIMISE:</Text>
              <Text style={[styles.value, { color: '#166534', fontSize: 14 }]}>
                {formatCurrency(result.creditOptimized.totalCredit)}/an
              </Text>
            </View>
            <View style={[styles.row, { marginTop: 10 }]}>
              <Text style={styles.label}>GAIN POTENTIEL:</Text>
              <Text style={[styles.value, { color: '#166534', fontWeight: 'bold' }]}>
                +{formatCurrency(result.creditGain)}/an
              </Text>
            </View>
          </View>
        )}

        <Text style={styles.sectionTitle}>Prochaines Etapes</Text>
        <View style={{ marginLeft: 10 }}>
          <Text style={{ marginBottom: 5 }}>1. Revoir ce rapport avec votre equipe de direction</Text>
          <Text style={{ marginBottom: 5 }}>2. Prioriser les recommandations selon vos ressources</Text>
          <Text style={{ marginBottom: 5 }}>3. Implementer un systeme de suivi du temps si pas en place</Text>
          <Text style={{ marginBottom: 5 }}>4. Planifier un appel de suivi avec Ran.AI Agency</Text>
        </View>

        <Text style={styles.sectionTitle}>Contact</Text>
        <View style={{ marginLeft: 10 }}>
          <Text style={{ marginBottom: 3 }}>Ran.AI Agency</Text>
          <Text style={{ marginBottom: 3 }}>Telephone: 514-918-1241</Text>
          <Text style={{ marginBottom: 3 }}>Email: info@ran-ai-agency.ca</Text>
          <Text style={{ marginBottom: 3 }}>Web: ran-ai-agency.ca</Text>
        </View>

        <View style={styles.disclaimer}>
          <Text>
            Ce rapport est fourni a titre informatif et ne constitue pas un avis fiscal ou juridique.
            Consultez un professionnel qualifie pour votre situation specifique. Les estimations de
            credit sont basees sur les informations fournies et peuvent varier selon la validation
            d'Investissement Quebec.
          </Text>
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Ran.AI Agency | 514-918-1241 | info@ran-ai-agency.ca
          </Text>
          <Text
            style={styles.pageNumber}
            render={({ pageNumber, totalPages }) => `Page ${pageNumber} / ${totalPages}`}
          />
        </View>
      </Page>
    </Document>
  );
}
