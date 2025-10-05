/**
 * Design Tokens - Centralized Design System
 * Single source of truth for all design values
 * B2B enterprise-ready with multi-tenant support
 */

// Import all tokens
import { colorTokens, darkColorTokens } from './colors';
import { typographyTokens, typographyPresets } from './typography';
import { spacingTokens, semanticSpacing } from './spacing';
import { shadowTokens, darkShadowTokens, elevation } from './shadows';
import { animationTokens, animationPresets, reducedMotion } from './animations';
import { borderTokens, borderPresets } from './borders';
import { opacityTokens, glassOpacity, backdropBlur, opacityPresets } from './opacity';

// Re-export all tokens
export {
  colorTokens,
  darkColorTokens,
  primitives,
  type ColorToken,
  type BrandColor,
  type FeedbackColor,
  type SurfaceColor,
  type TextColor,
} from './colors';

export {
  typographyTokens,
  typographyPresets,
  type FontSize,
  type FontWeight,
  type LineHeight,
  type LetterSpacing,
  type TypographyPreset,
} from './typography';

export {
  spacingTokens,
  semanticSpacing,
  type Spacing,
  type ComponentPadding,
  type LayoutSpacing,
} from './spacing';

export {
  shadowTokens,
  darkShadowTokens,
  elevation,
  type Shadow,
  type Elevation,
} from './shadows';

export {
  animationTokens,
  animationPresets,
  reducedMotion,
  type AnimationDuration,
  type AnimationEasing,
  type AnimationTransition,
  type AnimationPreset,
} from './animations';

export {
  borderTokens,
  borderPresets,
  type BorderRadius,
  type BorderWidth,
  type BorderStyle,
  type BorderPreset,
} from './borders';

export {
  opacityTokens,
  glassOpacity,
  backdropBlur,
  opacityPresets,
  type Opacity,
  type GlassOpacity,
  type BackdropBlur,
} from './opacity';

// Consolidated design tokens object
export const designTokens = {
  colors: colorTokens,
  colorsDark: darkColorTokens,
  typography: typographyTokens,
  typographyPresets,
  spacing: spacingTokens,
  semanticSpacing,
  shadows: shadowTokens,
  shadowsDark: darkShadowTokens,
  elevation,
  animations: animationTokens,
  animationPresets,
  reducedMotion,
  borders: borderTokens,
  borderPresets,
  opacity: opacityTokens,
  glassOpacity,
  backdropBlur,
  opacityPresets,
} as const;

// Helper function to get token value by path
export function getToken(path: string): string | number | object {
  const parts = path.split('.');
  let value: any = designTokens;

  for (const part of parts) {
    if (value && typeof value === 'object' && part in value) {
      value = value[part];
    } else {
      console.warn(`Token path "${path}" not found`);
      return '';
    }
  }

  return value;
}

// Type for all design tokens
export type DesignTokens = typeof designTokens;

// Default export
export default designTokens;
