/**
 * useNotifications Hook
 * Convenient hook for notifications management
 */

import { useUIContext } from '@/contexts';

export const useNotifications = () => {
  const { state, addNotification, removeNotification } = useUIContext();

  const notify = {
    info: (message: string, duration?: number) => {
      addNotification({ type: 'info', message, duration });
    },
    success: (message: string, duration?: number) => {
      addNotification({ type: 'success', message, duration });
    },
    warning: (message: string, duration?: number) => {
      addNotification({ type: 'warning', message, duration });
    },
    error: (message: string, duration?: number) => {
      addNotification({ type: 'error', message, duration });
    },
  };

  return {
    notifications: state.notifications,
    addNotification,
    removeNotification,
    notify,
    hasNotifications: state.notifications.length > 0,
  };
};
