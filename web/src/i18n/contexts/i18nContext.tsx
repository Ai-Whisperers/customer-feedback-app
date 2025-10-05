/**
 * i18n Context - Internationalization State Management
 * Dedicated context for language switching and translations
 * B2B Enterprise: Multi-language support
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { SupportedLanguage, TranslationKeys } from '../translations';
import { translations } from '../translations';

// Storage key for persisted language preference
const LANGUAGE_STORAGE_KEY = 'customer-feedback-analyzer:language';

// Default language
const DEFAULT_LANGUAGE: SupportedLanguage = 'es';

interface I18nState {
  language: SupportedLanguage;
  translations: TranslationKeys;
}

interface I18nContextValue extends I18nState {
  setLanguage: (language: SupportedLanguage) => void;
  toggleLanguage: () => void;
  t: (key: string, variables?: Record<string, string | number>) => string;
}

const I18nContext = createContext<I18nContextValue | undefined>(undefined);

// Helper function to get nested value by path (e.g., "common.loading")
function getNestedValue(obj: any, path: string): string {
  const keys = path.split('.');
  let value = obj;

  for (const key of keys) {
    if (value && typeof value === 'object' && key in value) {
      value = value[key];
    } else {
      console.warn(`Translation key not found: ${path}`);
      return path; // Return key as fallback
    }
  }

  return typeof value === 'string' ? value : path;
}

// Helper function to interpolate variables (e.g., "Hello {{name}}")
function interpolate(text: string, variables?: Record<string, string | number>): string {
  if (!variables) return text;

  return text.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    return variables[key] !== undefined ? String(variables[key]) : match;
  });
}

export const I18nProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Initialize state from localStorage or default
  const [state, setState] = useState<I18nState>(() => {
    if (typeof window !== 'undefined') {
      const storedLanguage = localStorage.getItem(LANGUAGE_STORAGE_KEY) as SupportedLanguage;
      if (storedLanguage && storedLanguage in translations) {
        return {
          language: storedLanguage,
          translations: translations[storedLanguage],
        };
      }
    }
    return {
      language: DEFAULT_LANGUAGE,
      translations: translations[DEFAULT_LANGUAGE],
    };
  });

  // Persist language preference to localStorage
  useEffect(() => {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, state.language);
  }, [state.language]);

  // Set document lang attribute for accessibility
  useEffect(() => {
    document.documentElement.lang = state.language;
  }, [state.language]);

  // Set language
  const setLanguage = useCallback((language: SupportedLanguage) => {
    setState({
      language,
      translations: translations[language],
    });
  }, []);

  // Toggle between ES/EN
  const toggleLanguage = useCallback(() => {
    const newLanguage: SupportedLanguage = state.language === 'es' ? 'en' : 'es';
    setLanguage(newLanguage);
  }, [state.language, setLanguage]);

  // Translation function with interpolation support
  const t = useCallback(
    (key: string, variables?: Record<string, string | number>): string => {
      const text = getNestedValue(state.translations, key);
      return interpolate(text, variables);
    },
    [state.translations]
  );

  const value: I18nContextValue = {
    ...state,
    setLanguage,
    toggleLanguage,
    t,
  };

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
};

// Hook to use i18n context
export const useI18nContext = () => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18nContext must be used within I18nProvider');
  }
  return context;
};
