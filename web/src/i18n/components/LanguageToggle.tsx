/**
 * LanguageToggle Component
 * Global language switcher between Spanish (ES) and English (EN)
 */

import React from 'react';
import { GlassButton } from '@/components/ui/GlassButton';
import { useLanguage } from '../hooks';

interface LanguageToggleProps {
  className?: string;
}

export const LanguageToggle: React.FC<LanguageToggleProps> = ({ className }) => {
  const { language, toggleLanguage, isSpanish, isEnglish } = useLanguage();

  // Language labels
  const getLanguageLabel = () => {
    if (isSpanish) return 'ES';
    if (isEnglish) return 'EN';
    return language.toUpperCase();
  };

  // Full language name for aria-label
  const getFullLanguageName = () => {
    if (isSpanish) return 'Español';
    if (isEnglish) return 'English';
    return language;
  };

  // Next language for accessibility
  const getNextLanguage = () => {
    if (isSpanish) return 'English';
    if (isEnglish) return 'Español';
    return 'language';
  };

  const ariaLabel = `Current language: ${getFullLanguageName()}. Click to switch to ${getNextLanguage()}`;

  return (
    <GlassButton
      variant="ghost"
      size="sm"
      onClick={toggleLanguage}
      ariaLabel={ariaLabel}
      className={className}
      title={`${getFullLanguageName()} → ${getNextLanguage()}`}
    >
      <span className="font-semibold text-sm" aria-hidden="true">
        {getLanguageLabel()}
      </span>
      <span className="sr-only">{ariaLabel}</span>
    </GlassButton>
  );
};
