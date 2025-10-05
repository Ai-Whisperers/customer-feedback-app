/**
 * Typography Design Tokens
 * Font families, sizes, weights, and line heights
 */

export const typographyTokens = {
  // Font families
  fontFamily: {
    sans: ['Roboto', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
    mono: ['Fira Code', 'Monaco', 'Courier New', 'monospace'],
    display: ['Roboto', 'system-ui', 'sans-serif'],
  },

  // Font sizes (base 16px = 1rem)
  fontSize: {
    xs: '0.75rem',      // 12px
    sm: '0.875rem',     // 14px
    base: '1rem',       // 16px
    lg: '1.125rem',     // 18px
    xl: '1.25rem',      // 20px
    '2xl': '1.5rem',    // 24px
    '3xl': '1.875rem',  // 30px
    '4xl': '2.25rem',   // 36px
    '5xl': '3rem',      // 48px
    '6xl': '3.75rem',   // 60px
    '7xl': '4.5rem',    // 72px
    '8xl': '6rem',      // 96px
    '9xl': '8rem',      // 128px
  },

  // Font weights
  fontWeight: {
    thin: 100,
    extralight: 200,
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
    black: 900,
  },

  // Line heights
  lineHeight: {
    none: 1,
    tight: 1.25,
    snug: 1.375,
    normal: 1.5,
    relaxed: 1.625,
    loose: 2,
  },

  // Letter spacing
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em',
  },
} as const;

// Typography presets for common use cases
export const typographyPresets = {
  h1: {
    fontSize: typographyTokens.fontSize['5xl'],
    fontWeight: typographyTokens.fontWeight.bold,
    lineHeight: typographyTokens.lineHeight.tight,
    letterSpacing: typographyTokens.letterSpacing.tight,
  },
  h2: {
    fontSize: typographyTokens.fontSize['4xl'],
    fontWeight: typographyTokens.fontWeight.bold,
    lineHeight: typographyTokens.lineHeight.tight,
    letterSpacing: typographyTokens.letterSpacing.tight,
  },
  h3: {
    fontSize: typographyTokens.fontSize['3xl'],
    fontWeight: typographyTokens.fontWeight.semibold,
    lineHeight: typographyTokens.lineHeight.snug,
  },
  h4: {
    fontSize: typographyTokens.fontSize['2xl'],
    fontWeight: typographyTokens.fontWeight.semibold,
    lineHeight: typographyTokens.lineHeight.snug,
  },
  h5: {
    fontSize: typographyTokens.fontSize.xl,
    fontWeight: typographyTokens.fontWeight.semibold,
    lineHeight: typographyTokens.lineHeight.normal,
  },
  h6: {
    fontSize: typographyTokens.fontSize.lg,
    fontWeight: typographyTokens.fontWeight.semibold,
    lineHeight: typographyTokens.lineHeight.normal,
  },
  body: {
    fontSize: typographyTokens.fontSize.base,
    fontWeight: typographyTokens.fontWeight.normal,
    lineHeight: typographyTokens.lineHeight.relaxed,
  },
  bodySmall: {
    fontSize: typographyTokens.fontSize.sm,
    fontWeight: typographyTokens.fontWeight.normal,
    lineHeight: typographyTokens.lineHeight.normal,
  },
  caption: {
    fontSize: typographyTokens.fontSize.xs,
    fontWeight: typographyTokens.fontWeight.normal,
    lineHeight: typographyTokens.lineHeight.normal,
  },
  button: {
    fontSize: typographyTokens.fontSize.base,
    fontWeight: typographyTokens.fontWeight.medium,
    lineHeight: typographyTokens.lineHeight.normal,
    letterSpacing: typographyTokens.letterSpacing.wide,
  },
} as const;

// Type exports
export type FontSize = keyof typeof typographyTokens.fontSize;
export type FontWeight = keyof typeof typographyTokens.fontWeight;
export type LineHeight = keyof typeof typographyTokens.lineHeight;
export type LetterSpacing = keyof typeof typographyTokens.letterSpacing;
export type TypographyPreset = keyof typeof typographyPresets;
