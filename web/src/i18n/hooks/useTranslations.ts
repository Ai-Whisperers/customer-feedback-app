/**
 * useTranslations Hook
 * Simplified hook for accessing translations
 */

import { useI18nContext } from '../contexts/i18nContext';

export const useTranslations = () => {
  const { t, translations, language } = useI18nContext();

  return {
    t,
    translations,
    language,
  };
};
