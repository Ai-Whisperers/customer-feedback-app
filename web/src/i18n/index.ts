/**
 * i18n Module - Barrel Export
 * Centralized internationalization system
 */

// Context and Provider
export { I18nProvider, useI18nContext } from './contexts/i18nContext';

// Hooks
export { useLanguage, useTranslations } from './hooks';

// Translations
export { translations, es, en } from './translations';
export type { SupportedLanguage, TranslationKeys, TranslationKey } from './translations';
