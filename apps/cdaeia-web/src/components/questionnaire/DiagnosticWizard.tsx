'use client';

import React, { useState, useCallback, useMemo } from 'react';
import { QUESTIONNAIRE_SECTIONS } from '@/lib/questionnaire-data';
import { DiagnosticResponses, DiagnosticResult, Section } from '@/lib/cdaeia-types';
import { calculateScore } from '@/lib/scoring-engine';
import { QuestionField } from './QuestionField';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import {
  Building,
  DollarSign,
  Users,
  Clock,
  Cpu,
  FileText,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const SECTION_ICONS: Record<string, React.ReactNode> = {
  Building: <Building className="w-5 h-5" />,
  DollarSign: <DollarSign className="w-5 h-5" />,
  Users: <Users className="w-5 h-5" />,
  Clock: <Clock className="w-5 h-5" />,
  Cpu: <Cpu className="w-5 h-5" />,
  FileText: <FileText className="w-5 h-5" />,
};

interface DiagnosticWizardProps {
  onComplete: (result: DiagnosticResult, responses: DiagnosticResponses) => void;
}

export function DiagnosticWizard({ onComplete }: DiagnosticWizardProps) {
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [responses, setResponses] = useState<DiagnosticResponses>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const sections = QUESTIONNAIRE_SECTIONS;
  const currentSection = sections[currentSectionIndex];
  const isFirstSection = currentSectionIndex === 0;
  const isLastSection = currentSectionIndex === sections.length - 1;

  // Calculate progress
  const totalQuestions = useMemo(() =>
    sections.reduce((acc, section) => acc + section.questions.length, 0),
    [sections]
  );

  const answeredQuestions = useMemo(() =>
    Object.keys(responses).filter(key => responses[key] !== null && responses[key] !== undefined && responses[key] !== '').length,
    [responses]
  );

  const progressPercentage = Math.round((answeredQuestions / totalQuestions) * 100);

  // Check if a question should be visible based on conditional logic
  const isQuestionVisible = useCallback((question: typeof currentSection.questions[0]) => {
    if (!question.conditional) return true;
    const dependentValue = responses[question.conditional.field];
    return dependentValue === question.conditional.value;
  }, [responses]);

  // Get visible questions for current section
  const visibleQuestions = useMemo(() =>
    currentSection.questions.filter(isQuestionVisible),
    [currentSection.questions, isQuestionVisible]
  );

  // Validate current section
  const validateSection = useCallback(() => {
    const newErrors: Record<string, string> = {};
    let isValid = true;

    for (const question of visibleQuestions) {
      if (question.required) {
        const value = responses[question.id];
        if (value === null || value === undefined || value === '') {
          newErrors[question.id] = 'Ce champ est requis';
          isValid = false;
        }
      }

      // Validate number ranges
      if (question.validation && responses[question.id] !== null && responses[question.id] !== undefined) {
        const value = responses[question.id] as number;
        if (question.validation.min !== undefined && value < question.validation.min) {
          newErrors[question.id] = `La valeur minimale est ${question.validation.min}`;
          isValid = false;
        }
        if (question.validation.max !== undefined && value > question.validation.max) {
          newErrors[question.id] = `La valeur maximale est ${question.validation.max}`;
          isValid = false;
        }
      }
    }

    setErrors(newErrors);
    return isValid;
  }, [visibleQuestions, responses]);

  // Handle response change
  const handleResponseChange = useCallback((questionId: string, value: unknown) => {
    setResponses(prev => ({ ...prev, [questionId]: value as DiagnosticResponses[string] }));
    // Clear error when user starts typing
    if (errors[questionId]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[questionId];
        return newErrors;
      });
    }
  }, [errors]);

  // Navigate between sections
  const goToNextSection = useCallback(() => {
    if (!validateSection()) return;

    if (isLastSection) {
      handleSubmit();
    } else {
      setCurrentSectionIndex(prev => prev + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [isLastSection, validateSection]);

  const goToPreviousSection = useCallback(() => {
    if (!isFirstSection) {
      setCurrentSectionIndex(prev => prev - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [isFirstSection]);

  const goToSection = useCallback((index: number) => {
    // Only allow going to previous sections or current section
    if (index <= currentSectionIndex) {
      setCurrentSectionIndex(index);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [currentSectionIndex]);

  // Submit the diagnostic
  const handleSubmit = useCallback(async () => {
    if (!validateSection()) return;

    setIsSubmitting(true);
    try {
      const result = calculateScore(responses);
      onComplete(result, responses);
    } catch (error) {
      console.error('Erreur lors du calcul:', error);
      setErrors({ _form: 'Une erreur est survenue lors du calcul. Veuillez réessayer.' });
    } finally {
      setIsSubmitting(false);
    }
  }, [responses, validateSection, onComplete]);

  // Check if section is complete
  const isSectionComplete = useCallback((section: Section) => {
    const sectionQuestions = section.questions.filter(q => {
      if (!q.conditional) return true;
      return responses[q.conditional.field] === q.conditional.value;
    });

    return sectionQuestions.every(q => {
      if (!q.required) return true;
      const value = responses[q.id];
      return value !== null && value !== undefined && value !== '';
    });
  }, [responses]);

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Progression du diagnostic
          </span>
          <span className="text-sm text-gray-500">
            {progressPercentage}% complété
          </span>
        </div>
        <Progress value={progressPercentage} className="h-2" />
      </div>

      {/* Section Navigation */}
      <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
        {sections.map((section, index) => {
          const isCompleted = isSectionComplete(section);
          const isCurrent = index === currentSectionIndex;
          const isAccessible = index <= currentSectionIndex;

          return (
            <button
              key={section.id}
              onClick={() => goToSection(index)}
              disabled={!isAccessible}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap',
                isCurrent
                  ? 'bg-blue-600 text-white'
                  : isCompleted
                  ? 'bg-green-100 text-green-700 hover:bg-green-200'
                  : isAccessible
                  ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  : 'bg-gray-50 text-gray-400 cursor-not-allowed'
              )}
            >
              {SECTION_ICONS[section.icon] || <FileText className="w-5 h-5" />}
              <span className="hidden sm:inline">{section.title}</span>
              {isCompleted && !isCurrent && (
                <CheckCircle className="w-4 h-4 text-green-600" />
              )}
            </button>
          );
        })}
      </div>

      {/* Current Section Card */}
      <Card className="mb-8">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              {SECTION_ICONS[currentSection.icon] || <FileText className="w-5 h-5" />}
            </div>
            <div>
              <CardTitle className="text-xl">{currentSection.title}</CardTitle>
              <CardDescription>{currentSection.description}</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {visibleQuestions.map((question) => (
            <QuestionField
              key={question.id}
              question={question}
              value={responses[question.id]}
              onChange={(value) => handleResponseChange(question.id, value)}
              error={errors[question.id]}
            />
          ))}

          {/* Time allocation warning */}
          {currentSection.id === 'temps' && (
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-amber-800">
                    Important: Les pourcentages doivent totaliser 100%
                  </p>
                  <p className="text-sm text-amber-700 mt-1">
                    Assurez-vous que la somme de toutes les allocations de temps égale 100%.
                    Seules les activités IA (développement, intégration, données, analytique)
                    sont éligibles au CDAEIA.
                  </p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Form-level error */}
      {errors._form && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{errors._form}</p>
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={goToPreviousSection}
          disabled={isFirstSection}
          className="gap-2"
        >
          <ChevronLeft className="w-4 h-4" />
          Précédent
        </Button>

        <Button
          onClick={goToNextSection}
          disabled={isSubmitting}
          className="gap-2"
        >
          {isSubmitting ? (
            'Calcul en cours...'
          ) : isLastSection ? (
            <>
              Voir les résultats
              <CheckCircle className="w-4 h-4" />
            </>
          ) : (
            <>
              Suivant
              <ChevronRight className="w-4 h-4" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
