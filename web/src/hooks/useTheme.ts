/**
 * useTheme Hook
 * Convenient hook for theme management
 */

import { useUIContext } from '@/contexts';

export const useTheme = () => {
  const { theme, setTheme, toggleTheme, state } = useUIContext();

  return {
    theme,
    setTheme,
    toggleTheme,
    isDark: theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches),
    isLight: theme === 'light' || (theme === 'system' && !window.matchMedia('(prefers-color-scheme: dark)').matches),
    isSystem: theme === 'system',
    highContrast: state.highContrast,
  };
};
