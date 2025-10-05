/**
 * UI State Types
 * Global state for UI preferences, theming, and frontend behavior
 */

export type Theme = 'light' | 'dark' | 'system';

export type Language = 'es' | 'en';

export type AnimationSpeed = 'none' | 'reduced' | 'normal' | 'fast';

export interface UIPreferences {
  theme: Theme;
  language: Language;
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
  language: Language;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  setLanguage: (language: Language) => void;
  toggleLanguage: () => void;
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
