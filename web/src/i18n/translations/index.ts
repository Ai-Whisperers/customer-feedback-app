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

// Recursive type to support deep nesting (any depth) - converts all leaf values to generic string
type DeepTranslationStructure<T> = {
  [K in keyof T]: T[K] extends string
    ? string
    : T[K] extends object
    ? T[K] extends readonly any[]
      ? T[K]
      : DeepTranslationStructure<T[K]>
    : T[K];
};

// Translation structure type (supports unlimited nesting depth, language-agnostic)
export type TranslationKeys = DeepTranslationStructure<ESTranslationKeys>;

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
