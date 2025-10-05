import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import type { UIContextValue, UIState, Theme, AnimationSpeed, Notification, UIPreferences } from '@/types';

const DEFAULT_PREFERENCES: UIPreferences = {
  theme: 'system',
  animationsEnabled: true,
  animationSpeed: 'normal',
  reducedMotion: false,
  fontSize: 'base',
  highContrast: false,
};

const DEFAULT_STATE: UIState = {
  ...DEFAULT_PREFERENCES,
  isSidebarOpen: false,
  isModalOpen: false,
  activeModal: null,
  notifications: [],
};

const STORAGE_KEY = 'app_ui_preferences';

const UIContext = createContext<UIContextValue | null>(null);

export const UIProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<UIState>(() => {
    // Load preferences from localStorage
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          return { ...DEFAULT_STATE, ...parsed };
        } catch (error) {
          console.error('Failed to parse stored UI preferences:', error);
        }
      }
    }
    return DEFAULT_STATE;
  });

  // Sync preferences to localStorage
  useEffect(() => {
    const preferences: UIPreferences = {
      theme: state.theme,
      animationsEnabled: state.animationsEnabled,
      animationSpeed: state.animationSpeed,
      reducedMotion: state.reducedMotion,
      fontSize: state.fontSize,
      highContrast: state.highContrast,
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
  }, [state]);

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement;

    if (state.theme === 'system') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.toggle('dark', isDark);
    } else {
      root.classList.toggle('dark', state.theme === 'dark');
    }
  }, [state.theme]);

  // Apply font size to document
  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute('data-font-size', state.fontSize);
  }, [state.fontSize]);

  // Apply high contrast mode
  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle('high-contrast', state.highContrast);
  }, [state.highContrast]);

  // Apply reduced motion
  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute('data-animation-speed', state.animationSpeed);

    if (state.reducedMotion || state.animationSpeed === 'none') {
      root.classList.add('reduce-motion');
    } else {
      root.classList.remove('reduce-motion');
    }
  }, [state.animationSpeed, state.reducedMotion]);

  // Listen for system theme changes
  useEffect(() => {
    if (state.theme !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => {
      document.documentElement.classList.toggle('dark', e.matches);
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [state.theme]);

  // Theme functions
  const setTheme = useCallback((theme: Theme) => {
    setState(prev => ({ ...prev, theme }));
  }, []);

  const toggleTheme = useCallback(() => {
    setState(prev => ({
      ...prev,
      theme: prev.theme === 'light' ? 'dark' : prev.theme === 'dark' ? 'system' : 'light',
    }));
  }, []);

  // Animation functions
  const setAnimationsEnabled = useCallback((enabled: boolean) => {
    setState(prev => ({ ...prev, animationsEnabled: enabled }));
  }, []);

  const setAnimationSpeed = useCallback((speed: AnimationSpeed) => {
    setState(prev => ({ ...prev, animationSpeed: speed }));
  }, []);

  const setReducedMotion = useCallback((enabled: boolean) => {
    setState(prev => ({ ...prev, reducedMotion: enabled }));
  }, []);

  // Accessibility functions
  const setFontSize = useCallback((size: UIPreferences['fontSize']) => {
    setState(prev => ({ ...prev, fontSize: size }));
  }, []);

  const setHighContrast = useCallback((enabled: boolean) => {
    setState(prev => ({ ...prev, highContrast: enabled }));
  }, []);

  // UI state functions
  const toggleSidebar = useCallback(() => {
    setState(prev => ({ ...prev, isSidebarOpen: !prev.isSidebarOpen }));
  }, []);

  const openModal = useCallback((modalId: string) => {
    setState(prev => ({
      ...prev,
      isModalOpen: true,
      activeModal: modalId,
    }));
  }, []);

  const closeModal = useCallback(() => {
    setState(prev => ({
      ...prev,
      isModalOpen: false,
      activeModal: null,
    }));
  }, []);

  // Notification functions
  const addNotification = useCallback((notification: Omit<Notification, 'id' | 'timestamp'>) => {
    const id = `notif-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newNotification: Notification = {
      ...notification,
      id,
      timestamp: Date.now(),
    };

    setState(prev => ({
      ...prev,
      notifications: [...prev.notifications, newNotification],
    }));

    // Auto-remove notification after duration
    if (notification.duration) {
      setTimeout(() => {
        removeNotification(id);
      }, notification.duration);
    }
  }, []);

  const removeNotification = useCallback((id: string) => {
    setState(prev => ({
      ...prev,
      notifications: prev.notifications.filter(n => n.id !== id),
    }));
  }, []);

  // Reset to defaults
  const resetPreferences = useCallback(() => {
    setState(DEFAULT_STATE);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const value = useMemo<UIContextValue>(
    () => ({
      state,
      theme: state.theme,
      setTheme,
      toggleTheme,
      setAnimationsEnabled,
      setAnimationSpeed,
      setReducedMotion,
      setFontSize,
      setHighContrast,
      toggleSidebar,
      openModal,
      closeModal,
      addNotification,
      removeNotification,
      resetPreferences,
    }),
    [
      state,
      setTheme,
      toggleTheme,
      setAnimationsEnabled,
      setAnimationSpeed,
      setReducedMotion,
      setFontSize,
      setHighContrast,
      toggleSidebar,
      openModal,
      closeModal,
      addNotification,
      removeNotification,
      resetPreferences,
    ]
  );

  return <UIContext.Provider value={value}>{children}</UIContext.Provider>;
};

export const useUIContext = (): UIContextValue => {
  const context = useContext(UIContext);
  if (!context) {
    throw new Error('useUIContext must be used within UIProvider');
  }
  return context;
};
