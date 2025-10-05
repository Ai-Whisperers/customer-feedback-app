/**
 * useLanguage Hook
 * Simplified hook for language switching
 */

import { useI18nContext } from '../contexts/i18nContext';

export const useLanguage = () => {
  const { language, setLanguage, toggleLanguage } = useI18nContext();

  return {
    language,
    setLanguage,
    toggleLanguage,
    isSpanish: language === 'es',
    isEnglish: language === 'en',
  };
};
