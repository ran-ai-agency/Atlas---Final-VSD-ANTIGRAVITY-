'use client';

import React from 'react';
import { Question } from '@/lib/cdaeia-types';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { cn } from '@/lib/utils';

interface QuestionFieldProps {
  question: Question;
  value: unknown;
  onChange: (value: unknown) => void;
  error?: string;
}

export function QuestionField({ question, value, onChange, error }: QuestionFieldProps) {
  const renderField = () => {
    switch (question.type) {
      case 'text':
        return (
          <Input
            id={question.id}
            value={(value as string) || ''}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Votre réponse..."
            className={cn(error && 'border-red-500')}
          />
        );

      case 'email':
        return (
          <Input
            id={question.id}
            type="email"
            value={(value as string) || ''}
            onChange={(e) => onChange(e.target.value)}
            placeholder="votre@courriel.com"
            className={cn(error && 'border-red-500')}
          />
        );

      case 'number':
        return (
          <Input
            id={question.id}
            type="number"
            value={(value as number) ?? ''}
            onChange={(e) => onChange(e.target.value ? Number(e.target.value) : null)}
            min={question.validation?.min}
            max={question.validation?.max}
            className={cn(error && 'border-red-500')}
          />
        );

      case 'currency':
        return (
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
            <Input
              id={question.id}
              type="number"
              value={(value as number) ?? ''}
              onChange={(e) => onChange(e.target.value ? Number(e.target.value) : null)}
              min={0}
              className={cn('pl-7', error && 'border-red-500')}
              placeholder="0"
            />
          </div>
        );

      case 'percentage':
        return (
          <div className="relative">
            <Input
              id={question.id}
              type="number"
              value={(value as number) ?? ''}
              onChange={(e) => onChange(e.target.value ? Number(e.target.value) : null)}
              min={0}
              max={100}
              className={cn('pr-8', error && 'border-red-500')}
              placeholder="0"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">%</span>
          </div>
        );

      case 'boolean':
        return (
          <RadioGroup
            value={value === true ? 'true' : value === false ? 'false' : ''}
            onValueChange={(v) => onChange(v === 'true')}
            className="flex gap-4"
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="true" id={`${question.id}-yes`} />
              <Label htmlFor={`${question.id}-yes`} className="font-normal cursor-pointer">
                Oui
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="false" id={`${question.id}-no`} />
              <Label htmlFor={`${question.id}-no`} className="font-normal cursor-pointer">
                Non
              </Label>
            </div>
          </RadioGroup>
        );

      case 'select':
        return (
          <RadioGroup
            value={(value as string) || ''}
            onValueChange={onChange}
            className="space-y-2"
          >
            {question.options?.map((option) => (
              <div
                key={option.value}
                className={cn(
                  'flex items-start space-x-3 p-3 rounded-lg border transition-colors cursor-pointer',
                  value === option.value
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                )}
              >
                <RadioGroupItem value={option.value} id={`${question.id}-${option.value}`} className="mt-0.5" />
                <Label htmlFor={`${question.id}-${option.value}`} className="font-normal cursor-pointer flex-1">
                  <div className="font-medium">{option.label}</div>
                  {option.description && (
                    <div className="text-sm text-gray-500">{option.description}</div>
                  )}
                </Label>
              </div>
            ))}
          </RadioGroup>
        );

      case 'multi_select':
        const selectedValues = (value as string[]) || [];
        return (
          <div className="space-y-2">
            {question.options?.map((option) => {
              const isChecked = selectedValues.includes(option.value);
              return (
                <div
                  key={option.value}
                  className={cn(
                    'flex items-start space-x-3 p-3 rounded-lg border transition-colors cursor-pointer',
                    isChecked
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  )}
                  onClick={() => {
                    if (isChecked) {
                      onChange(selectedValues.filter((v) => v !== option.value));
                    } else {
                      onChange([...selectedValues, option.value]);
                    }
                  }}
                >
                  <Checkbox
                    checked={isChecked}
                    onCheckedChange={(checked) => {
                      if (checked) {
                        onChange([...selectedValues, option.value]);
                      } else {
                        onChange(selectedValues.filter((v) => v !== option.value));
                      }
                    }}
                    className="mt-0.5"
                  />
                  <div className="flex-1">
                    <div className="font-medium">{option.label}</div>
                    {option.description && (
                      <div className="text-sm text-gray-500">{option.description}</div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        );

      default:
        return (
          <Input
            id={question.id}
            value={(value as string) || ''}
            onChange={(e) => onChange(e.target.value)}
          />
        );
    }
  };

  return (
    <div className="space-y-3">
      <div className="space-y-1">
        <Label htmlFor={question.id} className="text-base font-medium">
          {question.text}
          {question.required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        {question.helpText && (
          <p className="text-sm text-gray-500">{question.helpText}</p>
        )}
      </div>
      {renderField()}
      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  );
}
