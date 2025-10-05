import type { Config } from 'tailwindcss';
import { designTokens } from './src/design/tokens';

/**
 * Tailwind CSS Configuration
 * Integrated with centralized design token system
 */
const config: Config = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // Colors from design tokens
      colors: {
        // Brand colors
        brand: {
          primary: designTokens.colors.brand.primary,
          'primary-light': designTokens.colors.brand.primaryLight,
          'primary-dark': designTokens.colors.brand.primaryDark,
          secondary: designTokens.colors.brand.secondary,
          'secondary-light': designTokens.colors.brand.secondaryLight,
          'secondary-dark': designTokens.colors.brand.secondaryDark,
        },
        // Keep 'primary' alias for backward compatibility
        primary: {
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
        // Feedback/status colors
        success: designTokens.colors.feedback.success,
        error: designTokens.colors.feedback.error,
        warning: designTokens.colors.feedback.warning,
        info: designTokens.colors.feedback.info,
      },

      // Spacing from design tokens
      spacing: designTokens.spacing,

      // Typography
      fontFamily: {
        sans: designTokens.typography.fontFamily.sans,
        mono: designTokens.typography.fontFamily.mono,
        display: designTokens.typography.fontFamily.display,
      },
      fontSize: designTokens.typography.fontSize,
      fontWeight: designTokens.typography.fontWeight,
      lineHeight: designTokens.typography.lineHeight,
      letterSpacing: designTokens.typography.letterSpacing,

      // Borders
      borderRadius: designTokens.borders.radius,
      borderWidth: designTokens.borders.width,

      // Shadows
      boxShadow: {
        ...designTokens.shadows,
        // Glass shadows
        'glass-sm': designTokens.shadows.glass.sm,
        'glass-base': designTokens.shadows.glass.base,
        'glass-md': designTokens.shadows.glass.md,
        'glass-lg': designTokens.shadows.glass.lg,
        // Colored shadows
        'primary': designTokens.shadows.colored.primary,
        'secondary': designTokens.shadows.colored.secondary,
        'success': designTokens.shadows.colored.success,
        'error': designTokens.shadows.colored.error,
      },

      // Backdrop blur
      backdropBlur: designTokens.backdropBlur,

      // Opacity
      opacity: designTokens.opacity,

      // Animations from design tokens
      transitionDuration: designTokens.animations.duration,
      transitionTimingFunction: designTokens.animations.easing,

      // Custom animations (merged with existing)
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-slow': 'bounce 2s infinite',
        // New token-based animations
        'scale-in': 'scaleIn 150ms cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'scale-out': 'scaleOut 150ms cubic-bezier(0.4, 0, 1, 1)',
      },

      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        scaleOut: {
          '0%': { transform: 'scale(1)', opacity: '1' },
          '100%': { transform: 'scale(0.95)', opacity: '0' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};

export default config;
