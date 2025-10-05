/**
 * Shadow Design Tokens
 * Elevation system for depth and hierarchy
 */

export const shadowTokens = {
  // No shadow
  none: 'none',

  // Standard shadows (light theme)
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',

  // Inner shadow
  inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',

  // Glass/frosted glass shadows
  glass: {
    sm: '0 2px 4px 0 rgb(0 0 0 / 0.05), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    base: '0 4px 8px 0 rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    md: '0 8px 16px -2px rgb(0 0 0 / 0.1), 0 4px 8px -4px rgb(0 0 0 / 0.1)',
    lg: '0 12px 24px -4px rgb(0 0 0 / 0.15), 0 6px 12px -6px rgb(0 0 0 / 0.1)',
  },

  // Colored shadows (for buttons, cards with brand colors)
  colored: {
    primary: '0 10px 25px -5px rgba(14, 165, 233, 0.3), 0 4px 6px -4px rgba(14, 165, 233, 0.2)',
    secondary: '0 10px 25px -5px rgba(147, 51, 234, 0.3), 0 4px 6px -4px rgba(147, 51, 234, 0.2)',
    success: '0 10px 25px -5px rgba(34, 197, 94, 0.3), 0 4px 6px -4px rgba(34, 197, 94, 0.2)',
    error: '0 10px 25px -5px rgba(239, 68, 68, 0.3), 0 4px 6px -4px rgba(239, 68, 68, 0.2)',
  },
} as const;

// Dark mode shadows (more subtle)
export const darkShadowTokens = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.3)',
  base: '0 1px 3px 0 rgb(0 0 0 / 0.4), 0 1px 2px -1px rgb(0 0 0 / 0.4)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.4), 0 2px 4px -2px rgb(0 0 0 / 0.4)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.4), 0 4px 6px -4px rgb(0 0 0 / 0.4)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.4), 0 8px 10px -6px rgb(0 0 0 / 0.4)',
  '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.5)',
} as const;

// Semantic elevation levels
export const elevation = {
  0: shadowTokens.none,
  1: shadowTokens.sm,
  2: shadowTokens.base,
  3: shadowTokens.md,
  4: shadowTokens.lg,
  5: shadowTokens.xl,
  6: shadowTokens['2xl'],
} as const;

// Type exports
export type Shadow = keyof typeof shadowTokens;
export type Elevation = keyof typeof elevation;
