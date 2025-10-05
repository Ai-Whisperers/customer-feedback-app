/**
 * Spacing Design Tokens
 * Base scale: 4px (0.25rem)
 * Consistent spacing for margins, padding, gaps, etc.
 */

export const spacingTokens = {
  0: '0',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  7: '1.75rem',   // 28px
  8: '2rem',      // 32px
  9: '2.25rem',   // 36px
  10: '2.5rem',   // 40px
  11: '2.75rem',  // 44px
  12: '3rem',     // 48px
  14: '3.5rem',   // 56px
  16: '4rem',     // 64px
  20: '5rem',     // 80px
  24: '6rem',     // 96px
  28: '7rem',     // 112px
  32: '8rem',     // 128px
  36: '9rem',     // 144px
  40: '10rem',    // 160px
  44: '11rem',    // 176px
  48: '12rem',    // 192px
  52: '13rem',    // 208px
  56: '14rem',    // 224px
  60: '15rem',    // 240px
  64: '16rem',    // 256px
  72: '18rem',    // 288px
  80: '20rem',    // 320px
  96: '24rem',    // 384px
} as const;

// Semantic spacing tokens for common use cases
export const semanticSpacing = {
  // Component spacing
  componentPadding: {
    xs: spacingTokens[2],   // 8px
    sm: spacingTokens[3],   // 12px
    base: spacingTokens[4], // 16px
    lg: spacingTokens[6],   // 24px
    xl: spacingTokens[8],   // 32px
  },

  // Layout spacing
  layout: {
    gap: spacingTokens[4],     // 16px
    gutter: spacingTokens[6],  // 24px
    section: spacingTokens[12], // 48px
    page: spacingTokens[16],   // 64px
  },

  // Element spacing
  element: {
    iconGap: spacingTokens[2],   // 8px
    buttonPadding: spacingTokens[4], // 16px
    inputPadding: spacingTokens[3],  // 12px
    cardPadding: spacingTokens[6],   // 24px
  },
} as const;

// Type exports
export type Spacing = keyof typeof spacingTokens;
export type ComponentPadding = keyof typeof semanticSpacing.componentPadding;
export type LayoutSpacing = keyof typeof semanticSpacing.layout;
