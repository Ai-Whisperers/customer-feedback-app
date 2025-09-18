import React from 'react';
import { cn } from '@/utils/utils';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'light' | 'dark' | 'gradient';
  padding?: 'sm' | 'md' | 'lg' | 'xl';
  blur?: 'sm' | 'md' | 'lg';
  border?: boolean;
  shadow?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  variant = 'light',
  padding = 'lg',
  blur = 'md',
  border = true,
  shadow = 'lg',
}) => {
  const paddingClasses = {
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
    xl: 'p-8',
  };

  const blurClasses = {
    sm: 'backdrop-blur-sm',
    md: 'backdrop-blur-md',
    lg: 'backdrop-blur-lg',
  };

  const shadowClasses = {
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl',
    '2xl': 'shadow-2xl',
  };

  const variantClasses = {
    light: 'bg-white/80 dark:bg-gray-900/80 text-gray-900 dark:text-gray-100',
    dark: 'bg-gray-800/80 dark:bg-gray-950/80 text-gray-100 dark:text-gray-100',
    gradient: 'bg-gradient-to-br from-white/90 via-white/80 to-gray-100/70 dark:from-gray-900/90 dark:via-gray-800/80 dark:to-gray-700/70',
  };

  const borderClass = border ? 'border border-white/20' : '';

  return (
    <div
      className={cn(
        // Base styles
        'card-base',
        // Padding
        paddingClasses[padding],
        // Blur effect
        blurClasses[blur],
        // Shadow
        shadowClasses[shadow],
        // Variant
        variantClasses[variant],
        // Border
        borderClass,
        // Custom className
        className
      )}
    >
      {children}
    </div>
  );
};