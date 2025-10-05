/**
 * Opacity Design Tokens
 * Transparency values for glass design system and overlays
 */

export const opacityTokens = {
  // Standard opacity scale
  0: '0',
  5: '0.05',
  10: '0.1',
  20: '0.2',
  25: '0.25',
  30: '0.3',
  40: '0.4',
  50: '0.5',
  60: '0.6',
  70: '0.7',
  75: '0.75',
  80: '0.8',
  90: '0.9',
  95: '0.95',
  100: '1',
} as const;

// Glass Design System opacity values
export const glassOpacity = {
  // Glass surfaces (semi-transparent backgrounds)
  light: opacityTokens[80],   // 0.8 - Light glass
  medium: opacityTokens[60],  // 0.6 - Medium glass
  heavy: opacityTokens[40],   // 0.4 - Heavy glass

  // Backdrop blur opacity (for overlays)
  overlay: {
    light: opacityTokens[20],   // 0.2
    base: opacityTokens[40],    // 0.4
    heavy: opacityTokens[60],   // 0.6
  },

  // Component-specific
  border: opacityTokens[20],    // 0.2 - Subtle glass borders
  shadow: opacityTokens[10],    // 0.1 - Glass shadow
} as const;

// Backdrop blur values (for glass effects)
export const backdropBlur = {
  none: '0',
  sm: '2px',
  base: '8px',
  md: '12px',
  lg: '16px',
  xl: '24px',
  '2xl': '40px',
  '3xl': '64px',
} as const;

// Semantic opacity presets
export const opacityPresets = {
  disabled: opacityTokens[50],       // 0.5 - Disabled state
  hover: opacityTokens[90],          // 0.9 - Hover state
  active: opacityTokens[75],         // 0.75 - Active/pressed state
  loading: opacityTokens[60],        // 0.6 - Loading state
  placeholder: opacityTokens[40],    // 0.4 - Placeholder text
} as const;

// Type exports
export type Opacity = keyof typeof opacityTokens;
export type GlassOpacity = keyof typeof glassOpacity;
export type BackdropBlur = keyof typeof backdropBlur;
