/**
 * Animation Design Tokens
 * Motion durations, easing functions, and transitions
 */

export const animationTokens = {
  // Duration tokens
  duration: {
    instant: '0ms',
    fast: '150ms',
    base: '300ms',
    slow: '500ms',
    slower: '700ms',
    slowest: '1000ms',
  },

  // Easing functions
  easing: {
    linear: 'linear',
    ease: 'ease',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    // Custom easing for smooth animations
    smooth: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
    spring: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },

  // Common transitions (property + duration + easing)
  transition: {
    // Basic transitions
    colors: 'color 300ms cubic-bezier(0.4, 0, 0.2, 1), background-color 300ms cubic-bezier(0.4, 0, 0.2, 1), border-color 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    opacity: 'opacity 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    transform: 'transform 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    all: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',

    // Component-specific
    button: 'background-color 150ms cubic-bezier(0.4, 0, 0.2, 1), transform 150ms cubic-bezier(0.4, 0, 0.2, 1), box-shadow 150ms cubic-bezier(0.4, 0, 0.2, 1)',
    modal: 'opacity 300ms cubic-bezier(0.4, 0, 0.2, 1), transform 300ms cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    dropdown: 'opacity 150ms cubic-bezier(0, 0, 0.2, 1), transform 150ms cubic-bezier(0, 0, 0.2, 1)',
    tooltip: 'opacity 150ms cubic-bezier(0.4, 0, 0.2, 1)',
  },

  // Animation delays
  delay: {
    none: '0ms',
    short: '100ms',
    base: '200ms',
    long: '300ms',
  },
} as const;

// Animation presets for common use cases
export const animationPresets = {
  fadeIn: {
    from: { opacity: 0 },
    to: { opacity: 1 },
    duration: animationTokens.duration.base,
    easing: animationTokens.easing.easeOut,
  },
  fadeOut: {
    from: { opacity: 1 },
    to: { opacity: 0 },
    duration: animationTokens.duration.base,
    easing: animationTokens.easing.easeIn,
  },
  slideUp: {
    from: { transform: 'translateY(10px)', opacity: 0 },
    to: { transform: 'translateY(0)', opacity: 1 },
    duration: animationTokens.duration.base,
    easing: animationTokens.easing.easeOut,
  },
  slideDown: {
    from: { transform: 'translateY(-10px)', opacity: 0 },
    to: { transform: 'translateY(0)', opacity: 1 },
    duration: animationTokens.duration.base,
    easing: animationTokens.easing.easeOut,
  },
  scaleIn: {
    from: { transform: 'scale(0.95)', opacity: 0 },
    to: { transform: 'scale(1)', opacity: 1 },
    duration: animationTokens.duration.fast,
    easing: animationTokens.easing.spring,
  },
  scaleOut: {
    from: { transform: 'scale(1)', opacity: 1 },
    to: { transform: 'scale(0.95)', opacity: 0 },
    duration: animationTokens.duration.fast,
    easing: animationTokens.easing.easeIn,
  },
} as const;

// Reduced motion support (for accessibility)
export const reducedMotion = {
  duration: {
    instant: '0ms',
    fast: '0ms',
    base: '0ms',
    slow: '0ms',
  },
  transition: {
    colors: 'none',
    opacity: 'none',
    transform: 'none',
    all: 'none',
  },
} as const;

// Type exports
export type AnimationDuration = keyof typeof animationTokens.duration;
export type AnimationEasing = keyof typeof animationTokens.easing;
export type AnimationTransition = keyof typeof animationTokens.transition;
export type AnimationPreset = keyof typeof animationPresets;
