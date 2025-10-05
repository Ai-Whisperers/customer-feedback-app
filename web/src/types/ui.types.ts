/**
 * UI State Types
 * Global state for UI preferences, theming, and frontend behavior
 * NOTE: Language/i18n moved to dedicated i18nContext
 */

export type Theme = 'light' | 'dark' | 'system';

export type AnimationSpeed = 'none' | 'reduced' | 'normal' | 'fast';

export interface UIPreferences {
  theme: Theme;
  animationsEnabled: boolean;
  animationSpeed: AnimationSpeed;
  reducedMotion: boolean;
  fontSize: 'sm' | 'base' | 'lg' | 'xl';
  highContrast: boolean;
}

export interface UIState extends UIPreferences {
  isSidebarOpen: boolean;
  isModalOpen: boolean;
  activeModal: string | null;
  notifications: Notification[];
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  message: string;
  duration?: number;
  timestamp: number;
}

export interface UIContextValue {
  state: UIState;
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  setAnimationsEnabled: (enabled: boolean) => void;
  setAnimationSpeed: (speed: AnimationSpeed) => void;
  setReducedMotion: (enabled: boolean) => void;
  setFontSize: (size: UIPreferences['fontSize']) => void;
  setHighContrast: (enabled: boolean) => void;
  toggleSidebar: () => void;
  openModal: (modalId: string) => void;
  closeModal: () => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  resetPreferences: () => void;
}
