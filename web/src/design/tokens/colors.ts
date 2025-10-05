/**
 * Color Design Tokens
 * Centralized color system with primitive and semantic tokens
 * Following B2B enterprise multi-tenant requirements
 */

// Primitive Color Scales (raw values - DO NOT use directly in components)
const primitives = {
  blue: {
    50: '#f0f9ff',
    100: '#e0f2fe',
    200: '#bae6fd',
    300: '#7dd3fc',
    400: '#38bdf8',
    500: '#0ea5e9',
    600: '#0284c7',
    700: '#0369a1',
    800: '#075985',
    900: '#0c4a6e',
  },
  purple: {
    50: '#faf5ff',
    100: '#f3e8ff',
    200: '#e9d5ff',
    300: '#d8b4fe',
    400: '#c084fc',
    500: '#a855f7',
    600: '#9333ea',
    700: '#7e22ce',
    800: '#6b21a8',
    900: '#581c87',
  },
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  green: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
  },
  red: {
    50: '#fef2f2',
    100: '#fee2e2',
    200: '#fecaca',
    300: '#fca5a5',
    400: '#f87171',
    500: '#ef4444',
    600: '#dc2626',
    700: '#b91c1c',
    800: '#991b1b',
    900: '#7f1d1d',
  },
  yellow: {
    50: '#fefce8',
    100: '#fef9c3',
    200: '#fef08a',
    300: '#fde047',
    400: '#facc15',
    500: '#eab308',
    600: '#ca8a04',
    700: '#a16207',
    800: '#854d0e',
    900: '#713f12',
  },
  white: '#ffffff',
  black: '#000000',
} as const;

// Semantic Color Tokens (mapped to primitives - USE THESE in components)
export const colorTokens = {
  // Brand colors
  brand: {
    primary: primitives.blue[500],
    primaryLight: primitives.blue[400],
    primaryDark: primitives.blue[600],
    secondary: primitives.purple[600],
    secondaryLight: primitives.purple[500],
    secondaryDark: primitives.purple[700],
  },

  // Feedback/Status colors
  feedback: {
    success: primitives.green[500],
    successLight: primitives.green[100],
    successDark: primitives.green[700],
    error: primitives.red[500],
    errorLight: primitives.red[100],
    errorDark: primitives.red[700],
    warning: primitives.yellow[500],
    warningLight: primitives.yellow[100],
    warningDark: primitives.yellow[700],
    info: primitives.blue[500],
    infoLight: primitives.blue[100],
    infoDark: primitives.blue[700],
  },

  // Surface colors (backgrounds, cards, etc)
  surface: {
    background: primitives.gray[50],
    foreground: primitives.white,
    card: primitives.white,
    hover: primitives.gray[100],
    active: primitives.gray[200],
    border: primitives.gray[300],
    divider: primitives.gray[200],
  },

  // Text colors
  text: {
    primary: primitives.gray[900],
    secondary: primitives.gray[600],
    tertiary: primitives.gray[500],
    disabled: primitives.gray[400],
    inverse: primitives.white,
  },

  // Glass Design System colors (with opacity)
  glass: {
    light: {
      base: 'rgba(255, 255, 255, 0.8)',
      medium: 'rgba(255, 255, 255, 0.6)',
      heavy: 'rgba(255, 255, 255, 0.4)',
    },
    dark: {
      base: 'rgba(17, 24, 39, 0.8)',
      medium: 'rgba(17, 24, 39, 0.6)',
      heavy: 'rgba(17, 24, 39, 0.4)',
    },
  },

  // Gradient tokens for glass components
  gradients: {
    primary: `linear-gradient(135deg, ${primitives.blue[500]} 0%, ${primitives.purple[600]} 100%)`,
    primaryWithOpacity: `linear-gradient(135deg, rgba(14, 165, 233, 0.9) 0%, rgba(147, 51, 234, 0.9) 100%)`,
    secondary: `linear-gradient(135deg, ${primitives.purple[500]} 0%, ${primitives.blue[600]} 100%)`,
    success: `linear-gradient(135deg, ${primitives.green[400]} 0%, ${primitives.green[600]} 100%)`,
    error: `linear-gradient(135deg, ${primitives.red[400]} 0%, ${primitives.red[600]} 100%)`,
  },
} as const;

// Dark mode semantic colors
export const darkColorTokens = {
  surface: {
    background: primitives.gray[900],
    foreground: primitives.gray[800],
    card: primitives.gray[800],
    hover: primitives.gray[700],
    active: primitives.gray[600],
    border: primitives.gray[700],
    divider: primitives.gray[700],
  },

  text: {
    primary: primitives.white,
    secondary: primitives.gray[300],
    tertiary: primitives.gray[400],
    disabled: primitives.gray[600],
    inverse: primitives.gray[900],
  },
} as const;

// Export primitives for edge cases (rarely used)
export { primitives };

// Type exports for autocomplete
export type ColorToken = keyof typeof colorTokens;
export type BrandColor = keyof typeof colorTokens.brand;
export type FeedbackColor = keyof typeof colorTokens.feedback;
export type SurfaceColor = keyof typeof colorTokens.surface;
export type TextColor = keyof typeof colorTokens.text;
