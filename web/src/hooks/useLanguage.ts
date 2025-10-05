/**
 * useLanguage Hook
 * Convenient hook for language/i18n management
 */

import { useUIContext } from '@/contexts';

export const useLanguage = () => {
  const { language, setLanguage, toggleLanguage } = useUIContext();

  return {
    language,
    setLanguage,
    toggleLanguage,
    isSpanish: language === 'es',
    isEnglish: language === 'en',
    t: (key: string) => key, // Placeholder for future i18n implementation
  };
};
