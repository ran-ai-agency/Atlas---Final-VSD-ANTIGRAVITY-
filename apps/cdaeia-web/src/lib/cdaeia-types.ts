// Types pour l'application CDAEIA Diagnostic

export type QuestionType =
  | 'text'
  | 'email'
  | 'number'
  | 'currency'
  | 'percentage'
  | 'select'
  | 'multi_select'
  | 'boolean'
  | 'date';

export interface Option {
  value: string;
  label: string;
  description?: string;
}

export interface Question {
  id: string;
  section: string;
  text: string;
  type: QuestionType;
  required: boolean;
  helpText?: string;
  options?: Option[];
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
  };
  conditional?: {
    field: string;
    value: unknown;
  };
}

export interface Section {
  id: string;
  title: string;
  description: string;
  icon: string;
  questions: Question[];
}

export type EligibilityStatus = 'eligible' | 'partial' | 'not_eligible';
export type Priority = 'high' | 'medium' | 'low';
export type EffortLevel = 'low' | 'medium' | 'high';

export interface ScoreBreakdown {
  criterion: string;
  score: number;
  maxScore: number;
  status: 'pass' | 'warning' | 'fail';
  details: string;
  value?: unknown;
}

export interface CreditCalculation {
  eligibleEmployees: number;
  totalEligibleSalary: number;
  exclusionThreshold: number;
  netEligibleSalary: number;
  creditRate: number;
  refundablePortion: number;
  nonRefundablePortion: number;
  totalCredit: number;
}

export interface Recommendation {
  id: string;
  category: 'employee' | 'project' | 'process' | 'documentation';
  priority: Priority;
  title: string;
  description: string;
  expectedImpact: number;
  effortLevel: EffortLevel;
  estimatedWeeks: number;
  actionItems: string[];
}

export interface DiagnosticResult {
  totalScore: number;
  maxScore: number;
  percentage: number;
  eligibilityStatus: EligibilityStatus;
  statusMessage: string;
  scoreBreakdown: ScoreBreakdown[];
  creditCurrent: CreditCalculation | null;
  creditOptimized: CreditCalculation | null;
  creditGain: number;
  criticalIssues: string[];
  warnings: string[];
  recommendations: Recommendation[];
}

export interface DiagnosticResponses {
  [key: string]: string | number | boolean | string[] | null;
}

export interface Company {
  id: string;
  name: string;
  neq?: string;
  industry?: string;
  createdAt: Date;
}

export interface Assessment {
  id: string;
  companyId: string;
  status: 'draft' | 'in_progress' | 'completed';
  responses: DiagnosticResponses;
  result?: DiagnosticResult;
  createdAt: Date;
  completedAt?: Date;
}
