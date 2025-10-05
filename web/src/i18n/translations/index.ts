/**
 * Translations Index
 * Centralized exports for all supported languages
 */

import type { TranslationKeys as ESTranslationKeys } from './es';
import { es } from './es';
import { en } from './en';

export const translations = {
  es,
  en,
} as const;

export type SupportedLanguage = keyof typeof translations;

// Generic translation structure (flexible - accepts any language)
export type TranslationKeys = {
  [K in keyof ESTranslationKeys]: ESTranslationKeys[K] extends object
    ? { [P in keyof ESTranslationKeys[K]]: ESTranslationKeys[K][P] extends object ? Record<string, string> : string }
    : string;
};

// Helper type for nested translation keys (dot notation)
type DotPrefix<T extends string> = T extends '' ? '' : `.${T}`;
type DotNestedKeys<T> = (
  T extends object
    ? {
        [K in Exclude<keyof T, symbol>]: `${K}${DotPrefix<DotNestedKeys<T[K]>>}`;
      }[Exclude<keyof T, symbol>]
    : ''
) extends infer D
  ? Extract<D, string>
  : never;

export type TranslationKey = DotNestedKeys<ESTranslationKeys>;

// Export individual translations
export { es, en };
