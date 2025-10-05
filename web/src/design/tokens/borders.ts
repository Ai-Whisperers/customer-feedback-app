/**
 * Border Design Tokens
 * Border radius, widths, and styles
 */

export const borderTokens = {
  // Border radius
  radius: {
    none: '0',
    sm: '0.125rem',   // 2px
    base: '0.25rem',  // 4px
    md: '0.375rem',   // 6px
    lg: '0.5rem',     // 8px
    xl: '0.75rem',    // 12px
    '2xl': '1rem',    // 16px
    '3xl': '1.5rem',  // 24px
    full: '9999px',   // Fully rounded (pills, circles)
  },

  // Border widths
  width: {
    none: '0',
    thin: '1px',
    base: '2px',
    thick: '4px',
    thicker: '8px',
  },

  // Border styles
  style: {
    solid: 'solid',
    dashed: 'dashed',
    dotted: 'dotted',
    double: 'double',
    none: 'none',
  },
} as const;

// Semantic border presets for common use cases
export const borderPresets = {
  // Card borders
  card: {
    radius: borderTokens.radius.xl,
    width: borderTokens.width.thin,
    style: borderTokens.style.solid,
  },

  // Button borders
  button: {
    radius: borderTokens.radius.lg,
    width: borderTokens.width.base,
    style: borderTokens.style.solid,
  },

  // Input borders
  input: {
    radius: borderTokens.radius.md,
    width: borderTokens.width.thin,
    style: borderTokens.style.solid,
  },

  // Badge borders
  badge: {
    radius: borderTokens.radius.full,
    width: borderTokens.width.thin,
    style: borderTokens.style.solid,
  },

  // Modal borders
  modal: {
    radius: borderTokens.radius['2xl'],
    width: borderTokens.width.none,
    style: borderTokens.style.solid,
  },

  // Glass components (subtle borders)
  glass: {
    radius: borderTokens.radius.xl,
    width: borderTokens.width.thin,
    style: borderTokens.style.solid,
  },
} as const;

// Type exports
export type BorderRadius = keyof typeof borderTokens.radius;
export type BorderWidth = keyof typeof borderTokens.width;
export type BorderStyle = keyof typeof borderTokens.style;
export type BorderPreset = keyof typeof borderPresets;
